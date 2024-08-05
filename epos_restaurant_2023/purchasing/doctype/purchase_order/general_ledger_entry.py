import frappe
def submit_purchase_to_general_ledger_entry_on_submit(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	stock_asset_account = set([d.stock_account for d in self.purchase_order_products])
	if self.grand_total > 0:
		for acc in stock_asset_account:
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc,
				"debit_amount":sum([d.amount  for d in self.purchase_order_products if d.stock_account==acc]),
				"againt":self.default_credit_account,
				"voucher_type":"Purchase Order",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Income"#not use in db

			}
			doc["remark"] = "Accounting Entry for Stock"
			docs.append(doc)
		#post to payable account	
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":self.default_credit_account,
				"credit_amount":self.grand_total,
				"againt": ",".join(stock_asset_account),
				"voucher_type":"Purchase Order",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)
	if self.total_discount:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.default_discount_account,
			"credit_amount":self.total_discount,
			"againt":self.default_credit_account,
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark": "Purchase Order discount"
		}
		docs.append(doc)	

	if abs(self.total_expense_cost)>0:
		# deduct from stock asset
		expense_account = set([d.expense_account for d in self.purchase_order_products if d.expense_account])
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":frappe.get_cached_value("Business Branch", self.business_branch,"default_inventory_account"),
			"credit_amount": 0 if self.total_expense_cost<0 else abs(self.total_expense_cost),
			"debit_amount": 0 if self.total_expense_cost>0 else abs(self.total_expense_cost),
			"againt":",".join(expense_account),#get again from expense account
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark": "Average cost calculation deduction"
		}
		docs.append(doc)
		# update exprense account
		for ex_acc in expense_account:
			amount = sum([d.expense_cost for d in self.purchase_order_products if d.expense_account == ex_acc])
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":ex_acc,
				"debit_amount": 0 if amount<0 else abs(amount),
				"credit_amount": 0 if amount>0 else abs(amount),
				"againt":frappe.get_cached_value("Business Branch", self.business_branch,"default_inventory_account"),
				"voucher_type":"Purchase Order",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"remark": "Cost expense during average cost calculation"
			}
			docs.append(doc)
  
	submit_general_ledger_entry(docs=docs)
 
def submit_purchase_to_general_ledger_entry_on_cancel(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	# stock account
	stock_asset_account = set([d.stock_account for d in self.purchase_order_products])
	for acc in stock_asset_account:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":acc,
			"credit_amount":sum([d.amount for d in self.purchase_order_products if d.stock_account==acc]),
			"againt":self.default_credit_account,
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"is_canceclled":1,
			"type":"Income"#not use in db

		}
		doc["remark"] = "On Cancel Of Entry for Stock"
		docs.append(doc)
	#post to payable account	
	doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.default_credit_account,
			"debit_amount":self.grand_total,
			"againt": ",".join(stock_asset_account),
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"is_canceclled":1,
			"type":"Income"#not use in db
		}
	docs.append(doc)	
	submit_general_ledger_entry(docs=docs)	