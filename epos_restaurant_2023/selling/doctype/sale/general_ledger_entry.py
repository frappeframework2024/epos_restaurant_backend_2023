import frappe
from frappe import _

def submit_sale_to_general_ledger_entry(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	# income account
	for acc in set([d.default_income_account for d in self.sale_products]):
		if not acc:
				frappe.throw(_("Please enter income account"))
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":acc,
			"credit_amount":sum([d.sub_total for d in self.sale_products if d.default_income_account==acc]),
			"againt":self.customer + " - " + self.customer_name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Income"#not use in db
		}
		docs.append(doc)
	# Discount Account
	if self.total_discount:
		for  acc in set([d.default_discount_account for d in self.sale_products if d.default_discount_account and d.allow_discount==1]):
			if not acc:
				frappe.throw(_("Please enter default discount"))
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc,
				"debit_amount":sum([d.total_discount for d in self.sale_products if d.default_discount_account==acc and d.allow_discount==1]),
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Income"#not use in db

			}
			docs.append(doc)
  
	# asset account from payment
	if self.payment:
		for acc in set([d for d in self.payment if not d.payment_type_group=="On Account"]):
			if not  acc.default_account:
				frappe.throw(_("Please enter default account for payment type {payment_type}".format(payment_type=acc.payment_type)))
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc.default_account  ,
				"debit_amount":sum([d.amount + (d.fee_amount or 0) for d in self.payment  if d.default_account==acc.default_account]),
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Income"#not use in db

			}
			docs.append(doc)
	if self.balance:
		# post gl entry to default recivable account from business branch setting
		if not self.default_receivable_account:
			frappe.throw(_('Please select default receivable account'))
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.default_receivable_account,
			"debit_amount":self.balance,
			# "againt":",".join([d["account"] for d in docs]),
			"againt_voucher_type":"Sale",
			"againt_voucher_number": self.name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Asset"#not use in db

		}
		docs.append(doc)

 

	# tax account
	# tax 1 
	if self.tax_1_amount!=0:
		if not self.default_tax_1_account:
			frappe.throw(_("Please select tax 1 account"))	
		
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account": self.default_tax_1_account,
				"debit_amount":self.tax_1_amount if frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"credit_amount":self.tax_1_amount if not frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)
	# tax 2 
	if self.tax_2_amount!=0:
		if not self.default_tax_2_account:
			frappe.throw(_("Please select tax 2 account"))	
		
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account": self.default_tax_2_account,
				"debit_amount":self.tax_2_amount if frappe.get_cached_value("Chart Of Account",self.default_tax_2_account,"root_type") in ["Asset","Expenses"] else 0,
				"credit_amount":self.tax_2_amount if not frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)
	
 	# tax 3 
	if self.tax_3_amount!=0:
		if not self.default_tax_3_account:
			frappe.throw(_("Please select tax 3 account"))	
		
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account": self.default_tax_3_account,
				"debit_amount":self.tax_3_amount if frappe.get_cached_value("Chart Of Account",self.default_tax_3_account,"root_type") in ["Asset","Expenses"] else 0,
				"credit_amount":self.tax_3_amount if not frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)
	# change account

	# cost of good sold account
	if sum([d.quantity* (d.cost or 0) for d in self.sale_products if d.is_inventory_product==1]):
		if not self.default_cost_of_goods_sold_account:
				frappe.throw(_('Please select default cost of goods sold account'))
	
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account": self.default_cost_of_goods_sold_account,
				"debit_amount":sum([d.quantity* (d.cost or 0) for d in self.sale_products if d.is_inventory_product==1]),
				"againt":self.default_inventory_account,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Asset"#not use in db
			}
		docs.append(doc)
	if sum([d.quantity*(d.cost or 0)  for d in self.sale_products if d.is_inventory_product==1]):
	# deduct stock in hand
		if not self.default_inventory_account:
				frappe.throw(_('Please select default inventory account'))
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":self.default_inventory_account,
				"credit_amount":sum([d.quantity*(d.cost or 0)  for d in self.sale_products if d.is_inventory_product==1]),
				"againt":self.default_cost_of_goods_sold_account,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Asset"#not use in db
			}
		docs.append(doc)

	# change amount
	if self.changed_amount> 0:
		if not self.default_change_account:
			frappe.throw(_("Please select default change account"))
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":self.default_change_account,
				"credit_amount":self.changed_amount,
				"againt":self.customer + " - " + self.customer_name,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)
	# tip
	if self.tip_amount> 0:
		if not self.default_tip_account:
			frappe.throw(_("Please select default tip account"))
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":self.default_tip_account,
				"credit_amount":self.tip_amount,
				"againt":self.customer + " - " + self.customer_name,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)

	# tip
	if self.total_fee> 0:
		if not self.default_bank_fee_account:
			frappe.throw(_("Please select default bank fee account"))
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":self.default_bank_fee_account,
				"credit_amount":self.total_fee,
				"againt":self.customer + " - " + self.customer_name,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)
  
	submit_general_ledger_entry(docs=docs)


def submit_sale_to_general_ledger_entry_after_cancel(self):
 	pass