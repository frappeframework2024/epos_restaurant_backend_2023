# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from epos_restaurant_2023.selling.doctype.sale_payment.general_ledger_entry import submit_payment_to_general_ledger_entry_on_submit
from epos_restaurant_2023.api.account import cancel_general_ledger_entery
class SalePayment(Document):
	def validate(self):
		if self.flags.ignore_validate==True:
			return
		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			validate_account(self)
  
		#check if reservation deleted
		if self.pos_reservation:
			reservation = frappe.get_doc("POS Reservation", self.pos_reservation)			
			if reservation.reservation_status != "Confirmed" and not self.sale:
				frappe.throw("Payment not allow with this current reservation status. ({})".format(reservation.reservation_status))

			# frappe.throw("The pos reservation {} was void.".format(self.pos_reservation))
		else:
			if not self.sale:
				frappe.throw("Mandatory fields required in Sale Payment (Sale*)")

		# check if payment type is on-account
		if self.payment_type_group == "On Account":
			frappe.throw("Payment {} {}".format(self.payment_type,_("is not allow to process pay")))

		if (self.exchange_rate or 0) ==0 or self.currency == frappe.db.get_default("currency"):
			self.exchange_rate = 1
			self.change_exchange_rate = 1
		
		currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
		if self.transaction_type =="Changed":
			self.payment_amount = self.input_amount / self.change_exchange_rate 
		else:
			self.payment_amount = self.input_amount / self.exchange_rate 
		
		self.payment_amount = round(self.payment_amount,int(currency_precision))
		
   		
		if (self.payment_amount or 0) ==0:
			frappe.throw(_("Please enter payment amount"))
   
		if self.sale:
			#validate expense if is a submitted expense
			sale_status = frappe.db.get_value("Sale",self.sale,"docstatus")
			
			if not sale_status==1:
				frappe.throw(_("This sale is not submitted yet"))

			#check paid amount cannot over balance
			if self.check_valid_payment_amount:
				if self.payment_amount > self.balance:
					frappe.throw("Payment amount cannot greater than sale balance")

			
		

	def on_submit(self):
		# run enque
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			if not self.flags.ignore_post_general_ledger_entry:
				submit_payment_to_general_ledger_entry_on_submit(self)

		if self.flags.ignore_on_submit==True:
			return
       
		update_sale(self)
		if self.payment_type_group == "Voucher":
			self.update_customer_voucher_balance()
		self.update_customer_point()
	
	def on_cancel(self):
		
		# submit to general ledger entry
		# run this in enqueue
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			cancel_general_ledger_entery('Sale Payment',self.name)
		if self.flags.ignore_on_cancel==True:
			return
		update_sale(self)
		if self.payment_type_group == "Voucher":
			self.update_customer_voucher_balance()
		self.update_customer_point_on_cancel_sale()
		 

	def before_update_after_submit(self):
		if self.flags.ignore_before_update_after_submit==True:
			return
		if not self.sale:
			self.sale_date = None
			self.customer = None
			self.customer_name = None
			self.customer_group = None
			self.pos_profile = None
			self.outlet = None
			self.business_branch = None
			self.working_day = None
			self.cashier_shift = None
			self.sale_amount = 0
			self.total_paid = 0
			self.balance = 0

		update_sale(self)

		# Update Customer Point When Pay with Point
	def update_customer_point(self):
		if frappe.get_cached_value("Exely Itegration Setting",None,"enabled")==1:
			frappe.enqueue("epos_restaurant_2023.api.exely.submit_order_to_exely", queue='long', doc_name = self.name)
		# Update Customer Point
		point_setting = frappe.get_doc("Loyalty Point Settings")
		if point_setting.enabled==1:
			allow_earn_point = frappe.get_cached_value("Customer",self.customer,'allow_earn_point')
			
			if allow_earn_point==1:
				
				if self.payment_type_group != 'Point' and self.payment_type in (d.payment_type for d in point_setting.payment_type):
					total_point_get = (point_setting.to_point_earn * self.payment_amount)/point_setting.from_amount_earn
					frappe.db.sql("""Update `tabCustomer` set total_point_earn = total_point_earn + {0} where name = '{1}'""".format(total_point_get,self.customer))
					frappe.db.set_value('Sale Payment',self.name,{ 'allow_earn_point':1,'total_point_earn': total_point_get})
					frappe.db.sql("""UPDATE `tabSale` s
									JOIN (
										SELECT sale, SUM(total_point_earn) AS total_point_earn
										FROM `tabSale Payment`
										WHERE sale = '{0}' and docstatus = 1
										GROUP BY sale
									) payment ON s.name = payment.sale
									SET s.total_point_earn = payment.total_point_earn
									WHERE NAME = '{0}'
				   				""".format(self.sale))
					frappe.db.commit()
					
				# Customer Use Point
				if self.payment_type_group == "Point":
					customer_point = frappe.db.get_value("Customer",self.customer,['total_point_earn','allow_earn_point'],as_dict=1)
					total_point_redeem = (self.payment_amount * point_setting.to_point_sale) / point_setting.from_amount_sale
					if float(customer_point.total_point_earn) < float(total_point_redeem):
						frappe.throw(_("Point for {} not enough.".format(self.customer_name)))
						
					frappe.db.sql("Update `tabCustomer` set total_point_earn = total_point_earn - {} where name = '{}'".format(total_point_redeem,self.customer))
					frappe.db.commit()
	
	def update_customer_point_on_cancel_sale(self):
		frappe.db.sql("""
				UPDATE `tabSale` SET total_point_earn = 0
				WHERE NAME = '{0}'
			""".format(self.sale))
		frappe.db.sql("""
				UPDATE `tabCustomer` c
				JOIN (
					SELECT customer, SUM(total_point_earn) AS total_point_earn
					FROM `tabSale`
					WHERE customer = '{0}' and docstatus = 1
					GROUP BY customer
				) sale ON c.name = sale.customer
				SET c.total_point_earn = sale.total_point_earn
				WHERE NAME = '{0}'
			""".format(self.customer))
		frappe.db.commit()



		# Update Customer Voucher Balance
	def update_customer_voucher_balance(self):
		if self.sale_amount < self.payment_amount and self.payment_type_group == "Voucher" :
			frappe.throw("Payment amount must equal to grand total")
		# get Customer Total Voucher Payment
		voucher_payment_sql = """
				select coalesce(sum(payment_amount),0) payment_amount from `tabSale Payment`
				where customer = '{0}' and payment_type_group = 'Voucher' and docstatus = 1
			""".format(self.customer)
		voucher_credit_sql = """ 
							select 
								coalesce(sum(credit_amount),0) credit_amount
							from `tabVoucher`
							where customer = '{}' and docstatus = 1
							""".format(self.customer)
		total_credit_amount =  frappe.db.sql(voucher_credit_sql,as_dict=1)
		
		voucher_balance = frappe.db.get_value("Customer",self.customer,'voucher_balance')

		if (total_credit_amount[0].credit_amount <= 0 or voucher_balance < self.payment_amount) and self.docstatus == 1 :
			frappe.throw("Customer has no credit amount for {}".format(self.payment_type))
		total_voucher_payment = frappe.db.sql(voucher_payment_sql,as_dict=1)
		frappe.db.set_value('Customer', self.customer, {
			'voucher_balance': total_credit_amount[0].credit_amount - total_voucher_payment[0].payment_amount
		})


