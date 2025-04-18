# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import base64
from py_linq import Enumerable

from frappe.model.document import Document


class PurchaseRequest(Document):
	
	def validate(self):
		self.total_quantity = Enumerable(self.purchase_request_products).sum(lambda x: x.quantity or 0)
		self.total_amount = Enumerable(self.purchase_request_products).sum(lambda x: x.amount or 0)
		self.url_generate = get_confirm_url(self)

 
	def on_submit(self):
		self.url_generate = get_confirm_url(self)

	def on_update_after_submit(self):		
		
		if self.workflow_state == "Convert as PO":			
			doc = frappe.new_doc("Purchase Order")
			doc.posting_date = frappe.utils.nowdate() 
			doc.business_branch = self.business_branch
			doc.vendor = self.vendor
			doc.stock_location = self.stock_location
			doc.purchase_request = self.name
			for i in self.purchase_request_products: 
				doc.append("purchase_order_products", {
					"product_code": i.product_code, 
					"quantity": i.quantity,
					"cost": i.price,
					"unit":i.unit,
					"base_unit":i.base_unit,

				})
			doc.insert()
			frappe.db.sql("update `tabPurchase Request`  set purchase_order =%(purchase_order)s,url_generate = %(url_generate)s  where name =%(name)s", 
				 {
					 "name":self.name,
					"purchase_order":doc.name,
					"url_generate": get_confirm_url(self)
				})
		else: 
			frappe.db.sql("update `tabPurchase Request`  set url_generate = %(url_generate)s  where name =%(name)s", 
				{
					"name":self.name,
					"url_generate": get_confirm_url(self)
			})
 
		 


@frappe.whitelist(allow_guest=True)
def get_confirm_url(self):
	str_params = "doctype=Purchase Request&name={}&format=Purchase Request Invoice&workflow_state={}".format(self.name, self.workflow_state)
	str_params = base64.b64encode(str_params.encode()).decode('utf-8')
	str_params = base64.b64encode(str_params.encode()).decode('utf-8')
	return  "data=key{}estc&preview=1".format(str_params)
