# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import json
import re
from frappe.model.document import bulk_insert
import frappe
from collections.abc import Callable
from frappe.model.document import Document
from itertools import product
from frappe.query_builder import DocType
from frappe.utils import cint, cstr, now_datetime
import re

class GenerateProducts(Document):
	def validate(self):
		for fieldname in ("option_1", "option_2", "option_3"):
			tags = _parse_tags(self.get(fieldname))
			self.set(fieldname, json.dumps(tags, ensure_ascii=False) if tags else "")

	def before_save(self):
		global counter
		counter = 1
		if not self.is_new():
			old_doc = frappe.get_doc("Generate Products",self.name)
			changed_fields = [
				df.fieldname
				for df in frappe.get_meta(self.doctype).fields
				if self.get(df.fieldname) != old_doc.get(df.fieldname) and df.fieldname != "products"
			]
			fieldnames = [df.fieldname for df in frappe.get_meta(self.doctype).fields if df.fieldname != "products"]
			if self.show_generated_products:
				if any(f in fieldnames for f in changed_fields):
					self.products = []
					generate_products(self)
			else:
				self.products = []
		else:
			generate_products(self)
		
	def before_submit(self):
		existing_products = frappe.db.sql("select option_1,option_2,option_3 from `tabProduct` where parent_product_code = '{0}'".format(self.parent_product_code),as_dict=1)
		lookup = [(d["option_1"], d["option_2"],d["option_3"]) for d in existing_products]
		show_msg = 0
		new_products=[]
		if self.show_generated_products:
			new_products = [d for d in self.products if (d.option_1, d.option_2,d.option_3) not in lookup]
			show_msg = 1 if len(self.products) != len(new_products) else 0
			self.products = new_products
		else:
			generated_products = get_new_products(self)
			new_products = [d for d in generated_products if (str(d.split(":")[0]),str(d.split(":")[1]),str(d.split(":")[2])) not in lookup]
			show_msg = 1 if len(generated_products) != len(new_products) else 0
		if show_msg == 1:
			frappe.msgprint("Products with the same options as existing products will be removed")
		frappe.publish_realtime("generate_product", {"message": "Generating Products"},user=frappe.session.user)
		frappe.enqueue("epos_restaurant_2023.inventory.doctype.generate_products.generate_products.bulk_insert_products",self=self,generated_products=new_products,queue="long",enqueue_after_commit=True,job_name=f"Generate Products {self.name}")

def bulk_insert_products(self,generated_products):
	def get_product_docs():
		if self.show_generated_products:
			for p in self.products:
				doc = frappe.new_doc("Product")
				doc.name = p.product_code
				doc.product_code = p.product_code
				doc.product_name_en = p.product_name_en
				doc.product_name_kh = p.product_name_kh
				doc.product_category = p.product_category
				doc.unit = p.unit
				doc.is_inventory_product = p.is_inventory_product
				doc.revenue_group = p.revenue_group
				doc.price = p.price
				doc.cost = p.cost
				doc.option_1 = p.option_1
				doc.option_2 = p.option_2
				doc.option_3 = p.option_3
				doc.parent_product_code = self.parent_product_code
				yield doc
		else:
			index = get_last_index(self)
			for d in (generated_products):
				doc = frappe.new_doc("Product")
				generate_product(self, doc, index, d)
				index = index + 1
				yield doc
	bulk_insert("Product", get_product_docs(), chunk_size=10000)
	update_series(self.parent_product_code,self.series.split(".")[0],int(re.sub(r"\D", "",list(get_product_docs())[-1].product_code)))
	frappe.publish_realtime("generate_product", {"message": "Products Generated"},user=frappe.session.user)

def update_series(parent_product_code,key,counter):
	if not parent_product_code:
		series = DocType("Series")
		current = (frappe.qb.from_(series).where(series.name == key).for_update().select("current")).run()
		if current:
			if current[0][0] is not None:
				frappe.db.sql("UPDATE `tabSeries` SET `current` = `current` + %s WHERE `name`=%s", (counter, key))
		else:
			frappe.db.sql("INSERT INTO `tabSeries` (`name`, `current`) VALUES (%s, %s)", (key, counter))
		frappe.db.commit()

