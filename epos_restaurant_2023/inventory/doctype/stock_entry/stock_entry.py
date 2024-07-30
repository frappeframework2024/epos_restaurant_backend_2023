# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion,get_stock_location_product
from epos_restaurant_2023.inventory.inventory import check_uom_conversion
import frappe
from frappe import _
from py_linq import Enumerable
from frappe.model.document import Document
from epos_restaurant_2023.inventory.doctype.stock_entry.general_ledger_entry import submit_stock_to_general_ledger_entry_on_submit
from  epos_restaurant_2023.api.cache_function import get_doctype_value_cache
from epos_restaurant_2023.api.account import cancel_general_ledger_entery
from collections import defaultdict
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class StockEntry(Document):
	def validate(self):
		total_quantity = Enumerable(self.items).sum(lambda x: x.quantity or 0)
		total_amount = Enumerable(self.items).sum(lambda x: (x.quantity or 0)* (x.price or  0))

		self.total_quantity = total_quantity
		self.total_amount = total_amount
		# update default accunt
		update_default_account(self)
  
	def before_submit(self):
		for d in self.items:
			if d.unit !=d.base_unit:
				if not check_uom_conversion(d.base_unit, d.unit):
					frappe.throw(_("There is no UoM conversion from {} to {}".format(d.base_unit, d.unit)))

				current_stock = get_stock_location_product(self.stock_location, d.product_code)
				
				if current_stock is None or current_stock.quantity <= 0:
					frappe.throw(_("{} is not available in stock".format(d.product_code)))
				else:
					uom_conversion = get_uom_conversion(current_stock.unit, d.unit)
					if current_stock.quantity * uom_conversion < d.quantity:
						frappe.throw(_("{} is available only {} {} in stock".format(d.product_code, current_stock.quantity,current_stock.unit)))
      
	def on_submit(self):
		# if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
		# 	if not self.flags.ignore_post_general_ledger_entry:
		# 		submit_stock_to_general_ledger_entry_on_submit(self)
		GLEntry(self)
		update_inventory_on_submit(self)
		#frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_submit", queue='short', self=self)
	
	def on_cancel(self):
		# if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
		# 	cancel_general_ledger_entery('Stock Entry',self.name)
		GLEntry(self)
		update_inventory_on_cancel(self)
		#frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_cancel", queue='short', self=self)
	
@frappe.whitelist(allow_guest=True)
def get_expense_account(product_code,branch):
	expense_account = frappe.db.get_value('Product Default Account', {'parent': product_code,'business_branch':branch}, 'default_adjustment_account')
	if (expense_account or "") == "":
		expense_account = frappe.db.get_value('Business Branch',branch,'stock_adjustment_account')
	return expense_account

def update_default_account(self):
	pass
 
	# if not self.default_inventory_account:
	# 	self.default_inventory_account = get_doctype_value_cache("Business Branch",self.business_branch, "default_inventory_account")
	# # 1 get from product
	# if [x for x in self.items if not x.default_account]:
	# 	# get product default account_code from product
	# 	sql="select distinct parent as product_code, default_adjustment_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"

		 
	# 	product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.items if not x.default_account], "business_branch":self.business_branch},as_dict=1)
		
	# 	product_has_default_account = [d["product_code"] for d in product_account_codes]
		
		
	# 	for sp in [x for x in self.items if not x.default_account and x.product_code in product_has_default_account]:
	# 		sp.default_account = [d for d in product_account_codes if d["product_code"] == sp.product_code][0]['default_adjustment_account']

	# # 4 get account code from Business Branch
	# if [x for x in self.items if not x.default_account]:
	# 	for sp in [x for x in self.items if not x.default_account]:
	# 		sp.default_account = get_doctype_value_cache("Business Branch",self.business_branch, "stock_adjustment_account")

