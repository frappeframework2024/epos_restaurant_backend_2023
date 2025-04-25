# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from datetime import datetime

from frappe.model.document import Document


class SPASaleInvoice(Document):
	def validate(self): 

		if len ([ d for d in  self.items if d.quantity ==0]) > 0:
				frappe.throw(_("The quantity of item not allow value zero"))

		update_sale_product_data(self=self)
		self.item_discount = sum(  sp.discount_amount for sp in self.items if sp.discount_amount != 0)
		self.total_quantity = sum(sp.quantity for sp in self.items)
		self.sub_total = sum(sp.price * sp.quantity for sp in self.items)

		discountable_amount = sum(sp.price * sp.quantity for sp in self.items if sp.discount_amount == 0)
		self.discount_amount =  self.discount or 0 if self.discount_type == "Amount"  else discountable_amount * ((self.discount or 0)/100)
		self.total_discount = self.item_discount + self.discount_amount

		validate_tax(doc=self)		

		if self.is_new():
			

			pass


def update_sale_product_data(self):
	for sp in self.items:
		sp.discount_amount = sp.discount_amount or 0
		sp.discount_amount  =  (sp.discount or 0 if sp.discount_type == "Amount" else (sp.quantity * sp.price) * (sp.discount / 100) )
		sp.amount = (sp.quantity * sp.price) -  sp.discount_amount


def validate_tax(doc):
		if  doc.tax_rule:
			doc.tax_rule_data =[]
			if frappe.db.exists("Tax Rule", doc.tax_rule):
				_tax_rule = frappe.get_doc("Tax Rule", doc.tax_rule)
				doc.tax_rule_data = _tax_rule.tax_rule_data


				#
				amount = sum(sp.price * sp.quantity for sp in doc.items if sp.allow_tax == 1)				

				#tax 1
				doc.tax_1_taxable_amount = amount 
				## cal tax 1 after discount validate
				tax_val  = json.loads(doc.tax_rule_data)  
				if tax_val["calculate_tax_1_after_discount"] == 1:
					doc.tax_1_taxable_amount = amount - doc.total_discount




				
		else:
			pass
		return
		
		if doc.tax_rule:
			amount = doc.price * doc.quantity
			# if (doc.rate_include_tax == 1) :
			# 	priceBefore = get_ratebefore_tax(doc.sub_total - doc.total_discount,doc.tax_rule, doc.tax_1_rate, doc.tax_2_rate, doc.tax_3_rate)
			# 	amount =  priceBefore + doc.total_discount  	
			#Tax 1
			doc.taxable_amount_1 = amount
			#cal tax1 taxable after disc.
			if doc.calculate_tax_1_after_discount == 1:
				doc.taxable_amount_1 =   amount - doc.total_discount			 
				
			doc.taxable_amount_1 *= (doc.percentage_of_price_to_calculate_tax_1/100)
			doc.tax_1_amount =  (doc.taxable_amount_1 or 0) * ((doc.tax_1_rate or 0)/100)

			#Tax 2
			doc.taxable_amount_2 = amount
			#cal tax2 taxable after disc.
			if doc.calculate_tax_2_after_discount==1:
				doc.taxable_amount_2 = amount  - doc.total_discount

			#cal tax2 taxable after add tax1
			if doc.calculate_tax_2_after_adding_tax_1==1:
				doc.taxable_amount_2 +=  doc.tax_1_amount

			doc.taxable_amount_2 *= (doc.percentage_of_price_to_calculate_tax_2/100)
			doc.tax_2_amount =  (doc.taxable_amount_2 or 0) *  ((doc.tax_2_rate or 0) /100)

			#tax 3
			doc.taxable_amount_3 =  amount
			#cal tax3 taxable after disc.
			if doc.calculate_tax_3_after_discount==1:
				doc.taxable_amount_3 = amount - doc.total_discount 
			
			#cal tax3 taxable after add tax1
			if doc.calculate_tax_3_after_adding_tax_1==1:
				doc.taxable_amount_3 =   doc.taxable_amount_3 +  doc.tax_1_amount 
			
			#cal tax3 taxable after add tax2
			if doc.calculate_tax_3_after_adding_tax_2==1:
				doc.taxable_amount_3 = doc.taxable_amount_3 +  doc.tax_2_amount 
			
			doc.taxable_amount_3 *= (doc.percentage_of_price_to_calculate_tax_3/100)
			doc.tax_3_amount =  (doc.taxable_amount_3 or 0) *  ((doc.tax_3_rate or 0) /100)
			
			#total tax
			doc.total_tax = doc.tax_1_amount + doc.tax_2_amount + doc.tax_3_amount
		else:
			doc.taxable_amount_1 =0
			doc.tax_1_amount=0
			doc.taxable_amount_2 =0
			doc.tax_2_amount=0
			doc.taxable_amount_3 =0
			doc.tax_3_amount=0
			doc.total_tax =0
