# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import utils
from frappe import _
from datetime import datetime
from frappe.utils.data import strip
import copy

from epos_restaurant_2023.selling.doctype.customer.utils import update_fetch_from_fields
class Customer(Document):
	def validate(self):
		
		if self.flags.ignore_validate == True:
			return
		if self.date_of_birth:
			if datetime.strptime(str(self.date_of_birth), "%Y-%m-%d").date() >datetime.strptime(utils.today(), "%Y-%m-%d").date():
				frappe.throw(_("Date of birth cannot be greater than the current time"))

		if not self.customer_name_kh:
			self.customer_name_kh = self.customer_name_en

		if not self.qb_customer_name:
			self.qb_customer_id = None

		self.customer_code_name = "{} - {}".format(self.name,self.customer_name_en)

	def autoname(self):
		if self.flags.ignore_autoname == True:
			return
		
		from frappe.model.naming import set_name_by_naming_series, get_default_naming_series,make_autoname

		if strip(self.customer_code) =="":
			set_name_by_naming_series(self)
			self.customer_code = self.name	

		self.customer_code = strip(self.customer_code)
		self.name = self.customer_code


	def after_rename(self, old_name,new_name,merge):  
		if self.flags.ignore_after_rename == True:
			return
		frappe.db.set_value('Customer', new_name, {
			'customer_code_name': "{} - {}".format(new_name,self.customer_name_en),
			'customer_code': new_name		
		}) 
	def on_update(self):
		frappe.clear_document_cache("Customer", self.name)
		if 'edoor' in frappe.get_installed_apps():
			if self.creation !=self.modified:
				update_fetch_from_fields(self)



 
   
   
@frappe.whitelist()
def update_customer_infomation_to_transaction():
	frappe.enqueue(update_customer_infomation_to_transaction_eqnueue,queue="short")

def update_customer_infomation_to_transaction_eqnueue():
	frappe.db.sql("""UPDATE `tabSale` s
						INNER JOIN `tabCustomer` c ON s.customer = c.name
						SET s.customer_name = c.customer_name_en,
			   				s.phone_number = c.phone_number,
			   				s.customer_group = c.customer_group
			   """)

	frappe.db.sql("""UPDATE `tabSale Payment` sp
						INNER JOIN `tabCustomer` c ON sp.customer = c.name
						SET sp.customer_name = c.customer_name_en
			   """)
	frappe.db.commit()

@frappe.whitelist()
def get_customer_order_summary(customer):
	total_visit = 0
	total_order = 0
	total_annual_order = 0
	sql = "select count(name) as total_visit, sum(grand_total) as total_amount from `tabSale` where customer='{}' and docstatus=1".format(customer)
	data = frappe.db.sql(sql, as_dict=1)
	today = datetime.today()  
	year = today.strftime("%Y")
	
	
	if data:
		total_visit = data[0]["total_visit"]
		total_order = data[0]["total_amount"]

		
	sql = "select  sum(grand_total) as total_amount from `tabSale` where posting_date >= '{}-01-01' and customer='{}' and docstatus=1".format(year,customer)
	data = frappe.db.sql(sql, as_dict=1)
	if data:
		total_annual_order = data[0].total_amount
	voucher_balance = frappe.db.get_value("Customer",customer,'voucher_balance')
	return {
		"total_visit":int(total_visit or 0),
		"total_order":float( total_order or 0),
		"total_annual_order": float(total_annual_order  or 0),
		"voucher_balance": float( voucher_balance or 0)
	}

@frappe.whitelist()
def get_voucher_list_per_customer(customer):
	vouchers = frappe.db.get_list("Voucher",
		order_by='modified desc',
		fields=['name', 'credit_amount','actual_amount'],
		filters={
			'customer': customer,
			'docstatus':['!=','2']
		},
		page_length=5000)
	for v in vouchers:
		payments = frappe.db.get_list("Voucher Payment",
			fields=['name', 'payment_type','payment_amount'],
			filters={
				'customer': customer,
				'voucher': v.name,
				'docstatus':['!=','2']
			})
		v['payments'] = payments or []
	return vouchers

