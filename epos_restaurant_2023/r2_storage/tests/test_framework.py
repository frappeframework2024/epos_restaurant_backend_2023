"""Opt-in, rollback-only checks against the installed site's actual File controller.

Run on a development/test site with this app installed (R2 is fully mocked):
bench --site SITE execute epos_restaurant_2023.r2_storage.tests.test_framework.run
This creates temporary database rows and local files; all rows are rolled back.
"""

import base64
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import frappe
from PIL import Image

from epos_restaurant_2023.r2_storage import client, file_handler, storage
from epos_restaurant_2023.r2_storage.tests.test_storage import SETTINGS


def png():
	stream = io.BytesIO()
	Image.new("RGB", (4, 4), "blue").save(stream, format="PNG")
	return stream.getvalue()


class FrameworkTests(unittest.TestCase):
	def setUp(self):
		self.original_conf = dict(frappe.conf)
		frappe.conf.r2_storage = frappe._dict(SETTINGS)
		self.addCleanup(self.restore_config)
		self.temp = tempfile.TemporaryDirectory()
		self.addCleanup(self.temp.cleanup)
		self.s3 = MagicMock()
		self.s3.head_object.return_value = {"Metadata": client.ownership()}
		hooks = frappe.get_doc_hooks()
		self.assertIn(
			"epos_restaurant_2023.r2_storage.file_handler.sync_parent_attachments",
			hooks["*"]["on_update"],
		)
		for patcher in (
			patch.object(frappe, "form_dict", frappe._dict()),
			patch.object(frappe, "get_doc_hooks", return_value={
				"*": {"on_update": ["epos_restaurant_2023.r2_storage.file_handler.sync_parent_attachments"]},
				"File": hooks["File"],
			}),
			patch("frappe.model.document.run_server_script_for_doc_event"),
			patch.object(client, "get_client", return_value=self.s3),
			patch.object(storage, "journal_dir", return_value=Path(self.temp.name)),
		):
			patcher.start()
			self.addCleanup(patcher.stop)
		# Cleanup runs before stopping mocks, so no operation can reach Cloudflare.
		self.addCleanup(lambda: frappe.db.rollback())
		self.product = self.make_product()
		self.assertIsInstance(frappe.new_doc("File"), file_handler.R2File)

	def make_product(self, **values):
		name = "R2-TEST-" + uuid4().hex
		doc = frappe.get_doc({
			"doctype": "Product",
			"name": name,
			"product_code": name,
			"product_name_en": "R2 rollback test",
			**values,
		})
		doc.flags.update(
			ignore_mandatory=True,
			ignore_validate=True,
			ignore_before_save=True,
			ignore_on_update=True,
		)
		return doc.insert(ignore_permissions=True)

	def restore_config(self):
		frappe.conf.clear()
		frappe.conf.update(self.original_conf)

	def file(self, **values):
		data = {
			"doctype": "File",
			"file_name": f"r2-{uuid4().hex}.png",
			"content": png(),
			"is_private": 0,
			"attached_to_doctype": "Product",
			"attached_to_name": self.product.name,
		}
		data.update(values)
		return frappe.get_doc(data).insert(ignore_permissions=True)

	def test_standard_upload_field_and_multiple_attachments(self):
		main = self.file(attached_to_field="photo")
		self.assertTrue(main.file_url.startswith(SETTINGS["public_url"]))
		self.product.photo = main.file_url
		self.product.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Product", self.product.name, "photo"), main.file_url)
		first, second = self.file(), self.file()
		self.assertNotEqual(first.file_url, second.file_url)
		self.assertEqual(frappe.db.count("File", {"attached_to_name": self.product.name}), 3)
		self.assertEqual(self.s3.put_object.call_count, 3)
		self.assertEqual(frappe.get_doc("File", main.name).file_url, main.file_url)

	def test_draft_attachment_relinked_on_insert(self):
		temp_name = "new-product-" + uuid4().hex
		file = self.file(attached_to_name=temp_name, attached_to_field="photo")
		self.assertTrue(file.file_url.startswith("/files/"))
		self.s3.put_object.assert_not_called()
		product = self.make_product(photo=file.file_url, __temporary_name=temp_name)
		file.reload()
		self.assertTrue(file.file_url.startswith(SETTINGS["public_url"]))
		self.assertEqual(product.photo, file.file_url)
		self.assertEqual(frappe.db.get_value("Product", product.name, "photo"), file.file_url)
		self.assertEqual(file.attached_to_name, product.name)
		self.s3.put_object.assert_called_once()

	def test_legacy_save_file_api(self):
		from frappe.utils.file_manager import save_file

		file = save_file("r2-legacy.png", png(), "Product", self.product.name, is_private=0, df="photo")
		self.assertTrue(file.file_url.startswith(SETTINGS["public_url"]))
		self.s3.put_object.assert_called_once()

	def test_camera_upload_requires_product_write_permission(self):
		from epos_restaurant_2023.inventory.doctype.product.product import upload_photo

		image = "data:image/png;base64," + base64.b64encode(png()).decode()
		with (
			patch.object(frappe, "get_doc", return_value=self.product),
			patch.object(self.product, "check_permission", side_effect=frappe.PermissionError),
			self.assertRaises(frappe.PermissionError),
		):
			upload_photo(image, self.product.name)
		self.s3.put_object.assert_not_called()

	def test_detected_image_type_overrides_filename(self):
		file = self.file(file_name="actually-an-image.pdf")
		self.assertTrue(file.file_url.endswith(".png"))
		self.assertEqual(file.file_type, "PNG")
		self.assertEqual(self.s3.put_object.call_args.kwargs["Body"], png())

	def test_large_upload_stores_optimized_size_and_format(self):
		from epos_restaurant_2023.r2_storage.tests.test_image_optimizer import large_png

		frappe.conf.r2_storage.optimize_images = True
		original = large_png()
		previous_size = frappe.form_dict.get("file_size")
		try:
			frappe.form_dict.file_size = len(original)
			file = self.file(content=original, file_name="large-product.png")
		finally:
			frappe.form_dict.file_size = previous_size
		body = self.s3.put_object.call_args.kwargs["Body"]
		self.assertLess(len(body), len(original))
		self.assertTrue(file.file_name.endswith(".webp"))
		self.assertTrue(file.file_url.endswith(".webp"))
		self.assertEqual(file.file_type, "WEBP")
		self.assertEqual(frappe.db.get_value("File", file.name, "file_size"), len(body))
		self.product.photo = file.file_url
		self.product.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Product", self.product.name, "photo"), file.file_url)

	def test_parent_update_promotes_existing_local_photo(self):
		frappe.conf.r2_storage.enabled = False
		file = self.file(attached_to_field="photo")
		self.assertTrue(file.file_url.startswith("/files/"))
		frappe.conf.r2_storage.enabled = True
		self.product.photo = file.file_url
		self.product.save(ignore_permissions=True)
		file.reload()
		self.assertEqual(self.product.photo, file.file_url)
		self.assertTrue(file.file_url.startswith(SETTINGS["public_url"]))
		self.s3.put_object.assert_called_once()

	def test_actual_rollback_cleanup(self):
		file = self.file()
		frappe.db.rollback()
		self.assertFalse(frappe.db.exists("File", file.name))
		self.s3.delete_object.assert_called_once()
		self.assertEqual(list(Path(self.temp.name).glob("*.json")), [])

	def test_upload_failure_does_not_create_file_record(self):
		self.s3.put_object.side_effect = TimeoutError("secret details")
		with self.assertRaises(frappe.ValidationError):
			self.file()
		self.assertEqual(frappe.db.count("File", {"attached_to_name": self.product.name}), 0)

	def test_file_deletion_waits_for_commit_callback(self):
		frappe.conf.r2_storage.delete_on_file_delete = True
		file = self.file()
		# Settle the upload intent while File exists; no real DB commit is needed.
		frappe.db.after_commit.run()
		file.delete(ignore_permissions=True)
		self.s3.delete_object.assert_not_called()
		frappe.db.after_commit.run()
		self.s3.delete_object.assert_called_once()

	def test_replacement_updates_product_photo(self):
		file = self.file(attached_to_field="photo")
		self.product.photo = file.file_url
		self.product.save(ignore_permissions=True)
		old_url = file.file_url
		file.save_file(content=png(), overwrite=True)
		file.save(ignore_permissions=True)
		self.assertNotEqual(file.file_url, old_url)
		self.assertEqual(frappe.db.get_value("Product", self.product.name, "photo"), file.file_url)
		self.s3.delete_object.assert_not_called()

	def test_private_and_pdf_stay_local(self):
		from pypdf import PdfWriter

		private = self.file(is_private=1)
		self.assertTrue(private.file_url.startswith("/private/files/"))
		stream = io.BytesIO()
		writer = PdfWriter()
		writer.add_blank_page(width=72, height=72)
		writer.write(stream)
		pdf = self.file(file_name="r2-document.pdf", content=stream.getvalue())
		self.assertTrue(pdf.file_url.startswith("/files/"))
		self.s3.put_object.assert_not_called()


def run():
	result = unittest.TextTestRunner(verbosity=2).run(
		unittest.defaultTestLoader.loadTestsFromTestCase(FrameworkTests)
	)
	if not result.wasSuccessful():
		raise AssertionError("R2 framework tests failed")
	return {"tests": result.testsRun, "passed": True}
