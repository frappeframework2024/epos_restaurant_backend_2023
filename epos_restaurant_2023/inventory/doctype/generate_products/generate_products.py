# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import json
import re
from frappe.model.document import bulk_insert
import frappe
 
from frappe.model.document import Document
from itertools import product


class GenerateProducts(Document):
	def validate(self):
		for fieldname in ("option_1", "option_2", "option_3"):
			tags = _parse_tags(self.get(fieldname))
			self.set(fieldname, json.dumps(tags, ensure_ascii=False) if tags else "")

	def on_update(self):
		self.generate_product()

	def generate_product(self):
		options =  get_new_products(self)
		def get_product_docs():
			for index, d in enumerate(options):
				doc = frappe.new_doc("Product")
				doc.name = f"{self.product_code}-{index+1}"
				doc.product_code = doc.name
				doc.product_name = f"{self.parent_product}-{d}"
				doc.description = f"{self.parent_product}-{d}"
				doc.product_category = self.category
				doc.unit = "Unit"
				doc.is_inventory_product =1


				doc.product_name = "" 
				yield doc

		bulk_insert("Product", get_product_docs(), chunk_size=10_000)
	


def _parse_tags(value):
	"""Return unique, trimmed tags and accept legacy comma/newline text."""
	if not value:
		return []

	if isinstance(value, list):
		parsed = value
	else:
		try:
			parsed = json.loads(value)
		except (TypeError, json.JSONDecodeError):
			parsed = re.split(r"[,\r\n]+", str(value))

	if not isinstance(parsed, list):
		parsed = [parsed]

	tags = []
	seen = set()
	for item in parsed:
		tag = str(item).strip()
		key = tag.casefold()
		if tag and key not in seen:
			tags.append(tag)
			seen.add(key)

	return tags



	

def get_new_products(self):
	option_lists = [
		json.loads(self.option_1 or "[]"),
		json.loads(self.option_2 or "[]"),
		json.loads(self.option_3 or "[]"),
	]

	active_options = [values for values in option_lists if values]
	if not active_options:
		return []

	return [
		"-".join(option_values)
		for option_values in product(*active_options)
	]