@frappe.whitelist()
def get_unpaid_bills(name,is_payment = 0,bulk_sale_payment=''):
	bill_numbers = []
	if is_payment == 0:
		bill_numbers = frappe.db.get_all("Sale",filters={
			"customer":name,
			"docstatus":1,
			"balance": ['>','0']
		},fields=['*'],page_length=20 if is_payment == 1 else 100)
	else:
		bill_numbers = frappe.db.get_all("Sale",filters={
			"customer":name,
			"balance": ['=','0']
		},fields=['*'],page_length=20 if is_payment == 1 else 100)

	bill_list = []
	response = {"sales":[]}
	if len(bill_numbers) > 0:
		for bill in bill_numbers:
			sale_products = frappe.db.sql("""
									select 
								 	product_code,
									product_name,
								 	product_name_kh,
									`portion`,
									is_free,
									modifiers,
									discount,
									discount_amount,
									discount_type,
									sum(quantity) as quantity,
								 	price,
									sum(amount) as amount  
								 from `tabSale Product` 
								 where parent='{}' 
								 group by 
								 	product_code,
									product_name,
								 	product_name_kh,
									`portion`,
								 	is_free,
								 	modifiers,
								 	discount,
									discount_amount,
									discount_type, 
								 price""".format(bill["name"]),as_dict=1)
			if is_payment==0:
				payment = frappe.db.sql("""
									select 
								 	input_amount,
								 	currency,
						   			payment_type,
								 currency_precision
								 from `tabPOS Sale Payment` 
								 where parent='{}' 
								""".format(bill["name"]),as_dict=1)
			else:
				payment = frappe.db.sql("""
										select 
										input_amount,
										currency,
										payment_type,
										currency_precision
										from `tabSale Payment` 
										where bulk_sale_payment_name='{}' 
									""".format(bulk_sale_payment),as_dict=1)

			bill['sale_products'] = sale_products
			bill['payment'] = payment
			bill_list.append(bill)

	total_bill = len(bill_list)
	total_amount = sum(b.grand_total for b in  bill_list) or 0
	total_paid = sum(b.total_paid for b in  bill_list) or 0
	balance = sum(b.balance for b in  bill_list) or 0

	response["sales"] = bill_list or []
	response["total_bill"] = total_bill or 0
	response["total_amount"] = total_amount or 0
	response["total_paid"] = total_paid or 0
	response["balance"] = balance or 0

	return response


@frappe.whitelist()
def get_unpaid_customer(condition=''):
	if condition != '':
		condition = 'where {}'.format(condition)
	data = frappe.db.sql("""
     select 
        customer,
        customer_name,
        sum(grand_total) as grand_total,
        sum(total_paid) as total_paid,
        sum(balance) as balance
    from `tabSale`
	{}
    group by  
        customer,
        customer_name
""".format(condition),as_dict=1)

	return data

@frappe.whitelist()
def get_recent_payment():
	sql = """select
			a.parent as name,
			s.customer,
			s.customer_name,
			sum(s.grand_total) grand_total,
			sum(s.total_paid) total_paid,
			sum(s.balance) balance
		from `tabBulk Sale` a
		inner join `tabSale` s on a.sale = s.name
		group by 
			s.customer,
			s.customer_name
		order by a.creation desc
		limit 20
	"""
	data = frappe.db.sql(sql,as_dict=1)
	return data


@frappe.whitelist()
def recent_bills_payment(name):
	bill_numbers = []
	bill_numbers = frappe.db.get_all("Bulk Sale",filters={
		"parent":name
	},fields=['sale','sale_payment'])
	
	bill_list = []
	response = {"sales":[]}
	if len(bill_numbers) > 0:
		for bill in bill_numbers:

			sale = frappe.db.get_value('Sale',bill.sale,['*'],as_dict=1)
			sale_products = frappe.db.sql("""
									select 
								 	product_code,
									product_name,
								 	product_name_kh,
									`portion`,
									is_free,
									modifiers,
									discount,
									discount_amount,
									discount_type,
									sum(quantity) as quantity,
								 	price,
									sum(amount) as amount  
								 from `tabSale Product` 
								 where parent='{}' 
								 group by 
								 	product_code,
									product_name,
								 	product_name_kh,
									`portion`,
								 	is_free,
								 	modifiers,
								 	discount,
									discount_amount,
									discount_type, 
								 price""".format(bill["sale"]),as_dict=1)
			payment = frappe.db.sql("""
										select 
						   				name,
										input_amount,
										currency,
										payment_type,
										currency_precision
										from `tabSale Payment` 
										where name='{}' 
									""".format(bill['sale_payment']),as_dict=1)

			sale['sale_products'] = sale_products
			sale['payment'] = payment
			bill_list.append(sale)
	total_bill = len(bill_list)
	total_amount = sum(b.grand_total for b in  bill_list) or 0
	total_paid = sum(b.total_paid for b in  bill_list) or 0
	balance = sum(b.balance for b in  bill_list) or 0

	response["sales"] = bill_list or []
	response["total_bill"] = total_bill or 0
	response["total_amount"] = total_amount or 0
	response["total_paid"] = total_paid or 0
	response["balance"] = balance or 0

	return response



