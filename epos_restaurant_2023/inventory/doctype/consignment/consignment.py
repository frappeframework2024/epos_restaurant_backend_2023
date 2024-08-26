# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_stock_location_product, get_uom_conversion
from epos_restaurant_2023.inventory.inventory import check_uom_conversion
from epos_restaurant_2023.api.product import get_currenct_cost
from frappe.model.document import Document
from epos_restaurant_2023.api.account import submit_general_ledger_entry
from collections import defaultdict

class Consignment(Document):
	def before_insert(self):
		update_current_product_info(self)

	def validate(self):
		if self.from_stock_location == self.to_stock_location:
			frappe.throw("Cannot transfer to the same stock location.")

		total_quantity = sum((a.quantity or 0) for a in self.products)
		total_amount = sum((a.quantity or 0)* (a.cost or  0) for a in self.products)
		self.total_quantity = total_quantity
		self.total_amount = total_amount
  
	def before_submit(self):
		for p in self.products:
			if p.unit !=p.base_unit:
				if not check_uom_conversion(p.base_unit, p.unit):
					frappe.throw("There is no UoM conversion from {} to {}".format(p.base_unit, p.unit))
	
			current_stock = get_stock_location_product(self.from_stock_location, p.product)
			if current_stock is None or current_stock.quantity <= 0:
				frappe.throw("{} is not available in {}".format(p.product, self.from_stock_location))
			else:
				uom_conversion = get_uom_conversion(current_stock.unit, p.unit)
				if current_stock.quantity * uom_conversion < p.quantity:
					frappe.throw(("{} is available only {} in stock".format(p.product, current_stock.quantity)))

	
	def on_submit(self):
		GL_entry(self)
		if len(self.products)<=10:
			update_inventory_on_submit(self)
		else:
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.consignment.consignment.update_inventory_on_submit", queue='short', self=self)
					
	def on_cancel(self):
		GL_entry(self)
		if len(self.products)<=10:
			update_inventory_on_cancel(self)
		else:
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.consignment.consignment.update_inventory_on_cancel", queue='short', self=self)
 
def update_current_product_info(self):
	for a in self.products:
		p = get_currenct_cost(a.product,self.from_stock_location,a.unit)
		a.current_quantity = p["quantity"]
		a.cost = p["cost"]
		a.total_amount = a.quantity * a.cost

def update_inventory_on_submit(self):
	for p in self.products:
		update_to_stock(cancel=False, self=self,p=p)
		update_from_stock(cancel=False, self=self,p=p)

def update_inventory_on_cancel(self):
	for p in self.products:
		update_to_stock(cancel=True, self=self, p=p)
		update_from_stock(cancel=True, self=self,p=p)

def GL_entry(self):
	if self.include_payment == 1:
		payment_accounts = defaultdict(int)
		for a in self.payments:
			category = a.account
			value = a.amount
			payment_accounts[category] += value
		payment_accounts = dict(payment_accounts)
		if self.docstatus == 1:
			for b in payment_accounts:
				general_ledger_debit(self,{"account":b,"amount":payment_accounts[b]})
			general_ledger_credit(self,{"account":self.unearned_revenue_account,"amount":self.total_payment})
		else:
			for b in payment_accounts:
				general_ledger_credit(self,{"account":b,"amount":payment_accounts[b]})
			general_ledger_debit(self,{"account":self.unearned_revenue_account,"amount":self.total_payment})
	else:
		self.payments = []

def update_to_stock(cancel = False, self=None, p=None):
	uom_conversion = get_uom_conversion(p.base_unit, p.unit)
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Consignment",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': p.product,
		'unit':p.unit,
		'price':p.cost*uom_conversion,
		'stock_location':self.to_stock_location,
		'in_quantity': 0 if cancel else p.quantity / uom_conversion,
		'out_quantity': p.quantity / uom_conversion if cancel else 0,
		'note': "New consignment transfer from {} to {} submitted.".format(self.from_stock_location,self.to_stock_location),
		"action": "Cancel" if cancel else "Submit"
	})
def update_from_stock(cancel = False, self=None, p=None):
	uom_conversion = get_uom_conversion(p.base_unit, p.unit)
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Consignment",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': p.product,
		'unit':p.unit,
		'price':p.cost*uom_conversion,
		'stock_location':self.from_stock_location,
		'out_quantity':0 if cancel else p.quantity / uom_conversion,
		'in_quantity':p.quantity / uom_conversion if cancel else 0,
		'note': "New consignment transfer from {} to {} submitted.".format(self.from_stock_location,self.to_stock_location),
  		"action": "Cancel" if cancel else "Submit"
	})

@frappe.whitelist()
def get_payment_type_account(payment_type,branch):
	account = frappe.db.get_value('Payment Type Account', {'parent': payment_type,'business_branch':branch}, ['account'])
	return account

@frappe.whitelist()
def make_sale(consignment):
	consignment = frappe.get_doc("Consignment",consignment)
	sale = frappe.new_doc("Sale")
	sale.stock_location = consignment.to_stock_location
	sale.business_branch = consignment.business_branch
	sale.customer = consignment.employee
	sale.note = "Sale Consignment From {0}".format(consignment.employee)
	for a in consignment.products:
		child = frappe.new_doc("Sale Product")
		product = frappe.get_doc("Product",a.product)
		child.update({
		"product_code": a.product,
		"product_name": a.product_name,
		"quantity": a.quantity,
		"base_unit": a.base_unit,
		"unit": a.unit,
		"price": product.price,
		"cost": a.cost,
		"sub_total": product.price * a.quantity,
		"amount": product.price * a.quantity,
		"parenttype": "Sale",
    	"parentfield": "sale_products",
		"doctype": "Sale Product"
		})
		sale.sale_products.append(child)
	sale.total_quantity = consignment.total_quantity
	sale.sub_total = consignment.total_amount
	sale.grand_total = consignment.total_amount
	return sale.as_dict()

@frappe.whitelist()
def make_return_consignment(consignment):
	consignment = frappe.get_doc("Consignment",consignment)
	stock_transfer = frappe.new_doc("Stock Transfer")
	stock_transfer.from_stock_location = consignment.to_stock_location
	stock_transfer.to_stock_location = consignment.from_stock_location
	stock_transfer.consignment = consignment.name
	stock_transfer.note = "Return Consignment From {0}".format(consignment.employee)
	for a in consignment.products:
		child = frappe.new_doc("Stock Transfer Products")
		child.update({
		"product_code": a.product,
		"product_name": a.product_name,
		"quantity": a.quantity,
		"base_unit": a.base_unit,
		"base_cost": a.cost,
		"unit": a.unit,
		"cost": a.cost,
		"amount": a.total_amount,
		"parenttype": "Stock Transfer",
    	"parentfield": "stock_transfer_products",
		"doctype": "Stock Transfer Products"
		})
		stock_transfer.stock_transfer_products.append(child)
	return stock_transfer.as_dict()

def general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Stock Adjustment",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Accounting For Stock Adjustment"
	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)

def general_ledger_credit(self,account):
    docs = []
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":account["account"],
        "credit_amount":account["amount"],
        "voucher_type":"Stock Adjustment",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Accounting For Stock Adjustment"
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)