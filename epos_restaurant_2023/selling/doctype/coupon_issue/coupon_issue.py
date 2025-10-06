# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CouponIssue(Document):
	def validate(self):
		if self.expired_date<self.posting_date:
			frappe.throw(_("Expired date must be greater than posting date"))
		
		


		self.validate_coupon_code()



	def before_submit(self):
		if not self.debit_account:
			frappe.throw(_("Please select debit account code"))
		
		if not self.credit_account:
			frappe.throw(_("Please select credit account code"))

		if self.coupon_amount <=0:
			frappe.throw(_("Please enter coupon amount"))


		if self.customer:
			# check if employee current active use coupon
			sql = "select name from `tabCoupon Codes` where customer=%(customer)s  and coupon_status = 'Used'"
			if frappe.db.sql(sql,{"customer":self.customer, "coupon_number":self.coupon_number}):
				frappe.throw(_("This employee is already have active use coupon"))


		if not self.customer and self.employee:
			self.create_customer()

		
		if self.coupon_type=="Digital Coupon":
			self.create_coupon_code()



	def on_submit(self):
		
		if self.coupon_type=="Coupon Card":
			frappe.db.set_value("Coupon Codes",self.coupon,{
				"coupon_status":"Used",
				"price":self.coupon_amount,
				"coupon_value":self.coupon_amount,
				"balance_amount":self.coupon_amount,
				"balance_coupon_value":self.coupon_amount,
				"sale_date":self.posting_date,
				"customer":self.customer,
				"customer_name":self.employee_name,
				"expired_date":str(self.posting_date) + " 23:59:59",
				"note":"បញ្ជេញគូប៉ុងអោយផ្នែកគ្រប់គ្រង " + self.employee_name 
				})

		self.add_coupon_transaction()
		
		

		self.add_gl_entry()
		
	def before_cancel(self):
		if frappe.db.exists("Coupon Transaction",{"coupon_code":self.coupon,"transaction_type":"Used"}):
			frappe.throw(_("You cannot cancel this coupon issue. This coupon number have been used in coupon transaction"))


	def on_cancel(self):
		# validate coupon use transaction if have use not allow to delete
		# frappe.throw(str(frappe.as_json(self)))
		frappe.db.sql("delete from `tabCoupon Transaction` where coupon_code = %(coupon_code)s and reference_doctype = 'Coupon Issue' and reference_name = %(name)s",{"name":self.name,"coupon_code":self.coupon})


		# now I (Pheakdey) delete gl record when delete if have proble later will use reverse posting transaction
		# why i use this for fast dev
		frappe.db.sql("delete from `tabGeneral Ledger` where voucher_type='Coupon Issue' and voucher_number=%(name)s",{"name":self.name})

		#update coupon code to Unused and price, coupon value, balance  =  0
		if self.coupon_type=="Coupon Card":
			frappe.db.set_value("Coupon Codes",self.coupon,{
				"coupon_status":"Unused",
				"price":0,
				"coupon_value":0,
				"balance_amount":0,
				"balance_coupon_value":0,
				"sale_date":None,
				"customer":"",
				"customer_name":"",
				"expired_date":None,
				"note":""
				})
		else:
			# we check coupon transaction type = Digital Coupon if user cancel issue we delete record from tab Coupon Code
			frappe.db.sql("delete from `tabCoupon Codes` where name = %(name)s",{"name":self.coupon})
		

 
		self.coupon = ""
		
	def validate_coupon_code(self):
		
		# check if this coupon code is still not use
		if self.coupon_type == "Coupon Card":
			self.coupon_number = frappe.get_cached_value("Coupon Codes",self.coupon,"coupon")
			sql = "select name from `tabCoupon Codes` where name=%(coupon_code)s and coupon_status<> 'Unused'"
			if frappe.db.sql(sql,{"coupon_code":self.coupon}):
				frappe.throw(_("This coupon code is already used"))

		else:
			# validate on digital coupon
			if self.coupon:
				if frappe.db.get_value("Coupon Codes",self.coupon,"reference_doctype")!="Coupon Issue":
					frappe.throw("dopme")
					self.coupon = ""
			# check coupon existing 
			sql = "select name from `tabCoupon Codes` where coupon=%(coupon_number)s and coupon_status in ('Used','Unused') limit 1"
			if frappe.db.sql(sql,{"coupon_number":self.coupon_number}):
				frappe.throw(_("This coupon number is already in used."))

			 

	def create_coupon_code(self):
		site_config = frappe.get_site_config()
		from epos_restaurant_2023.utils import encrypt_aes_base64
		doc = frappe.get_doc({
			"doctype":"Coupon Codes",
			"reference_doctype":"Coupon Issue",
			"reference_name":self.name,
			"coupon":self.coupon_number,
			"coupon_url":site_config.get("coupon_code_url") + encrypt_aes_base64(self.coupon_number),
			"coupon_status":"Used",
			"created_by":frappe.get_cached_value("User",frappe.session.user,"full_name"),
			"price":self.coupon_amount,
			"coupon_value":self.coupon_amount,
			"customer":self.customer,
			"customer_name":self.employee_name,
			"expired_date": str(self.expired_date) + " 23:59:59",
			"balance_amount":self.coupon_amount,
			"balance_coupon_value":self.coupon_amount,
			"note":"បញ្ជេញគូប៉ុងអោយមេផ្នែកគ្រប់គ្រង " + self.employee_name ,
			"sale_date":self.posting_date
 
		}).insert(ignore_permissions=True)
		self.coupon = doc.name

	def create_customer(self):
		if not self.customer:
			if not frappe.db.exists("Customer Group","Management"):
				self.create_customer_group()

			doc = frappe.get_doc(
			{	
				"customer_code":self.employee,
				"customer_name_en": self.employee_name,
				"doctype": "Customer",
				"customer_group":"Management",
				"phone_number":frappe.get_cached_value("Employee",self.employee,"phone_number_1"),
				"gender": frappe.get_cached_value("Employee",self.employee,"gender")
			}
			)
			doc.insert(ignore_permissions=True)
			self.customer = doc.name
			frappe.db.set_value("Employee",self.employee,"customer",doc.name)
	
	def create_customer_group(self):
		frappe.get_doc(
			{	
				"customer_group_en":"Management",
				"doctype": "Customer Group",
			}
		).insert(ignore_permissions=True)

	def add_coupon_transaction(self):
		doc =frappe.get_doc( {
			"doctype":"Coupon Transaction",
			"business_branch":self.business_branch,
			"posting_date":self.posting_date,
			"expired_date":str( self.expired_date) + " 23:59:58" , # will add with houre
			"transaction_type":"Coupon Issue",
			"coupon_code":self.coupon,
			"coupon_number":self.coupon_number,
			"transaction_date":self.creation,
			"customer":self.customer,
			"customer_name":self.employee_name,
			"customer_photo":self.photo,
			"input_actual_amount":self.coupon_amount,
			"actual_amount":self.coupon_amount,
			"input_coupon_amount":self.coupon_amount,
			"coupon_amount":self.coupon_amount,
			"exchange_rate":1,
			"reference_doctype":"Coupon Issue",
			"reference_name":self.name
		})
		doc.insert(ignore_permissions=True)

	def add_gl_entry(self):
		from epos_restaurant_2023.api.account import submit_general_ledger_entry
		docs = []
		# debit account is expense account
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.debit_account,
			"debit_amount":self.coupon_amount,
			"voucher_type":"Coupon Issue",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark": "បញ្ជេញគូប៉ុងអោយផ្នែកគ្រប់គ្រង " + self.employee_name + "។ លេខគូប៉ុង " + self.coupon_number,
			"is_cancelled":0,
			"party_type":"Employee",
			"party": self.employee,
			"party_name": self.employee_name

		}
		docs.append(doc)

		# credit account to payable
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":self.credit_account,
			"credit_amount":self.coupon_amount,
			"voucher_type":"Coupon Issue",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark": "បញ្ជេញគូប៉ុងអោយផ្នែកគ្រប់គ្រង " + self.employee_name + "។ លេខគូប៉ុង " + self.coupon_number,
			"is_cancelled":0,
			"party_type":"Employee",
			"party": self.employee,
			"party_name": self.employee_name

		}
		docs.append(doc)
		submit_general_ledger_entry(docs,commit=False)
		


	