@frappe.whitelist()
def get_pos_misc_sale(customer_name):
	sales = """
        SELECT 
            sp.product_name, 
            sp.quantity, 
            sp.price, 
            sp.discount_amount, 
            sp.amount, 
            s.name 
        FROM  `tabSale Product` sp
        INNER JOIN `tabSale` s  ON  s.name = sp.parent
        WHERE 
            s.customer = %(customer_name)s
		order by
			s.name
    """
	sale = frappe.db.sql(sales, {'customer_name':customer_name}, as_dict=1)

	used = []
	sale_names = [x["name"] for x in sale if x["name"] not in [u["name"] for u in used] and not used.append(x) ]
	data = []
	for s in sale_names:
		data.append({"name":s,"sale_products":[b for b in sale if b["name"]==s]})
	return 	data 

@frappe.whitelist()
def get_guest_folio_list(customer_name):
	data=[]
	if 'edoor' in frappe.get_installed_apps():
		sql = """ 
			select
				name,
				property,
				reservation, 
				reservation_stay,
				posting_date,
				business_source,
				room_types,
				room_types_alias,
				rooms,
				total_credit,
				total_debit,
				balance,
				status,
				note
			from `tabReservation Folio` 
			where guest=%(customer_name)s
		"""
		data = frappe.db.sql(sql, {'customer_name':customer_name}, as_dict=1)
	return data


@frappe.whitelist()
def get_guest_stay_history(customer_name):
	data=[]
	if 'edoor' in frappe.get_installed_apps():
		sql = """
			select
				name,
				reservation,
				reference_number,
				reservation_type,
				group_code,
				reservation_date,
				arrival_date,
				departure_date,
				room_nights,
				rooms,
				guest,
				guest_name,
				business_source,
				adr,
				total_amount,
				reservation_status,
				rooms_data
			from `tabReservation Stay` 
			where guest=%(customer_name)s
		"""
		data = frappe.db.sql(sql, {'customer_name':customer_name}, as_dict=1)
	return data

@frappe.whitelist()
def get_guest_note_detail(customer_name):
	data=[]
	if 'edoor' in frappe.get_installed_apps():
		sql = """
			select 
				name, 
				content, 
				creation, 
				modified_by,
				subject,
				reference_doctype,
				reference_name,
				comment_by,
				custom_audit_trail_type,
				custom_posting_date,
				modified
			from  
				`tabComment` 
			where 
				custom_guest = %(customer_name)s and comment_type = 'Comment'
		"""
		data = frappe.db.sql(sql, {'customer_name':customer_name}, as_dict=1)
	return data


@frappe.whitelist()
def  get_customer_search_link(txt):
	data = frappe.db.get_list('Customer',
		fields=['customer_name_en','name','gender','phone_number','phone_number_2'],
		or_filters={
			"customer_name_en":['like','%' + txt+'%'],
			"customer_name_kh":['like','%' + txt+'%'],
			"name":['like','%' + txt+'%']
		}
	)
	return data


@frappe.whitelist()
def get_customer_document(customer_name):
	data=[]
	if 'edoor' in frappe.get_installed_apps():
		sql = """
			select 
				f.name, 
				f.custom_title, 
				f.custom_description, 
				f.file_size, 
				f.file_url, 
				f.file_name, 
				f.attached_to_name, 
				f.attached_to_doctype, 
				f.owner, 
				f.creation, 
				f.modified, 
				f.modified_by,
				f.file_type,
				c.customer_name_en
			from 
				`tabFile` f
			inner join `tabCustomer` c on f.attached_to_name = c.name
			where 
				f.attached_to_doctype='Customer' and 
				f.attached_to_name=%(customer_name)s and 
				f.custom_show_in_edoor=1
		"""
		data = frappe.db.sql(sql, {'customer_name':customer_name}, as_dict=1)
	return data