# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import json

class POSReservation(Document):
	def validate(self): 
		#check if new
		if self.is_new():
			if self.reservation_status and self.reservation_status not in ["Pending","Reserved"]:
				self.reservation_status = "Reserved" 
		
		self.status = self.reservation_status
		self.total_guest = (self.adult or 0) +  (self.child or 0) + (self.elderly or 0)
		self.update_table_number()
		

	def before_cancel(self): 
		status = frappe.get_doc("POS Reservation Status",self.reservation_status)
		self.status = self.reservation_status
		self.reservation_status_color = status.color
		self.reservation_status_background_color = status.background_color
		self.total_deposit = 0
	

	def on_update_after_submit(self):
		self.update_table_number()
  
		if self.reservation_status == "Dine-in" or self.reservation_status == "Checked Out":
			status = frappe.get_doc("POS Reservation Status",self.reservation_status) 
			self.reservation_status_color = status.color
			self.reservation_status_background_color = status.background_color
			frappe.db.sql("update `tabPOS Reservation` set workflow_state='{1}' where name='{0}'".format(self.name, self.reservation_status))

	def on_cancel(self):
		payments = frappe.get_list("Sale Payment",fields=["name"], filters={"pos_reservation":self.name,"docstatus":1})
		for p in payments:
			sale_payment = frappe.get_doc("Sale Payment", p.name)
			sale_payment.cancel()
			sale_payment.delete()
   
	def update_table_number(self):
		pass
    	# doc = frappe.get_doc("POS Reservation", self.name)
		# xx = doc.meta.get_field("table_number")
		# frappe.throw(xx)
		# if self.table_id:
		# 	table_name = frappe.get_cached_value("Tables Number", self.table_id, "tbl_number")

		# 	self.table_number = table_name
		# 	frappe.msgprint(table_name)

			
		
