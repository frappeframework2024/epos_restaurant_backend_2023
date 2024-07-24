# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BulkSalePayment(Document):
	def on_submit(self):
		if len(self.sale_list) <= 20:
			add_sale_payment_enqueue(self)
		else:
			frappe.enqueue(add_sale_payment_enqueue,queue="short",doc=self)
		self.reload()

	def on_cancel(self):
		if len(self.sale_list) <= 20:
			on_cancel_enqueue(self)
		else:
			frappe.enqueue(on_cancel_enqueue,queue="short",doc=self)
		self.reload()
	@frappe.whitelist()
	def get_sale_payment_naming_series(self):
		return frappe.get_meta("Sale Payment").get_field("naming_series").options

def on_cancel_enqueue(doc):
	for d in doc.sale_list:
			cancel_sale_payment(d)

def add_sale_payment_enqueue(self):
	for d in self.sale_list:
			add_sale_payment(d,self)

def cancel_sale_payment(d):
	doc = frappe.get_doc('Sale Payment', d.sale_payment)
	doc.cancel()

@frappe.whitelist()
def get_sale_by_customer(customer,stock_location):
	sales = frappe.db.sql("select name sale,grand_total amount,total_paid payment_amount,balance,stock_location from `tabSale` where customer = '{0}' and stock_location = '{1}' and docstatus = 1 and balance > 0".format(customer,stock_location),as_dict=1)
	return sales

def add_sale_payment(doc,self):
	frappe.throw(str(frappe.get_doc("Sale",doc.sale)))
	p = frappe.new_doc("Sale Payment")
	p.naming_series = self.sale_payment_naming_series
	p.posting_date = doc.posting_date
	p.payment_type = doc.payment_type
	p.bulk_sale_payment_name = self.name
	p.currency = doc.currency
	p.exchange_rate = doc.exchange_rate
	p.input_amount = doc.input_amount
	p.sale = doc.sale
	p.note = doc.note
	if doc.fee_amount > 0:
		p.fee_amount = doc.fee_amount
		p.payment_amount = doc.sale_amount
		
	else:
		p.payment_amount = doc.sale_amount

	if self.cashier_shift:
		p.cashier_shift = self.cashier_shift
	if self.working_day:
		p.working_day = self.working_day

	p.insert()
	p.submit()

	bs = frappe.get_doc("Bulk Sale",doc.name)
	bs.sale_payment = p.name
	bs.save()

	update_sale_balance(doc)


def update_sale_balance(doc):
	currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
	if currency_precision=='':
			currency_precision = "2"
	if doc.sale:
		data = frappe.db.sql("select  ifnull(sum(payment_amount),0)  as total_paid from `tabSale Payment` where docstatus=1 and sale='{}' and payment_amount>0".format(doc.sale))
		sale_amount = frappe.db.get_value('Sale', doc.sale, 'grand_total')
		if data and sale_amount:
			balance =round(sale_amount,int(currency_precision))-round(data[0][0], int(currency_precision))
			if balance<0:
				balance = 0
			frappe.db.set_value('Sale', doc.sale,  {'total_paid': round(data[0][0],int(currency_precision)),'balance': balance})