import frappe

def update_fetch_from_fields(self):
	data_for_updates = []

	if self.has_value_changed("customer_name_en"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_name='{}'".format(self.customer_name_en)})
		data_for_updates.append({"doctype":"Sale Payment","update_field":"customer_name='{}'".format(self.customer_name_en)})
	if self.has_value_changed("photo"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_photo='{}'".format(self.photo)})
	if self.has_value_changed("customer_group"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_group='{}'".format(self.customer_group)})
		data_for_updates.append({"doctype":"Sale Payment","update_field":"customer_group='{}'".format(self.customer_group)})		
	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			sql="update `tab{}` set {} where customer='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				self.name
			)
			
			frappe.db.sql(sql)
	data_for_updates_guest = []
	if self.has_value_changed("customer_name_en"):
		#Tax Invoice
		data_for_updates_guest.append({"doctype":"Tax Invoice","update_field":"customer_name='{}'".format(self.customer_name_en)})
		#Additional Stay Guest
		data_for_updates_guest.append({"doctype":"Additional Stay Guest","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Deposit Ledger
		data_for_updates_guest.append({"doctype":"Deposit Ledger","update_field":"guest_name='{}'".format(self.customer_name_en)})
		#Desk Folio
		data_for_updates_guest.append({"doctype":"Desk Folio","update_field":"guest_name='{}'".format(self.customer_name_en)})
	if self.has_value_changed("phone_number"):
		data_for_updates_guest.append({"doctype":"Tax Invoice","update_field":"phone_number='{}'".format(self.phone_number)})
		#Additional Stay Guest	
		data_for_updates_guest.append({"doctype":"Additional Stay Guest","update_field":"phone_number_1='{}'".format(self.phone_number)})
		#Deposit Ledger
		data_for_updates_guest.append({"doctype":"Deposit Ledger","update_field":"phone_number='{}'".format(self.phone_number)})
		#Desk Folio
		data_for_updates_guest.append({"doctype":"Desk Folio","update_field":"phone_number='{}'".format(self.phone_number)})
	if self.has_value_changed("phone_number_2"):
		#Additional Stay Guest
		data_for_updates_guest.append({"doctype":"Additional Stay Guest","update_field":"phone_number_2='{}'".format(self.phone_number_2)})	
	if self.has_value_changed("photo"): 
		#Additional Stay Guest
		data_for_updates_guest.append({"doctype":"Additional Stay Guest","update_field":"photo='{}'".format(self.photo)})
	if self.has_value_changed("email_address"): 
		#Additional Stay Guest
		data_for_updates_guest.append({"doctype":"Additional Stay Guest","update_field":"email_address='{}'".format(self.email_address)})
		#Deposit Ledger
		data_for_updates_guest.append({"doctype":"Deposit Ledger","update_field":"email='{}'".format(self.email_address)})	
		#Desk Folio
		data_for_updates_guest.append({"doctype":"Desk Folio","update_field":"email='{}'".format(self.email_address)})
	if data_for_updates_guest:
		for d in set([x["doctype"] for x in data_for_updates_guest]):
			sql="update `tab{}` set {} where guest='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates_guest if x["doctype"]==d]),
				self.name
			)
			frappe.db.sql(sql)