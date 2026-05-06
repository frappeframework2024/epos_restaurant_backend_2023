# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import json
from  epos_restaurant_2023.api.cache_function import get_default_account_from_pos_config, get_default_account_from_revenue_group, get_doctype_value_cache
from epos_restaurant_2023.api.account import cancel_general_ledger_entery,submit_general_ledger_entry
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_stock_location_by_pos_profile,check_uom_conversion, get_product_cost, get_stock_location_product, get_uom_conversion, update_product_quantity
import frappe
from frappe import utils
from frappe import _
from frappe.utils.data import getdate,fmt_money
from py_linq import Enumerable
from frappe.model.document import Document
import datetime
from copy import deepcopy
from decimal import Decimal
from frappe.utils import add_to_date
from epos_restaurant_2023.api.exely import cancel_order,submit_order_to_exely
from epos_restaurant_2023.selling.doctype.sale.general_ledger_entry import submit_sale_to_general_ledger_entry
 
class Sale(Document):
	def validate(self): 	
		lock_db(self=self)
		# frappe.throw(str(self.working_day))	
		if not frappe.db.get_default('exchange_rate_main_currency'):
			frappe.throw('Main Exchange Currency not yet config. Please contact to system administrator for solve')

		if self.pos_profile:
			if not self.working_day:
				data = (frappe.db.sql("select name from `tabWorking Day` where business_branch=%(business_branch)s and is_closed = 0 order by posting_date limit 1",{"business_branch":self.business_branch},as_dict=1) or [])
				if len(data)>0:
					self.working_day = data[0]["name"]
				else:
					frappe.throw(_("Please start working day first"))

			if not self.cashier_shift: 		
				data = (frappe.db.sql("select name from `tabCashier Shift` where business_branch=%(business_branch)s and pos_profile=%(pos_profile)s and is_closed = 0 order by posting_date limit 1",{"business_branch":self.business_branch,"pos_profile":self.pos_profile},as_dict=1) or [])
				if len(data)>0:
					self.cashier_shift= data[0]["name"]
				else:
					frappe.throw(_("Please start shift first"))
			else:
				if frappe.get_cached_value("Cashier Shift",self.cashier_shift,"is_closed") == 1:
					frappe.throw(_("Cashier shift has been closed or You're trying to close bill from a different POS Profile."))
		
		if self.working_day:
			if not self.cashier_shift: 
				frappe.throw(_("Sale cannot allow with cashier shift"))

			working_day = frappe.get_cached_doc("Working Day", self.working_day)
			self.posting_date = working_day.posting_date
		
		# printed_date
		if not self.printed_date:
			self.printed_date = datetime.datetime.now()

		# paid date
		if not self.paid_date:
			self.paid_date = datetime.datetime.now()

		# set waiting number
		if self.is_new():
			if self.waiting_number_prefix:
				from frappe.model.naming import make_autoname
				self.waiting_number = make_autoname(self.waiting_number_prefix)
 

		if self.discount_type =="Percent" and self.discount > 100:
			frappe.throw(_("discount percent cannot greater than 100 percent"))

			   
		if self.docstatus ==0:
			if self.working_day:
				is_closed = frappe.get_cached_value('Working Day', self.working_day,"is_closed")
				if is_closed==1:
					pass
					##frappe.throw(_("Working day was closed"))

			if self.cashier_shift:
				is_closed = frappe.get_cached_value('Cashier Shift', self.cashier_shift,"is_closed")
				if is_closed==1:
					pass
					##frappe.throw(_("Cashier shift was closed"))

		#validate outlet
		if self.outlet and self.business_branch:
			if frappe.get_value("Outlet",self.outlet,"business_branch") != self.business_branch:
				frappe.throw(_("The outlet {} is not belong to business branch {}".format(self.outlet, self.business_branch)))
		
		#validate stock location
		if self.stock_location and self.business_branch:
			if frappe.get_value("Stock Location",self.stock_location,"business_branch") != self.business_branch:
				frappe.throw(_("The stock location {} is not belong to business branch {}".format(self.stock_location, self.business_branch)))
		

		#validate exhcange rate change
		to_currency = frappe.db.get_default("second_currency")
		if( frappe.db.get_default("exchange_rate_main_currency") !=frappe.db.get_default("currency") ):
			to_currency = frappe.db.get_default("currency") 

		sql_exchange_rate = """select 
									exchange_rate,
									change_exchange_rate 
								from `tabCurrency Exchange` 
								where to_currency = '{}' and to_currency != from_currency
									and docstatus = 1 
								order by 
								posting_date desc, 
								modified desc limit 1""".format(to_currency)
		exch = frappe.db.sql(sql_exchange_rate,as_dict=1) 
		if exch:
			self.exchange_rate = exch[0].exchange_rate
			self.change_exchange_rate = exch[0].change_exchange_rate	

		else:
			self.exchange_rate = 1
			self.change_exchange_rate  = 1
		default_customer = frappe.get_cached_value("POS Profile",self.pos_profile,'default_customer')
		if len([d for d in self.sale_products if d.is_park == 1]) > 0 and self.customer == default_customer:
			frappe.throw("Please select a customer for park")

		#validate sale product 
		validate_sale_product(self)

		# validate sale cash coupon claim
		validate_cash_coupon_claim(self)
  
		validate_pos_payment(self,skip_check=1)
		#validate sale summary

		#set is foc by check payment pyment if have is_foc payment type
		self.is_foc = 0

		## check table if have make foc to sale when discount 100%
		if self.table_id:
			_table = frappe.get_cached_doc("Tables Number",self.table_id)
			if _table.is_foc and self.discount==100 and self.discount_type =="Percent":
				self.is_foc = 1


		currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
		if currency_precision=='':
			currency_precision = "2"
		
		if Enumerable(self.payment).where(lambda x: (x.is_foc or 0) ==1).count()>=1:
			self.is_foc = 1

		total_quantity = Enumerable(self.sale_products).where(lambda x:(x.is_timer_product or 0) == 0).sum(lambda x: x.quantity or 0)
		sub_total = Enumerable(self.sale_products).sum(lambda x: (x.quantity or 0)* (x.price or  0) + ((x.quantity or 0)*(x.modifiers_price or 0)) )
  
		sale_discountable_amount =Enumerable(self.sale_products).where(lambda x:x.allow_discount ==1 and (x.discount_amount or 0)==0).sum(lambda x: (x.quantity or 0)* (x.price or  0) + + ((x.quantity or 0)*(x.modifiers_price or 0)))

		self.total_quantity = total_quantity
		self.sale_discountable_amount = math_round(sale_discountable_amount  , int(currency_precision)) 
		
		# calculate sale discount
		if self.discount:
			if self.discount_type =="Percent":
				# self.sale_discount = self.sale_discountable_amount * self.discount / 100
				# self.sale_discount = round(self.sale_discount  , int(currency_precision)) 

				self.sale_discount = Enumerable(self.sale_products).sum(lambda x:  (x.sale_discount_amount or 0))
			else:
				self.sale_discount = self.discount or 0
				if self.discount > self.sale_discountable_amount:
					frappe.throw("Discount amount cannot greater than discountable amount")
		self.sale_discount = math_round(self.sale_discount, int(currency_precision))

		self.product_discount = Enumerable(self.sale_products).where(lambda x:x.allow_discount ==1).sum(lambda x: x.discount_amount)		
		self.product_discount=math_round(self.product_discount  , int(currency_precision)) 
		self.total_discount = (self.product_discount or 0) + (self.sale_discount or 0)  
		#tax 
		self.taxable_amount_1  = Enumerable(self.sale_products).where(lambda x:x.tax_rule).sum(lambda x: x.taxable_amount_1)
		self.taxable_amount_2  = Enumerable(self.sale_products).where(lambda x:x.tax_rule).sum(lambda x: x.taxable_amount_2)
		self.taxable_amount_3  = Enumerable(self.sale_products).where(lambda x:x.tax_rule).sum(lambda x: x.taxable_amount_3)
		self.tax_1_amount  = Enumerable(self.sale_products).where(lambda x:x.tax_rule).sum(lambda x: x.tax_1_amount)
		self.tax_2_amount  = Enumerable(self.sale_products).where(lambda x:x.tax_rule).sum(lambda x: x.tax_2_amount)
		self.tax_3_amount  = Enumerable(self.sale_products).where(lambda x:x.tax_rule).sum(lambda x: x.tax_3_amount)
		self.total_tax  = Enumerable(self.sale_products).where(lambda x:x.tax_rule).sum(lambda x: x.total_tax)
		total_rate_include_tax  = Enumerable(self.sale_products).where(lambda x:x.tax_rule and x.rate_include_tax == 1).sum(lambda x: x.total_tax)
		# total_rate_include_tax  = 0
		self.sub_total = sub_total	- total_rate_include_tax
		self.grand_total =( sub_total - (self.total_discount or 0))  + self.total_tax - total_rate_include_tax
		self.grand_total =math_round(self.grand_total, int(currency_precision))
	  
		self.total_paid =  Enumerable(self.payment).where(lambda x: x.payment_type_group !='On Account').sum(lambda x: x.amount or 0)
		self.total_paid = math_round ( ((self.total_paid or 0) + (self.deposit or 0)), int(currency_precision))

		self.total_fee =  Enumerable(self.payment).sum(lambda x: x.fee_amount or 0)
		self.total_paid_with_fee = math_round(( self.total_paid + (self.total_fee or 0)), int(currency_precision))

		if self.grand_total <0 and self.grand_total != self.total_paid:
			frappe.throw("Return payment amount must be the same as grand total")

		_balance = math_round(self.grand_total  , int(currency_precision)) -  math_round((self.total_paid or 0)  , int(currency_precision))

		_total_claim_coupon = 0
		if len(self.cash_coupon_items) and (self.total_cash_coupon_claim or 0) > 0:
			_total_claim_coupon = math_round((self.total_cash_coupon_claim or 0)  , int(currency_precision))
			if _total_claim_coupon > self.grand_total:
				frappe.throw("Your coupon claim and payment is over balance.")

			_balance -= _total_claim_coupon
		
		_balance = _balance - (self.total_trade_in_amount or 0)
  
		self.balance = _balance		

		if (self.sale_discount or 0) > 0:
			self.crypto_able_amount =  0	
		else:
			self.crypto_able_amount = Enumerable(self.sale_products).sum(lambda x: x.crypto_able_amount or 0)	

		# if self.pos_profile:
		self.changed_amount = (self.total_paid + _total_claim_coupon) - self.grand_total
		if math_round(self.changed_amount,int(currency_precision)) <= generate_decimal(int(currency_precision)):
			self.changed_amount = 0


		if self.balance<0:
			self.balance = 0
			

		if not self.created_by:
			self.created_by = frappe.get_user().doc.full_name

		if not self.closed_by and self.docstatus==1:
			self.closed_by = frappe.get_doc("User",self.modified_by).full_name
			self.closed_date = datetime.datetime.now()


		if self.sale_status:
			sale_status_doc = frappe.get_cached_doc("Sale Status", self.sale_status)
			self.sale_status_color = sale_status_doc.background_color
			self.sale_status_priority  = sale_status_doc.priority
		# commission
		
		if self.agent_name:
			if self.commission_type=="Percent":
				self.commission_amount = (self.grand_total * self.commission/100); 
			else:
				self.commission_amount = self.commission

		if self.docstatus ==1:
			self.sale_status = "Closed"
			self.sale_status_color = frappe.get_value("Sale Status","Closed","background_color")
		
		# update total coupon value to sale
		self.total_coupon_value = sum([(d.total_coupon_value or 0) for d in self.sale_products])
		# update default accunt
		update_default_account(self) 
		validate_pos_payment(self,skip_check=0)
		self.validate_coupon_codes()

	 

	@frappe.whitelist()
	def get_sale_payment_naming_series(self):
		return frappe.get_meta("Sale Payment").get_field("naming_series").options
	
	def on_update(self): 
		if self.flags.ignore_on_update == True:
			return 
		#add sale product spa commission
		update_status(self)
		add_sale_product_spa_commission(self)

		#delete product that parent_sale_product not exists 
		frappe.db.sql("delete from `tabSale Product` where parent='{0}' and ifnull(reference_sale_product,'')!='' and  ifnull(reference_sale_product,'') not in (select name from `tabSale Product` where parent='{0}')".format(self.name))
		
		## update cash coupon information
		on_update_coupon_information(self)
	
	def before_save(self):
		update_sale_sale_product_cost(self)
		on_generate_custom_bill_number(self)


	def after_insert(self):

		if self.flags.ignore_after_insert == True:
			return 
		#add sale product spa commission
		if not self.time_in:
			pass	
		add_sale_product_spa_commission(self)
 
	def before_cancel(self):
		self.docstatus = 2
		update_status(self)
		if frappe.get_cached_value("Exely Itegration Setting",None,"enabled")==1:
			if self.exely_transaction_id:
				cancel_order(transaction_id = self.exely_transaction_id, sale = self.name, comment = "ePOS Restaurant Cancel Order")

	def before_submit(self):
		lock_db(self=self)
		update_sale_sale_product_cost(self)
		if self.flags.ignore_before_submit == True:
			return 
		on_get_revenue_account_code(self)
		self.append_quantity = None
		self.scan_barcode = None


		## end generate custom bill format
		for d in self.sale_products:
			if d.is_inventory_product:
				if d.unit !=d.base_unit:
					if not check_uom_conversion(d.base_unit, d.unit):
						frappe.throw(_("There is no UoM conversion for product {}-{} from {} to {}".format(d.product_code, d.product_name, d.base_unit, d.unit)))
		# chekc if user pay to room we need to check if folio is still open
		if "edoor" in frappe.get_installed_apps():
			room_payment = [x for x in self.payment if x.payment_type == "Pay to Room"]
			if room_payment:
				room_payment = room_payment[0] 
				if frappe.db.get_value("Reservation Folio",room_payment.folio_number,"status") =="Closed":
					frappe.throw("This folio number {} in room {} is already closed".format(room_payment.folio_number,room_payment.room_number))

		
		# validate redeem amount  with sale type redeem
		# check redeem amount with coupon amount remaining

	
	
	def on_submit(self):
		lock_db(self=self)

		if self.flags.ignore_on_submit == True:
			return 

		if not self.time_out:
			pass

		if "edoor" in frappe.get_installed_apps():
			create_folio_transaction_from_pos_trnasfer(self) 
		

		# update_inventory_on_submit(self)			
		add_payment_to_sale_payment(self) 

		## update cash coupon information
		on_update_coupon_information(self)		

		update_status(self)

		## set pos reservation status to checked out
		update_pos_reservation_status(self)

		#update inventory
		is_update_inventory = False
		if self.pos_profile:
			enable_calculate_inventory_on_sale = frappe.get_cached_value("POS Profile",self.pos_profile,"enable_calculate_inventory_on_sale")
			if enable_calculate_inventory_on_sale:
				is_update_inventory = True
		else:
			is_update_inventory = True
		
		if is_update_inventory:
			update_inventory_on_submit(self)
		#end update inventory

		update_customer_bill_balance(self.customer)

		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.create_folio_transaction_from_pos_trnasfer", queue='short', self=self)
		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.update_inventory_on_submit", queue='short', self=self)
		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.add_payment_to_sale_payment", queue='short', self=self)
		
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			add_coupon_GL_entry(self)
			submit_sale_to_general_ledger_entry(self)
			commission_general_ledger_entry(self)

		if frappe.get_cached_value("Exely Itegration Setting",None,"enabled")==1:
			if len( self.payment) > 0:
				payments = [ d for d in self.payment if d.is_pay_to_room == 1]
				if len(payments) >0:
					submit_order_to_exely(self.name)
				else:
					frappe.enqueue("epos_restaurant_2023.api.exely.submit_order_to_exely", queue='long', doc_name = self.name)
		update_sales_order_and_delivery_note_status(self)

		if self.sale_type in ["Sale Coupon","Top Up","Redeem"]: 
			update_coupon_transaction(self)



		# Release Lock
		unlock_db(self)
		

	def on_cancel(self):
		if self.flags.ignore_on_cancel == True:
			return 

		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			cancel_general_ledger_entery("Sale", self.name)	
			commission_general_ledger_entry(self)
		

		## update cash coupon information
		on_update_coupon_information(self)

		on_sale_delete_update(self)
		sql_delete_bulk = """ delete from `tabBulk Sale` where sale = '{}' """.format(self.name)
		# frappe.throw(sql_delete_bulk)
		frappe.db.sql(sql_delete_bulk)		

		update_customer_bill_balance(self.customer)

		# update to folio transaction
		
		update_pos_pay_to_room_adjustment(self)

		# delete payment from POS Sale Payment
		frappe.db.sql("delete from `tabPOS Sale Payment` where parent = '{}'".format(self.name))
		frappe.db.commit()

		is_update_inventory = False
		if self.pos_profile:
			enable_calculate_inventory_on_sale = frappe.get_cached_value("POS Profile",self.pos_profile,"enable_calculate_inventory_on_sale")
			if enable_calculate_inventory_on_sale:
				is_update_inventory = True
		else:
			is_update_inventory = True
		
		if is_update_inventory:
			update_inventory_on_cancel(self)
		update_sales_order_and_delivery_note_status(self)
		if len(self.payment) == 1 :
			if self.payment[0].payment_type_group == "On Account":
				update_customer_point_on_cancel_sale(self.name,self.customer,self.customer_name)
		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.update_inventory_on_cancel", queue='short', self=self)

	def get_auto_name(self):
		from frappe.model.naming import make_autoname
		return  make_autoname(self.custom_bill_number_prefix)
	

 
	def validate_coupon_codes(self):
		if self.sale_type =="Sale Coupon":
			if self.sale_products:
				coupons = self.sale_products[0].coupons
				if not isinstance(coupons, dict):
					coupons = json.loads(coupons)
			 
				if coupons:
					for c in coupons:
						# lockx_db(c.get("name"))
						sql = "select coupon_status from `tabCoupon Codes` where name = %(coupon_code)s and coupon_status= 'Unused'"
						
						check_coupon_data = frappe.db.sql(sql,{"coupon_code":c.get("name")})
						if not check_coupon_data:
							frappe.throw("គូប៉ុងលេខ {} បានប្រើប្រាសសរួចហើយ".format(c.get("coupon")))
						
						# check if this coupon code already have in Coupon Transaction with transaction_type= Sale Coupon
						sql="select name from `tabCoupon Transaction` where coupon_code = %(coupon_code)s and transaction_type='Sale Coupon' limit 1"
						coupon_already_sold = frappe.db.sql(sql, {"coupon_code":c.get("name")})
						if coupon_already_sold:
							frappe.throw("គូប៉ុងលេខ {} បានប្រើប្រាសសរួចហើយ".format(c.get("coupon")))

		if self.sale_type =="Top Up":
			# server validation for top up check if coupon have sale record
			if self.sale_products:
				coupon = self.sale_products[0].coupons
				if not isinstance(coupon, dict):
					coupon = json.loads(coupon)[0]
					
					# lockx_db(coupon.get("coupon"))
					sql = "select name from `tabCoupon Transaction` where coupon_code = %(coupon_code)s and transaction_type = 'Sale Coupon' limit 1"
					if not frappe.db.sql(sql,{"coupon_code":coupon.get("name")}):
						frappe.throw(_("This coupon number is not a used coupon. Please sale this coupon first."))

					# check last transaction is top_up then check duration of top
					sql = "select creation from `tabCoupon Transaction` where coupon_code = %(coupon_code)s and transaction_type = 'Top Up' order by creation desc limit 1"
					last_top_up_data = frappe.db.sql(sql,{"coupon_code":coupon.get("name")},as_dict=1)
					if last_top_up_data:
						# frappe.throw("end {} => start {}".format(frappe.utils.getdate(frappe.utils.now())
						# ,
						# frappe.utils.getdate(last_top_up_data[0].get("creation"))
						# ))
						from frappe.utils import get_datetime
						diff_seconds = (get_datetime(frappe.utils.now()) -  get_datetime(last_top_up_data[0].get("creation"))).total_seconds()
						if diff_seconds<=15:
							frappe.throw("សូមរង់ចាំ១៥វិនាទីមុនពេលបញ្ចូលប្រាក់ក្នុងគូប៉ុងម្តងទៀត។")





		elif self.sale_type =="Redeem":
			
			for sp in self.sale_products:
				if sp.coupons:
					coupons = json.loads(sp.coupons)
					for c in coupons:
						lock_db(name = c.get("coupon"))
						sql = "select sum(actual_amount) as balance from `tabCoupon Transaction` where coalesce(status,'') <> 'Deleted' and  coupon_code =%(coupon_id)s"
						data = frappe.db.sql(sql, {"coupon_id":c.get("name")},as_dict=1)
						
						if data:
						

							if(math_round(data[0].get("balance")) != math_round(abs(sp.amount))):
								frappe.throw(_("Invalid redeem amount. Please check coupon balance again."))
						else:
							frappe.throw(_("Invalid  Coupon Code"))
 