def update_inventory_on_submit(self):
	entry_type =frappe.db.get_value("Stock Entry Type", self.entry_type, "purpose")
	if entry_type == 'Stock In':
		for p in self.items:
			if p.is_inventory_product:
				uom_conversion = get_uom_conversion(p.base_unit, p.unit)			
				add_to_inventory_transaction({
					'doctype': 'Inventory Transaction',
					'transaction_type':"Stock Entry",
					'transaction_date':self.posting_date,
					'transaction_number':self.name,
					'product_code': p.product_code,
					'unit':p.unit,
					'stock_location':self.stock_location,
					'in_quantity':p.quantity / uom_conversion,
					"price":p.base_cost,
					'note': 'New stock Entry submitted.',
					"stock_entry_type":self.entry_type,
					"action": "Submit"
				})
	if entry_type == 'Stock Out':
		for p in self.items:
			if p.is_inventory_product:
				uom_conversion = get_uom_conversion(p.base_unit, p.unit)			
				add_to_inventory_transaction({
					'doctype': 'Inventory Transaction',
					'transaction_type':"Stock Entry",
					'transaction_date':self.posting_date,
					'transaction_number':self.name,
					'product_code': p.product_code,
					'unit':p.unit,
					'stock_location':self.stock_location,
					'out_quantity':p.quantity / uom_conversion,
					"price":p.base_cost,
					'note': 'New stock Entry submitted.',
					"stock_entry_type":self.entry_type,
					"action": "Submit"
				})

def update_inventory_on_cancel(self):
	entry_type =frappe.db.get_value("Stock Entry Type", self.entry_type, "purpose")
	if entry_type == 'Stock In':
		for p in self.items:
			if p.is_inventory_product:
				uom_conversion = get_uom_conversion(p.base_unit, p.unit)
				add_to_inventory_transaction({
					'doctype': 'Inventory Transaction',
					'transaction_type':"Stock Entry",
					'transaction_date':self.posting_date,
					'transaction_number':self.name,
					'product_code': p.product_code,
					'unit':p.unit,
					'stock_location':self.stock_location,
					'out_quantity':p.quantity / uom_conversion,
					"price":p.base_cost,
					'note': 'Stock Entry cancelled.',
     				"stock_entry_type":self.entry_type,
					"action": "Cancel"
				})
	if entry_type == 'Stock Out':
		for p in self.items:
			if p.is_inventory_product:
				uom_conversion = get_uom_conversion(p.base_unit, p.unit)
				add_to_inventory_transaction({
					'doctype': 'Inventory Transaction',
					'transaction_type':"Stock Entry",
					'transaction_date':self.posting_date,
					'transaction_number':self.name,
					'product_code': p.product_code,
					'unit':p.unit,
					'stock_location':self.stock_location,
					'in_quantity':p.quantity / uom_conversion,
					"price":p.base_cost,
					'note': 'Stock Entry cancelled.',
					"stock_entry_type":self.entry_type,
					"action": "Cancel"
				})

def GLEntry(self):
	if self.docstatus == 1:
		inventory_account = frappe.db.get_value('Business Branch',self.business_branch,'default_inventory_account')
		if self.purpose == "Stock In":
			expense_general_ledger_debit(self,account = {"account":inventory_account,"amount":self.total_amount})
		else:
			expense_general_ledger_credit(self,account = {"account":inventory_account,"amount":self.total_amount})

		expense_accounts = defaultdict(int)
		for a in self.items:
			category = a.expense_account
			value = a.amount
			expense_accounts[category] += value
		expense_accounts = dict(expense_accounts)
		for a in expense_accounts:
			if self.purpose == "Stock In":
				expense_general_ledger_credit(self,account = {"account":a,"amount":expense_accounts[a]})
			else:
				expense_general_ledger_debit(self,account = {"account":a,"amount":expense_accounts[a]})


def expense_general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Stock Entry",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Stock Entry {} Entry Type {}".format(self.name,self.entry_type)

	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)

def expense_general_ledger_credit(self,account):
    docs = []
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":account["account"],
        "credit_amount":account["amount"],
        "voucher_type":"Stock Entry",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Stock Entry {} Entry Type {}".format(self.name,self.entry_type)
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)