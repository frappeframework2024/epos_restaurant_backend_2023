# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_product_cost, get_uom_conversion,get_stock_location_product,update_product_quantity
from epos_restaurant_2023.inventory.inventory import check_uom_conversion
import frappe
from frappe.model.document import Document


class Produce(Document):
		
	def on_submit(self):
		update_produce(self)

	def on_cancel(self):
		cancel_produce(self)

def update_inventory_on_submit(self):
	for p in self.product_items:
		if p.is_inventory:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)			
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Produce",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion,
				"price":p.base_cost,
				'note': 'New stock take submitted.',
				"action": "Submit"
			})

def update_inventory_on_cancel(self):
	for p in self.product_items:
		if p.is_inventory:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Produce",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity / uom_conversion,
				"price":p.base_cost,
				'note': 'Stock take cancelled.',
    			"action": "Cancel"
			})

def update_produce(self):
	uom_conversion = get_uom_conversion(self.base_unit, self.unit)
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Produce",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': self.product,
		'unit':self.unit,
		'stock_location':self.stock_location,
		'in_quantity':self.quantity / uom_conversion,
		"uom_conversion":uom_conversion,
		'note': 'New purchase order submitted.',
		'action': 'Submit'
	})
	update_inventory_on_submit(self)
		
def cancel_produce(self):
	uom_conversion = get_uom_conversion(self.base_unit, self.unit)
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Produce",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': self.product,
		'unit':self.unit,
		'stock_location':self.stock_location,
		'out_quantity':self.quantity / uom_conversion,
		'note': 'Purchase order cancelled.',
		'action': 'Cancel'
	})
	update_inventory_on_cancel(self)