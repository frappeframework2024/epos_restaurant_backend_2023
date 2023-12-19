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
			if self.reservation_status and self.reservation_status != "Reserved":
				self.reservation_status = "Reserved" 
		
		self.status = self.reservation_status
	

 
			
		
