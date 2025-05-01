# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from datetime import datetime

from frappe.model.document import Document


class SPASaleInvoice(Document):
	def validate(self): 	

		#get exchange rate
		if self.is_new() or self.exchange_rate is None or self.change_exchange_rate is None:
			main_currency = frappe.get_doc("Currency",frappe.db.get_default("currency"))
			second_currency = frappe.get_doc("Currency",frappe.db.get_default("second_currency"))
			exchange_rate_main_currency = frappe.db.get_default("exchange_rate_main_currency")
			to_currency = second_currency.name
			if (exchange_rate_main_currency != main_currency.name):
				to_currency = main_currency.name 

			exchange_rate = frappe.db.sql("""select 
											exchange_rate,
											change_exchange_rate
										from `tabCurrency Exchange` 
										where docstatus=1 
										and from_currency= %(from_currency)s
										and to_currency=%(to_currency) s
										order by posting_date desc
										limit 1""",{
											"from_currency":exchange_rate_main_currency,
											"to_currency":to_currency,
										}, as_dict= 1)
			self.exchange_rate = exchange_rate[0]["exchange_rate"] or 1
			self.change_exchange_rate = exchange_rate[0]["change_exchange_rate"] or 1

		if len ([ d for d in  self.items if d.quantity ==0]) > 0:
				frappe.throw(_("The quantity of item not allow value zero"))
		update_sale_product_data(self=self)
		self.item_discount = round_value(sum(  sp.discount_amount for sp in self.items if sp.discount_amount != 0))
		self.total_quantity = round_value( sum(sp.quantity for sp in self.items))
		self.sub_total = round_value( sum(sp.price * sp.quantity for sp in self.items))

		discountable_amount = sum(sp.price * sp.quantity for sp in self.items if sp.discount_amount == 0)
		self.discount_amount =  self.discount or 0 if self.discount_type == "Amount"  else discountable_amount * ((self.discount or 0)/100)
		self.total_discount = self.item_discount + self.discount_amount

		validate_tax(doc=self)	

		self.total_amount = round_value(self.sub_total - self.total_discount + self.tax_1_amount + self.tax_2_amount + self.tax_3_amount)


		#payment validate

		validate_payment(self)


	def on_submit(self):
		if len([d for d in self.items if d.is_required_therapist == 1 and  len(d.therapist_data or [])<=0  ]) >0:
			frappe.throw(_("Please assign therapist before submit"))
			
		validate_payment_on_submit(self)

		#generate to sale
		generate_to_sale(self)

	def on_cancel(self):
		pass

def update_sale_product_data(self):
	for sp in self.items:
		sp.discount_amount = sp.discount_amount or 0
		sp.discount_amount  =  round_value( (sp.discount or 0 if sp.discount_type == "Amount" else (sp.quantity * sp.price) * (sp.discount / 100) ))
		sp.amount = round_value( (sp.quantity * sp.price) -  sp.discount_amount)

 
