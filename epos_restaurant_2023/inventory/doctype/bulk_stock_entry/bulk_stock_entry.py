# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import random

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from epos_restaurant_2023.inventory.doctype.bulk_stock_entry.helper import (
	create_purchase_order,
	create_stock_adjustment,
)
from epos_restaurant_2023.inventory.inventory import get_product_qty,get_product_cost



class BulkStockEntry(Document):
	def before_submit(self):
		
		if self.transaction_type == "Purchase Order":
			if not [row for row in self.products if flt(row.quantity) != 0]:
				frappe.throw("Please add at least one product with quantity greater ")
		
			self.set(
				"products",
				[row for row in self.products if flt(row.quantity) != 0],
			)
		else: # stock adjustment
			if not [row for row in self.products if flt(row.quantity) != 0 or flt(row.cost) != flt(row.current_cost)]:
				frappe.throw("Please add at least one product with quantity greater or update cost")
		
			self.set(
					"products",
					[row for row in self.products if flt(row.quantity) != 0 or flt(row.cost) != flt(row.current_cost)],
				)
		self.update_summary()

	
	def on_submit(self):
		if self.transaction_type == "Purchase Order":
			return create_purchase_order(self)
		if self.transaction_type == "Stock Adjustment":
			return create_stock_adjustment(self)

		frappe.throw("Please select a valid transaction type")

	@frappe.whitelist()
	def get_current_product_qty(self, row_name=None):
		if not self.stock_location:
			frappe.throw("Please stock location first")

		if row_name:
			row = next((x for x in self.products if x.name == row_name), None)
			if row:
				
				row.current_quantity = get_product_qty(stock_location =  self.stock_location,product= row.get("product_code"))
				row.current_cost = get_product_cost(stock_location =  self.stock_location,product_code= row.get("product_code"))
				row.cost = row.current_cost

		self.update_summary()


	@frappe.whitelist()
	def get_product(self, product_code=None, options=None):
		if not self.stock_location:
			frappe.throw("Please stock location first")
		
		if not self.search_product_code:
			frappe.throw("Please enter product code")
		

		product_code = (product_code or "").strip()

		if not product_code:
			return []

		options = frappe.parse_json(options) or {}
		conditions = ["parent_product_code = %(product_code)s"]
		values = {"product_code": product_code, "stock_location":self.stock_location}

		for fieldname in ("option_1", "option_2", "option_3"):
			selected_options = options.get(fieldname) or []
			if isinstance(selected_options, str):
				selected_options = [selected_options]
			selected_options = [
				str(value).strip() for value in selected_options if str(value).strip()
			]

			if selected_options:
				conditions.append(f"`{fieldname}` IN %({fieldname})s")
				values[fieldname] = tuple(selected_options)
		sql = f"""
				SELECT 
					p.product_code, 
					p.product_name_en AS product_name,
					p.option_1,
					p.option_2,
					p.option_3,
					if(coalesce(l.cost,0) > 0, l.cost,p.cost) as cost,
					l.quantity as current_quantity,
					p.unit

				FROM `tabProduct` p 
				left join  `tabStock Location Product` l on l.product_code = p.name and l.stock_location = %(stock_location)s
				WHERE coalesce(p.disabled,0) = 0 and  {" AND ".join(conditions)}
				
			"""
		products =  frappe.db.sql(
			sql,
			values,
			as_dict=True,
		)
		# remove product that dont have enter qty 
		if self.transaction_type == "Purchase Order":
			self.set(
				"products",
				[row for row in self.products if flt(row.quantity) != 0],
			)

		else:
			self.set(
				"products",
				[row for row in self.products if flt(row.quantity) != 0 or flt(row.cost) != 0],
			)


		# check if product code not have in self.products then add data to child table products
		existing_product_codes = {
			row.get("product_code")
			for row in self.products
			if row.get("product_code")
		}
		
		for product in products:
			product_code = product.get("product_code")
			if not product_code or product_code in existing_product_codes:
				continue

			self.append(
				"products",
				{
					"product_code": product_code,
					"product_name": product.get("product_name"),
					"current_quantity": product.get("current_quantity") or 0,
					"current_cost": product.get("cost") or 0,
					"cost": product.get("cost") or 0,
					"option_1":product.get("option_1"),
					"option_2":product.get("option_2"),
					"option_3":product.get("option_3"),
					"unit":product.get("unit")
				},
			)
			existing_product_codes.add(product_code)

		self.update_summary()
		return products

	@frappe.whitelist()
	def update_product(self, row=None):
		row_data = frappe.parse_json(row) or {}
		row_name = row_data.get("name")

		if not row_name:
			return

		row = next((x for x in self.products if x.name == row_name), None)
		if row:
			row.total_cost = flt(row_data.get("quantity")) * flt(row_data.get("cost"))

		self.update_summary()

	@frappe.whitelist()
	def update_summary(self):
		products  = [x for x in self.products if x.product_code] 
		products = products or []

		self.total_product = len(products )
		self.total_quantity = sum(x.get("quantity") or 0 for x in products if x.quantity )
		self.total_cost = sum(x.get("total_cost") or 0 for x in products if x.total_cost)



@frappe.whitelist()
def search_product(txt=None):
	txt = (txt or "").strip()
	search_text = f"%{txt}%"
	start_text = f"{txt}%"

	return [
		row[0]
		for row in frappe.db.sql(
			"""
				SELECT 
					distinct
				 parent_product_code
				FROM `tabProduct`
				WHERE COALESCE(disabled, 0) = 0
					AND COALESCE(parent_product_code, '') != ''
					AND parent_product_code LIKE %(search_text)s
				ORDER BY
					CASE
						WHEN parent_product_code LIKE %(start_text)s THEN 0
						ELSE 1
					END,
					parent_product_code
				LIMIT 20
			""",
			{
				"search_text": search_text,
				"start_text": start_text,
			},
		)
	]
