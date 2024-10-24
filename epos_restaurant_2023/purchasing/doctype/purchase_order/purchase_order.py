# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt


from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion
from epos_restaurant_2023.inventory.inventory import check_uom_conversion,calculate_average_cost,update_inventory_transaction_status
import frappe
from frappe import _
from py_linq import Enumerable
from frappe.model.document import Document
from epos_restaurant_2023.purchasing.doctype.purchase_order.general_ledger_entry import submit_purchase_to_general_ledger_entry_on_submit,submit_purchase_to_general_ledger_entry_on_cancel
class PurchaseOrder(Document):
		
	def validate(self):
		validate_discount(self)
		self.total_quantity = Enumerable(self.purchase_order_products).sum(lambda x: x.quantity or 0)
		self.discountable_amount = Enumerable(self.purchase_order_products).where(lambda x:(x.discount_amount or 0)==0).sum(lambda x: (x.quantity or 0)* (x.cost or  0))
		self.sub_total = Enumerable(self.purchase_order_products).sum(lambda x: (x.quantity or 0)* (x.cost or  0))
		self.discount_amount = Enumerable(self.purchase_order_products).sum(lambda x: x.po_discount_amount or 0)
		self.product_discount = Enumerable(self.purchase_order_products).sum(lambda x: x.discount_amount)
		self.total_discount = (self.product_discount or 0) + (self.discount_amount or 0)
		self.grand_total =( self.sub_total - (self.total_discount or 0))
		self.balance = self.grand_total  - (self.total_paid or 0)
   
	def on_submit(self):
		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			validate_account(self)
			submit_purchase_to_general_ledger_entry_on_submit(self)
		 
		if len(self.purchase_order_products)<=10:
			update_inventory_on_submit(self)
		else:
			frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_submit", queue='short', self=self)

		# update last purchase cost to product
		sql ="""
			update `tabProduct` p
			join `tabPurchase Order Products` pp 
			on 
				pp.product_code = p.name and 
				p.last_purchase_cost != pp.cost and 
				pp.parent = %(parent)s
			set 
				p.last_purchase_cost = pp.cost
		"""
		frappe.db.sql(sql,{"parent": self.name})

	def on_cancel(self):
		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			submit_purchase_to_general_ledger_entry_on_cancel(self)
		if len(self.purchase_order_products)>=10:
			update_inventory_on_cancel(self)
		else:
			frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_cancel", queue='short', self=self)

	def before_submit(self):
		for d in self.purchase_order_products:
			if d.base_unit != d.unit:
				if not check_uom_conversion(d.base_unit, d.unit):
					frappe.throw(_("There is no UoM conversion from {} to {}".format(d.base_unit, d.unit)))

def validate_discount(self):
	if self.discount:
		discount_percent = ((self.discount/100)  if self.discount_type == 'Percent' else self.discount/self.discountable_amount)
		for a in self.purchase_order_products:
			if a.discount_amount == 0:
				a.po_discount_percent = discount_percent * 100
				a.po_discount_amount = a.sub_total*discount_percent
				a.total_discount = a.discount_amount + a.po_discount_amount
	else:
		for a in self.purchase_order_products:
			if a.discount_amount == 0:
				a.po_discount_percent = a.po_discount_amount = 0
				a.total_discount = a.discount_amount + a.po_discount_amount
				a.amount = a.sub_total - a.total_discount
	total = sum(a.sub_total - a.total_discount for a in self.purchase_order_products)
	if total < 0:
		frappe.throw("Discount amount can not be greater than total amount")


def update_inventory_on_submit(self):
	for p in self.purchase_order_products:
		uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Purchase Order",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': p.product_code,
			'unit':p.unit,
			'previous_cost': p.base_cost*uom_conversion,
			'stock_location':self.stock_location,
			'in_quantity':p.quantity / uom_conversion,
			"uom_conversion":uom_conversion,
			"price":calculate_average_cost(p.product_code,self.stock_location,(p.quantity / uom_conversion),(p.sub_total - p.total_discount)),
			'note': 'New purchase order submitted.',
			"has_expired_date":p.has_expired_date,
			"expired_date":p.expired_date,
			'action': 'Submit'
		})
		
def update_inventory_on_cancel(self):
	for p in self.purchase_order_products:
		uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Purchase Order",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': p.product_code,
			'unit':p.unit,
			'previous_cost': p.base_cost*uom_conversion,
			'stock_location':self.stock_location,
			'out_quantity':p.quantity / uom_conversion,
			"price": calculate_average_cost(p.product_code,self.stock_location,(p.quantity / uom_conversion),(p.sub_total - p.total_discount),self.name),
			'note': 'Purchase order cancelled.',
			'action': 'Cancel'
		})
		update_inventory_transaction_status(self.name)

def validate_account(self):
	if not self.default_credit_account:
		self.default_credit_account = frappe.get_cached_value("Business Branch", self.business_branch, "default_credit_account")
	
	if not self.default_discount_account:
		self.default_discount_account = frappe.get_cached_value("Business Branch", self.business_branch, "default_purchase_discount_account")
 
	for p in self.purchase_order_products:
		if not p.stock_account:
			p.stock_account = frappe.get_cached_value("Business Branch", self.business_branch,"default_inventory_account")

@frappe.whitelist(allow_guest=True) 
def get_accounts(branch,product):
	doc = frappe.get_cached_doc("Product",product)
	expense_account = None
	if doc.default_account:
		expense_account = [d for d in doc.default_account if d.business_branch == branch]
		if expense_account:
			expense_account = expense_account[0].default_expense_account
	if not expense_account:
		expense_account = frappe.get_cached_value("Business Branch", branch,"default_cost_of_good_sold_account")
	stock_account = frappe.db.get_value("Business Branch", branch,"default_inventory_account")
	return {"stock_account":stock_account,"expense_account":expense_account}