def validate_tax(doc):	 
	if  doc.tax_rule:
		doc.tax_rule_data =[]
		if frappe.db.exists("Tax Rule", doc.tax_rule):
			_tax_rule = frappe.get_doc("Tax Rule", doc.tax_rule)
			doc.tax_rule_data = _tax_rule.tax_rule_data
			#
			amount = round_value( sum(sp.price * sp.quantity for sp in doc.items if sp.allow_tax == 1))

			#load tax rule
			tax_val  = json.loads(doc.tax_rule_data)  	
			doc.tax_1_rate = tax_val["tax_1_rate"]	
			doc.tax_2_rate = tax_val["tax_2_rate"]	
			doc.tax_3_rate = tax_val["tax_3_rate"]	

			#tax 1
			doc.tax_1_taxable_amount = amount 
			## cal tax 1 after discount validate

			if tax_val["calculate_tax_1_after_discount"] == 1:					
				doc.tax_1_taxable_amount = amount - doc.total_discount

			doc.tax_1_taxable_amount *= (tax_val["percentage_of_price_to_calculate_tax_1"]/100)
			doc.tax_1_amount = round_value( (doc.tax_1_taxable_amount or 0) * ((doc.tax_1_rate or 0)/100))

			#tax 2
			doc.tax_2_taxable_amount = amount 
			#cal tax2 taxable after disc.
			if tax_val["calculate_tax_2_after_discount"]==1:
				doc.tax_2_taxable_amount = amount  - doc.total_discount

			#cal tax2 taxable after add tax1
			if tax_val["calculate_tax_2_after_adding_tax_1"]==1:
				doc.tax_2_taxable_amount +=  doc.tax_1_amount

			doc.tax_2_taxable_amount *= (tax_val["percentage_of_price_to_calculate_tax_2"]/100)
			doc.tax_2_amount =  round_value((doc.tax_2_taxable_amount or 0) *  ((doc.tax_2_rate or 0) /100))

			#tax 3
			doc.tax_3_taxable_amount =  amount
			#cal tax3 taxable after disc.
			if tax_val["calculate_tax_3_after_discount"]==1:
				doc.tax_3_taxable_amount = amount - doc.total_discount 
			
			#cal tax3 taxable after add tax1
			if tax_val["calculate_tax_3_after_adding_tax_1"]==1:
				doc.tax_3_taxable_amount =   doc.tax_3_taxable_amount +  doc.tax_1_amount 
			
			#cal tax3 taxable after add tax2
			if tax_val["calculate_tax_3_after_adding_tax_2"]==1:
				doc.tax_3_taxable_amount = doc.tax_3_taxable_amount +  doc.tax_2_amount 
			
			doc.tax_3_taxable_amount *= (tax_val["percentage_of_price_to_calculate_tax_3"]/100)
			doc.tax_3_amount = round_value(  (doc.tax_3_taxable_amount or 0) *  ((doc.tax_3_rate or 0) /100))
			
			#total tax
			# doc.total_tax = doc.tax_1_amount + doc.tax_2_amount + doc.tax_3_amount

	else:
		doc.tax_1_rate = None	
		doc.tax_1_taxable_amount =0
		doc.tax_1_amount=0

		doc.tax_2_rate = None
		doc.tax_2_taxable_amount =0
		doc.tax_2_amount=0

		doc.tax_3_rate = None	
		doc.tax_3_taxable_amount =0
		doc.tax_3_amount=0
			# doc.total_tax =0

	return {
		"tax_1_rate":doc.tax_1_rate,
		"tax_2_rate":doc.tax_2_rate,
		"tax_3_rate":doc.tax_3_rate,
		"tax_1_taxable_amount":doc.tax_1_taxable_amount,
		"tax_2_taxable_amount":doc.tax_2_taxable_amount,
		"tax_3_taxable_amount":doc.tax_3_taxable_amount,
		"tax_1_amount":doc.tax_1_amount,
		"tax_2_amount":doc.tax_2_amount,
		"tax_3_amount":doc.tax_3_amount,
	}

def validate_payment(self):
	for p in self.payments:
		p.amount = round_value(p.input_amount/(p.exchange_rate or 1))

	total_payment_amount = round_value(sum(p.amount for p in self.payments))
	self.total_paid = total_payment_amount
	change_amount = (self.total_paid or 0) - self.total_amount
	self.changed_amount = (0 if change_amount <= 0 else change_amount)	
	balance = round_value( self.total_amount - (self.total_paid or 0))
	self.balance = 0 if balance < 0 else balance


def validate_payment_on_submit(self):
	total_payment_amount =round_value( sum(p.amount for p in self.payments))
	if total_payment_amount < self.total_amount:
		frappe.throw(_("Please kindly make full payment for this invoice"))


def generate_to_sale(self):
	create_new = False
	if self.sale:
		#check sale exist
		if not frappe.db.exists("SPA Sale", self.sale):
			create_new = True
	else:
		create_new = True

	if create_new:
		doc_json = {
			"doctype": "Sale",	
			"business_branch":self.business_branch,
			"outlet":self.outlet,
			"stock_location":self.stock_location,
			"custom_bill_number":self.name,
			"customer": self.customer,
			"posting_date": self.posting_date,
			"tax_rule": self.tax_rule,
			"exchange_rate": self.exchange_rate,
			"change_exchange_rate": self.change_exchange_rate,
			"sale_products":[],
			"payment":[]
		}

		items_json=[]
		date_obj = datetime.strptime(self.posting_date, "%Y-%m-%d").date()
		for sp in self.items: 
			items_json.append({
				"product_code":sp.article,
				"product_name":sp.article_name_en,
				"product_name_kh":sp.article_name_kh,
				"portion":sp.duration,
				"quantity":sp.quantity,
				"price":sp.price,
				"regular_price":sp.regular_price,
				"discount":sp.discount,
				"discount_type":sp.discount_type,
				"discount_amount":sp.discount_amount,
				"selling_price":sp.price,
				"tax_rule": self.tax_rule if sp.allow_tax == 1 else "NONE_TAX",
				"time_in":  datetime.combine(date_obj, datetime.strptime(sp.time_in, "%H:%M:%S").time()) ,
				"time_out": datetime.combine(date_obj, datetime.strptime(sp.time_out, "%H:%M:%S").time())  ,
				"is_require_employee": sp.is_required_therapist,
				"employee_names": sp.therapist_name,
				"employees": sp.therapist_data,
				"unit":sp.unit,
				"base_unit":sp.unit,
			})

		doc_json["sale_products"] = items_json	

		payment_json=[]
		for p in self.payments:
			payment_json.append({
				"input_amount":p.input_amount,
				"amount":p.amount,
				"payment_type":p.payment_type,
				"exchange_rate":p.exchange_rate,
			})
		doc_json["payment"] = payment_json


		doc = frappe.get_doc(doc_json)
		doc.flags.ignore_permissions = True  # Skip all permission checks
		doc.insert()  # Save
		doc.submit()  # Submit
		self.sale = doc.name

