# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion
from epos_restaurant_2023.inventory.inventory import check_uom_conversion
import frappe
from frappe.model.document import Document


class Produce(Document):
		
	def on_submit(self):
		update_produce(self)

	def on_cancel(self):
		update_produce(self)
	
	def validate(self):
		self.total_quantity = sum(a.quantity for a in self.produce_items)
		self.total_amount = sum(a.amount for a in self.produce_items)
		if self.source_location == self.target_location:
			frappe.throw("Source Location And Target Location Can Not Be The Same")
	
	@frappe.whitelist(allow_guest=True)
	def get_bom_items(self):
		bom_items = frappe.db.sql("select product,product_name,unit,cost,quantity,amount,base_unit from `tabBOM Items` where parent = '{0}'".format(self.bom),as_dict=True)
		return bom_items

@frappe.whitelist(allow_guest=True)
def get_default_bom(product):
	default_bom = frappe.db.sql("select name from `tabBOM` where product = '{0}' and is_active = 1 and is_default = 1".format(product),as_dict=True)
	if len(default_bom)>0:
		default_bom = default_bom[0].name
	else:
		default_bom = "None"
	return default_bom

def update_produce_item(self):
	for p in self.produce_items:
		uom_conversion = get_uom_conversion(p.base_unit, p.unit)			
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Produce",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': p.product,
			'unit':p.unit,
			'stock_location':self.source_location,
			'in_quantity': (p.quantity / uom_conversion) if self.docstatus == 2 else 0,
			'out_quantity':(p.quantity / uom_conversion) if self.docstatus == 1 else 0,
			"price":p.cost,
			'note': 'Produce Material Stock Take.' if self.docstatus == 1 else "Cancel Produce Material",
			"action": "Submit"
		})

def update_produce(self):
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Produce",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': self.product,
		'unit':self.unit,
		'stock_location':self.target_location,
		'in_quantity': self.quantity if self.docstatus == 1 else 0,
		'out_quantity': self.quantity if self.docstatus == 2 else 0,
		"uom_conversion": 1,
		'note': 'Produce Product Stock In.' if self.docstatus == 1 else "Cancel Produce Product",
		'action': 'Submit'
	})
	update_produce_item(self)