def lock_db(name=None,self=None):
	if name:
		lock = frappe.db.sql("SELECT GET_LOCK('_{}', 0)".format(name))[0][0]
	
		if not lock:
			frappe.throw(_("This coupon code is being use by other transaction. Please try again later."))
	if self:
		for sp in self.sale_products:
			if sp.coupons:
				coupons = json.loads(sp.coupons)
				for c in coupons:
					lock = frappe.db.sql("SELECT GET_LOCK('_{}', 0)".format(c.get("coupon")))[0][0]
					if not lock:
						frappe.throw(_("This coupon code is being use by other transaction. Please try again later."))
						
def unlock_db(self):
	for sp in self.sale_products:
		if sp.coupons:
			coupons = json.loads(sp.coupons)
			for c in coupons:
				
				frappe.db.sql("DO RELEASE_LOCK('_{}')".format(c.get("coupon")))


def math_round(value, precision = None):
	import math
	import decimal
	if not precision:
		precision = int( frappe.get_cached_value("System Settings", None, "currency_precision") or 0)
	
	# 1. Define the precision context (e.g., 1E-2 for 2 decimal places)
	power = decimal.Decimal('1E-' + str(precision))
	# 2. Convert value to a string first to ensure accurate Decimal representation
	dec_value = decimal.Decimal(str(value)) 
	# 3. Quantize (round) using the standard ROUND_HALF_UP rule
	result = dec_value.quantize(power, rounding=decimal.ROUND_HALF_UP)
	# Return as a float for consistency with your original function signature
	return float(result)

	# result = math.floor(((value or 0) * math.pow(10, (precision or 0) )) + 0.5) / math.pow(10, (precision or 0))
	# return result

