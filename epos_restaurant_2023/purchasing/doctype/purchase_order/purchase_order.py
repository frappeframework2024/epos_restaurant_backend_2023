# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt


from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion, update_product_quantity,get_stock_location_product
from epos_restaurant_2023.inventory.inventory import check_uom_conversion,calculate_average_cost,get_last_inventory_transaction,update_inventory_transaction_status
import frappe
from frappe import _
from frappe.utils import flt
from py_linq import Enumerable
from frappe.model.document import Document
from epos_restaurant_2023.purchasing.doctype.purchase_order.general_ledger_entry import submit_purchase_to_general_ledger_entry_on_submit,submit_purchase_to_general_ledger_entry_on_cancel
class PurchaseOrder(Document):
		
	def validate(self):
		validate_po_discount(self)

  
		#validate sale summary
		total_quantity = Enumerable(self.purchase_order_products).sum(lambda x: x.quantity or 0)
		sub_total = Enumerable(self.purchase_order_products).sum(lambda x: (x.quantity or 0)* (x.cost or  0))
		po_discountable_amount =Enumerable(self.purchase_order_products).where(lambda x:(x.discount_amount or 0)==0).sum(lambda x: (x.quantity or 0)* (x.cost or  0))

		self.total_quantity = total_quantity
		self.po_discountable_amount = po_discountable_amount
		self.sub_total = sub_total
		# calculate sale discount
		if self.discount:
			if self.discount_type =="Percent":
				self.po_discount = self.po_discountable_amount * self.discount / 100
			else:
				self.po_discount = self.discount or 0

		self.product_discount = Enumerable(self.purchase_order_products).sum(lambda x: x.discount_amount)
		self.total_discount = (self.product_discount or 0) + (self.po_discount or 0)
		self.grand_total =( sub_total - (self.total_discount or 0))
		self.balance = self.grand_total  - (self.total_paid or 0)
	
 
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			validate_account(self)
   
			


	def on_submit(self):
		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			submit_purchase_to_general_ledger_entry_on_submit(self)
		 
		if len(self.purchase_order_products)>=10:
			update_inventory_on_submit(self)
		else:
			frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_submit", queue='short', self=self)

		# update last purchase cost to product
		sql ="""
			update `tabProduct` p
			join `tabPurchase Order Products` pp 
			on 
				pp.product_code = p.name and 
				p.last_purchase_cost != pp.cost and 
				pp.parent = %(parent)s
			set 
				p.last_purchase_cost = pp.cost

		"""
		frappe.db.sql(sql,{"parent": self.name})

		

		
		

		
	def on_cancel(self):
		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			submit_purchase_to_general_ledger_entry_on_cancel(self)
		if len(self.purchase_order_products)>=10:
			update_inventory_on_cancel(self)
		else:
			frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_cancel", queue='short', self=self)


	def before_submit(self):
		for d in self.purchase_order_products:
			calculate_stock_adjustment_cost(self,d)
			if d.is_inventory_product:
				if d.base_unit != d.unit:
					if not check_uom_conversion(d.base_unit, d.unit):
						frappe.throw(_("There is no UoM conversion from {} to {}".format(d.base_unit, d.unit)))
		self.total_expense_cost = sum(a.expense_cost for a in self.purchase_order_products)

def calculate_stock_adjustment_cost(self,item):
	item.expense_cost = 0

	current_stock = frappe.db.sql("select cost,quantity from `tabStock Location Product` where stock_location='{}' and product_code='{}'".format(self.stock_location, item.product_code), as_dict=1)
	
	if current_stock:
		current_qty = float(current_stock[0]["quantity"])
		if current_qty < 0:
			current_cost = float(current_stock[0]["cost"])
			current_stock_cost = current_qty * current_cost

			new_qty = float(item.quantity)
			new_cost = float(item.cost)
			new_stock_cost = new_cost * new_qty

			item.expense_cost = current_stock_cost + new_stock_cost - ((current_qty + new_qty) * new_cost)

