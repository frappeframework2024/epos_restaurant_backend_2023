# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_restaurant_2023.inventory.inventory import check_uom_conversion


class BOM(Document):
	def validate(self):
		validate_amount(self)
		validate_uom_conversion(self)

def validate_amount(self):
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
					error += "Row #{0} Please Add UoM conversion From {1} To {2}".format(d.idx, d.base_unit, d.unit)
	if error:
		frappe.throw(error)