def update_sales_order_and_delivery_note_status(self):
	if self.sales_order:
		sales_order_product = frappe.db.sql("""
						select
						a.product_code,
						a.base_unit,
						a.unit,
						a.quantity,
						0 as converted_qty
						from `tabSales Order Product` a
						inner join `tabSales Order` b on b.name = a.parent
						where b.name = '{}' and b.docstatus = 1""".format(self.sales_order),as_dict=1)
		delivery_note_product = frappe.db.sql("""
						select
						a.product_code,
						a.base_unit,
						a.unit,
						a.quantity,
						0 as converted_qty
						from `tabDelivery Note Product` a
						inner join `tabDelivery Note` b on b.name = a.parent
						where {0} = '{1}' and b.docstatus = 1""".format(("b.name" if self.delivery_note else "b.sales_order"),self.delivery_note if self.delivery_note else self.sales_order),as_dict=1)
		sale_products = frappe.db.sql("""
						select 
						a.product_code,
						a.unit,
						a.base_unit,
						a.quantity,
						0 as converted_qty
						from `tabSale Product` a
						inner join `tabSale` b on b.name = a.parent
						where b.sales_order = '{}' and b.docstatus = 1""".format(self.sales_order),as_dict=1)
		if len(sales_order_product) > 0:
			for a in sales_order_product:
				uom_conversion = get_uom_conversion(a.base_unit,a.unit)
				a.converted_qty = a.quantity * uom_conversion

		if len(delivery_note_product) > 0:
			for a in delivery_note_product:
				uom_conversion = get_uom_conversion(a.base_unit,a.unit)
				a.converted_qty = a.quantity * uom_conversion

		if len(sale_products) > 0:
			for a in sale_products:
				uom_conversion = get_uom_conversion(a.base_unit,a.unit)
				a.converted_qty = a.quantity * uom_conversion

		sales_order_product_qty = Enumerable(sales_order_product).sum(lambda x: x.converted_qty or 0)
		delivery_note_product_qty = Enumerable(delivery_note_product).sum(lambda x: x.converted_qty or 0)
		sale_product_qty = Enumerable(sale_products).sum(lambda x: x.converted_qty or 0)
		sales_order_status = ""
		if sales_order_product_qty == sale_product_qty:
			sales_order_status = "Completed"
		elif sales_order_product_qty > sale_product_qty:
			if delivery_note_product_qty == sales_order_product_qty and sale_product_qty>0:
				sales_order_status = "Partially Billed"
			elif delivery_note_product_qty == sales_order_product_qty and sale_product_qty==0:
				sales_order_status = "To Bill"
			else:
				sales_order_status = "To Deliver and Bill"
		else:
			sales_order_status = "To Bill"
		frappe.db.set_value("Sales Order",self.sales_order,"status",sales_order_status)
		
		delivery_status = ""
		if self.delivery_note:
			if delivery_note_product_qty == sale_product_qty:
				delivery_status = "Completed"
			elif delivery_note_product_qty > sale_product_qty:
				delivery_status = "Partially Billed"
			else:
				delivery_status = "To Bill"
			frappe.db.set_value("Delivery Note",self.delivery_note,"status",delivery_status)
		else:
			delivery_note = frappe.get_all("Delivery Note",filters={"sales_order":self.sales_order,"docstatus":1},fields=["name"])
			for a in delivery_note:
				frappe.db.set_value("Delivery Note",a.name,"status","To Bill" if sales_order_status == "To Deliver and Bill" else sales_order_status)
		frappe.db.commit()

## generate custom bill number
def on_generate_custom_bill_number(self):
	return
	if (self.custom_bill_number or "") == "":
		if self.pos_profile:
			pos_config_name = frappe.get_cached_value("POS Profile",self.pos_profile,"pos_config")
			pos_config = frappe.get_cached_value("POS Config",pos_config_name,["pos_bill_number_prefix","generate_bill_number_on_create"], as_dict=1)
			if pos_config.generate_bill_number_on_create == 1 and  self.is_new():
				if pos_config.pos_bill_number_prefix:
					from frappe.model.naming import make_autoname
					self.custom_bill_number = make_autoname(pos_config.pos_bill_number_prefix)
		else:
			if self.custom_bill_number_prefix:
				from frappe.model.naming import make_autoname
				self.custom_bill_number = make_autoname(self.custom_bill_number_prefix)

#update sale and sale product cost / cross profit
def update_sale_sale_product_cost(self):
	#update profit for commission
	total_cost = 0
	total_second_cost = 0
	for p in self.sale_products:
		pos_profile = p.pos_profile if p.pos_profile else self.pos_profile
		sale_product_stock_location = get_stock_location_by_pos_profile(p.product_code,pos_profile,self.stock_location)
		uom_conversion = get_uom_conversion(p.base_unit, p.unit)
		cost = get_product_cost(sale_product_stock_location, p.product_code)/uom_conversion
		## update sale product cost 
		p.cost = cost
		p_second_cost = (frappe.db.get_value('Product',{'product_code':p.product_code}, 'secondary_cost') or 0)
		total_cost += (((cost or 0) * (p.quantity or 0)) or 0)
		if p_second_cost != 0:
			total_second_cost += ((p_second_cost/uom_conversion)* (p.quantity or 0))
	self.sale_grand_total = self.grand_total
	self.sale_profit = self.grand_total - total_cost
	self.total_secondary_cost = total_second_cost
	self.second_sale_profit = self.grand_total - total_second_cost
	self.total_cost = total_cost
	self.profit = self.grand_total - total_cost
	self.second_profit = self.grand_total - total_second_cost 

def update_pos_pay_to_room_adjustment(self):
	#check sale has payment type transfer to edoor and user cancel order 
    # then we check payment type adjustment account then post adjustment account to edoor pms
	if 'edoor' in frappe.get_installed_apps():
		payments =  deepcopy(self.payment)
		for p in [d for d in payments if d.folio_transaction_number and d.folio_transaction_type and  not d.cancel_order_adjustment_account_code]:
			frappe.throw("There is no cancel order adjustment account code for payment type {}. Please config it in POS Config Setting.".format(p.payment_type))
		for p in [d for d in payments if d.folio_transaction_type and d.folio_transaction_number and d.cancel_order_adjustment_account_code]:
			data = {
					'doctype': 'Folio Transaction',
					"is_base_transaction":1,
					'posting_date':self.posting_date,
					'transaction_type': p.folio_transaction_type,
					'transaction_number': p.folio_transaction_number,
					'reference_number':self.name,
					"input_amount":p.amount,
					"amount":p.amount,
					"quantity": 1 if frappe.get_cached_value("Account Code",p.cancel_order_adjustment_account_code,"allow_enter_quantity") ==1 else 0,
					"report_quantity": 1 if frappe.get_cached_value("Account Code",p.cancel_order_adjustment_account_code,"show_quantity_in_report") ==1 else 0,
					"transaction_amount":p.amount,
					"total_amount":p.amount,
					"account_code":p.cancel_order_adjustment_account_code,
					"property":self.business_branch,
					"is_auto_post":1,
					"sale": self.name,
					"tbl_number":self.tbl_number,
					"type":"Credit",
					"guest":self.customer,
					"guest_name":self.customer_name,
					"guest_type":self.customer_group,
					"nationality": "" if not self.customer else  frappe.db.get_value("Customer",self.customer,"country"),
					"report_description": "{} ({})" .format( frappe.get_cached_value("Account Code",p.cancel_order_adjustment_account_code,"account_name"),self.name) ,
				} 
			

			doc = frappe.get_doc(data)
			doc.insert(ignore_permissions=True)	
			# update folio summary credit and debit balance
			frappe.enqueue("edoor.api.folio_transaction.update_reservation_folio", queue='short', name=p.folio_transaction_number, doc=None, run_commit=True )
			reservation = frappe.get_cached_value("Reservation Folio",p.folio_transaction_number,"reservation")
			reservation_stay = frappe.get_cached_value("Reservation Folio",p.folio_transaction_number,"reservation_stay")
			frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = reservation, reservation_stay=reservation_stay)
 
def commission_general_ledger_entry(self):
	commissions=[]
	total_commission = ((self.commission_01 or 0) + (self.commission_02 or 0) + (self.commission_03 or 0) +(self.commission_04 or 0) +(self.commission_05 or 0) )
	if total_commission>0:
		if self.commission_01_account and self.commission_01 > 0:
			commissions.append({"amount":self.commission_01,"account":self.commission_01_account,"employee":a.commission_01_to})
		if self.commission_02_account and self.commission_02 > 0:
			commissions.append({"amount":self.commission_02,"account":self.commission_02_account,"employee":a.commission_02_to})
		if self.commission_03_account and self.commission_03 > 0:
			commissions.append({"amount":self.commission_03,"account":self.commission_03_account,"employee":a.commission_03_to})
		if self.commission_04_account and self.commission_04 > 0:
			commissions.append({"amount":self.commission_04,"account":self.commission_04_account,"employee":a.commission_04_to})
		if self.commission_05_account and self.commission_05 > 0:
			commissions.append({"amount":self.commission_05,"account":self.commission_05_account,"employee":a.commission_05_to})
		if self.docstatus == 1:
			general_ledger_debit(self,account = {"account":self.default_commission_expense_account,"amount":total_commission})
			for a in commissions:
				general_ledger_credit(self,account = {"account":a["account"],"amount":a["amount"],"party":a["employee"]})
		else:
			general_ledger_credit(self,account = {"account":self.default_commission_expense_account,"amount":total_commission})
			for a in commissions:
				general_ledger_debit(self,account = {"account":a["account"],"amount":a["amount"],"party":a["employee"]})

	total_commission = sum(((a.commission_01 or 0)+(a.commission_02 or 0)+(a.commission_03 or 0)+(a.commission_04 or 0)+(a.commission_05 or 0)) for a in self.sale_products)
	if total_commission>0:
		commissions=[]
		for a in self.sale_products:
			if a.commission_01_account and a.commission_01 > 0:
				commissions.append({"amount":a.commission_01,"account":a.commission_01_account,"employee":a.commission_01_to})
			if a.commission_02_account and a.commission_02 > 0:
				commissions.append({"amount":a.commission_02,"account":a.commission_02_account,"employee":a.commission_02_to})
			if a.commission_03_account and a.commission_03 > 0:
				commissions.append({"amount":a.commission_03,"account":a.commission_03_account,"employee":a.commission_03_to})
			if a.commission_04_account and a.commission_04 > 0:
				commissions.append({"amount":a.commission_04,"account":a.commission_04_account,"employee":a.commission_04_to})
			if a.commission_05_account and a.commission_05 > 0:
				commissions.append({"amount":a.commission_05,"account":a.commission_05_account,"employee":a.commission_05_to})
		if self.docstatus == 1:
			general_ledger_debit(self,account = {"account":self.default_commission_expense_account,"amount":total_commission})
			for a in commissions:
				general_ledger_credit(self,account = {"account":a["account"],"amount":a["amount"],"party":a["employee"]})
		else:
			general_ledger_credit(self,account = {"account":self.default_commission_expense_account,"amount":total_commission})
			for a in commissions:
				general_ledger_debit(self,account = {"account":a["account"],"amount":a["amount"],"party":a["employee"]})

def general_ledger_debit(self,account,is_commission = 1):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Sale",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Sale Commission" if is_commission == 1 else "",
		"is_cancelled":1 if self.docstatus == 2 else 0
	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs,commit=False)

def general_ledger_credit(self,account,is_commission = 1):
    docs = []
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":account["account"],
        "credit_amount":account["amount"],
        "voucher_type":"Sale",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Sale Commission" if is_commission == 1 else "",
		"party_type": "Employee" if is_commission == 1 else None,
		"party":account["party"] if is_commission == 1 else None,

		"is_cancelled":1 if self.docstatus == 2 else 0
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs,commit=False)

def update_status(self):
	status = ""
	if self.docstatus == 0:
		status = "Draft"
	elif self.docstatus == 2:
		status = "Cancelled"
	else:
		if self.balance == 0:
			status = "Paid"
		elif self.balance > 0 and self.total_paid > 0:
			status = "Partially Paid"
		else:
			status = "Unpaid"
	frappe.db.set_value('Sale', self.name, 'status', status, update_modified=False)
	if self.sale_quotation:
		update_sale_quotation(self)

def update_sale_quotation(self):
	pass
	status = ""
	if self.docstatus == 1:
		status = "Ordered"
	else:
		status = "Open"
	frappe.db.set_value('Sale Quotation', self.sale_quotation, 'status', status, update_modified=False)
    
def on_sale_delete_update(self):
	spa_commission = "update `tabSale Product SPA Commission` set is_deleted = 1  where sale = '{}'".format(self.name)			
	frappe.db.sql(spa_commission)

	if self.from_reservation:
		if frappe.db.exists("POS Reservation", self.from_reservation):
			
			frappe.db.sql("update `tabPOS Reservation` set workflow_state='Confirmed' where name='{0}'".format(self.from_reservation))
			reservation = frappe.get_doc("POS Reservation", self.from_reservation)
			if reservation:
				reservation.reservation_status = "Confirmed"
				reservation.status = "Confirmed"
				reservation.save()

def generate_decimal(precision: int) -> Decimal:
    return Decimal('0.1') ** precision

