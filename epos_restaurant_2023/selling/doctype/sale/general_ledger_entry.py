import frappe
def submit_sale_to_general_ledger_entry(self):
    
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	# income account
	for acc in set([d.default_income_account for d in self.sale_products]):
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":acc,
			"credit_amount":sum([d.amount for d in self.sale_products if d.default_income_account==acc]),
			"againt":self.customer + " - " + self.customer_name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Income"#not use in db

		}
		docs.append(doc)
	# Discount Account
	if self.total_discount:
		for  acc in set([d.default_discount_account for d in self.sale_products if d.default_discount_account]):
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc,
				"debit_amount":sum([d.total_discount for d in self.sale_products if d.default_discount_account==acc]),
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Income"#not use in db

			}
			docs.append(doc)
  
	# asset account from payment
	if self.payment:
		for acc in set([d.default_account for d in self.payment if not d.payment_type_group=="On Account"]):
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc,
				"debit_amount":sum([d.amount for d in self.payment if d.default_account==acc]),
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Income"#not use in db

			}
			docs.append(doc)
	if self.balance:
		# post gl entry to default recivable account from business branch setting

		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":frappe.db.get_value("Business Branch", self.business_branch, "default_receivable_account"),
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

	# change account

	# cost of good sold account
	doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":frappe.db.get_value("Business Branch", self.business_branch, "default_cost_of_good_sold_account"),
			"debit_amount":sum([d.quantity* (d.cost or 0) for d in self.sale_products if d.is_inventory_product==1]),
			"againt":frappe.db.get_value("Business Branch", self.business_branch, "stock_adjustment_account"),
			"againt_voucher_type":"Sale",
			"againt_voucher_number": self.name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Asset"#not use in db
		}
	docs.append(doc)
	# deduct stock in hand
	doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":frappe.db.get_value("Business Branch", self.business_branch, "default_inventory_account"),
			"credit_amount":sum([d.quantity*(d.cost or 0)  for d in self.sale_products if d.is_inventory_product==1]),
			"againt":frappe.db.get_value("Business Branch", self.business_branch, "default_cost_of_good_sold_account"),
			"againt_voucher_type":"Sale",
			"againt_voucher_number": self.name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Asset"#not use in db
		}
	docs.append(doc)

	


	submit_general_ledger_entry(docs=docs)