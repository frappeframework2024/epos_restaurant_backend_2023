# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_restaurant_2023.inventory.inventory import check_uom_conversion,get_product_qty


class BOM(Document):
	def validate(self):
		validate_amount(self)
		validate_uom_conversion(self)
		validate_is_default(self)
	
	@frappe.whitelist()
	def update_cost(bom):
		stock_location = frappe.db.get_list('Stock Location',filters={'disabled': 0},fields=['name'],as_list=False)
		bom = frappe.get_doc("BOM", bom)
		for a in stock_location:
			stock_entry = frappe.new_doc("Stock Adjustment")
			stock_entry.stock_location = a.name
			stock_entry.append("products",{
				'product_code' : bom.product,
				'product_name' : bom.product_name,
				'unit' : bom.product_unit,
				'base_unit' : bom.product_unit,
				'cost' : bom.total_cost,
				'qty' : get_product_qty(bom.product,a.stock_location)})
			stock_entry.docstatus = 1
			stock_entry.save()
		return "Cost Updated For All Stock Location"

def validate_amount(self):
	self.total_qty = sum(a.quantity for a in self.items)
	self.total_cost = sum(a.amount for a in self.items)
	error = ""
	for a in self.items:
		if a.amount <=0:
			error += "Row #{0} Quantity Can Not Be Zero.</br>".format(a.idx)
	if error:
		frappe.throw(error)

def validate_uom_conversion(self):
	error = ""
	for d in self.items:
		if d.unit != d.base_unit:
			if not check_uom_conversion(d.base_unit, d.unit):
					error += "Row #{0} Please Add UoM Conversion From <b>{1}</b> To <b>{2}</b>".format(d.idx, d.base_unit, d.unit)
	if error:
		frappe.throw(error)

def validate_is_default(self):
	data = frappe.db.sql("select count(*) is_default from `tabBOM` where product = '{}' and is_active=1 and is_default=1 and name <> '{}'".format(self.product,self.name),as_dict=True)
	if data:
		if data[0].is_default > 0 and self.is_default == 1:
			frappe.msgprint("This Product Already Has Default BOM. Removing Is Default")
			self.is_default = 0
			self.reload()