#function round decimal value
def round_value(value, precision = 2):
	return round(value,precision)


@frappe.whitelist()
def get_product_by_id(name):
	doc = frappe.get_doc("Product", name)
	if len( doc.product_price) > 0:
		result = []
		for d in doc.product_price:
			result.append({
				"is_require_employee": doc.is_require_employee,
				"portion": d.portion,
				"base_unit":doc.unit, 
				"unit":d.unit, 
				"price": d.price
			})
		return result
	
	else:
		return [{
			"is_require_employee": doc.is_require_employee,
			"portion": "",
			"base_unit":doc.unit, 
			"unit":doc.unit, 
			"price": doc.price
		}]


@frappe.whitelist()
def client_script_update_summary(param):
	doc = json.loads(param)	

 
	#udpate sale item summary
	for sp in doc["items"]:
		sp["discount_amount"] = sp["discount_amount"] or 0
		sp["discount_amount"]  =  round_value( (sp["discount"] or 0 if sp["discount_type"] == "Amount" else (sp["quantity"] * sp["price"]) * (sp["discount"] / 100) ))
		sp["amount"] = round_value( (sp["quantity"] * sp["price"]) -  sp["discount_amount"])
	##end update sale item summary


	doc["item_discount"] = round_value(sum(sp["discount_amount"] for sp in doc["items"] if sp["discount_amount"] != 0))
	doc["total_quantity"] = round_value( sum(sp["quantity"] for sp in doc["items"]))
	doc["sub_total"] = round_value( sum(sp["price"] * sp["quantity"] for sp in doc["items"]))

	discountable_amount = sum(sp["price"] * sp["quantity"] for sp in doc["items"] if sp["discount_amount"] == 0)
	doc["discount_amount"] =  doc["discount"] or 0 if doc["discount_type"] == "Amount"  else discountable_amount * ((doc["discount"] or 0)/100)
	doc["total_discount"] = doc["item_discount"] + doc["discount_amount"]

	##tax validate
	doc["tax_rule_data"] = None
	if  doc["tax_rule"]:
		if frappe.db.exists("Tax Rule", doc["tax_rule"]):
			_tax_rule = frappe.get_doc("Tax Rule", doc["tax_rule"])
 
			doc["tax_rule_data"] = _tax_rule.tax_rule_data
			
			amount = round_value( sum(sp["price"] * sp["quantity"] for sp in doc["items"] if sp["allow_tax"] == 1))		 

			#load tax rule
			tax_val  = json.loads(doc["tax_rule_data"])
			doc["tax_1_rate"] = tax_val["tax_1_rate"]	
			doc["tax_2_rate"] = tax_val["tax_2_rate"]	
			doc["tax_3_rate"] = tax_val["tax_3_rate"]	

			#tax 1
			doc["tax_1_taxable_amount"] = amount 
			## cal tax 1 after discount validate

			if tax_val["calculate_tax_1_after_discount"] == 1:					
				doc["tax_1_taxable_amount"] = amount - doc["total_discount"]

			doc["tax_1_taxable_amount"] *= (tax_val["percentage_of_price_to_calculate_tax_1"]/100)
			doc["tax_1_amount"] = round_value( (doc["tax_1_taxable_amount"] or 0) * ((doc["tax_1_rate"] or 0)/100))

			#tax 2
			doc["tax_2_taxable_amount"] = amount 
			#cal tax2 taxable after disc.
			if tax_val["calculate_tax_2_after_discount"]==1:
				doc["tax_2_taxable_amount"] = amount  - doc["total_discount"]

			#cal tax2 taxable after add tax1
			if tax_val["calculate_tax_2_after_adding_tax_1"]==1:
				doc["tax_2_taxable_amount"] +=  doc["tax_1_amount"]

			doc["tax_2_taxable_amount"] *= (tax_val["percentage_of_price_to_calculate_tax_2"]/100)
			doc["tax_2_amount"] =  round_value((doc["tax_2_taxable_amount"] or 0) *  ((doc["tax_2_rate"] or 0) /100))

			#tax 3
			doc["tax_3_taxable_amount"] =  amount
			#cal tax3 taxable after disc.
			if tax_val["calculate_tax_3_after_discount"]==1:
				doc["tax_3_taxable_amount"] = amount - doc["total_discount"] 
			
			#cal tax3 taxable after add tax1
			if tax_val["calculate_tax_3_after_adding_tax_1"]==1:
				doc["tax_3_taxable_amount"] =   doc["tax_3_taxable_amount"] +  doc["tax_1_amount"] 
			
			#cal tax3 taxable after add tax2
			if tax_val["calculate_tax_3_after_adding_tax_2"]==1:
				doc["tax_3_taxable_amount"] = doc["tax_3_taxable_amount"] +  doc["tax_2_amount"] 
			
			doc["tax_3_taxable_amount"] *= (tax_val["percentage_of_price_to_calculate_tax_3"]/100)
			doc["tax_3_amount"] = round_value(  (doc["tax_3_taxable_amount"] or 0) *  ((doc["tax_3_rate"] or 0) /100))
			
			#total tax
			# doc.total_tax = doc.tax_1_amount + doc.tax_2_amount + doc.tax_3_amount

	else:
		doc["tax_1_rate"] = None	
		doc["tax_1_taxable_amount"] =0
		doc["tax_1_amount"]=0

		doc["tax_2_rate"] = None
		doc["tax_2_taxable_amount"] =0
		doc["tax_2_amount"]=0

		doc["tax_3_rate"] = None	
		doc["tax_3_taxable_amount"] =0
		doc["tax_3_amount"]=0
			# doc.total_tax =0

	##end tax validate


	doc["total_amount"] = round_value(doc["sub_total"] - doc["total_discount"] + doc["tax_1_amount"] + doc["tax_2_amount"] + doc["tax_3_amount"])


	##validate payment
	for p in doc["payments"]:
		p["amount"] = round_value(p["input_amount"]/(p["exchange_rate"] or 1))

	total_payment_amount = round_value(sum(p["amount"] for p in doc["payments"]))
	doc["total_paid"] = total_payment_amount
	change_amount = (doc["total_paid"] or 0) - doc["total_amount"]
	doc["balance"] = round_value( doc["total_amount"] - (doc["total_paid"] or 0))
	doc["balance"] = 0 if doc["balance"]  < 0 else doc["balance"]

	doc["changed_amount"] = (0 if change_amount <= 0 else change_amount)	
	
	return {
		"item_discount":doc["item_discount"],
		"total_quantity":doc["total_quantity"],
		"sub_total":doc["sub_total"],
		"discount_amount":doc["discount_amount"],
		"total_discount":doc["total_discount"],
		"tax_rule_data":json.loads( doc["tax_rule_data"] or '[]'),
		"tax_1_rate":doc["tax_1_rate"],
		"tax_2_rate":doc["tax_2_rate"],
		"tax_3_rate":doc["tax_3_rate"],
		"tax_1_taxable_amount":doc["tax_1_taxable_amount"],
		"tax_2_taxable_amount":doc["tax_2_taxable_amount"],
		"tax_3_taxable_amount":doc["tax_3_taxable_amount"],
		"tax_1_amount":doc["tax_1_amount"],
		"tax_2_amount":doc["tax_2_amount"],
		"tax_3_amount":doc["tax_3_amount"],
		"total_amount": doc["total_amount"],
		"total_paid": doc["total_paid"],
		"changed_amount": doc["changed_amount"],
		"balance": doc["balance"],
	}


