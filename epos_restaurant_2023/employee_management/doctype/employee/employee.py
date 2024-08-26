# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import base64
import frappe
from frappe.model.document import Document

class Employee(Document):
	def validate(self):
		if self.flags.ignore_validate == True:
			return
		if self.password:
			self.pos_pin_code = str( base64.b64encode(self.password.encode("utf-8")).decode("utf-8"))

	def on_update(self):
		if self.is_selling_agent == 1 and self.generate_customer == 0:
			customer = frappe.new_doc("Customer")
			customer.customer_group = "General"
			customer.customer_code = self.employee_code
			customer.customer_name_en = self.employee_name
			customer.customer_name_kh = self.employee_name
			customer.gender = self.gender
			customer.phone_number_1 = self.phone_number_1
			customer.phone_number_2 = self.phone_number_2
			customer.email_address = self.email_address
			customer.province = self.province
			customer.district = self.district
			customer.commune = self.commune
			customer.village = self.village
			customer.address = self.address
			customer.insert()
			self.generate_customer = 1
		elif self.is_selling_agent == 1 and self.generate_customer == 1:
			c = frappe.db.sql("select count(name) count from `tabCustomer` where name = '{0}'".format(self.employee_code),as_dict=1)
			if c:
				if c[0].count>0:
					customer = frappe.get_doc("Customer",self.employee_code)
					customer.customer_name_en = self.employee_name
					customer.customer_name_kh = self.employee_name
					customer.gender = self.gender
					customer.phone_number_1 = self.phone_number_1
					customer.phone_number_2 = self.phone_number_2
					customer.email_address = self.email_address
					customer.province = self.province
					customer.district = self.district
					customer.commune = self.commune
					customer.village = self.village
					customer.address = self.address
					customer.save()
				else:
					self.generate_customer = 0
					self.on_update()
		else:
			pass
		
		if self.flags.ignore_on_update == True:
			return 
		 
		if self.allow_login:
			if self.user_id:
				doc = frappe.get_doc("User", self.user_id)
				
				doc.enabled = 1
				doc.username = self.username
				doc.first_name = self.employee_name
				doc.role_profile_name = self.role_profile
				doc.module_profile = self.module_profile
				doc.user_image = self.photo
				
				if self.password:
					doc.new_password = self.password

				
				doc.save()
				
				if self.password:
					self.password = None
					self.save()
					# frappe.enqueue("epos_restaurant_2023.employee_management.doctype.employee.employee.set_password", queue='short', user_id=doc.name, password = self.password)

			else:
				
				doc = frappe.get_doc({
						"doctype":"User",
						"enabled": 1,
						"email": self.email_address  if self.email_address else "{}@mail.com".format(self.username),
						"first_name": self.employee_name,
						"username": self.username,
						"language": "en",
						"time_zone": "Asia/Phnom_Penh",
						"send_welcome_email": 0,
						"role_profile_name": self.role_profile,
						"module_profile": self.module_profile,
						"user_type": "System User",
						"new_password":self.password,
						"user_image" : self.photo
						
					}
				).insert()

				# if self.password:
				# 	frappe.enqueue("epos_restaurant_2023.employee_management.doctype.employee.employee.set_password", queue='short', user_id=doc.name, password = str(self.password))

				self.password = None
				self.user_id = doc.name
				self.save()


		else:
			if self.user_id:
				doc = frappe.get_doc("User", self.user_id)
				doc.enabled = 0
				doc.save()

	# def on_trash(self):
	# 	frappe.throw("delete me")

