
import frappe
from frappe import _
from epos_restaurant_2023.inventory.inventory import (
	get_product_cost, 
	get_uom_conversion
)

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
			"amount":sum([d.sub_total for d in self.sale_products if d.default_income_account==acc]),
			"againt":self.customer + " - " + self.customer_name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Income"
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
				"amount":sum([d.total_discount for d in self.sale_products if d.default_discount_account==acc and d.allow_discount==1]),
				"againt":self.customer + " - " + self.customer_name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
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
		for acc in set([d for d in self.payment if not d.payment_type_group=="On Account"]):
			if not  acc.default_account:
				frappe.throw(_("Please enter default account for payment type {payment_type}".format(payment_type=acc.payment_type)))
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":acc.default_account  ,
				"amount":sum([d.amount + (d.fee_amount or 0) for d in self.payment  if d.default_account==acc.default_account]),
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
			"amount":self.balance,
			# "againt":",".join([d["account"] for d in docs]),
			"againt_voucher_type":"Sale",
			"againt_voucher_number": self.name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Asset",
			"party_type": "Customer",
			"party":self.customer

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
			}
		docs.append(doc)

	# cost of good sold account
	
	if sum([d.quantity* (d.cost or 0) for d in self.sale_products if d.is_inventory_product==1]):	

		if not self.default_cost_of_goods_sold_account:
				frappe.throw(_('Please select default cost of goods sold account'))
	
		doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account": self.default_cost_of_goods_sold_account,
				"amount":sum([d.quantity* (d.cost or 0) for d in self.sale_products if d.is_inventory_product==1]),
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
				"amount":sum([d.quantity*(d.cost or 0)  for d in self.sale_products if d.is_inventory_product==1])*-1,
				"againt":self.default_cost_of_goods_sold_account,
				"againt_voucher_type":"Sale",
				"againt_voucher_number": self.name,
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"type":"Asset"#not use in db
			}
		docs.append(doc)

	
	# cost of good sold for product have recipes
	total_amount = 0
	for sp in self.sale_products:
		if (sp.is_inventory_product or 0) == 0:
			product = frappe.get_cached_doc("Product",sp.product_code)
			if len(product.product_recipe or []) > 0:
				for r in product.product_recipe:
					recipe = frappe.get_cached_doc("Product",r.product)
					if recipe.is_inventory_product == 1:
						# get cost or recipe item
						cost = get_product_cost(self.stock_location,r.product)
						uom_conversion = get_uom_conversion(recipe.unit,r.unit)
						total_amount += total_amount + (cost / uom_conversion * r.quantity)
	if total_amount > 0:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account": self.default_cost_of_goods_sold_account,
			"amount":total_amount,
			"againt":self.default_inventory_account,
			"againt_voucher_type":"Sale",
			"againt_voucher_number": self.name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Asset"
		}
		docs.append(doc)
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account": self.default_inventory_account,
			"amount":total_amount*-1,
			"againt":self.default_cost_of_goods_sold_account,
			"againt_voucher_type":"Sale",
			"againt_voucher_number": self.name,
			"voucher_type":"Sale",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
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
					"business_branch": self.business_branch,
				}
			docs.append(doc)
   
	submit_general_ledger_entry(docs=docs)


 