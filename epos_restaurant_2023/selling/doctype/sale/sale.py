# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import json
from  epos_restaurant_2023.api.cache_function import get_default_account_from_pos_config, get_default_account_from_revenue_group, get_doctype_value_cache
from epos_restaurant_2023.api.account import cancel_general_ledger_entery,submit_general_ledger_entry
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, check_uom_conversion, get_product_cost, get_stock_location_product, get_uom_conversion, update_product_quantity
import frappe
from frappe import utils
from frappe import _
from frappe.utils.data import getdate,fmt_money
from py_linq import Enumerable
from frappe.model.document import Document
import datetime
from copy import deepcopy
from decimal import Decimal
from epos_restaurant_2023.api.exely import submit_order_to_exely
from epos_restaurant_2023.selling.doctype.sale.general_ledger_entry import submit_sale_to_general_ledger_entry
class Sale(Document):
	def validate(self):
		if not frappe.db.get_default('exchange_rate_main_currency'):
			frappe.throw('Main Exchange Currency not yet config. Please contact to system administrator for solve')
   
			#frappe.throw(_("Please select your working day"))
		if self.pos_profile:
			if not self.working_day:
				sql="select name from `tabWorking Day` where business_branch=%(business_branch)s and is_closed = 0 order by posting_date limit 1"
				data = frappe.db.sql(sql,{"business_branch":self.business_branch},as_dict=1)
				if len(data)>0:
					self.working_day = data[0]["name"]
				else:
					frappe.throw(_("Please start working day first"))

			if not self.cashier_shift: 
				sql="select name from `tabCashier Shift` where business_branch=%(business_branch)s and pos_profile=%(pos_profile)s and is_closed = 0 order by posting_date limit 1"
				data = frappe.db.sql(sql,{"business_branch":self.business_branch,"pos_profile":self.pos_profile},as_dict=1)
				if len(data)>0:
					self.cashier_shift= data[0]["name"]
				else:
					frappe.throw(_("Please start shift first"))
		
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
  
		validate_pos_payment(self)
		#validate sale summary

		#set is foc by check payment pyment if have is_foc payment type
		self.is_foc = 0

		## check table if have make foc to sale when discount 100%
		if self.table_id:
			_table = frappe.get_cached_doc("Tables Number",self.table_id)
			if _table.is_foc and self.discount==100 and self.discount_type =="Percent":
				self.is_foc = 1


		
		if Enumerable(self.payment).where(lambda x: (x.is_foc or 0) ==1).count()>=1:
			self.is_foc = 1

		total_quantity = Enumerable(self.sale_products).where(lambda x:(x.is_timer_product or 0) == 0).sum(lambda x: x.quantity or 0)
		sub_total = Enumerable(self.sale_products).sum(lambda x: (x.quantity or 0)* (x.price or  0) + ((x.quantity or 0)*(x.modifiers_price or 0)) )
  
		sale_discountable_amount =Enumerable(self.sale_products).where(lambda x:x.allow_discount ==1 and (x.discount_amount or 0)==0).sum(lambda x: (x.quantity or 0)* (x.price or  0) + + ((x.quantity or 0)*(x.modifiers_price or 0)))

		self.total_quantity = total_quantity
		self.sale_discountable_amount = sale_discountable_amount
		
		# calculate sale discount
		if self.discount:
			if self.discount_type =="Percent":
				self.sale_discount = self.sale_discountable_amount * self.discount / 100
			else:
				self.sale_discount = self.discount or 0
				if self.discount > self.sale_discountable_amount:
					frappe.throw("Discount amount cannot greater than discountable amount")
		
		self.product_discount = Enumerable(self.sale_products).where(lambda x:x.allow_discount ==1).sum(lambda x: x.discount_amount)		
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

		currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
		if currency_precision=='':
			currency_precision = "2"

		self.grand_total =( sub_total - (self.total_discount or 0))  + self.total_tax - total_rate_include_tax
	  
		self.total_paid =  Enumerable(self.payment).where(lambda x: x.payment_type_group !='On Account').sum(lambda x: x.amount or 0)
		self.total_paid = (self.total_paid or 0) + (self.deposit or 0)

		self.total_fee =  Enumerable(self.payment).sum(lambda x: x.fee_amount or 0)
		self.total_paid_with_fee = self.total_paid + (self.total_fee or 0)


		_balance = round(self.grand_total  , int(currency_precision)) -  round((self.total_paid or 0)  , int(currency_precision))

		_total_claim_coupon = 0
		if len(self.cash_coupon_items) and (self.total_cash_coupon_claim or 0) > 0:
			_total_claim_coupon = round((self.total_cash_coupon_claim or 0)  , int(currency_precision))
			if _total_claim_coupon > self.grand_total:
				frappe.throw("Your coupon claim and payment is over balance.")

			_balance -= _total_claim_coupon
		self.balance = _balance		

		if (self.sale_discount or 0) > 0:
			self.crypto_able_amount =  0	
		else:
			self.crypto_able_amount = Enumerable(self.sale_products).sum(lambda x: x.crypto_able_amount or 0)	

		# if self.pos_profile:
		self.changed_amount = (self.total_paid + _total_claim_coupon) - self.grand_total
		if round(self.changed_amount,int(currency_precision)) <= generate_decimal(int(currency_precision)):
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
		
		
		# update default accunt
		update_default_account(self)

	@frappe.whitelist()
	def get_sale_payment_naming_series(self):
		return frappe.get_meta("Sale Payment").get_field("naming_series").options
	
	def on_update(self): 
		if self.flags.ignore_on_update == True:
			return 
		#add sale product spa commission
		add_sale_product_spa_commission(self)

		#delete product that parent_sale_product not exists 
		frappe.db.sql("delete from `tabSale Product` where parent='{0}' and ifnull(reference_sale_product,'')!='' and  ifnull(reference_sale_product,'') not in (select name from `tabSale Product` where parent='{0}')".format(self.name))
		
		## update cash coupon information
		on_update_coupon_information(self)

		#update profit for commission
		total_cost = 0
		total_second_cost = 0
		for p in self.sale_products:
			total_cost += get_product_cost(self.stock_location, p.product_code) * p.quantity
			total_second_cost += (frappe.get_cached_value('Product',{'product_code':p.product_code}, 'secondary_cost')* p.quantity)
		self.sale_grand_total = self.grand_total
		self.sale_profit = self.grand_total - total_cost
		self.total_secondary_cost = total_second_cost
		self.second_sale_profit = self.grand_total - total_second_cost
		frappe.db.sql("update `tabSale` set total_cost = {0} , profit=grand_total - {0} , second_profit = grand_total - {1} where name='{2}'".format(total_cost,total_second_cost, self.name))
	# Generata Bill Number On Insert
	def before_insert(self):
		if self.pos_profile:
			pos_config_name = frappe.get_cached_value("POS Profile",self.pos_profile,"pos_config")
			pos_config = frappe.get_cached_value("POS Config",pos_config_name,["pos_bill_number_prefix","generate_bill_number_on_create"], as_dict=1)
			
			if pos_config.generate_bill_number_on_create == 1:
				if pos_config.pos_bill_number_prefix:
					from frappe.model.naming import make_autoname
					self.custom_bill_number = make_autoname(pos_config.pos_bill_number_prefix)
		else:
			if self.custom_bill_number_prefix:
				from frappe.model.naming import make_autoname
				self.custom_bill_number = make_autoname(self.custom_bill_number_prefix)

	def after_insert(self):
		if self.flags.ignore_after_insert == True:
			return 
		#add sale product spa commission
		if not self.time_in:
			pass	
		add_sale_product_spa_commission(self)

	def before_cancel(self):
		update_status(self)

	def before_submit(self):
		
		if self.flags.ignore_before_submit == True:
			return 
		on_get_revenue_account_code(self)

		self.append_quantity = None
		self.scan_barcode = None

		# generate custom bill format
		if not self.custom_bill_number:
				if self.pos_profile:
					pos_config = frappe.get_cached_value("POS Profile",self.pos_profile,"pos_config")
					bill_number_prefix = frappe.get_cached_value("POS Config",pos_config,"pos_bill_number_prefix")
					if bill_number_prefix:
						from frappe.model.naming import make_autoname
						self.custom_bill_number = make_autoname(bill_number_prefix)
				else:
					if self.custom_bill_number_prefix:
						from frappe.model.naming import make_autoname
						self.custom_bill_number = make_autoname(self.custom_bill_number_prefix)

		## end generate custom bill format
		for d in self.sale_products:
			if d.is_inventory_product:
				if d.unit !=d.base_unit:
					if not check_uom_conversion(d.base_unit, d.unit):
						frappe.throw(_("There is no UoM conversion for product {}-{} from {} to {}".format(d.product_code, d.product_name, d.base_unit, d.unit)))

		update_inventory_product_cost(self)
	
	def on_submit(self):
     
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

		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.create_folio_transaction_from_pos_trnasfer", queue='short', self=self)
		update_inventory_on_submit(self)
		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.update_inventory_on_submit", queue='short', self=self)

		# frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.add_payment_to_sale_payment", queue='short', self=self)

		update_customer_bill_balance(self)
		
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			submit_sale_to_general_ledger_entry(self)
			commission_general_ledger_entry(self)



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
		frappe.db.commit()

		update_customer_bill_balance(self)

		frappe.enqueue("epos_restaurant_2023.selling.doctype.sale.sale.update_inventory_on_cancel", queue='short', self=self)


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

