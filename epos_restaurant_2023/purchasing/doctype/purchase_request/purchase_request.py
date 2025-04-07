# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from py_linq import Enumerable

from frappe.model.document import Document


class PurchaseRequest(Document):
	
	def validate(self):
		self.total_quantity = Enumerable(self.purchase_request_products).sum(lambda x: x.quantity or 0)
		self.total_amount = Enumerable(self.purchase_request_products).sum(lambda x: x.amount or 0)

 
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
			frappe.db.sql("update `tabPurchase Request`  set purchase_order =%(purchase_order)s where name =%(name)s", {"name":self.name,"purchase_order":doc.name})
			
			