def update_inventory_on_submit(self):
	cost = 0 
	for p in self.sale_products:
		pos_profile = p.pos_profile if p.pos_profile else self.pos_profile
		if p.is_inventory_product:			
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			sale_product_stock_location = get_stock_location_by_pos_profile(p.product_code,pos_profile,self.stock_location)
			cost = get_product_cost(sale_product_stock_location, p.product_code) / uom_conversion
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Sale",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'portion':p.portion,
				'unit':p.unit,
				'stock_location': sale_product_stock_location,
				'out_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				'note': 'New sale submitted.',
    			'action': 'Submit'
			})
		else:
			doc = frappe.get_cached_doc("Product",p.product_code)
			#check if product has receipt and loop update from product receip
			update_product_recipe_to_inventory(self,doc, p.quantity, "Submit",p,pos_profile)	
			#udpate cost for none stock product			
			cost = doc.cost or 0
			if doc.product_price:
				prices = Enumerable(doc.product_price).where(lambda x:x.business_branch == self.business_branch and x.price_rule == self.price_rule and x.unit == "Unit" and x.portion ==p.portion).first_or_default()
				if prices:
					cost = prices.cost

		#check if product have modifier then check receipt in modifer and update to inventory
		if p.modifiers_data:
			for m in json.loads(p.modifiers_data):
				modifier_doc = frappe.get_cached_doc("Modifier Code",m['modifier'])
				for d in modifier_doc.product_recipe:
					if d.is_inventory_product:
						uom_conversion = get_uom_conversion(d.base_unit, d.unit)
						add_to_inventory_transaction({
							'doctype': 'Inventory Transaction',
							'transaction_type':"Sale",
							'transaction_date':self.posting_date,
							'transaction_number':self.name,
							'product_code': d.product,
							'unit':d.unit,
							'stock_location':get_stock_location_by_pos_profile(d.product,pos_profile,self.stock_location),
							'out_quantity':(p.quantity* d.quantity) / uom_conversion,
							"uom_conversion":uom_conversion,
							'note': 'Update Recipe Quantity from modifer ({}) after New sale submitted.'.format(m["modifier"]),
							'action': 'Submit'
						})

		
		#check if product is combo menu then get item from the combo menu item and update to inventory
		if p.is_combo_menu:
			update_combo_menu_to_inventory(self,p,"Submit")
		#frappe.db.sql("update `tabSale Product` set cost = {} where name='{}'".format(cost, p.name))
   
	#update total cost to sale and profit to sale
	total_cost = 0
	cost_datas = frappe.db.sql("select coalesce(sum(cost * quantity),0) as total_cost from `tabSale Product` where parent= %(sale)s", {"sale": self.name}, as_dict = 1)
	if cost_datas:
		total_cost = cost_datas[0]["total_cost"] or 0
  
	frappe.db.sql("update `tabSale` set total_cost = {0} , profit=grand_total - {0} where name=%(sale)s".format(total_cost), {"sale":self.name})

def update_product_recipe_to_inventory(self,product,base_quantity,action,sale_product,pos_profile=""):
	current_pos_profile = pos_profile if pos_profile != "" else self.pos_profile
	inventory_products = [x for x in product.product_recipe if x.is_inventory_product == 1]
	inventory_products = [x for x in inventory_products if (not x.price_rule or x.price_rule == self.price_rule)]
	inventory_products = [x for x in inventory_products if (not x.sale_type or x.sale_type == self.sale_type)]

	for d in inventory_products:
		if d.portion == sale_product.portion or (d.portion or "") == "":
			uom_conversion = get_uom_conversion(d.base_unit, d.unit)
			note = ""
			if action =="Submit":
				note = 'Update Recipe Quantity after New sale submitted.'
			else:
				note =  'Update Recipe Quantity after cancel order.'

			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Sale",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': d.product,
				'unit':d.unit,
				'stock_location':get_stock_location_by_pos_profile(d.product,current_pos_profile,self.stock_location),
				'in_quantity':(base_quantity* d.quantity) / uom_conversion if action=="Cancel" else 0,
				'out_quantity':(base_quantity* d.quantity) / uom_conversion if action=="Submit" else 0,
				"uom_conversion":uom_conversion,
				'note': note,
				'action': action
			})

def update_combo_menu_to_inventory(self, product,action):
	if product.is_combo_menu:
		combo_menu_data = json.loads(product.combo_menu_data)
		update_combo_menu_to_inventory_transaction(self,product,action, combo_menu_data)
			
def update_combo_menu_to_inventory_transaction(self,product,action,combo_menu_data):
	pos_profile = product.pos_profile if product.pos_profile else self.pos_profile
	for p in combo_menu_data:
		doc = frappe.get_cached_doc("Product",p["product_code"])
		if doc.is_inventory_product:
			uom_conversion = get_uom_conversion( doc.unit,p["unit"])
			note =""
			if action =="Submit":
				note = 'New sale submitted. Inventory deduct from combo menu {}({})'.format(product.product_name, product.product_code)
			else:
				note = "Order cancelled. Inventory added from combo menu {}({})".format(product.product_name, product.product_code)
			
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Sale",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': doc.name,
				'unit':p["unit"],
				'stock_location':get_stock_location_by_pos_profile(doc.name,pos_profile,self.stock_location),
				"in_quantity": (p["quantity"] * product.quantity) / uom_conversion if action =="Cancel" else 0,
				'out_quantity': (p["quantity"] * product.quantity) / uom_conversion if action =="Submit" else 0,
				"uom_conversion":uom_conversion,
				'note': note,
				'action': action
			})
		else:
			#check if product have receipt then update to stock
			# base qty here is = sale product quantity * combo product quantity
			update_product_recipe_to_inventory(self,doc,product.quantity * p["quantity"], action,product,pos_profile)
					
def update_inventory_on_cancel(self):
	for p in self.sale_products:
		pos_profile = p.pos_profile if p.pos_profile else self.pos_profile
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Sale",
				'transaction_number':self.name,
				'transaction_date':self.posting_date,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':get_stock_location_by_pos_profile(p.product_code,pos_profile,self.stock_location),
				'in_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				"price":p.cost,
				'note': 'Sale invoice cancelled.',
				'action': 'Cancel'
			})
		else:
			doc = frappe.get_cached_doc("Product",p.product_code)
			for d in doc.product_recipe:
				if d.is_inventory_product:
					uom_conversion = get_uom_conversion(d.base_unit, d.unit)
					add_to_inventory_transaction({
						'doctype': 'Inventory Transaction',
						'transaction_type':"Sale",
						'transaction_date':self.posting_date,
						'transaction_number':self.name,
						'product_code': d.product,
						'unit':d.unit,
						'stock_location':get_stock_location_by_pos_profile(d.product,pos_profile,self.stock_location),
						'in_quantity':(p.quantity* d.quantity) / uom_conversion,
						"uom_conversion":uom_conversion,
						'note': 'Update Recipe Quantity after Sale Invoice Cancelled.',
						'action': 'Cancel'
					})	
		#check if product has modifier and then chekc if modiifer have receipt then run script to update receipe

		if p.modifiers_data:
			for m in json.loads(p.modifiers_data):
				modifier_doc = frappe.get_cached_doc("Modifier Code",m['modifier'])
				for d in modifier_doc.product_recipe:	
					uom_conversion = get_uom_conversion(d.base_unit, d.unit)
					add_to_inventory_transaction({
						'doctype': 'Inventory Transaction',
						'transaction_type':"Sale",
						'transaction_date':self.posting_date,
						'transaction_number':self.name,
						'product_code': d.product,
						'unit':d.unit,
						'stock_location':get_stock_location_by_pos_profile(d.product,pos_profile,self.stock_location),
						'in_quantity':(p.quantity* d.quantity) / uom_conversion,
						"uom_conversion":uom_conversion,
						'note': 'Update Recipe Quantity from modifer ({}) after Sale Invoice Cancelled.'.format(m["modifier"]),
						'action': 'Cancel'
					})	

		#check if product is combo menu then get item from the combo menu item and update to inventory
		if p.is_combo_menu:
			update_combo_menu_to_inventory(self,p,"Cancel")
		
def add_payment_to_sale_payment(self):
	if self.payment:
		for p in self.payment:		 
			if p.payment_type_group !='On Account':
					doc = frappe.get_doc({
							'doctype': 'Sale Payment',
							'naming_series': self.sale_payment_naming_series,
							'posting_date':self.posting_date,
							'payment_type': p.payment_type,
							'currency':p.currency,
							'exchange_rate':p.exchange_rate,
							'change_exchange_rate':p.change_exchange_rate,
							'sale':self.name,
							'input_amount':p.input_amount,
							"payment_amount":p.amount,
							"docstatus":1,
							"check_valid_payment_amount":0,
							"pos_profile":self.pos_profile,
							"working_day":self.working_day,
							"cashier_shift":self.cashier_shift,
							"room_number":p.room_number,
							"folio_number":p.folio_number,
							"folio_transaction_number":p.folio_transaction_number,
							"folio_transaction_type":p.folio_transaction_type,
							"use_room_offline":p.use_room_offline,
							"account_code":p.account_code,
							"fee_amount":p.fee_amount,
							"fee_percentage":p.fee_percentage,
							"issue_gift_voucher":p.issue_gift_voucher,
							"pos_sale_payment":p.name,
							"is_generate_qr":p.is_generate_qr,
							"aba_pay_transaction":p.aba_pay_transaction,
							"add_from_sale":1
						})
					doc.flags.ignore_post_general_ledger_entry = True
					doc.flags.ignore_update_sale = True
					doc.insert()
			else:
				update_customer_point(self.customer,p.payment_type_group,p.amount,None,self.name,self.customer_name)
		if (self.changed_amount or 0)>0:
			payment_type = frappe.get_cached_value("ePOS Settings",None,"changed_payment_type")		
			account_code = "" 
			exchange_rate = 1
			if self.pos_profile:
				pos_config = frappe.get_cached_value('POS Profile', self.pos_profile, 'pos_config')					
				pos_config_data = frappe.get_cached_doc('POS Config', pos_config)
				pos_config_payment_type = Enumerable(pos_config_data.payment_type).where(lambda x:x.payment_type==payment_type)				
				if pos_config_payment_type:
					account_code = pos_config_payment_type[0].account_code
					exchange_rate = pos_config_payment_type[0].change_exchange_rate		
			else:
				pt = frappe.get_cached_doc('Payment Type', payment_type)
				exchange_rate = pt.change_exchange_rate or 1

			doc = frappe.get_doc({
					'doctype': 'Sale Payment',
					'naming_series': self.sale_payment_naming_series,
					"transaction_type":"Changed",
					'posting_date':self.posting_date,
					'payment_type': payment_type,
					'sale':self.name,
					'input_amount':(self.changed_amount * exchange_rate ) * -1, 
					"docstatus":1,
					"check_valid_payment_amount":0,
					"pos_profile":self.pos_profile,
					"working_day":self.working_day,
					"cashier_shift":self.cashier_shift,
					"note": "Changed amount in sale order {}".format(self.name),
					"account_code":account_code,
					"add_from_sale":1
				})
			doc.flags.ignore_post_general_ledger_entry = True
			doc.insert()