def validate_account(self):
    # set default account
		# account_paid_to
		if not self.account_paid_to:
			sql = "select account from `tabPayment Type Account` where business_branch=%(business_branch)s and parent=%()s limit 1"
			data = frappe.db.sql(sql,{"business_branch":self.business_branch},as_dict=1)
			frappe.throw(str(data))
			if data:
				self.account_paid_to = data[0]["account"]

		# account_paid_from
		if not self.account_paid_from:
			self.account_paid_from = frappe.db.get_value("Business Branch",self.business_branch,"default_receivable_account")
   
  
      


def update_sale(self):
	currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
	if currency_precision=='':
			currency_precision = "2"

	_deposit = 0
	#update reservation deposit		
	if self.pos_reservation:
		if self.is_reservation_deposit:
			_sql1 = """select 
				ifnull(sum(payment_amount),0)  as total_deposit 
			from `tabSale Payment` 
			where pos_reservation='{}' 
				and is_reservation_deposit=1 
				and docstatus=1 
				and payment_amount > 0""".format(self.pos_reservation)
			_data = frappe.db.sql(_sql1)
			if _data:
				_deposit = round(_data[0][0],int(currency_precision))
				frappe.db.set_value("POS Reservation",self.pos_reservation,{
					"total_deposit":_deposit
				})

	# update sale balance and paid
	if self.sale:
		data = frappe.db.sql("select  ifnull(sum(payment_amount),0)  as total_paid from `tabSale Payment` where docstatus=1 and sale='{}' and payment_amount>0".format(self.sale),as_dict=1)
		sale_amount = frappe.db.get_value('Sale', self.sale, 'grand_total')
		if data and sale_amount:
			balance =round(sale_amount,int(currency_precision))-round(data[0].total_paid, int(currency_precision))  
			status = ""
			if balance == 0:
				status = "Paid"
			elif balance >0 and data[0].total_paid>0:
				status = "Partially Paid"
			else:
				status = "Unpaid"
			if balance<0:
				balance = 0
			
			update_sale_status = "Update `tabSale` set total_paid = %(total_paid)s , balance = %(balance)s,status=%(status)s where name = %(sale)s"
			frappe.db.sql(update_sale_status,{
				'total_paid': round(data[0].total_paid,int(currency_precision)),
				'balance': balance,
				'status': status,
				'sale':self.sale
			})
			frappe.db.commit()
		# update customer balance
		
