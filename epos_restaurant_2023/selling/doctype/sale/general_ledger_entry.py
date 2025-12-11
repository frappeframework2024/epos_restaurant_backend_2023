
import frappe
import json
from frappe import _
from  epos_restaurant_2023.api.cache_function import get_default_account_from_pos_config, get_default_account_from_revenue_group
from epos_restaurant_2023.inventory.inventory import (
	get_product_cost, 
	get_uom_conversion
)

def submit_sale_to_general_ledger_entry(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	sale_products = [a for a in self.sale_products if (a.coupons or "") == ""]
	docs = []
	# income account'
	for acc in set([d.default_income_account for d in sale_products]):
		if not acc:
				frappe.throw(_("Please enter income account"))
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":acc,
			"amount":sum([d.sub_total for d in sale_products if d.default_income_account==acc]),
			"againt":self.customer + " - " + self.customer_name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"party_type":"Customer",
			"party":self.customer,
			"party_name":self.customer_name,
			"type":"Income"
		}
	
		docs.append(doc)
	# Discount Account
	if self.total_discount:
		discount_sale_products = [d for d in self.sale_products if d.allow_discount==1]
 

		if  set([d.default_discount_account for d in discount_sale_products if not d.default_discount_account and d.allow_discount==1]):
			frappe.throw(_("Please enter default discount"))

		for  acc in set([d.default_discount_account for d in discount_sale_products if d.default_discount_account and d.allow_discount==1]):

			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc,
				"amount":sum([d.total_discount for d in discount_sale_products if d.default_discount_account==acc and d.allow_discount==1]),
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name,
				"type":"Income"#not use in db

			}
			root_type = frappe.get_cached_value("Chart Of Account",acc,"root_type")
			if root_type == "Income":
				if doc["amount"] > 0:
					doc["credit_amount"] = doc["amount"]
				else:
					doc["debit_amount"] = doc["amount"]
			docs.append(doc)
  
	# asset account from payment
	if self.payment:
		error = ""
		for a in self.payment:
			if (a.default_account or "") == "":
				error += ("Please enter default account for payment type '{0}'</br>".format(a.payment_type))
		if error:
			frappe.throw(error)

		for acc in set([d.default_account for d in self.payment if not d.payment_type_group=="On Account"]):
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc  ,
				"amount":sum([d.amount + (d.fee_amount or 0) for d in self.payment  if d.default_account==acc]),
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Income",
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name,
				"remark": "Redeem Coupon" if self.sale_type == "Redeem" else "",
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
			"amount":self.balance,
			# "againt":",".join([d["account"] for d in docs]),
			"againt_voucher_type":"Sale",
			"againt_voucher_number": self.name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Asset",
			"party_type": "Customer",
			"party": self.customer,
			"party_name":self.customer_name

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
				"amount":self.tax_1_amount if frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"amount":self.tax_1_amount if not frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name,
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
				"amount":self.tax_2_amount if frappe.get_cached_value("Chart Of Account",self.default_tax_2_account,"root_type") in ["Asset","Expenses"] else 0,
				"amount":self.tax_2_amount if not frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name
			}
		docs.append(doc)
	
 	# tax 3 
	# tax 3
	if self.tax_3_amount!=0:
		if not self.default_tax_3_account:
			frappe.throw(_("Please select tax 3 account"))	
		
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account": self.default_tax_3_account,
				"amount":self.tax_3_amount if frappe.get_cached_value("Chart Of Account",self.default_tax_3_account,"root_type") in ["Asset","Expenses"] else 0,
				"amount":self.tax_3_amount if not frappe.get_cached_value("Chart Of Account",self.default_tax_1_account,"root_type") in ["Asset","Expenses"] else 0,
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name,
			}
		docs.append(doc)

	# cost of good sold account
	
	if sum([d.quantity* (d.cost or 0) for d in sale_products if d.is_inventory_product==1]):	
		for acc in set([d.default_expense_account for d in sale_products]):
			if not acc:
				frappe.throw(_("Please enter expense account"))
			for inv in set([d.default_inventory_account for d in sale_products]):
				goods_sold_amount = sum([d.quantity* (d.cost or 0) for d in sale_products if (d.is_inventory_product==1 and d.default_expense_account==acc and d.default_inventory_account == inv)])
				if goods_sold_amount != 0:
					doc = {
							"doctype":"General Ledger",
							"posting_date":self.posting_date,
							"account": acc,
							"amount":goods_sold_amount,
							"againt": inv,
							"againt_voucher_type":"Sale",
							"againt_voucher_number": self.name,
							"voucher_type":"Sale",
							"voucher_number":self.name,
							"business_branch": self.business_branch,
							"party_type":"Customer",
							"party":self.customer,
							"party_name":self.customer_name,
							"type":"Asset"#not use in db
						}
					docs.append(doc)
	if sum([d.quantity*(d.cost or 0)  for d in sale_products if d.is_inventory_product==1]):
	# deduct stock in hand
		for acc in set([d.default_expense_account for d in sale_products]):
			if not acc:
				frappe.throw(_("Please enter expense account"))
			for inv in set([d.default_inventory_account for d in sale_products]):
				stock_in_hand_amount = sum([d.quantity*(d.cost or 0)  for d in sale_products if (d.is_inventory_product==1 and d.default_expense_account==acc and d.default_inventory_account == inv)])
				if stock_in_hand_amount != 0:
					doc = {
							"doctype":"General Ledger",
							"posting_date":self.posting_date,
							"account":inv,
							"amount":stock_in_hand_amount*-1,
							"againt":acc,
							"againt_voucher_type":"Sale",
							"againt_voucher_number": self.name,
							"voucher_type":"Sale",
							"voucher_number":self.name,
							"business_branch": self.business_branch,
							"party_type":"Customer",
							"party":self.customer,
							"party_name":self.customer_name,
							"type":"Asset"#not use in db
						}
					docs.append(doc)
	
	
	# cost of good sold for product have recipes
	recipe_acc = []
	recipe_inventory_acc = []
	for sp in sale_products:
		if (sp.is_inventory_product or 0) == 0:
			product = frappe.get_cached_doc("Product",sp.product_code)
			if len(product.product_recipe or []) > 0:
				for r in product.product_recipe:
					recipe = frappe.get_cached_doc("Product",r.product)
					if recipe.is_inventory_product == 1:
						# get cost or recipe item
						cost = get_product_cost(self.stock_location,r.product)
						uom_conversion = get_uom_conversion(recipe.unit,r.unit)
						total_amount = (cost / uom_conversion * r.quantity)
						stock_acc = get_recipe_defalt_inventory_account(self,recipe)
						recipe_acc.append({"account":get_expense_account(self,recipe),"stock_account":stock_acc,"total_amount":total_amount})
						recipe_inventory_acc.append({"account":stock_acc})
	group_recipe_acc = set([d["account"] for d in recipe_acc])
	recipe_inventory_acc = set([d["account"] for d in recipe_inventory_acc])
	if len(group_recipe_acc) > 0:
		for acc in group_recipe_acc:
			for inventory_acc in recipe_inventory_acc:
				recipe_amount = sum([d["total_amount"] for d in recipe_acc if d["account"]==acc and d["stock_account"] == inventory_acc])
				if recipe_amount != 0:
					doc = {
						"doctype":"General Ledger",
						"posting_date":self.posting_date,
						"account": acc,
						"amount":recipe_amount,
						"againt": inventory_acc,
						"againt_voucher_type":"Sale",
						"againt_voucher_number": self.name,
						"voucher_type":"Sale",
						"voucher_number":self.name,
						"business_branch": self.business_branch,
						"party_type":"Customer",
						"party":self.customer,
						"party_name":self.customer_name,
						"type":"Asset"
					}
					docs.append(doc)
					doc = {
						"doctype":"General Ledger",
						"posting_date":self.posting_date,
						"account": inventory_acc,
						"amount": recipe_amount*-1,
						"againt": acc,
						"againt_voucher_type":"Sale",
						"againt_voucher_number": self.name,
						"voucher_type":"Sale",
						"voucher_number":self.name,
						"business_branch": self.business_branch,
						"party_type":"Customer",
						"party":self.customer,
						"party_name":self.customer_name,
						"type":"Asset"
					}
					docs.append(doc)
		
	# cash coupon claim
	if self.total_cash_coupon_claim> 0:
		if not self.default_cash_coupon_claim_account:
			frappe.throw(_("Please select default cash coupon account"))
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":self.default_cash_coupon_claim_account,
				"amount":self.total_cash_coupon_claim,
				"againt":self.customer + " - " + self.customer_name,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name,
				"business_branch": self.business_branch,
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
				"party_type":"Customer",
			"party":self.customer,
			"party_name":self.customer_name,
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
				"amount":self.tip_amount,
				"againt":self.customer + " - " + self.customer_name,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name,
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
				"amount":self.total_fee,
				"againt":self.customer + " - " + self.customer_name,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"party_type":"Customer",
				"party":self.customer,
				"party_name":self.customer_name,
				"business_branch": self.business_branch,
			}
		docs.append(doc)
  
	if self.trade_in_products:
		amount = sum([d.amount for d in self.trade_in_products if d.is_inventory==1])
		if amount > 0:
			doc = {
					"doctype":"General Ledger",
					"posting_date":self.posting_date,
					"account":frappe.get_cached_value("Business Branch",self.business_branch,"default_inventory_account"),
					"credit_amount":amount,
					# "againt": self.customer + " - " + self.customer_name,
					"againt_voucher_type":"Sale",
					"againt_voucher_number": self.name,
					"voucher_type":"Sale",
					"voucher_number":self.name,
					"party_type":"Customer",
					"party":self.customer,
					"party_name":self.customer_name,
					"business_branch": self.business_branch,
				}
			docs.append(doc)
   
		# post to expense account
		amount = sum([d.amount for d in self.trade_in_products if d.is_inventory ==0])
		if amount > 0:
			doc = {
					"doctype":"General Ledger",
					"posting_date":self.posting_date,
					"account":frappe.get_cached_value("Business Branch",self.business_branch,"default_sale_expense_account"),
					"debit_amount":amount,
					# "againt": self.customer + " - " + self.customer_name,
					"againt_voucher_type":"Sale",
					"againt_voucher_number": self.name,
					"voucher_type":"Sale",
					"voucher_number":self.name,
					"party_type":"Customer",
					"party":self.customer,
					"party_name":self.customer_name,
					"business_branch": self.business_branch,
				}
			docs.append(doc)
   
	submit_general_ledger_entry(docs=docs)