def validate_sale_product(self):
	currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
	if currency_precision=='':
		currency_precision = "2"
		
	sale_discount = self.discount  
	if sale_discount>0:
		if self.discount_type=="Amount":
			discountable_amount = Enumerable(self.sale_products).where(lambda x: x.allow_discount==1 and x.discount==0).sum(lambda x: (x.quantity or 0)* (x.price or  0))
			if discountable_amount>0:
				sale_discount= math_round( (sale_discount / discountable_amount ),int(currency_precision)) * 100
			sale_discount = sale_discount or 0
	# coupon expired date duration

	coupon_expired_duration = frappe.get_cached_value("ePOS Settings",None,"default_coupon_expired")

	for d in self.sale_products:
		# serve validate get product config to update to sale product config
		# allow discount is very important for validate chart of account code to post discount amount to GL Entry
		
		allow_discount = frappe.get_cached_value("Product",d.product_code,"allow_discount")
		d.allow_discount = allow_discount
		

		d.regular_price = d.regular_price if d.regular_price else d.price
		# validate product free
		if(d.is_free and d.price > 0):
			frappe.throw(_("Cannot set price becouse this product is free"))
		
		d.sub_total = (d.quantity or 0) * (d.price or 0) + (d.quantity or 0) * (d.modifiers_price or 0)
		if (d.discount_type or "Percent")=="Percent":
			d.discount_amount = d.sub_total * (d.discount or 0) / 100
			d.discount_amount = math_round(d.discount_amount  , int(currency_precision))
		else:
			d.discount_amount = d.discount or 0
		# check if sale has discount
		if sale_discount>0 and d.allow_discount and d.discount==0:
			d.sale_discount_percent = sale_discount  
			d.sale_discount_amount = (sale_discount/100) * d.sub_total
		else:
			d.sale_discount_percent = 0  
			d.sale_discount_amount = 0

		
		d.sale_discount_amount=math_round(d.sale_discount_amount  , int(currency_precision)) 
		
		d.total_discount = (d.sale_discount_amount or 0) + (d.discount_amount or 0)

		validate_tax(d)
		d.amount = (d.sub_total - d.discount_amount) 
		d.total_revenue = (d.sub_total - d.total_discount) 
		if d.rate_include_tax == 0:
			d.amount += d.total_tax
			d.total_revenue += d.total_tax

		## update cryto able amount
		if d.total_discount > 0 or d.allow_crypto_claim == 0 :
			d.crypto_able_amount = 0
		else:
			d.crypto_able_amount = d.amount 


		# update total coupon value
		if self.sale_type in ["Sale Coupon","Top Up","Redeem"]: 
			d.total_coupon_value = (d.coupon_value or 0) * (d.quantity or 0) * (-1 if self.sale_type=="Redeem" else 1)
			if self.docstatus == 1 and frappe.get_cached_value("Product",d.product_code,"is_coupon")==1:
				d.coupon_expired_date = add_to_date(datetime.datetime.now(),days=coupon_expired_duration)

			 
			if d.coupons:
				if abs(d.quantity) != len(json.loads(d.coupons)):
					frappe.throw(_("Invalid Coupon Quantity"))

			
			


def add_coupon_GL_entry(self):
	def general_ledger(self,account):
		if abs(account["amount"]) > 0:
			docs = []
			doc = {
				"doctype":"General Ledger",
				"posting_date":self.posting_date,
				"account":account["account"],
				"amount":account["amount"],
				"voucher_type":"Sale",
				"voucher_number":self.name,
				"business_branch": self.business_branch,
				"remark": "",
				"party_type": "Customer",
				"party":account["party"],
				"remark": "Redeem Coupon" if self.sale_type == "Redeem" else "",
				"is_cancelled":1 if self.docstatus == 2 else 0
			}
			if account["party"]:
				doc["party_name"] = self.customer_name

			docs.append(doc)
			submit_general_ledger_entry(docs=docs,commit=False)
	
	coupons = []
	for a in self.sale_products:
		if len((a.coupons or "")) > 0:
			coupons.append({
				"amount":(a.amount or 0),
				"expense_amount":(a.total_coupon_value or 0) - (a.sub_total or 0),
				"coupon_amount":a.total_coupon_value,
				"income_account":a.default_income_account,
				"expense_account":a.default_coupon_expense_account
			})
	income_account = list(set([d["income_account"] for d in coupons if d.get("income_account","") != ""]))
	expense_account = list(set([d["expense_account"] for d in coupons if d.get("expense_account","") != ""]))
	if len(income_account)>0:
		for a in income_account:
			general_ledger(self,account = {"account":a,"amount":sum(b.get("coupon_amount") for b in coupons if b.get("income_account","") == a),"party":self.customer})
	if len(expense_account)>0:
		for a in expense_account:	 
			general_ledger(self,account = {"account":a,"amount":sum(b.get("expense_amount") for b in coupons if b.get("expense_account","") == a),"party":""})



def add_sale_product_spa_commission(self):			
	frappe.db.sql("delete from `tabSale Product SPA Commission` where sale = '{}'".format(self.name))
	for sp in self.sale_products:		 
		if sp.is_require_employee and sp.employees: 
			for em in json.loads(sp.employees): 
				data ={
					'doctype': 'Sale Product SPA Commission',
					'sale':self.name,
					'sale_product': sp.name,
					'product_name':sp.product_name,
					'product_name_kh':sp.product_name_kh,
					"employee":em['employee_id'],
					"employee_name":em['employee_name'],
					"duration_title":em['duration_title'],
					"duration":em['duration'],
					"commission_amount":em['commission_amount'],
					"is_overtime":em['is_overtime']
				} 
				doc = frappe.get_doc(data)
				doc.insert() 
				
def create_folio_transaction_from_pos_trnasfer(self):
	for p in self.payment:
		if p.folio_transaction_type and (p.folio_transaction_number or p.reservation_stay):
			if (p.account_code or "") == "":
				pos_config = frappe.get_cached_value('POS Profile', self.pos_profile, 'pos_config')			
				pos_config_data = frappe.get_cached_doc('POS Config', pos_config)
				pos_config_payment_type = Enumerable(pos_config_data.payment_type).where(lambda x:x.payment_type==p.payment_type)
				if pos_config_payment_type:
					p.account_code = pos_config_payment_type[0].account_code	
			if not p.account_code:
				frappe.throw("Please account code for Payment type {}".format(p.payment_type))

			transaction_number = p.folio_transaction_number
			if p.folio_transaction_type=="Reservation Folio" and not  p.folio_transaction_number and p.reservation_stay:
				guest_folio =  create_guest_folio(self, p.reservation_stay)
				if (guest_folio):
					transaction_number = guest_folio.name
				else:
					frappe.throw(_("There's problem with create guest folio. Please try again."))
    
    
			data = {
					'doctype': 'Folio Transaction',
					"is_base_transaction":1,
					'posting_date':self.posting_date,
					'transaction_type': p.folio_transaction_type,
					'transaction_number': transaction_number,
					'reference_number':self.name,
					"input_amount":p.amount,
					"amount":p.amount,
					"quantity": 1 if frappe.get_cached_value("Account Code",p.account_code,"allow_enter_quantity") ==1 else 0,
					"report_quantity": 1 if frappe.get_cached_value("Account Code",p.account_code,"show_quantity_in_report") ==1 else 0,
					"transaction_amount":p.amount,
					"total_amount":p.amount,
					"account_code":p.account_code,
					"property":self.business_branch,
					"is_auto_post":1,
					"sale": self.name,
					"tbl_number":self.tbl_number,
					"type":"Debit",
					"guest":self.customer,
					"guest_name":self.customer_name,
					"guest_type":self.customer_group,
					"report_description": "{} ({})" .format( frappe.get_cached_value("Account Code",p.account_code,"account_name"),self.name) ,
					"nationality": "" if not self.customer else  frappe.get_cached_value("Customer",self.customer,"country")
				}
			
			doc = frappe.get_doc(data)
			doc.insert(ignore_permissions=True)	
			# update folio summary credit and debit balance
			frappe.enqueue("edoor.api.folio_transaction.update_reservation_folio", queue='short', name=transaction_number, doc=None, run_commit=True )
			reservation = frappe.get_cached_value("Reservation Folio",transaction_number,"reservation")
			reservation_stay = frappe.get_cached_value("Reservation Folio",transaction_number,"reservation_stay")
			frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = reservation, reservation_stay=reservation_stay)

def create_guest_folio(self,reservation_stay):
    from edoor.api.frontdesk import get_working_day    
    working_day = get_working_day(self.business_branch)   
    doc = frappe.get_doc({
		"doctype":"Reservation Folio",
  		"guest":self.customer,
		"property":self.business_branch,
		"working_day":working_day["name"],
		"cashier_shift":working_day["cashier_shift"]["name"],
		"reservation_stay":reservation_stay,
		"posting_date":working_day["date_working_day"],
		"note":"This folio was created by {} from POS when transfer bill to room".format(frappe.get_cached_value("User",frappe.session.user,"full_name"))
	})
    doc.insert(ignore_permissions=True)
    return doc

def on_get_revenue_account_code(self):
	for sp in self.sale_products:
		values = {
			'outlet': self.outlet,
			'shift': self.shift_name,
			'revenue_group': sp.revenue_group
			}
		data = frappe.db.sql("""
				select 
					name,
					code,
					account_code,
					discount_account,
					tax_1_account,
					tax_2_account,
					tax_3_account
				from `tabRevenue Code` 
				where outlet=%(outlet)s
				and shift = %(shift)s
				and revenue_group=%(revenue_group)s
			""",values=values, as_dict=1)
		if data:
			sp.revenue_code = data[0].code
			sp.account_code = data[0].account_code
			sp.discount_account = data[0].discount_account
			sp.tax_1_account = data[0].tax_1_account
			sp.tax_2_account = data[0].tax_2_account
			sp.tax_3_account = data[0].tax_3_account

def validate_pos_payment(self,skip_check):
	error = ""
	currency = frappe.db.get_default("currency")
	for d in self.payment:
		if not d.default_account and skip_check == 0:
			error += "Please set default account for payment type <b>{}</b>. ".format(d.payment_type)
		d.exchange_rate = d.exchange_rate if d.currency != currency else 1
		d.change_exchange_rate = d.change_exchange_rate if d.currency != currency else 1		
		d.amount = (d.input_amount or 0 ) / (d.exchange_rate or 1)
	if error != "" and skip_check == 0:
		frappe.throw(error)

def validate_cash_coupon_claim(self):
	for cc in self.cash_coupon_items:
		cc.posting_date = self.posting_date

	self.total_cash_coupon_claim = 0

	if len(self.cash_coupon_items)>0:
		sql = """select name,parent, member, amount, claim_amount, balance, unlimited,expiry_date, docstatus from `tabCash Coupon Items` where name in %(name)s"""
	
		coupons = frappe.db.sql(sql,{
			"name":[d.coupon_code for d in self.cash_coupon_items]
		}, as_dict= 1) 

		


		## check invalite coupon code
		invalid_coupon = [c for c in  coupons if not c["docstatus"] is 1]
		if len (invalid_coupon) > 0:
			frappe.throw("There are invalid coupon code ({})".format(", ".join( [d["name"]  for d in invalid_coupon])))

		coupon_codes = [c["name"] for c in coupons]

		## claim sale coupon 
		## get sale coupon
		sale_coupon_sql = """select name,coupon_number,cash_coupon_claim,cash_coupon_balance, cash_coupon_amount, docstatus, end_date from `tabSale Coupon` where name in %(name)s"""
		sale_coupons = frappe.db.sql(sale_coupon_sql, {"name":[d.coupon_code for d in self.cash_coupon_items]}, as_dict = 1)
		if len(sale_coupons ) > 0:
			invalid_sale_coupon = [sc for sc in sale_coupons if not sc["docstatus"] is 1]
			if len (invalid_sale_coupon)>0:
				frappe.throw("There are invalid coupon code ({})".format(", ".join( [d["name"]  for d in invalid_coupon])))
			
			coupon_codes = coupon_codes + [sc["name"] for sc in sale_coupons]

		## remove sale cash coupon item not exist db
		[self.cash_coupon_items.remove(d) for d in self.get('cash_coupon_items') if not d.coupon_code in coupon_codes]
 
		
		## set value and check expired, balance
		claim_amount = 0
		for d in coupons:		
			for c in [x for x in self.cash_coupon_items if x.coupon_code == d["name"]]:
				claim_amount = sum([(i.claim_amount or 0) for i in self.cash_coupon_items if i.coupon_code == d["name"]])
				if d["balance"] < claim_amount:
					frappe.throw("Cash Coupon {} not enought balance for claim with amount {}. Current balance is {}".format(d["name"],frappe.format_value(claim_amount, {"fieldtype":"Currency"}) ,frappe.format_value( d["balance"], {"fieldtype":"Currency"})))
				c.member = d["member"]
				c.cash_coupon = d["parent"]
				if d["unlimited"] == 0:   
					if d["expiry_date"] < datetime.datetime.strptime(str( self.posting_date), '%Y-%m-%d').date() :
						frappe.throw("The coupon {} was expired".format(d["name"]))

		

		sale_coupon_claim_amount = 0
		if len (sale_coupons) > 0:
			for sc in sale_coupons:
				for c in [x for x in self.cash_coupon_items if x.coupon_code == sc["name"]]:
					sale_coupon_claim_amount = sum([(i.claim_amount or 0) for i in self.cash_coupon_items if i.coupon_code == sc["name"]])
					if sc["cash_coupon_balance"] < sale_coupon_claim_amount:
						frappe.throw("Sale Coupon {} not enought balance for claim with amount {}. Current balance is {}".format(sc["name"],frappe.format_value(sale_coupon_claim_amount, {"fieldtype":"Currency"}) ,frappe.format_value( d["balance"], {"fieldtype":"Currency"})))
					c.sale_coupon = sc["name"]
					if sc["end_date"] < datetime.datetime.strptime(str( self.posting_date), '%Y-%m-%d').date() :
						frappe.throw("The coupon {} was expired".format(sc["name"]))

		self.total_cash_coupon_claim = claim_amount + sale_coupon_claim_amount		

