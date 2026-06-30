# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction,get_uom_conversion
from epos_restaurant_2023.api.product import get_currenct_cost
from epos_restaurant_2023.api.account import submit_general_ledger_entry
import frappe
from frappe import _
from frappe.model.document import Document
from py_linq import Enumerable

class StockAdjustment(Document):
	def validate(self):
		update_current_product_info(self)
		update_default_inventory_account(self)
		epos_setting = frappe.get_doc('ePOS Settings')
		error = ""
		for p in self.products:
			if p.is_inventory_product == 1 and epos_setting.allow_negative_stock == 0:
				if p.quantity < 0:
					error = error + ("Product <b>{0}</b> QTY Not Allow Negative".format(p.product_code))
		if error != "":
			frappe.throw(error)

		total_quantity = Enumerable(self.products).sum(lambda x: x.quantity or 0)
		total_cost = Enumerable(self.products).sum(lambda x: x.total_amount or 0)
		total_current_quantity = Enumerable(self.products).sum(lambda x: x.current_quantity or 0)
		total_current_cost = Enumerable(self.products).sum(lambda x: x.total_current_cost or 0)

		self.total_quantity = total_quantity
		self.total_cost = total_cost

		self.total_current_quantity = total_current_quantity
		self.total_current_cost = total_current_cost
		
		self.difference_quantity = self.total_quantity - self.total_current_quantity; 
		self.difference_cost = self.total_cost - self.total_current_cost; 
		self.difference_amount = self.difference_cost

	def on_submit(self):
		if len(self.products)<=10:
			update_inventory_on_submit(self)
		else:
			frappe.publish_realtime("product_notification", {"message": "Updating inventory"},user=frappe.session.user)
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_adjustment.stock_adjustment.update_inventory_on_submit", queue='long', self=self)
		
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			if self.difference_amount != 0 or self.difference_quantity != 0:
				general_ledger(self)
	
	def before_cancel(self):
		frappe.throw(_("Stock adjustment transaction is not allow to cancel."))


def update_default_inventory_account(self):
	for a in self.products:
		default_inventory_account = frappe.get_cached_value("Business Branch", self.business_branch,"default_inventory_account")
		p = frappe.get_doc("Product",a.product_code)
		if p.default_account:
			acc = [b.default_stock_account for b in p.default_account if b.business_branch == self.business_branch][0]
			if acc:
				a.stock_account = acc
			else:
				a.stock_account = self.inventory_account if self.inventory_account else default_inventory_account
		else:
			a.stock_account = self.inventory_account if self.inventory_account else default_inventory_account

def update_current_product_info(self):
	for a in self.products:
		p = get_currenct_cost(a.product_code,self.stock_location,a.unit)
		a.current_quantity = float(p["quantity"])
		a.current_cost = float(p["cost"])
		a.total_current_cost = a.current_quantity * a.current_cost
		a.total_secondary_cost = a.quantity * a.secondary_cost
		a.difference_quantity =  a.quantity - a.current_quantity
		a.difference_amount =  float(a.cost * a.quantity) - float(a.current_cost * a.current_quantity)

def update_inventory_on_submit(self):
	for p in self.products:
		if p.is_inventory_product and (p.quantity != p.current_quantity or p.cost != p.current_cost):
			difference_qty = p.quantity - p.current_quantity
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock Adjustment",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity': abs(difference_qty) if difference_qty < 0 else 0,
				'in_quantity': difference_qty if difference_qty >= 0 else 0,
				"price":p.cost,
				'note': 'New Stock adjustment submitted.',
				"action":"Submit"
			})
	frappe.publish_realtime("product_notification", {"message": "Inventory updated successfully."},user=frappe.session.user)


def general_ledger(self):
	for acc in set([d.stock_account for d in self.products]):
		amount = sum([a.difference_amount for a in self.products if a.stock_account == acc])
		if amount > 0:
			general_ledger_debit(self,{"account":acc,"amount":abs(amount)})
		else:
			general_ledger_credit(self,{"account":acc,"amount":abs(amount)})
	if self.difference_amount > 0:
		general_ledger_credit(self,{"account":self.difference_account,"amount":abs(self.difference_amount)})
	else:
		general_ledger_debit(self,{"account":self.difference_account,"amount":abs(self.difference_amount)})

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