def update_inventory_on_submit(self):
	
	for p in self.purchase_order_products:
		if p.is_inventory_product:
			uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Purchase Order",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				"price":calculate_average_cost(p.product_code,self.stock_location,(p.quantity / uom_conversion),p.cost*uom_conversion),
				'note': 'New purchase order submitted.',
				"has_expired_date":p.has_expired_date,
				"expired_date":p.expired_date,
    			'action': 'Submit'
			})

 
			
def update_inventory_on_cancel(self):
	for p in self.purchase_order_products:
		if p.is_inventory_product:
			uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Purchase Order",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion,
				"price": get_last_inventory_transaction(p.product_code,self.stock_location,self.name),
				'note': 'Purchase order cancelled.',
				'action': 'Cancel'
			})
			update_inventory_transaction_status(self.name)
			
def validate_po_discount(self):
	po_discount = self.discount  
	if po_discount>0:
		if self.discount_type=="Amount":
			discountable_amount = Enumerable(self.purchase_order_products).where(lambda x: x.discount==0).sum(lambda x: (x.quantity or 0)* (x.cost or  0))
			po_discount=(po_discount / discountable_amount ) * 100
 
	for d in self.purchase_order_products:
		d.sub_total = (d.quantity or 0) * (d.cost or 0)
		if (d.discount_type or "Percent")=="Percent":
			d.discount_amount = (flt(d.sub_total) * flt(d.discount or 0)) / 100
		else:
			d.discount_amount = d.discount or 0
		# check if sale has discount
		if po_discount>0 and d.discount==0:
			
			d.po_discount_percent = po_discount  
			d.po_discount_amount = (po_discount/100) * d.sub_total
		else:
			d.po_discount_percent = 0  
			d.po_discount_amount = 0

		d.total_discount = (d.po_discount_amount or 0) + (d.discount_amount or 0)
		d.amount = (d.sub_total - d.discount_amount)

@frappe.whitelist()
def get_exchange_rate():    
    main_currency = frappe.db.get_single_value("ePOS Settings", "currency")
    exchange_rate_main_currency = frappe.db.get_single_value("ePOS Settings", "exchange_rate_main_currency")
    second_currency = frappe.db.get_single_value("ePOS Settings", "second_currency")
    if exchange_rate_main_currency == second_currency:
        second_currency  = main_currency    
    
    data = frappe.db.sql("select exchange_rate  from `tabCurrency Exchange` where from_currency='{}' and to_currency='{}' and docstatus=1 order by posting_date desc, modified desc limit 1".format(exchange_rate_main_currency, second_currency),as_dict=1)
    exchange_rate = 1

    if len(data):
        exchange_rate = data[0]["exchange_rate"]    
    return exchange_rate or 1



def validate_account(self):
	if not self.default_credit_account:
		self.default_credit_account = frappe.get_cached_value("Business Branch", self.business_branch, "default_credit_account")
	
	if not self.default_discount_account:
		self.default_discount_account = frappe.get_cached_value("Business Branch", self.business_branch, "default_purchase_discount_account")
 
	for p in self.purchase_order_products:
		if not p.default_account:
			if p.is_inventory_product:
				p.default_account = frappe.get_cached_value("Business Branch", self.business_branch,"default_inventory_account")
		if not p.default_expense_account:
			p.default_expense_account = get_expense_account(self.business_branch, p.product_code)

@frappe.whitelist(allow_guest=True) 
def get_expense_account(business_branch,product_code):
    doc = frappe.get_cached_doc("Product",product_code)
    account = None
    if doc.default_account:
        account = [d for d in doc.default_account if d.business_branch == business_branch]
        if account:
            account = account[0].default_expense_account
    
    if not account:
        account = frappe.get_cached_value("Business Branch", business_branch,"default_cost_of_good_sold_account")
        
    return account or ""
