# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class BulkPurchaseOrderPayment(Document):
	def on_submit(self):
		if len(self.purchase_order_list) <= 20:
			add_purchase_order_payment_enqueue(self)
		else:	
			frappe.enqueue(add_purchase_order_payment_enqueue,queue="short",doc=self)
		self.reload()
		
	def on_cancel(self):
		if len(self.purchase_order_list) <= 20:
			on_cancel_enqueue(self)
		else:
			frappe.enqueue(on_cancel_enqueue,queue="short",doc=self)
		self.reload()

def on_cancel_enqueue(doc):
	for d in doc.purchase_order_list:
			cancel_purchase_order_payment(d)

def add_purchase_order_payment_enqueue(doc):
	for d in doc.purchase_order_list:
			add_purchase_order_payment(d)

def cancel_purchase_order_payment(d):
	doc = frappe.get_doc('Purchase Order Payment', d.purchase_order_payment)
	doc.cancel()

@frappe.whitelist()
def get_purchase_order_by_vendor(vendor,stock_location):
	purhase_order = frappe.db.sql("select name purchase_order,grand_total amount,total_paid payment_amount,balance,stock_location from `tabPurchase Order` where vendor = '{0}' and stock_location='{1}' and docstatus = 1 and balance > 0.01".format(vendor,stock_location),as_dict=1)
	return purhase_order

def add_purchase_order_payment(doc):
	p = frappe.new_doc("Purchase Order Payment")
	p.purchase_order_date = doc.posting_date
	p.payment_type = doc.payment_type
	p.currency = doc.currency
	p.exchange_rate = doc.exchange_rate
	p.payment_amount = doc.payment_amount
	p.input_amount = doc.input_amount
	p.purchase_order = doc.purchase_order
	p.note = doc.note
	p.insert()
	p.submit()

	bs = frappe.get_doc("Bulk Purchase Order",doc.name)
	bs.purchase_order_payment = p.name
	bs.save()

	update_purchase_balance(doc)


def update_purchase_balance(doc):
	data = frappe.db.sql("select  ifnull(sum(payment_amount),0)  as total_paid from `tabPurchase Order Payment` where docstatus=1 and purchase_order='{}'".format(doc.purchase_order))
	purchase_order_amount = frappe.db.get_value('Purchase Order', doc.purchase_order, 'grand_total')
	if data and purchase_order_amount:
		frappe.db.set_value('Purchase Order', doc.purchase_order,  {
			'total_paid': data[0][0] ,
			'balance': purchase_order_amount - data[0][0]  
		})
