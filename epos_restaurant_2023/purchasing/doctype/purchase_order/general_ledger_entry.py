import frappe
def submit_purchase_to_general_ledger_entry_on_submit(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	# stock account
	stock_asset_account = set([d.default_account for d in self.purchase_order_products])
	if self.grand_total > 0:
		for acc in stock_asset_account:
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc,
				"debit_amount":sum([d.amount  for d in self.purchase_order_products if d.default_account==acc]),
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
		
		# post discount to expense account
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
  
	submit_general_ledger_entry(docs=docs)
 
def submit_purchase_to_general_ledger_entry_on_cancel(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	# stock account
	stock_asset_account = set([d.default_account for d in self.purchase_order_products])
	for acc in stock_asset_account:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":acc,
			"credit_amount":sum([d.amount for d in self.purchase_order_products if d.default_account==acc]),
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