def generate_products(self):
	options =  get_new_products(self)
	index = get_last_index(self)
	for d in (options):
		p = frappe.new_doc("Generate Products Item")
		generate_product(self, p, index, d)
		self.append("products", p)
		index = index + 1

def get_last_index(self):
	last_index = frappe.db.sql("SELECT REGEXP_REPLACE(name, '[^0-9]', '') as `index` FROM `tabProduct` where parent_product_code = '{0}' ORDER BY cast(REGEXP_REPLACE(name, '[^0-9]', '') as int) desc limit 1".format(self.parent_product_code),as_dict=1)
	if last_index:
		return int(last_index[0]["index"]) or 0
	else:
		return 0

def generate_product(self, p, index, d):
	parent_product_code = self.parent_product_code or local_make_autoname(self.series)
	if p.doctype == "Product":
		p.name = f"{parent_product_code}-{index+1}" if self.parent_product_code else f"{parent_product_code}"
	p.product_code = f"{parent_product_code}-{index+1}" if self.parent_product_code else f"{parent_product_code}"
	option_1 = str(d.split(":")[0]) if len(d.split(":")) > 0 else ""
	option_2 = str(d.split(":")[1]) if len(d.split(":")) > 1 else ""
	option_3 = str(d.split(":")[2]) if len(d.split(":")) > 2 else ""
	p.option_1 = "" if option_1 == "None" else option_1
	p.option_2 = "" if option_2 == "None" else option_2
	p.option_3 = "" if option_3 == "None" else option_3
	option_1_prefix = self.option_1_prefix + ": "+ p.option_1 if self.option_1_prefix and p.option_1 else p.option_1
	option_2_prefix = ", "+self.option_2_prefix + ": "+ p.option_2 if self.option_2_prefix and p.option_2 else ", "+p.option_2 if p.option_2 else ""
	option_3_prefix = ", "+self.option_3_prefix + ": "+ p.option_3 if self.option_3_prefix and p.option_3 else ", "+p.option_3 if p.option_3 else ""
	product_name_en = self.product_name_en if self.product_name_en else parent_product_code
	product_name_kh = self.product_name_kh if self.product_name_kh else parent_product_code
	p.product_name_en = product_name_en+" "+option_1_prefix+option_2_prefix+option_3_prefix
	p.product_name_kh = product_name_kh+" "+option_1_prefix+option_2_prefix+option_3_prefix
	p.product_category = self.category
	p.unit = self.unit
	p.is_inventory_product = self.is_inventory_product
	p.revenue_group = self.revenue_group
	p.price = self.price
	p.cost = self.cost

def local_make_autoname(key=""):
	parts = key.split(".")
	return parse_naming_series(parts)

def parse_naming_series(parts: list[str] | str) -> str:
	name = ""
	_sentinel = object()
	if isinstance(parts, str):
		parts = parts.split(".")
	series_set = False
	today = now_datetime()
	for e in parts:
		if not e:
			continue
		part = ""
		if e.startswith("#"):
			if not series_set:
				digits = len(e)
				part = getseries(name, digits)
				series_set = True
		elif e == "YY":
			part = today.strftime("%y")
		elif e == "MM":
			part = today.strftime("%m")
		elif e == "DD":
			part = today.strftime("%d")
		elif e == "YYYY":
			part = today.strftime("%Y")
		elif e == "WW":
			part = determine_consecutive_week_number(today)
		elif e == "timestamp":
			part = str(today)
		elif method := frappe.get_hooks("naming_series_variables", {}).get(e):
			part = frappe.get_attr(method[0])(doc, e)
		else:
			part = e
		if isinstance(part, str):
			name += part
		elif isinstance(part, NAMING_SERIES_PART_TYPES):
			name += cstr(part).strip()
	return name

counter = 0
def getseries(key, digits):
	global counter
	series = DocType("Series")
	current = (frappe.qb.from_(series).where(series.name == key).for_update().select("current")).run()
	current = current[0][0] if current and current[0][0] is not None else 0
	current = cint(current) + cint(counter)
	counter = counter + 1
	return ("%0" + str(digits) + "d") % current

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
		json.loads(self.option_1 or '["None"]'),
		json.loads(self.option_2 or '["None"]'),
		json.loads(self.option_3 or '["None"]'),
	]
	active_options = [values for values in option_lists if values]
	if not active_options:
		return []
	return [
		":".join(option_values)
		for option_values in product(*active_options)
	]