def general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Sale",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Sale Commission",
		"is_cancelled":1 if self.docstatus == 2 else 0
	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)

def general_ledger_credit(self,account):
    docs = []
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":account["account"],
        "credit_amount":account["amount"],
        "voucher_type":"Sale",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Sale Commission",
		"party_type": "Employee",
		"party":account["party"],
		"is_cancelled":1 if self.docstatus == 2 else 0
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)

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
		self.status = status
    
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
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			cost = get_product_cost(self.stock_location, p.product_code)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Sale",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'portion':p.portion,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				'note': 'New sale submitted.',
    			'action': 'Submit'
			})
		else:
			doc = frappe.get_cached_doc("Product",p.product_code)
			#check if product has receipt and loop update from product receip

			update_product_recipe_to_inventory(self,doc, p.quantity, "Submit")		

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
							'stock_location':self.stock_location,
							'out_quantity':(p.quantity* d.quantity) / uom_conversion,
							"uom_conversion":uom_conversion,
							'note': 'Update Recipe Quantity from modifer ({}) after New sale submitted.'.format(m["modifier"]),
							'action': 'Submit'
						})

		
		#check if product is combo menu then get item from the combo menu item and update to inventory
		if p.is_combo_menu:
			update_combo_menu_to_inventory(self,p,"Submit")
		
		frappe.db.sql("update `tabSale Product` set cost = {} where name='{}'".format(cost, p.name))
   
	#update total cost to sale and profit to sale
	total_cost = 0
	cost_datas = frappe.db.sql("select sum(cost * quantity) from `tabSale Product` where parent='{}'".format(self.name))
	if cost_datas:
		total_cost = cost_datas[0][0]
  
	frappe.db.sql("update `tabSale` set total_cost = {0} , profit=grand_total - {0} where name='{1}'".format(total_cost, self.name))

