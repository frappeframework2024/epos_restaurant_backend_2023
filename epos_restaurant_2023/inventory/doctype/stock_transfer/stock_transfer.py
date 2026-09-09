# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from py_linq import Enumerable
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction,get_uom_conversion,check_uom_conversion
from frappe.model.document import Document
from epos_restaurant_2023.inventory.inventory import get_product_qty
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class StockTransfer(Document):
	def validate(self):
		update_default_inventory_account(self)
		epos_setting = frappe.get_doc('ePOS Settings')
		error = ""
		if self.from_stock_location == self.to_stock_location:
			frappe.throw("Cannot transfer to the same stock location.")
		for p in self.stock_transfer_products:
			if p.is_inventory_product == 1:
				if p.unit !=p.base_unit:
					if not check_uom_conversion(p.base_unit, p.unit):
						frappe.throw("There is no UoM conversion from {} to {}".format(p.base_unit, p.unit))
				if epos_setting.allow_negative_stock == 0:
					available_qty = get_product_qty(p.product_code, self.from_stock_location) * get_uom_conversion(p.unit, p.base_unit)
					if p.quantity > available_qty:
						error = error + ("Product <b>{0}</b> QTY In Stock Location <b>{1}</b> Are Not Enough</br>".format(p.product_code, self.from_stock_location))
		if error != "":
			frappe.throw(error)
			
		total_quantity = Enumerable(self.stock_transfer_products).sum(lambda x: x.quantity or 0)
		total_amount = Enumerable(self.stock_transfer_products).sum(lambda x: (x.quantity or 0)* (x.cost or  0))

		self.total_quantity = total_quantity
		self.total_amount = total_amount
		
	def before_save(self):
		for a in self.stock_transfer_products:
			a.total_secondary_cost = a.quantity * a.secondary_cost
			a.amount = a.quantity * a.cost
	
	def on_submit(self):
		if len(self.stock_transfer_products)<=10:
			update_inventory_on_submit(self)
		else:
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_transfer.stock_transfer.update_inventory_on_submit", queue='short', self=self)
		submit_general_ledger(self)		
			
	def on_cancel(self):
		if len(self.stock_transfer_products)>=10:
			update_inventory_on_cancel(self)
		else:
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_transfer.stock_transfer.update_inventory_on_cancel", queue='short', self=self)
		submit_general_ledger(self)
 
def update_inventory_on_submit(self):
	for p in self.stock_transfer_products:
		if p.is_inventory_product:
			update_to_stock(cancel=False, self=self,p=p)
			update_from_stock(cancel=False, self=self,p=p)

def update_inventory_on_cancel(self):
	for p in self.stock_transfer_products:
		if p.is_inventory_product:
			update_to_stock(cancel=True, self=self, p=p)
			update_from_stock(cancel=True, self=self,p=p)

def update_to_stock(cancel = False, self=None, p=None):
	uom_conversion = get_uom_conversion(p.base_unit, p.unit)
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Stock Transfer",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': p.product_code,
		'unit':p.unit,
		'stock_location':self.to_stock_location,
		'in_quantity': 0 if cancel else p.quantity / uom_conversion,
		'out_quantity': p.quantity / uom_conversion if cancel else 0,
		'note': "New stock transfer from {} to {} submitted.".format(self.from_stock_location,self.to_stock_location),
		"action": "Cancel" if cancel else "Submit",
		"has_expired_date":p.has_expired_date,
		"expired_date":p.expired_date
	})
def update_from_stock(cancel = False, self=None, p=None):
	uom_conversion = get_uom_conversion(p.base_unit, p.unit)
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Stock Transfer",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': p.product_code,
		'unit':p.unit,
		'stock_location':self.from_stock_location,
		'out_quantity':0 if cancel else p.quantity / uom_conversion,
		'in_quantity':p.quantity / uom_conversion if cancel else 0,
		'note': "New stock transfer from {} to {} submitted.".format(self.from_stock_location,self.to_stock_location),
  		"action": "Cancel" if cancel else "Submit"
	})

def update_default_inventory_account(self):
	for a in self.stock_transfer_products:
		default_inventory_account = frappe.get_cached_value("Business Branch", self.from_business_branch,"default_inventory_account")
		p = frappe.get_doc("Product",a.product_code)
		if p.default_account:
			acc = [b.default_stock_account for b in p.default_account if b.business_branch == self.from_business_branch][0]
			if acc:
				a.stock_account = acc
			else:
				a.stock_account = default_inventory_account
		else:
			a.stock_account = default_inventory_account

def submit_general_ledger(self):
	for acc in set([d.stock_account for d in self.stock_transfer_products]):
		amount = sum([a.amount for a in self.stock_transfer_products if a.stock_account == acc])
		if amount > 0:
			if self.docstatus == 1:
				general_ledger(self,{"account":acc,"amount":amount})
			else:
				general_ledger(self,{"account":acc,"amount":amount*-1})
	if self.total_amount > 0:
		if self.docstatus == 1:
			general_ledger(self,{"account":self.to_account,"amount":self.total_amount*-1})
		else:
			general_ledger(self,{"account":self.to_account,"amount":self.total_amount})

def general_ledger(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"amount":account["amount"],
		"voucher_type":"Stock Transfer",
		"voucher_number":self.name,
		"business_branch": self.from_business_branch,
		"remark": "Accounting For Stock Transfer"
	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)