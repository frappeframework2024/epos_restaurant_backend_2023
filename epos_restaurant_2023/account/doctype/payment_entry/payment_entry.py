# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class PaymentEntry(Document):
	def validate(self):
		validate_paid_amount(self)
	
	def on_submit(self):
		GL_entry(self)
		
	def on_cancel(self):
		GL_entry(self)

def validate_paid_amount(self):
	error = ""
	for a in self.payment_entry_reference:
		if a.paid_amount > a.total_amount:
			error += "Row #{} Paid Amount Cannot Be Greater That Total Amount.</br>".format(a.idx)
	if error:
		frappe.throw(error)
	self.set("payment_entry_reference", self.get("payment_entry_reference", {"paid_amount": ["not in", [0, None, ""]]}))
	frappe.db.sql("delete from `tabPayment Entry Reference` where parent = '{0}' and paid_amount = 0".format(self.name))

@frappe.whitelist()
def get_reference_detail(doctype,docname):
	balance = frappe.db.get_value(doctype,docname,'balance')
	return (balance or 0)

@frappe.whitelist()
def get_mode_of_payment_detail(branch="",mode_of_payment="",party_type="",posting_date="",party=""):
	party_account = ""
	mode_of_payment_account = ""

	if mode_of_payment:
		mode_of_payment_account = frappe.db.get_value('Payment Type Account', {'parent': mode_of_payment,'business_branch':branch}, ['account'])

	if party_type == "Customer":
		party_account = frappe.db.get_value('Business Branch', {'name':branch}, ['default_receivable_account'])
	elif party_type == "Vendor":
		party_account = frappe.db.get_value('Business Branch', {'name':branch}, ['default_credit_account'])
	else:
		party_account = frappe.db.get_value(party_type,{'name':party},"commission_account")
	party_balance = 0

	if posting_date != "" and party != "":
		party_balance = get_account_balance(posting_date,party_type,party,party_account)
	mode_of_payment_balance = get_account_balance(posting_date=posting_date,account=mode_of_payment_account)
	return{"mode_of_payment_account":mode_of_payment_account,"mode_of_payment_balance":(mode_of_payment_balance or 0),"party_account":party_account,"party_balance":party_balance}

@frappe.whitelist()
def get_party_detail(party_type,party,posting_date):
	fields = []
	name = ""
	commission_account = ""
	if party_type == "Customer":
		fields.append("customer_name_en")
	elif party_type == "Employee":
		fields.append("employee_name")
	else:
		fields.append("vendor_name")
	p = frappe.db.get_value(party_type,{'name':party},fields,as_dict=1)
	if party_type == "Customer":
		name = p.customer_name_en
	elif party_type == "Employee":
		name = p.employee_name
		commission_account = frappe.db.get_value(party_type,{'name':party},"commission_account")
	else:
		name = p.vendor_name
	
	return {"name":name,"balance":get_account_balance(posting_date,party_type,party,commission_account),"account":commission_account}

def get_account_balance(posting_date="",party_type="",party="",account=""):
	balance = 0
	filters = "and posting_date <= '{0}'".format(posting_date)
	if account != "":
		filters += "and account = '{0}'".format(account)
	else:
		if party_type != "" and party != "":
			filters += "and party = '{0}' and party_type = '{1}'".format(party,party_type)
		else:
			return 0
	balances = frappe.db.sql("""SELECT 
				sum(debit_amount) - sum(credit_amount) balance
				FROM `tabGeneral Ledger`
				WHERE is_cancelled=0 
				{0}""".format(filters),as_dict=1)
	if balances:
		balance = balances[0].balance
	
	return balance or 0

def update_doc_amount(self,doc):
	currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
	if doc.reference_doctype == "Sale":
		cb = frappe.db.get_value('Sale', doc.reference_name,['balance','grand_total','total_paid'],as_dict=1) 
		balance = round(cb.balance,int(currency_precision)) - round(doc.paid_amount,int(currency_precision)) if self.docstatus == 1 else round(cb.balance,int(currency_precision)) + round(doc.paid_amount,int(currency_precision))
		status = ""
		if balance == 0:
			status = "Paid"
		elif balance > 0 and balance < cb.grand_total:
			status = "Partially Paid"
		else:
			status = "Unpaid"
		if balance<0:
			balance = 0
		
		update_sale_status = "Update `tabSale` set total_paid = %(total_paid)s , balance = %(balance)s,status=%(status)s where name = %(sale)s"
		frappe.db.sql(update_sale_status,{
			'total_paid': round((cb.total_paid),int(currency_precision)) + round((doc.paid_amount),int(currency_precision)) if self.docstatus == 1 else round((cb.total_paid),int(currency_precision)) - round((doc.paid_amount),int(currency_precision)),
			'balance': balance,
			'status': status,
			'sale':doc.reference_name
		})
		frappe.db.commit()
	elif doc.reference_doctype == "Purchase Order":
		poa = frappe.db.get_value('Purchase Order', doc.reference_name, ['grand_total','balance','total_paid'],as_dict=1)
		balance = round(poa.balance,int(currency_precision)) - round(doc.paid_amount,int(currency_precision)) if self.docstatus == 1 else round(poa.balance,int(currency_precision)) + round(doc.paid_amount,int(currency_precision))
		frappe.db.set_value('Purchase Order', doc.reference_name,  {
			'total_paid': round((poa.total_paid),int(currency_precision)) + round((doc.paid_amount),int(currency_precision)) if self.docstatus == 1 else round((poa.total_paid),int(currency_precision)) - round((doc.paid_amount),int(currency_precision)),
			'balance': balance
		})
	else:
		pass

def GL_entry(self):
	if self.docstatus == 1:
		general_ledger_debit(self,{"account":self.account_paid_to,"amount":self.paid_amount})
		if len(self.payment_entry_reference)>0:
			for a in self.payment_entry_reference:
				update_doc_amount(self,a)
				general_ledger_credit(self,{"account":self.account_paid_from,"amount":a.paid_amount})
		else:
			general_ledger_credit(self,{"account":self.account_paid_from,"amount":self.paid_amount})
		if self.unallocated_amount > 0:
			general_ledger_credit(self,{"account":self.account_paid_from,"amount":self.unallocated_amount})
	else:
		general_ledger_credit(self,{"account":self.account_paid_to,"amount":self.paid_amount})
		if len(self.payment_entry_reference)>0:
			for a in self.payment_entry_reference:
				update_doc_amount(self,a)
				general_ledger_debit(self,{"account":self.account_paid_from,"amount":a.paid_amount})
		else:
			general_ledger_debit(self,{"account":self.account_paid_from,"amount":self.paid_amount})
		if self.unallocated_amount > 0:
			general_ledger_debit(self,{"account":self.account_paid_from,"amount":self.unallocated_amount})

def general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Payment Entry",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Accounting For Payment Entry"
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
        "voucher_type":"Payment Entry",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"party_type": self.party_type,
		"party":self.party,
		"remark": "Accounting For Payment Entry"
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)