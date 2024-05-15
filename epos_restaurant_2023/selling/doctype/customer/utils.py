import frappe

def update_fetch_from_fields(self):
	data_for_updates = []
	condiction_keys = [
		{
      		"key":"guest",
   			"doctypes":["POS Reservation","Deposit Ledger","Tax Invoice","Additional Stay Guest","Room Occupy","Reservation Room Rate","Reservation Folio","Reservation Stay","Reservation","Folio Transaction","Reservation Folio","Desk Folio"]
      	}
	]
	

	if self.has_value_changed("customer_name_en"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_name='{}'".format(self.customer_name_en)})
		data_for_updates.append({"doctype":"Sale Payment","update_field":"customer_name='{}'".format(self.customer_name_en)})
		#Voucher
		data_for_updates.append({"doctype":"Voucher","update_field":"customer_name='{}'".format(self.customer_name_en)})
		#Voucher Payment
		data_for_updates.append({"doctype":"Voucher Payment","update_field":"customer_name='{}'".format(self.customer_name_en)})
	if self.has_value_changed("phone_number"):	
		#Voucher
		data_for_updates.append({"doctype":"Voucher","update_field":"phone='{}'".format(self.phone_number)})
		#Voucher Payment
		data_for_updates.append({"doctype":"Voucher Payment","update_field":"phone='{}'".format(self.phone_number)})
	if self.has_value_changed("photo"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_photo='{}'".format(self.photo)})
	if self.has_value_changed("customer_group"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_group='{}'".format(self.customer_group)})
		data_for_updates.append({"doctype":"Sale Payment","update_field":"customer_group='{}'".format(self.customer_group)})		

	if self.has_value_changed("customer_name_en"):
		#Tax Invoice
		data_for_updates.append({"doctype":"Tax Invoice","update_field":"customer_name='{}'".format(self.customer_name_en)})
		#Additional Stay Guest
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Deposit Ledger
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Desk Folio
		data_for_updates.append({"doctype":"Desk Folio","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Folio Transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#POS Reservation
		data_for_updates.append({"doctype":"POS Reservation","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Reservation Folio
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Reservation Room Rate
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Room Occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"guest_name='{}'".format(self.customer_name_en)})
		
	if self.has_value_changed("phone_number"):
		data_for_updates.append({"doctype":"Tax Invoice","update_field":"phone_number='{}'".format(self.phone_number)})
		#Additional Stay Guest	
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"phone_number_1='{}'".format(self.phone_number)})
		#Deposit Ledger
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"phone_number='{}'".format(self.phone_number)})
		#Desk Folio
		data_for_updates.append({"doctype":"Desk Folio","update_field":"phone_number='{}'".format(self.phone_number)})
		#POS Reservation
		data_for_updates.append({"doctype":"POS Reservation","update_field":"phone_number='{}'".format(self.phone_number)})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"phone_number='{}'".format(self.phone_number)})
		#Reservation Folio
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"phone_number='{}'".format(self.phone_number)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_phone_number='{}'".format(self.phone_number)})
	if self.has_value_changed("phone_number_2"):
		#Additional Stay Guest
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"phone_number_2='{}'".format(self.phone_number_2)})	
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"phone_number_2='{}'".format(self.phone_number_2)})
	if self.has_value_changed("photo"): 
		#Additional Stay Guest
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"photo='{}'".format(self.photo)})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"guest_photo='{}'".format(self.photo)})
		#Reservation Folio
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"photo='{}'".format(self.photo)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_photo='{}'".format(self.photo)})
	if self.has_value_changed("email_address"): 
		#Additional Stay Guest
		data_for_updates.append({"doctype":"Additional Stay Guest","update_field":"email_address='{}'".format(self.email_address)})
		#Deposit Ledger
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"email='{}'".format(self.email_address)})	
		#Desk Folio
		data_for_updates.append({"doctype":"Desk Folio","update_field":"email='{}'".format(self.email_address)})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"email_address='{}'".format(self.email_address)})
		#Reservation Folio
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"email='{}'".format(self.email_address)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_email='{}'".format(self.email_address)})
	if self.has_value_changed("customer_group"): 
		#Folio Transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"guest_type='{}'".format(self.customer_group)})
		#Reservation
		data_for_updates.append({"doctype":"Reservation","update_field":"guest_type='{}'".format(self.customer_group)})
		#Reservation Room Rate
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_type='{}'".format(self.customer_group)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"guest_type='{}'".format(self.customer_group)})
		#Room Occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"guest_type='{}'".format(self.customer_group)})
	if self.has_value_changed("country"): 
		#Folio Transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"nationality='{}'".format(self.country)})
		#Reservation Stay
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"nationality='{}'".format(self.country)})
		#Room Occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"nationality='{}'".format(self.country)})
		
  
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

			frappe.db.sql(sql)