"""Store public File uploads and linked local images in Cloudflare R2."""

import io
from pathlib import PurePosixPath

import frappe
from frappe.core.doctype.file.file import File
from frappe.model.document import Document
from frappe.utils import cint
from frappe.utils.image import strip_exif_data

from . import client, storage
from .config import doctype_folder, enabled, fail, get_config, setting
from .image_optimizer import optimize_image
from .utils import image_type, managed_key


def eligibility(doc):
	if doc.is_folder or cint(doc.is_private) or frappe.session.user == "Guest":
		return None
	if not doc.attached_to_doctype or not doc.attached_to_name:
		return None
	folder = doctype_folder(doc.attached_to_doctype)
	if not folder or not enabled():
		return None
	if str(doc.attached_to_name).startswith("new-") and not frappe.db.exists(
		doc.attached_to_doctype, doc.attached_to_name
	):
		return None  # Frappe links draft attachments to the saved name after insert.
	return get_config(), folder


def attachment_rows(doc):
	yield doc
	for df in doc.meta.get_table_fields():
		yield from doc.get(df.fieldname) or []


def update_references(doc, old_url):
	"""Use metadata and equality checks; never overwrite a user's replacement field."""
	if not old_url or not doc.attached_to_doctype or not doc.attached_to_name:
		return
	if not frappe.db.exists(doc.attached_to_doctype, doc.attached_to_name):
		return
	parent = frappe.get_doc(doc.attached_to_doctype, doc.attached_to_name)
	for row in attachment_rows(parent):
		for df in row.meta.get("fields", {"fieldtype": ["in", ["Attach", "Attach Image"]]}):
			if row.get(df.fieldname) == old_url:
				row.db_set(df.fieldname, doc.file_url, update_modified=False)
				replacements = getattr(frappe.local, "r2_url_replacements", None)
				if replacements is None:
					replacements = frappe.local.r2_url_replacements = {}
				replacements[(row.doctype, row.name, df.fieldname, old_url)] = doc.file_url
				if row is parent:
					if row.doctype == "Product" and df.fieldname == row.meta.image_field:
						for doctype in ("Temp Product Menu", "eMenu Popular Products"):
							if frappe.db.exists("DocType", doctype):
								frappe.db.set_value(
									doctype, {"product_code": row.name, "photo": old_url},
									"photo", doc.file_url, update_modified=False,
								)
					if not doc.attached_to_field:
						doc.attached_to_field = df.fieldname
						frappe.db.set_value(
							"File", doc.name, "attached_to_field", df.fieldname, update_modified=False
						)


