import frappe

def update_fetch_from_fields(self):
	data_for_updates = []
	condiction_keys = [
		{
      		"key":"guest",
   			"doctypes":["POS Reservation","Deposit Ledger","Tax Invoice","Additional Stay Guest","Room Occupy","Reservation Room Rate","Reservation Folio","Reservation Stay","Reservation","Folio Transaction","Reservation Folio","Desk Folio","Revenue Forecast Breakdown","Reservation Stay Room"]
      	}
	]
 
	changed_data = {}
	
 

	if self.has_value_changed("photo"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_photo='{}'".format(self.photo)})
	if self.has_value_changed("customer_group"):
		changed_data["customer_group"] = self.customer_group
		data_for_updates.append({"doctype":"Sale","update_field":"customer_group=%(customer_group)s"})
		data_for_updates.append({"doctype":"Sale Payment","update_field":"customer_group=%(customer_group)s"})		

	if self.has_value_changed("customer_name_en"):
		changed_data["customer_name_en"] = self.customer_name_en

		data_for_updates.append({"doctype":"Sale","update_field":"customer_name=%(customer_name_en)s"})
		data_for_updates.append({"doctype":"Sale Payment","update_field":"customer_name=%(customer_name_en)s"})
		#Voucher
		data_for_updates.append({"doctype":"Voucher","update_field":"customer_name=%(customer_name_en)s"})
		#Voucher Payment
		data_for_updates.append({"doctype":"Voucher Payment","update_field":"customer_name=%(customer_name_en)s"})		
		#POS Reservation
		data_for_updates.append({"doctype":"POS Reservation","update_field":"guest_name=%(customer_name_en)s"})	
		#Tax Invoice
		data_for_updates.append({"doctype":"Tax Invoice","update_field":"customer_name=%(customer_name_en)s"})


		if 'edoor' in frappe.get_installed_apps():
			#Additional Stay Guest
			data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"guest_name=%(customer_name_en)s"})
			#Deposit Ledger
			data_for_updates.append({"doctype":"Deposit Ledger","update_field":"guest_name=%(customer_name_en)s"})
			#Desk Folio
			data_for_updates.append({"doctype":"Desk Folio","update_field":"guest_name=%(customer_name_en)s"})
			#Folio Transaction
			data_for_updates.append({"doctype":"Folio Transaction","update_field":"guest_name=%(customer_name_en)s"})
			#Reservation
			data_for_updates.append({"doctype":"Reservation","update_field":"guest_name=%(customer_name_en)s"})
			#Reservation Folio
			data_for_updates.append({"doctype":"Reservation Folio","update_field":"guest_name=%(customer_name_en)s"})
			#Reservation Room Rate
			data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_name=%(customer_name_en)s"})
			#Reservation Stay
			data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_name=%(customer_name_en)s"})
			#Room Occupy
			data_for_updates.append({"doctype":"Room Occupy","update_field":"guest_name=%(customer_name_en)s"})
			# reservaiton stay room
			data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"guest_name=%(customer_name_en)s"})
			

		
	if self.has_value_changed("phone_number"):
		changed_data["phone_number"] = self.phone_number
		#Voucher
  
		data_for_updates.append({"doctype":"Voucher","update_field":"phone=%(phone_number)s"})
		#Voucher Payment
		data_for_updates.append({"doctype":"Voucher Payment","update_field":"phone=%(phone_number)s"})
	
		data_for_updates.append({"doctype":"Tax Invoice","update_field":"phone_number=%(phone_number)s"})
		#POS Reservation
		data_for_updates.append({"doctype":"POS Reservation","update_field":"phone_number=%(phone_number)s"})
		
		if 'edoor' in frappe.get_installed_apps():
			#Additional Stay Guest	
			data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"phone_number_1=%(phone_number)s"})
			#Deposit Ledger
			data_for_updates.append({"doctype":"Deposit Ledger","update_field":"phone_number=%(phone_number)s"})
			#Desk Folio
			data_for_updates.append({"doctype":"Desk Folio","update_field":"phone_number=%(phone_number)s"})
			#Reservation
			data_for_updates.append({"doctype":"Reservation","update_field":"phone_number=%(phone_number)s"})
			#Reservation Folio
			data_for_updates.append({"doctype":"Reservation Folio","update_field":"phone_number=%(phone_number)s"})
			#Reservation Stay
			data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_phone_number=%(phone_number)s"})

	if self.has_value_changed("phone_number_2") and ('edoor' in frappe.get_installed_apps()):
		changed_data["phone_number_2"] = self.phone_number_2
		#Additional Stay Guest
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"phone_number_2=%(phone_number_2)s"})	
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"phone_number_2=%(phone_number_2)s"})	

	if self.has_value_changed("photo") and ('edoor' in frappe.get_installed_apps()): 
		#Additional Stay Guest
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"photo='{}'".format(self.photo)})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"guest_photo='{}'".format(self.photo)})
		#Reservation Folio
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"photo='{}'".format(self.photo)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_photo='{}'".format(self.photo)})

	if self.has_value_changed("email_address") and ('edoor' in frappe.get_installed_apps()): 
		changed_data["email_address"] = self.email_address
		#Additional Stay Guest
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"email_address=%(email_address)s"})
		#Deposit Ledger
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"email=%(email_address)s"})	
		#Desk Folio
		data_for_updates.append({"doctype":"Desk Folio","update_field":"email=%(email_address)s"})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"email_address=%(email_address)s"})
		#Reservation Folio
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"email=%(email_address)s"})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_email=%(email_address)s"})

	if self.has_value_changed("customer_group") and ('edoor' in frappe.get_installed_apps()): 
		changed_data["customer_group"] = self.customer_group
		#Folio Transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"guest_type=%(customer_group)s"})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"guest_type=%(customer_group)s"})
		#Reservation Room Rate
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_type=%(customer_group)s"})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_type=%(customer_group)s"})
		#Room Occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"guest_type=%(customer_group)s"})
		#Revenue Forecast Breakdown
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"guest_type=%(customer_group)s"})
	if self.has_value_changed("country") and ('edoor' in frappe.get_installed_apps()): 
		#Folio Transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"nationality='{}'".format(self.country)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"nationality='{}'".format(self.country)})
		#Room Occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"nationality='{}'".format(self.country)})
		#Revenue Forecast Breakdown
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"nationality='{}'".format(self.country)})
		
  
	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			key = [f["key"] for f in condiction_keys if d in f["doctypes"]]
			
			key = "customer" if not key else key[0]

			sql="update `tab{}` set {} where {}='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				key,
				self.name
			)
			 
			frappe.db.sql(sql,changed_data)