def get_expense_account(self,recipe):
	account = ""
	# 1 get from product
	sql="select default_expense_account from `tabProduct Default Account` where parent = %(parents)s and business_branch =%(business_branch)s"
	acc = frappe.db.sql(sql, {"parents":recipe.name, "business_branch":self.business_branch},as_dict=1)
	if len(acc) > 0:
		account = acc[0]["default_expense_account"]
  
	# 2 get from pos_config
	if account == "":
		acc = get_default_account_from_pos_config(json.dumps({"business_branch": self.business_branch, "pos_config":self.pos_config, "revenue_groups" : list([recipe.revenue_group])}))
		if len(acc)>0:
			account = acc[0]["default_expense_account"]

	# 3 get account code from revenue group 
	if account == "":
		acc = get_default_account_from_revenue_group(json.dumps( {"business_branch": self.business_branch, "revenue_groups": list([recipe.revenue_group])}))
		if len(acc)>0:
			account = acc[0]["default_expense_account"]
	
	# 4 get account code from revenue group 
	if account == "":
		acc = frappe.get_cached_value("Business Branch",self.business_branch, "default_cost_of_good_sold_account")
		if acc:
			account = acc
	
	return account

def get_recipe_defalt_inventory_account(self,recipe):
	account = ""
	acc = [d.default_stock_account for d in recipe.default_account if d.business_branch == self.business_branch]
	if acc:
		account = acc[0]
	else:
		account = frappe.get_cached_value("Business Branch",self.business_branch,"default_inventory_account")
	return account