def update_product_recipe_to_inventory(self,product,base_quantity,action):

	for d in product.product_recipe:
		if d.is_inventory_product:
			if not d.sale_type or d.sale_type == self.sale_type:
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
					'stock_location':self.stock_location,
					'in_quantity':(base_quantity* d.quantity) / uom_conversion if action=="Cancel" else 0,
					'out_quantity':(base_quantity* d.quantity) / uom_conversion if action=="Submit" else 0,
					"uom_conversion":uom_conversion,
					'note': note,
					'action': action
				})

def update_combo_menu_to_inventory(self, product,action):
	if product.is_combo_menu:
		combo_menu_data = json.loads(product.combo_menu_data)
		update_combo_menu_to_inventor_transaction(self,product,action, combo_menu_data)
			
def update_combo_menu_to_inventor_transaction(self,product,action,combo_menu_data):
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
				'stock_location':self.stock_location,
				"in_quantity": (p["quantity"] * product.quantity) / uom_conversion if action =="Cancel" else 0,
				'out_quantity': (p["quantity"] * product.quantity) / uom_conversion if action =="Submit" else 0,
				"uom_conversion":uom_conversion,
				'note': note,
				'action': action
			})
		else:
			#check if product have receipt then update to stock
			# base qty here is = sale product quantity * combo product quantity
			update_product_recipe_to_inventory(self,doc,product.quantity * p["quantity"], action)
					
