# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from epos_restaurant_2023.selling.doctype.sale_payment.general_ledger_entry import submit_payment_to_general_ledger_entry_on_submit
from epos_restaurant_2023.api.account import cancel_general_ledger_entery
from epos_restaurant_2023.selling.doctype.sale.sale import update_customer_bill_balance, update_customer_point, update_customer_point_on_cancel_sale
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
		
		grand_total = frappe.db.get_value("Sale",self.sale,"grand_total")
		if (self.payment_amount or 0) == 0 and (grand_total or 0) > 0:
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
		update_customer_point(self.customer,self.payment_type_group,self.payment_amount,self.name,self.sale,self.customer_name)

		## update crypto
		update_customer_saving_crypto(self)
		update_voucher(self)
	
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
		update_customer_point_on_cancel_sale(self.sale,self.customer,self.customer_name)

		## cancel crypto
		update_customer_saving_crypto(self)
		 

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

def update_voucher(self):
	frappe.db.sql("update `tabIssue Gift Voucher` set used = 1 where name = '{0}'".format(self.issue_gift_voucher))
	frappe.db.commit()

def validate_account(self):
	business_branch = self.property  if self.is_reservation_deposit else self.business_branch
    # set default account
	if not self.is_new():
		sql = "select payment_type from `tabSale Payment` where name = %(name)s"
		sale_payment = frappe.db.sql(sql, {"name":self.name}, as_dict=1)
		if sale_payment[0].payment_type != self.payment_type:
			self.account_paid_to = None
	
	# account_paid_to
	if not self.account_paid_to:
		sql = "select account from `tabPayment Type Account` where business_branch=%(business_branch)s and parent=%(payment_type)s limit 1"
		data = frappe.db.sql(sql,{"business_branch":business_branch,"payment_type":self.payment_type},as_dict=1)
		if data:
			self.account_paid_to = data[0]["account"]

	# account_paid_from
	branch = frappe.db.get_value('Business Branch', business_branch,  ['default_cash_account', 'default_receivable_account'], as_dict=1)
	if not self.account_paid_to :
		self.account_paid_to = branch.default_cash_account
	if not self.account_paid_from:
		self.account_paid_from = branch.default_receivable_account

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
	if not self.flags.ignore_update_sale:
		if self.sale:
			data = frappe.db.sql("select  ifnull(sum(payment_amount),0)  as total_paid from `tabSale Payment` where docstatus=1 and sale='{}' and payment_amount>0".format(self.sale),as_dict=1)
			value = frappe.db.get_value('Sale', self.sale,  ["grand_total","total_cash_coupon_claim"], as_dict = 1)
			if data and value["grand_total"]:
				total_paid = (round(data[0].total_paid, int(currency_precision)) +  round((value["total_cash_coupon_claim"] or 0),int(currency_precision)))
				balance = round((value["grand_total"] or 0),int(currency_precision))  - total_paid
				status = ""
				if balance == 0:
					status = "Paid"
				elif balance >0 and total_paid>0:
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
	if self.sale:	
		if not self.add_from_sale:
			update_customer_bill_balance(self.customer)

def update_customer_saving_crypto(self):
	if self.payment_type_group == "Crypto":
		from frappe.utils.synchronization import filelock
		lock_name = f"customer_crypto_balance_{self.name}"
		with filelock(lock_name, timeout=30):
			sql = """ update `tabCustomer` c
						inner join (
							select 
								%(customer)s as customer,
						sum(sp.payment_amount) as total_claim_amount
					from `tabSale Payment` sp 
					where sp.payment_type_group = 'Crypto'
					and sp.docstatus = 1
					and sp.customer = %(customer)s
					) _c on c.name = _c.customer
					set c.total_crypto_claim = _c.total_claim_amount,
					c.total_crypto_balance = c.total_crypto_amount - (_c.total_claim_amount + c.total_crypto_balance_expired )
					where c.name = %(customer)s and c.is_system_customer = 0"""
			frappe.db.sql(sql,{"customer":self.customer})
			frappe.db.commit()
		