def on_update_coupon_information(self):	
	if len(self.cash_coupon_items ) > 0 and self.docstatus in (1,2):
		cash_coupons = [s for s in self.cash_coupon_items if s.cash_coupon]
		if len(cash_coupons)>0:
			set_value = """c.claim_amount =  t.total_claim_amount,
					c.balance = c.amount - t.total_claim_amount"""			
			
			## update claim amount , balance in cash coupon item 
			sql = """update `tabCash Coupon Items` c
					inner join (
						select 
							x.coupon_code,
							sum(x.claim_amount) as total_claim_amount 
						from `tabSale Cash Coupon Claim` x
						where coalesce(x.cash_coupon,'') != '' 
						and x.coupon_code in %(coupon_codes)s
						and x.docstatus = 1
						group by x.coupon_code
					) t on c.`code` = t.coupon_code
					set {}
					where c.`code` in %(coupon_codes)s""".format(set_value)	
					
			frappe.db.sql(sql, {"sale":self.name,"coupon_codes": [c.coupon_code for c in cash_coupons ]})

			# update cash coupn total claim
			seen = set()
			[x for x in cash_coupons if x.cash_coupon not in [s["coupon_code"] for s in seen] and not seen.add(x)]
			
			if len (seen) > 0:
				update_sql = """update `tabCash Coupon` c
					inner join (
						select 
							x.parent,
							sum(x.claim_amount) as total_claim_amount,
							sum(x.balance) as total_balance
						from `tabCash Coupon Items` x 
						where  x.parent in %(parent)s
						group by x.parent
					) i on i.parent = c.`name`
						set c.total_claim = i.total_claim_amount,
						c.total_balance = i.total_balance
					where c.name in %(parent)s"""
				
				frappe.db.sql(update_sql, {"parent":[m.coupon_code for m in seen ]})

				## update coupon information on customer 
				from epos_restaurant_2023.api.api import update_cash_coupon_summary_to_customer
				update_cash_coupon_summary_to_customer([m.member for m in seen])

		sale_coupons = [s for s in self.cash_coupon_items if s.sale_coupon]
		if len(sale_coupons) > 0:
			update_value = """sc.cash_coupon_claim = c.total_claim_amount, sc.cash_coupon_balance = sc.cash_coupon_amount -  c.total_claim_amount"""			
			update_sale_coupon_sql = """update `tabSale Coupon` sc
			inner join (
				select 
					s.coupon_code,
					sum(s.claim_amount) as total_claim_amount 
				from `tabSale Cash Coupon Claim` s
				where coalesce(s.sale_coupon,'')!= '' 
				and s.docstatus = 1
				and s.coupon_code in %(coupon_codes)s
				group by s.coupon_code
			) c on c.coupon_code = sc.name
			set {}
			where sc.name in %(coupon_codes)s""".format(update_value)

			frappe.db.sql(update_sale_coupon_sql, {"sale":self.name,"coupon_codes": [c.coupon_code for c in sale_coupons ]})

def validate_tax(doc):
		
		if doc.tax_rule:
			amount = doc.sub_total
			if (doc.rate_include_tax == 1) :
				priceBefore = get_ratebefore_tax(doc.sub_total - doc.total_discount,doc.tax_rule, doc.tax_1_rate, doc.tax_2_rate, doc.tax_3_rate)
				amount =  priceBefore + doc.total_discount  
			
			doc.selling_price = 0 if doc.quantity == 0 else   ((amount / doc.quantity) or 0) - (doc.modifiers_price or 0)


			#Tax 1
			doc.taxable_amount_1 = amount
			#cal tax1 taxable after disc.
			if doc.calculate_tax_1_after_discount == 1:
				doc.taxable_amount_1 =   amount - doc.total_discount			 
				
			doc.taxable_amount_1 *= (doc.percentage_of_price_to_calculate_tax_1/100)
			doc.tax_1_amount =  (doc.taxable_amount_1 or 0) * ((doc.tax_1_rate or 0)/100)

			#Tax 2
			doc.taxable_amount_2 = amount
			#cal tax2 taxable after disc.
			if doc.calculate_tax_2_after_discount==1:
				doc.taxable_amount_2 = amount  - doc.total_discount

			#cal tax2 taxable after add tax1
			if doc.calculate_tax_2_after_adding_tax_1==1:
				doc.taxable_amount_2 +=  doc.tax_1_amount

			doc.taxable_amount_2 *= (doc.percentage_of_price_to_calculate_tax_2/100)
			doc.tax_2_amount =  (doc.taxable_amount_2 or 0) *  ((doc.tax_2_rate or 0) /100)

			#tax 3
			doc.taxable_amount_3 =  amount
			#cal tax3 taxable after disc.
			if doc.calculate_tax_3_after_discount==1:
				doc.taxable_amount_3 = amount - doc.total_discount 
			
			#cal tax3 taxable after add tax1
			if doc.calculate_tax_3_after_adding_tax_1==1:
				doc.taxable_amount_3 =   doc.taxable_amount_3 +  doc.tax_1_amount 
			
			#cal tax3 taxable after add tax2
			if doc.calculate_tax_3_after_adding_tax_2==1:
				doc.taxable_amount_3 = doc.taxable_amount_3 +  doc.tax_2_amount 
			
			doc.taxable_amount_3 *= (doc.percentage_of_price_to_calculate_tax_3/100)
			doc.tax_3_amount =  (doc.taxable_amount_3 or 0) *  ((doc.tax_3_rate or 0) /100)
			
			#total tax
			doc.total_tax = doc.tax_1_amount + doc.tax_2_amount + doc.tax_3_amount
		else:
			doc.taxable_amount_1 =0
			doc.tax_1_amount=0
			doc.taxable_amount_2 =0
			doc.tax_2_amount=0
			doc.taxable_amount_3 =0
			doc.tax_3_amount=0
			doc.total_tax =0
		
def get_ratebefore_tax(amount, t_rule, tax_1_rate, tax_2_rate, tax_3_rate):
	tax_rule = frappe.get_cached_doc("Tax Rule",t_rule)
	amount=amount or 0
	
	t1_r = (tax_1_rate or 0) / 100
	t2_r = (tax_2_rate or  0)  / 100
	t3_r = (tax_3_rate or 0)  / 100

	tax_1_amount = 0
	tax_2_amount = 0
	tax_3_amount = 0
	price = 0

	t1_af_disc = tax_rule.calculate_tax_1_after_discount
	t2_af_disc = tax_rule.calculate_tax_2_after_discount

	t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1

	t3_af_disc	= tax_rule.calculate_tax_3_after_discount

	t3_af_add_t1 =  tax_rule.calculate_tax_3_after_adding_tax_1
	t3_af_add_t2 =   tax_rule.calculate_tax_3_after_adding_tax_2


	tax_rate_con = 0
	tax_rate_con = (1 + t1_r + t2_r 
						+ (t1_r * t2_af_add_t1 * t2_r) 
						+ t3_r + (t1_r * t3_af_add_t1 * t3_r) 
						+ (t2_r * t3_af_add_t2 * t3_r)
						+ (t1_r * t2_af_add_t1 * t2_r * t3_af_add_t2 * t3_r))

						

	tax_rate_con = tax_rate_con or 1

	price = amount /  (tax_rate_con or 1)

	return  price

def update_pos_reservation_status(self):
	if self.from_reservation:
		if frappe.db.exists("POS Reservation", self.from_reservation):
			status = frappe.get_cached_doc("POS Reservation Status","Checked Out") 
			frappe.db.set_value('POS Reservation', self.from_reservation,{
				"reservation_status": 'Checked Out',
				"status":"Checked Out",
				"reservation_status_color":status.color,
				"reservation_status_background_color": status.background_color,
				"workflow_state": "Checked Out",
			})



@frappe.whitelist()
def get_park_item_to_redeem(business_branch):
	from epos_restaurant_2023.api.api import get_current_working_day
	result_dict = []
	sales=[]
	current_working_day = get_current_working_day(business_branch=business_branch)
	sql = """
			select 
				a.*,
				s.customer_name,
				s.customer,
				s.phone_number
			from `tabSale Product` a
			inner join `tabSale` s on a.parent = s.name
			where 
				is_park = 1 and
				is_redeem = 0 and 
				expired_date >= '{0}' and
				s.docstatus = 1 and 
				s.business_branch='{1}'
		""".format(getdate(str(current_working_day['posting_date'])).strftime('%Y-%m-%d'),business_branch)
	park_item_list = frappe.db.sql(sql,as_dict=1)
	
	for item in park_item_list:
		sales.append({"sale":item.parent,"customer":item.customer,"customer_name": item.customer_name,"phone_number":item.phone_number})

	for s in sales:
		park_items = [d for d in park_item_list if d.parent == s["sale"]] or []
		result_dict.append({"sale":s["sale"],"customer_name":s["customer_name"],"customer_code":s["customer"],"phone":s["phone_number"],"products":park_items })


	return result_dict

def update_default_account(self):
	if not frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
		return
	update_default_income_account(self)
	update_default_discount_account(self)
	update_default_sale_cash_coupon_claim_account(self)
	update_default_payment_account(self)
	update_default_tip_account(self)
	update_default_change_account(self)
	update_default_expense_account(self)
	update_default_coupon_expense_account(self)
	update_default_inventory_account(self)

def update_default_inventory_account(self):
	default_inventory_account = frappe.get_cached_value("Business Branch", self.business_branch,"default_inventory_account")
	if [x for x in self.sale_products if not x.default_inventory_account]:
		sql="select distinct parent as product_code, default_stock_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.sale_products if not x.default_inventory_account] or [""], "business_branch":self.business_branch},as_dict=1)
		product_has_default_account = [d["product_code"] for d in product_account_codes]
		for sp in [x for x in self.sale_products if not x.default_inventory_account and x.product_code in product_has_default_account]:
			sp.default_inventory_account = [d for d in product_account_codes if d["product_code"] == sp.product_code][0]["default_stock_account"] 
	
	if [x for x in self.sale_products if not x.default_inventory_account]:
		sql="select distinct parent as product_category, default_inventory_account from `tabProduct Category Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		category_account_codes = frappe.db.sql(sql, {"parents":[x.product_category for x in self.sale_products if not x.default_inventory_account] or [""], "business_branch":self.business_branch},as_dict=1)
		category_has_default_account = [d["product_category"] for d in category_account_codes]
		for sp in [x for x in self.sale_products if not x.default_inventory_account and x.product_category in category_has_default_account]:
			sp.default_inventory_account = [d for d in category_account_codes if d["product_category"] == sp.product_category][0]["default_inventory_account"] 

	if [x for x in self.sale_products if not x.default_inventory_account]:
		for sp in [x for x in self.sale_products if not x.default_inventory_account]:
			sp.default_inventory_account = default_inventory_account

