# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from epos_restaurant_2023.configuration.doctype.epos_settings.epos_settings import main_currency
from epos_restaurant_2023.purchasing.doctype.purchase_order_payment.general_ledger_entry import submit_purchase_payment_to_general_ledger_entry_on_submit
from epos_restaurant_2023.api.account import cancel_general_ledger_entery
class PurchaseOrderPayment(Document):
	def validate(self):
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			validate_account(self)
		currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
		if currency_precision=='':
			currency_precision = "2"

		if (self.exchange_rate or 0) ==0 or self.currency == frappe.db.get_default("currency"):
			self.exchange_rate = 1
   
		self.payment_amount = self.input_amount /self.exchange_rate 
   		
		if (self.payment_amount or 0) ==0:
			frappe.throw(_("Please enter payment amount"))

		#validate expense if is a submitted expense
		purchase_order_status = frappe.db.get_value("Purchase Order",self.purchase_order,"docstatus")
		
		if not purchase_order_status==1:
			frappe.throw("This purchase order is not submitted yet")

		#check paid amount cannot over balance
		if round(self.payment_amount  , int(currency_precision)) - round(self.balance  , int(currency_precision)) > 0 :
			frappe.throw("Payment amount cannot greater than purchase balance")

	def on_submit(self):
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			submit_purchase_payment_to_general_ledger_entry_on_submit(self)
		
		update_purchase_order(self)

	def on_cancel(self):
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			cancel_general_ledger_entery('Purchase Order Payment',self.name)
   
		update_purchase_order(self)
def validate_account(self):
	if not self.account_paid_from:
		sql = "select account from `tabPayment Type Account` where business_branch=%(business_branch)s and parent = %(parent)s  limit 1"
		data = frappe.db.sql(sql,{"business_branch":self.business_branch,'parent':self.payment_type},as_dict=1)
		if data:
			self.account_paid_from = data[0]["account"]

def update_purchase_order(self):
	data = frappe.db.sql("select  ifnull(sum(payment_amount),0)  as total_paid from `tabPurchase Order Payment` where docstatus=1 and purchase_order='{}'".format(self.purchase_order))
	purchase_order_amount = frappe.db.get_value('Purchase Order', self.purchase_order, 'grand_total')
	if data and purchase_order_amount:
		balance = purchase_order_amount - data[0][0]
		frappe.db.set_value('Purchase Order', self.purchase_order,  {
			'total_paid': data[0][0] ,
			'balance': (0 if balance <= main_currency().smallest_currency_fraction_value else balance)
		})