def update_inventory_on_cancel(self):
	for p in self.sale_products:
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Sale",
				'transaction_number':self.name,
				'transaction_date':self.posting_date,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
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
						'stock_location':self.stock_location,
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
						'stock_location':self.stock_location,
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
						})
					doc.flags.ignore_post_general_ledger_entry = True
					doc.insert()
   
		if (self.changed_amount or 0)>0:
			pos_config = frappe.get_cached_value('POS Profile', self.pos_profile, 'pos_config')			
			payment_type = frappe.get_cached_value("ePOS Settings",None,"changed_payment_type")			
			pos_config_data = frappe.get_cached_doc('POS Config', pos_config)
			pos_config_payment_type = Enumerable(pos_config_data.payment_type).where(lambda x:x.payment_type==payment_type)
			account_code = "" 
			exchange_rate = 1
			if pos_config_payment_type:
				account_code = pos_config_payment_type[0].account_code
				exchange_rate = pos_config_payment_type[0].change_exchange_rate		

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
					"account_code":account_code
				})
			doc.flags.ignore_post_general_ledger_entry = True
			doc.insert()

def validate_sale_product(self):
	sale_discount = self.discount  
	if sale_discount>0:
		if self.discount_type=="Amount":
			discountable_amount = Enumerable(self.sale_products).where(lambda x: x.allow_discount==1 and x.discount==0).sum(lambda x: (x.quantity or 0)* (x.price or  0))
			if discountable_amount>0:
				sale_discount=(sale_discount / discountable_amount ) * 100
			sale_discount = sale_discount or 0
		
	for d in self.sale_products:
		d.regular_price = d.regular_price if d.regular_price else d.price
		# validate product free
		if(d.is_free and d.price > 0):
			frappe.throw(_("Cannot set price becouse this product is free"))
		
		d.sub_total = (d.quantity or 0) * (d.price or 0) + (d.quantity or 0) * (d.modifiers_price or 0)
		if (d.discount_type or "Percent")=="Percent":
			d.discount_amount = d.sub_total * (d.discount or 0) / 100
		else:
			d.discount_amount = d.discount or 0

		# check if sale has discount
		if sale_discount>0 and d.allow_discount and d.discount==0:
			
			d.sale_discount_percent = sale_discount  
			d.sale_discount_amount = (sale_discount/100) * d.sub_total
		else:
			d.sale_discount_percent = 0  
			d.sale_discount_amount = 0

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

def add_sale_product_spa_commission(self):	
	query = "delete from `tabSale Product SPA Commission` where sale = '{}'".format(self.name)			
	frappe.db.sql(query)
	for sp in self.sale_products:		 
		if sp.is_require_employee:
			if sp.employees: 
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

def validate_pos_payment(self):
	currency = frappe.db.get_default("currency")
	
	for d in self.payment:
		d.exchange_rate = d.exchange_rate if d.currency != currency else 1
		d.change_exchange_rate = d.change_exchange_rate if d.currency != currency else 1		
		d.amount = d.amount #(d.input_amount or 0 ) / (d.exchange_rate or 1)

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
			
			doc.selling_price = ((amount / doc.quantity) or 0) - (doc.modifiers_price or 0)


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
 
