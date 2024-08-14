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
				"debit_amount":sum([(d.sub_total-d.total_discount)  for d in self.purchase_order_products if d.stock_account==acc]),
				"againt":self.default_credit_account,
				"voucher_type":"Purchase Order",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"remark" : "Accounting Entry Purchase Order"
			}
			docs.append(doc)
	
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":self.default_credit_account,
				"credit_amount":(self.sub_total),
				"againt": ",".join(stock_asset_account),
				"voucher_type":"Purchase Order",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"remark" : "Accounting Entry Purchase Order",
				"party_type" : "Vendor",
				"party":self.vendor
			}
		docs.append(doc)

	if self.total_discount > 0:
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
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.default_credit_account,
			"debit_amount":self.total_discount,
			"againt":self.default_discount_account,
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark": "Purchase Order discount",
			"party_type" : "Vendor",
			"party":self.vendor
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
			"credit_amount":sum([(d.sub_total-d.total_discount) for d in self.purchase_order_products if d.stock_account==acc]),
			"againt":self.default_credit_account,
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"is_canceclled":1,
			"remark" : "Cancel Purchase Order"
		}
		docs.append(doc)
	#post to payable account	
	doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.default_credit_account,
			"debit_amount":self.sub_total,
			"againt": ",".join(stock_asset_account),
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"is_canceclled":1,
			"remark" : "Cancel Purchase Order"
		}
	docs.append(doc)	
	
	if self.total_discount > 0:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.default_discount_account,
			"debit_amount":self.total_discount,
			"againt":self.default_credit_account,
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"is_canceclled":1,
			"remark" : "Cancel Purchase Order"
		}
		docs.append(doc)
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.default_credit_account,
			"credit_amount":self.total_discount,
			"againt":self.default_discount_account,
			"voucher_type":"Purchase Order",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"is_canceclled":1,
			"remark" : "Cancel Purchase Order"
		}
		docs.append(doc)
	submit_general_ledger_entry(docs=docs)	