@frappe.whitelist()
# @frappe.whitelist(allow_guest= True)
def get_therapist_data(duration=None): 
	therapist_sql = """select `name` as employee_id, employee_name from `tabEmployee` where show_in_pos_assign_employee = 1 and disabled = 0"""
	duration_sql = """select concat(duration_title, case when is_overtime = 1 then '(OT)' else '' end) as  duration_title,duration_value as duration, commission,commission_value,is_overtime,mapping_value from `tabPredefine SPA Duration Code` order by duration_value"""
	commission_sql = """select `name`, commission_title,commission_value from `tabPredefine SPA Commission Code` order by  commission_value"""

	therapist_data = frappe.db.sql(therapist_sql, as_dict=1)
	duration_data = frappe.db.sql(duration_sql, as_dict=1)
	commission_data = frappe.db.sql(commission_sql, as_dict=1)

	idx = 0
	for d in [ dur for dur in duration_data if dur["mapping_value"]== duration] :
		idx +=1
		if idx <= 1:
			commission = [com for com in commission_data if d["commission"] == com["name"] ]
			if len(commission) > 0:
				d["selected"] = 1
				commission[0]["selected"] = 1 
 
	return {
		"therapies":therapist_data,
		"durations":duration_data,
		"commissions":commission_data,
	}