def update_default_income_account(self):
	# 1 get from product
	if [x for x in self.sale_products if not x.default_income_account]:
		# get product default account_code from product
		sql="select distinct parent as product_code, default_income_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.sale_products if not x.default_income_account], "business_branch":self.business_branch},as_dict=1)
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

	# 3 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_income_account]:
		revenue_group_account_codes = get_default_account_from_revenue_group(json.dumps( {"business_branch": self.business_branch, "revenue_groups": list(set([d.revenue_group for d in self.sale_products if not d.default_income_account]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_income_account and x.revenue_group in revenue_group_has_default_account]:
				sp.default_income_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_income_account"] 

	# 4 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_income_account]:
		for sp in [x for x in self.sale_products if not x.default_income_account]:
			sp.default_income_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_income_account")

 
def update_default_discount_account(self):
	# 1 get from product
	
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		# get product default account_code from product
		sql="select distinct parent as product_code, default_discount_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.sale_products if not x.default_discount_account and x.allow_discount==1], "business_branch":self.business_branch},as_dict=1)
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
	
	# 3 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		revenue_group_account_codes = get_default_account_from_revenue_group(json.dumps( {"business_branch": self.business_branch, "revenue_groups": list(set([d.revenue_group for d in self.sale_products if not d.default_discount_account and d.allow_discount==1 ]))}))
		revenue_group_has_default_account = [d["revenue_group"] for d in revenue_group_account_codes]
		for sp in [x for x in self.sale_products if not x.default_discount_account and x.revenue_group in revenue_group_has_default_account and x.allow_discount==1]:
				sp.default_discount_account = [d for d in revenue_group_account_codes if d["revenue_group"] == sp.revenue_group][0]["default_discount_account"] 

	# 4 get account code from revenue group 
	if [x for x in self.sale_products if not x.default_discount_account and x.allow_discount==1]:
		for sp in [x for x in self.sale_products if not x.default_discount_account and   x.allow_discount==1]:
			sp.default_discount_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_sale_discount_account")

def update_default_sale_cash_coupon_claim_account(self):
	
	if self.total_cash_coupon_claim > 0: 		
		if not self.default_cash_coupon_claim_account: 
			self.default_cash_coupon_claim_account = frappe.get_cached_value("Business Branch",self.business_branch,"default_sale_cash_coupon_claim_account" )
	


def update_default_payment_account(self):
    
	for p in [d for d in self.payment if not d.default_account]:
		 
		default_account = frappe.get_cached_value("Payment Type",p.payment_type, "default_account")
		if default_account:
			default_account = [d for d in default_account if d.business_branch == self.business_branch]
			if default_account:
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

        
def update_inventory_product_cost(self):
	sql = """
			select 
				product_code,
				cost 
			from `tabStock Location Product` 
			where
				stock_location = %(stock_location)s and 
				business_branch = %(business_branch)s and 
				product_code in %(product_codes)s
		
	"""
	is_inventory = 0
	for d in self.sale_products:
		if d.is_inventory_product == 1:
			is_inventory += 1
	if is_inventory>0:
		data = frappe.db.sql(sql, {"name":self.name, "stock_location":self.stock_location,"business_branch":self.business_branch, "product_codes":[d.product_code for d in self.sale_products if d.is_inventory_product==1]},as_dict=1)
		if data:
			for sp in [x for x in self.sale_products if x.is_inventory_product ==1]:
				cost_data = [d for d in data if d["product_code"]==sp.product_code]
				if cost_data:
					sp.cost =  cost_data[0]["cost"]
    
def update_customer_bill_balance(self):
	sql ="""update `tabCustomer` c 
			inner join (
						select 
							s.customer, 
							coalesce(sum(s.balance),0) as total_balance 
						from `tabSale` s
						where s.docstatus = 1 and s.customer = %(customer)s 
						group by s.customer) _s on _s.customer = c.name
				set c.balance = _s.total_balance + c.total_coupon_balance + c.membership_balance
			where c.name = %(customer)s"""
	frappe.db.sql(sql,{"customer":self.customer})

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