class R2FileMixin(Document):
	def get_content(self, *args, **kwargs):
		if not self.get("content") and self.is_remote_file and enabled():
			config = get_config()
			if key := managed_key(config, self.file_url):
				return client.read_owned(config, key)
		return super().get_content(*args, **kwargs)

	def _open_stored_bytes(self):
		if self.is_remote_file and enabled():
			config = get_config()
			if managed_key(config, self.file_url):
				return io.BytesIO(self.get_content())
		return super()._open_stored_bytes()

	def save_file(self, content=None, decode=False, ignore_existing_file_check=False, overwrite=False):
		eligible = eligibility(self)
		if eligible and (content is not None or not self.is_remote_file):
			if content is not None:
				self.content = content
				self.decode = decode
			payload = self.get_content()
			if self._upload_image(payload, *eligible):
				return {"file_name": self.file_name, "file_url": self.file_url}
			content, decode = payload, False
			self.content = payload
		return super().save_file(content, decode, ignore_existing_file_check, overwrite)

	def _upload_image(self, payload, config, folder):
		if not isinstance(payload, bytes):
			payload = payload.encode() if isinstance(payload, str) else bytes(payload)
		image_format = image_type(payload, self.file_name, config.max_bytes, self.get("content_type"))
		if not image_format:
			return False

		self._content = payload
		self.check_max_file_size()
		self.file_type = image_format[0].upper()
		self.validate_file_extension()
		payload, stored_format = optimize_image(payload, image_format, config)
		file_name = PurePosixPath(self.file_name)
		if file_name.suffix.lower() != "." + stored_format[0]:
			file_name = file_name.with_suffix("." + stored_format[0])
		if stored_format[1] == "image/jpeg" and frappe.get_system_settings(
			"strip_exif_metadata_from_uploaded_images"
		):
			payload = strip_exif_data(payload, image_format[1])
		self._content = payload
		self.file_size = self.check_max_file_size()
		if len(payload) > config.max_bytes:
			fail("Image exceeds r2_storage.max_file_size_mb.")
		self.file_type = stored_format[0].upper()
		if check_content := getattr(self, "check_content", None):
			check_content()

		old_url = self.file_url
		local_url = old_url if not self.get("blob") else None
		self.file_url = storage.store(config, folder, payload, stored_format, local_url)
		self.file_name = str(file_name)
		self.content = payload
		self.decode = False
		self.content_hash = None
		self.blob = None
		self.content_type = stored_format[1]
		self.flags.r2_previous_url = old_url
		self.flags.r2_uploaded_url = self.file_url
		self.flags.r2_stored_size = len(payload)
		return True

	def upload_local_image(self):
		if not (self.file_url or "").startswith("/files/") or not (eligible := eligibility(self)):
			return False
		self.validate_file_path()
		try:
			content = self.get_content()
		except FileNotFoundError:
			frappe.logger("r2_storage").warning("Local attachment missing; skipped R2 upload for File %s.", self.name)
			return False
		return self._upload_image(content, *eligible)

	def before_save(self):
		if parent := getattr(super(), "before_save", None):
			parent()
		if self.flags.r2_uploaded_url and self.flags.r2_uploaded_url == self.file_url:
			# Core validate() may have overwritten file_size with the request's original size.
			self.file_size = self.flags.r2_stored_size

	def validate_duplicate_entry(self):
		if not self.file_url or self.flags.r2_uploaded_url != self.file_url:
			return super().validate_duplicate_entry()

	def before_validate(self):
		if parent := getattr(super(), "before_validate", None):
			parent()
		if self.is_remote_file:
			base = setting("public_url")
			if enabled() and base and self.file_url and self.file_url.startswith(base.rstrip("/") + "/"):
				config = get_config()
				if key := managed_key(config, self.file_url):
					if cint(self.is_private):
						fail(
							"An R2 image is publicly accessible. Upload a separate private file to use private storage."
						)
					if self.flags.r2_uploaded_url != self.file_url:
						storage.protect_reference(config, key)
			return
		self.upload_local_image()

	def on_update(self):
		if parent := getattr(super(), "on_update", None):
			parent()
		old_url = self.flags.pop("r2_previous_url", None)
		if old_url and old_url != self.file_url:
			update_references(self, old_url)
		previous = self.get_doc_before_save()
		if previous and previous.file_url != self.file_url and enabled():
			storage.delete_after_commit(previous.file_url)

	def on_trash(self):
		super().on_trash()
		if enabled():
			storage.delete_after_commit(self.file_url)


class R2File(R2FileMixin, File):
	"""Frappe 15 controller override that retains the core File lifecycle."""


def sync_parent_attachments(doc, method=None):
	"""Move eligible linked images to R2 and refresh the parent's in-memory fields."""
	if not doctype_folder(doc.doctype) or not enabled() or frappe.session.user == "Guest":
		return

	for name in frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": doc.doctype,
			"attached_to_name": doc.name,
			"is_private": 0,
			"is_folder": 0,
			"file_url": ["like", "/files/%"],
		},
		pluck="name",
	):
		file_doc = frappe.get_doc("File", name)
		if file_doc.upload_local_image():
			file_doc.save(ignore_permissions=True)

	replacements = getattr(frappe.local, "r2_url_replacements", None) or {}
	for row in attachment_rows(doc):
		for df in row.meta.get("fields", {"fieldtype": ["in", ["Attach", "Attach Image"]]}):
			new_url = replacements.get((row.doctype, row.name, df.fieldname, row.get(df.fieldname)))
			if new_url and frappe.db.get_value(row.doctype, row.name, df.fieldname) == new_url:
				row.set(df.fieldname, new_url)