def update_default_coupon_expense_account(self):
	# 1 get from product
	if [x for x in self.sale_products if not x.default_coupon_expense_account]:
		# get product default account_code from product
		sql="select distinct parent as product_code, default_coupon_expense_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.sale_products if not x.default_coupon_expense_account] or [""], "business_branch":self.business_branch},as_dict=1)
		product_has_default_account = [d["product_code"] for d in product_account_codes]


		for sp in [x for x in self.sale_products if not x.default_coupon_expense_account and x.product_code in product_has_default_account]:
			# 1 get from product
			sp.default_coupon_expense_account = [d for d in product_account_codes if d["product_code"] == sp.product_code][0]["default_coupon_expense_account"] 
  
	# 2 get from pos_config
	if [x for x in self.sale_products if not x.default_coupon_expense_account]:
		revenue_group_account_codes = get_default_account_from_pos_config( json.dumps( {"business_branch": self.business_branch, "pos_config":self.pos_config, "revenue_groups" : list(set([d.revenue_group for d in self.sale_products if not d.default_coupon_expense_account]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_coupon_expense_account and x.revenue_group in revenue_group_has_default_account]:
				sp.default_coupon_expense_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_coupon_expense_account"] 

	# 3 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_coupon_expense_account]:
		revenue_group_account_codes = get_default_account_from_revenue_group(json.dumps( {"business_branch": self.business_branch, "revenue_groups": list(set([d.revenue_group for d in self.sale_products if not d.default_coupon_expense_account]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_coupon_expense_account and x.revenue_group in revenue_group_has_default_account]:
				sp.default_coupon_expense_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_coupon_expense_account"] 

	# 4 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_coupon_expense_account]:
		for sp in [x for x in self.sale_products if not x.default_coupon_expense_account]:
			sp.default_coupon_expense_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_coupon_expense_account")

def update_default_income_account(self):
	# 1 get from product
	if [x for x in self.sale_products if not x.default_income_account]:
		# get product default account_code from product
		sql="select distinct parent as product_code, default_income_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.sale_products if not x.default_income_account] or [""], "business_branch":self.business_branch},as_dict=1)
		product_has_default_account = [d["product_code"] for d in product_account_codes]
		for sp in [x for x in self.sale_products if not x.default_income_account and x.product_code in product_has_default_account]:
			# 1 get from product
			sp.default_income_account = [d for d in product_account_codes if d["product_code"] == sp.product_code][0]["default_income_account"] 
  
	# 2 get from pos_config
	if [x for x in self.sale_products if not x.default_income_account]:
		revenue_group_account_codes = get_default_account_from_pos_config( json.dumps( {"business_branch": self.business_branch, "pos_config":self.pos_config, "revenue_groups" : list(set([d.revenue_group for d in self.sale_products if not d.default_income_account]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_income_account and x.revenue_group in revenue_group_has_default_account]:
				sp.default_income_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_income_account"] 

	if [x for x in self.sale_products if not x.default_income_account]:
		sql="select distinct parent as product_category, default_income_account from `tabProduct Category Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		category_account_codes = frappe.db.sql(sql, {"parents":[x.product_category for x in self.sale_products if not x.default_income_account] or [""], "business_branch":self.business_branch},as_dict=1)
		category_has_default_account = [d["product_category"] for d in category_account_codes]
		for sp in [x for x in self.sale_products if not x.default_income_account and x.product_category in category_has_default_account]:
			sp.default_income_account = [d for d in category_account_codes if d["product_category"] == sp.product_category][0]["default_income_account"]

	# 3 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_income_account]:
		revenue_group_account_codes = get_default_account_from_revenue_group(json.dumps( {"business_branch": self.business_branch, "revenue_groups": list(set([d.revenue_group for d in self.sale_products if not d.default_income_account]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_income_account and x.revenue_group in revenue_group_has_default_account]:
				sp.default_income_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_income_account"] 

	# 4 get account code from branch
	if [x for x in self.sale_products if not x.default_income_account]:
		for sp in [x for x in self.sale_products if not x.default_income_account]:
			sp.default_income_account = frappe.get_cached_value("Business Branch",self.business_branch,  "default_income_account" if not sp.coupons else "default_unearned_revenue_account" )
 
def update_default_discount_account(self):
	# 1 get from product
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		# get product default account_code from product
		sql="select distinct parent as product_code, default_discount_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.sale_products if not x.default_discount_account and x.allow_discount==1] or [""], "business_branch":self.business_branch},as_dict=1)
		product_has_default_account = [d["product_code"] for d in product_account_codes]
		for sp in [x for x in self.sale_products if not x.default_discount_account and x.product_code in product_has_default_account and  x.allow_discount==1]:
			# 1 get from product
			sp.default_discount_account = [d for d in product_account_codes if d["product_code"] == sp.product_code][0]["default_discount_account"] 
  
	# 2 get from pos_config
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		revenue_group_account_codes = get_default_account_from_pos_config( json.dumps( {"business_branch": self.business_branch, "pos_config":self.pos_config, "revenue_groups" : list(set([d.revenue_group for d in self.sale_products if not d.default_discount_account and d.allow_discount==1] ))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_discount_account and x.revenue_group in revenue_group_has_default_account and  x.allow_discount==1]:
			sp.default_discount_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_discount_account"] 
	
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		sql="select distinct parent as product_category, default_discount_account from `tabProduct Category Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		category_account_codes = frappe.db.sql(sql, {"parents":[x.product_category for x in self.sale_products if not x.default_discount_account and x.allow_discount==1] or [""], "business_branch":self.business_branch},as_dict=1)
		category_has_default_account = [d["product_category"] for d in category_account_codes]
		for sp in [x for x in self.sale_products if not x.default_discount_account and x.product_category in category_has_default_account and  x.allow_discount==1]:
			sp.default_discount_account = [d for d in category_account_codes if d["product_category"] == sp.product_category][0]["default_discount_account"]

	# 3 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		revenue_group_account_codes = get_default_account_from_revenue_group(json.dumps( {"business_branch": self.business_branch, "revenue_groups": list(set([d.revenue_group for d in self.sale_products if not d.default_discount_account and d.allow_discount==1 ]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_discount_account and x.revenue_group in revenue_group_has_default_account and x.allow_discount==1]:
				sp.default_discount_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_discount_account"] 

	# 4 get account code from branch group 
 
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		for sp in [x for x in self.sale_products if not x.default_discount_account and   x.allow_discount==1]:
			sp.default_discount_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_sale_discount_account")

def update_default_expense_account(self):
	# 1 get from product
	if [x for x in self.sale_products]:
		# get product default account_code from product
		sql="select distinct parent as product_code, default_expense_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.sale_products if not x.default_expense_account] or [""], "business_branch":self.business_branch},as_dict=1)
		product_has_default_account = [d["product_code"] for d in product_account_codes]
		for sp in [x for x in self.sale_products if not x.default_expense_account and x.product_code in product_has_default_account]:
			# 1 get from product
			sp.default_expense_account = [d for d in product_account_codes if d["product_code"] == sp.product_code][0]["default_expense_account"] 
  
	# 2 get from pos_config
	if [x for x in self.sale_products if not x.default_expense_account]:
		revenue_group_account_codes = get_default_account_from_pos_config( json.dumps( {"business_branch": self.business_branch, "pos_config":self.pos_config, "revenue_groups" : list(set([d.revenue_group for d in self.sale_products if not d.default_expense_account]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_expense_account and x.revenue_group in revenue_group_has_default_account]:
				sp.default_expense_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_expense_account"] 

	if [x for x in self.sale_products]:
		sql="select distinct parent as product_category, default_expense_account from `tabProduct Category Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		category_account_codes = frappe.db.sql(sql, {"parents":[x.product_category for x in self.sale_products if not x.default_expense_account] or [""], "business_branch":self.business_branch},as_dict=1)
		category_has_default_account = [d["product_category"] for d in category_account_codes]
		for sp in [x for x in self.sale_products if not x.default_expense_account and x.product_category in category_has_default_account]:
			sp.default_expense_account = [d for d in category_account_codes if d["product_category"] == sp.product_category][0]["default_expense_account"] 

	# 3 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_expense_account]:
		revenue_group_account_codes = get_default_account_from_revenue_group(json.dumps( {"business_branch": self.business_branch, "revenue_groups": list(set([d.revenue_group for d in self.sale_products if not d.default_expense_account]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_expense_account and x.revenue_group in revenue_group_has_default_account]:
				sp.default_expense_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_expense_account"] 

	# 4 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_expense_account]:
		for sp in [x for x in self.sale_products if not x.default_expense_account]:
			sp.default_expense_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_cost_of_good_sold_account")

def update_default_sale_cash_coupon_claim_account(self):
	if self.total_cash_coupon_claim > 0: 		
		if not self.default_cash_coupon_claim_account: 
			self.default_cash_coupon_claim_account = frappe.get_cached_value("Business Branch",self.business_branch,"default_sale_cash_coupon_claim_account" )

def update_default_payment_account(self):
	for p in [d for d in self.payment]:
		default_account = frappe.get_cached_value("Payment Type",p.payment_type, "default_account")
		if default_account:
			default_account = [d for d in default_account if d.business_branch == self.business_branch]
			if default_account and not p.default_account:
				p.default_account = default_account[0].account
	 

def update_default_tip_account(self):
	if self.tip_amount>0:
		if not self.default_tip_account:
			self.default_tip_account = frappe.get_cached_value("POS Config",self.pos_config,"default_tip_account" )
		if not self.default_tip_account:
			self.default_tip_account = frappe.get_cached_value("Business Branch",self.business_branch,"default_tip_account" )

def update_default_change_account(self):
	if self.changed_amount>0:
		if not self.default_change_account:
			self.default_change_account = frappe.get_cached_value("POS Config",self.pos_config,"default_change_account" )
		if not self.default_change_account:
			self.default_change_account = frappe.get_cached_value("Business Branch",self.business_branch,"default_change_account" )

def update_customer_bill_balance(customer):
	import time
	from pymysql.err import OperationalError
	is_system_customer = frappe.db.get_value('Customer', customer, 'is_system_customer')
	if is_system_customer == 0:
		sql = """UPDATE `tabCustomer` c
				LEFT JOIN (
					SELECT 
						SUM(balance) AS total_sale_balance
					FROM `tabSale`
					WHERE docstatus = 1 
					AND customer = %(customer)s
				) s ON 1=1
				SET c.balance = 
					COALESCE(s.total_sale_balance, 0)
					+ COALESCE(c.total_coupon_balance, 0)
					+ COALESCE(c.membership_balance, 0)
				WHERE c.name = %(customer)s and c.is_system_customer = 0"""
		max_retries=4
		for attempt in range(max_retries):
			try:
				frappe.db.sql(sql, {"customer": customer})
				frappe.db.commit()
				return 

			except OperationalError as e:
				if e.args[0] in (1213, 1205):
					frappe.db.rollback()
					if attempt < max_retries - 1:
						time.sleep(0.2 * (2 ** attempt))
						continue
					else:
						frappe.log_error(f"Deadlock after {max_retries} retries for {customer}","Customer Balance Update Deadlock")
						raise
				else:
					frappe.db.rollback()
					raise

@frappe.whitelist()
def change_table_number(data):
	sale = data['sale']
	default_customer = frappe.db.get_value("Tables Number",data['tbl_name'],'default_customer')
	
	if default_customer:
		customer_doc = frappe.get_doc("Customer",default_customer)
		frappe.db.set_value("Sale",sale,{
			'table_id':data['tbl_name'],
			'tbl_number':data['tbl_number'],
			'customer':default_customer,
			'customer_name':customer_doc.customer_name_en,
			'customer_photo':customer_doc.photo,
			'customer_group':customer_doc.customer_group
		})
	else:
		frappe.db.set_value("Sale",sale,{
			'table_id':data['tbl_name'],
			'tbl_number':data['tbl_number']
		})

def update_coupon_transaction(self):
	coupon_transactions = []
	for sp in self.sale_products:
		if sp.coupons:

			coupon = json.loads(sp.coupons)
			if coupon:
				for c in coupon:
					ct_doc = frappe.get_doc({
						"doctype": "Coupon Transaction",
						"reference_doctype":"Sale",
						"reference_name":self.name,
						"business_branch": self.business_branch,
						"pos_profile": self.pos_profile, 
						"pos_station":self.pos_station_name,
						"sale":self.name,
						"cashier_shift":self.cashier_shift,
						"working_day":self.working_day, 
						"coupon_number":c.get("coupon"),
						"coupon_code":c.get("name"),#this field is primary key of coupon code
						"posting_date":self.posting_date,
						"transaction_date":self.creation,
						"sale_product":sp.name,
						"product_code":sp.product_code,
						"transaction_type":self.sale_type,
						"input_actual_amount":sp.total_revenue/sp.quantity ,#sale product add input amount
						"actual_amount":sp.total_revenue/sp.quantity,
						"input_coupon_amount":sp.coupon_value,# no field in sale produdft yet
						"coupon_amount":sp.coupon_value,
						"currency":frappe.get_cached_value("ePOS Settings",None,"currency"), #no field in sale product yet
						"exchange_rate":1, #no field in sale product yet
						"status":"Active",
						"created_by": self.closed_by,
						"customer":self.customer,
						"customer_name":self.customer_name,
						"expired_date":sp.coupon_expired_date,
						"note":sp.note

					})
					if (self.sale_type =="Redeem"):
						ct_doc.input_actual_amount = ct_doc.input_actual_amount * -1
						ct_doc.actual_amount = ct_doc.actual_amount * -1

					ct_doc.insert(ignore_permissions=True,ignore_links=True)
					coupon_transactions.append({"name":ct_doc.name,"coupon_code":ct_doc.coupon_code, "coupon":ct_doc.coupon_number}) 

			
	if coupon_transactions and self.sale_type in ["Sale Coupon","Redeem","Top Up"]:
		update_coupon_codes(coupon_transactions,self.sale_type)
		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.update_coupon_codes", queue='short', coupon_transactions=coupon_transactions,sale_type=self.sale_type) 

def update_coupon_codes(coupon_transactions,sale_type):
	if sale_type=="Sale Coupon":
		sql ="""
			update `tabCoupon Codes` cc
			join `tabCoupon Transaction` ct on ct.coupon_number = cc.coupon 
				and ct.transaction_type = 'Sale Coupon'
			SET
				cc.coupon = ct.coupon_number,
				cc.coupon_status = "Used",
				cc.sale_date = ct.posting_date,
				cc.sale= ct.sale, 
				cc.working_day = ct.working_day,
				cc.cashier_shift = ct.cashier_shift,
				cc.pos_profile = ct.pos_profile,
				cc.pos_station = ct.pos_station,
				cc.price = ct.actual_amount,
				cc.coupon_value = ct.coupon_amount,
				cc.created_by = ct.created_by,
				cc.customer = ct.customer,
				cc.customer_name = ct.customer_name,
				cc.expired_date = ct.expired_date,
				cc.sale_creation = ct.creation

			where
				ct.name in %(coupon_transaction_names)s and 
				cc.name in %(coupon_codes)s 
				

		"""
		frappe.db.sql(sql,{
			"coupon_transaction_names":[d["name"] for d in coupon_transactions],
			"coupon_codes":[d["coupon_code"] for d in coupon_transactions]
			 
		})
	elif  sale_type=="Top Up":
		# frappe.throw(str([d["coupon_code"] for d in coupon_transactions]))
		sql ="""
			update `tabCoupon Codes` cc
			join (
				select 
					coupon_code ,
					sum(actual_amount) as  actual_amount,
					sum(coupon_amount) as coupon_amount
				from `tabCoupon Transaction` 
				where
					coupon_code in %(coupon_codes)s and 
					transaction_type = 'Top Up'
				group by 
					coupon_code
			) ct on ct.coupon_code = cc.name
			SET
				cc.top_up_amount = ct.actual_amount,
				cc.top_up_coupon_value = ct.coupon_amount
			where
				cc.name in %(coupon_codes)s """

		frappe.db.sql(sql,{
			"coupon_codes":[d["coupon_code"] for d in coupon_transactions]
		})

	elif sale_type=="Redeem":
		sql ="""
			update `tabCoupon Codes` cc
			join `tabCoupon Transaction` ct on ct.coupon_number = cc.coupon 
				and ct.transaction_type = 'Redeem'
			SET
				
				cc.redeem_amount = ct.actual_amount,
				cc.redeem_coupon_value = ct.coupon_amount,
				cc.coupon_status = 'Redeemed'

			where
				ct.name in %(coupon_transaction_names)s and 
				cc.name in %(coupon_codes)s 
				

		"""
		frappe.db.sql(sql,{
			"coupon_transaction_names":[d["name"] for d in coupon_transactions],
			"coupon_codes":[d["coupon_code"] for d in coupon_transactions]
			 
		})
	
	# update balance 
	frappe.db.sql("""
				update `tabCoupon Codes` 
			   set balance_amount = (price + top_up_amount + redeem_amount) -  use_amount,
			   balance_coupon_value = (coupon_value +top_up_coupon_value  + redeem_coupon_value) - (use_coupon_value)
			   where 
			   		name in %(names)s
			   
	""",{"names":[d["coupon_code"] for d in coupon_transactions]})

@frappe.whitelist(methods="POST")
def change_payment_type(data,old_data):
	if not data.get("note"):
		frappe.throw(_("Please enter note"))
	
	sql = """
		update `tabPOS Sale Payment`
		set
			payment_type = %(payment_type)s,
			payment_type_group = %(payment_type_group)s,
			input_amount = %(input_amount)s,
			amount = %(input_amount)s / %(exchange_rate)s,
			currency = %(currency)s,
			exchange_rate = %(exchange_rate)s,
			currency_symbol = %(currency_symbol)s,
			currency_precision = %(currency_precision)s,
			currency_format = %(currency_format)s,
			payment_type_group = %(payment_type_group)s,
			default_account = %(default_account)s
		where name=%(name)s
	"""
	sale_doc = frappe.get_cached_doc("Sale",data.get("parent"))

	business_branch =sale_doc.business_branch

	payment_type_doc = frappe.get_cached_doc("Payment Type",data.get("payment_type"))
	
	data["default_account"] = [d for d in payment_type_doc.default_account if d.business_branch == business_branch ][0].account
	frappe.db.sql(sql,data)


	# update data to sale payment
	sql = """
		update 
		`tabSale Payment`
		SET
			payment_type = %(payment_type)s,
			payment_type_group = %(payment_type_group)s,
			input_amount = %(input_amount)s,
			payment_amount = %(input_amount)s / %(exchange_rate)s,
			currency = %(currency)s,
			exchange_rate = %(exchange_rate)s,
			symbol = %(currency_symbol)s,
			currency_precision = %(currency_precision)s,
			payment_type_group = %(payment_type_group)s,
			account_paid_to = %(default_account)s
		where
			sale = %(parent)s and transaction_type = 'Payment' 

	"""
	frappe.db.sql(sql,data)

	# update gl
	sql = """
		update `tabGeneral Ledger`
			set 
				account = %(new_account)s,
				account_type = %(account_type)s
		where
			voucher_type = 'Sale' and 
			voucher_number = %(sale)s and 
			account = %(old_account)s
	"""
	frappe.db.sql(sql, {
		"new_account":data.get("default_account"),
		"account_type": frappe.get_cached_value("Chart Of Account",data.get("default_account"),"account_type"),
		"old_account":old_data.get("default_account"),
		"sale":data.get("parent"),
	})
	frappe.db.commit()
	sale_doc.add_comment("Comment", "បានផ្លាស់ប្តូរប្រភេទទូទាត់ប្រាក់ ពី <strong>{}</strong> ទៅ <strong>{}</strong>។ <br/>មូលហេតុ៖ {}".format(old_data.get("payment_type"),data.get("payment_type"),data.get("note"))) 
	frappe.msgprint(_("Change payment type successfully"))


# Update Customer Point When Pay with Point
def update_customer_point(customer,payment_type_group,payment_amount,name,sale,customer_name):
	point_setting = frappe.get_doc("Loyalty Point Settings")
	if point_setting.enabled==1:
		customer_doc = frappe.db.get_value('Customer', customer, ['allow_earn_point', 'total_point_earn'], as_dict=1)
		if customer_doc.allow_earn_point==1:
			if payment_type_group != 'Point':
				total_point_get = (point_setting.to_point_earning * (payment_amount))/point_setting.from_amount_earning
				add_point_history(sale,total_point_get,customer,customer_name,"Earning")
				frappe.db.sql("""Update `tabCustomer` set total_point_earn = total_point_earn + {0} where name = '{1}'""".format(total_point_get,customer))
				frappe.db.sql("""UPDATE `tabSale` set total_point_earn = {0} WHERE NAME = '{1}'""".format(total_point_get,sale))
				frappe.db.commit()
			# Customer Use Point
			if payment_type_group == "Point":
				customer_point = frappe.db.get_value("Customer",customer,['total_point_earn','allow_earn_point'],as_dict=1)
				total_point_redeem = (payment_amount * point_setting.to_point_redeeming) / point_setting.from_amount_redeeming
				add_point_history(sale,total_point_redeem,customer,customer_name,"Redeeming")
				if name:
					frappe.db.set_value('Sale Payment',name,{'spent_point': total_point_redeem})
				frappe.db.set_value('Sale',sale,{'total_point_spent': total_point_redeem})
				if float(customer_point.total_point_earn) < float(total_point_redeem):
					frappe.throw(_("Point for customer {} are not enough.".format(customer_name)))
				frappe.db.sql("Update `tabCustomer` set total_point_earn = round((total_point_earn - {}),6) where name = '{}'".format(total_point_redeem,customer))
				frappe.db.commit()

def update_customer_point_on_cancel_sale(sale,customer,customer_name):
	sale = frappe.db.sql("""SELECT sum(coalesce(total_point_earn, 0)) total_point_earn, sum(coalesce(total_point_spent, 0)) total_point_spent FROM `tabSale` WHERE name = '{0}' """.format(sale),as_dict=1)
	if sale:
		sale = sale[0]
		point_earn = sale["total_point_earn"]
		point_spent = sale["total_point_spent"]
		if (point_spent or 0) != 0:
			add_point_history(sale,point_spent,customer,customer_name,"Cancel Earning")
		if (point_earn or 0) != 0:
			add_point_history(sale,point_earn,customer,customer_name,"Cancel Redeeming")
		frappe.db.sql("""UPDATE `tabCustomer` c SET c.total_point_earn = c.total_point_earn + {0} - {1} WHERE NAME = '{2}'""".format((point_spent or 0),(point_earn or 0),customer))
		frappe.db.commit()

def add_point_history(sale,transaction_point,customer,customer_name,transaction_type="Earning"):
	from datetime import datetime
	point_setting = frappe.get_doc("Loyalty Point Settings")
	point_history = frappe.new_doc("Loyalty Point History")
	point_history.sale = sale
	point_history.customer = customer
	point_history.customer_name = customer_name
	point_history.posting_date = datetime.now().date()
	point_history.transaction_type = transaction_type
	point_history.previous_point = float(frappe.db.get_value("Customer",customer,'total_point_earn'))
	point_history.transaction_point = float(transaction_point) if transaction_type in ["Earning","Cancel Earning"] else float(transaction_point) * -1
	point_history.current_point = point_history.previous_point + point_history.transaction_point
	point_history.from_amount_earning = point_setting.from_amount_earning
	point_history.to_point_earning = point_setting.to_point_earning
	point_history.from_amount_redeeming = point_setting.from_amount_redeeming
	point_history.to_point_redeeming = point_setting.to_point_redeeming
	note = "" 
	if transaction_type == "Earning":
		note = "Earning {0} points from sale {1}".format(transaction_point,sale)
	elif transaction_type == "Cancel Earning":
		note = "Cancel sale {0} paid with {1} points".format(sale, transaction_point)
	elif transaction_type == "Cancel Redeeming":
		note = "Sale {0} Cancelled".format(sale)
	else:
		note = "Sale {0} Redeem {1} points".format(sale, transaction_point)
	point_history.note = note
	point_history.save()