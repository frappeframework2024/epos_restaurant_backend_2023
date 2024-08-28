# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

from datetime import datetime
import json # from python std library
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import strip
from py_linq import Enumerable
from frappe.utils import add_years
from epos_restaurant_2023.api.account import submit_general_ledger_entry
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, check_uom_conversion, get_uom_conversion, update_product_quantity,get_stock_location_product
import itertools
from epos_restaurant_2023.inventory.doctype.product.utils import update_fetch_from_field

class Product(Document):
	def validate(self):
		gen_variant = self.generate_variants()
		self.product_variants = []
		for a in gen_variant:
			self.append("product_variants",a)
		if self.flags.ignore_validate==True:
			return 

		if self.is_combo_menu==1:
			self.is_recipe=0
			if self.is_inventory_product:
				self.is_inventory_product = 0
		validate_default_accounts(self)
		error_list=[]
		for v in self.product_variants:
			if v.variant_code is None or v.variant_code == "":
				error_list.append("""Row: {0} Product Code Can't Be Empty""".format(v.idx))
			# item = frappe.db.sql("select name from `tabProduct` where name = '{0}'".format(v.variant_code),as_dict=1)
			# if item : 
			# 	error_list.append("""Row: {0} Product Code {1} Already Exist""".format(v.idx,frappe.bold(v.variant_code)))
			# variant = frappe.db.sql("select name from `tabProduct Variants` where variant_code = '{0}' and name != '{1}'".format(v.variant_code,v.name),as_dict=1)
			# if variant : 
			# 	error_list.append("""Row: {0} Product Code {1} Already Exist""".format(v.idx,frappe.bold(v.variant_code)))
		if len(error_list) > 0:
				for msg in error_list:
					frappe.msgprint(msg)
				raise frappe.ValidationError(error_list)

		# lock uncheck inventory product
		if not self.is_new():
			old_product = frappe.get_doc('Product', self.product_code)
			has_inventory_transaction = frappe.db.exists("Inventory Transaction", {"product_code": self.name})
			if old_product.is_inventory_product and not self.is_inventory_product and has_inventory_transaction:
				frappe.throw(_("Cannot uncheck inventory product"))

			if old_product.unit != self.unit and has_inventory_transaction:
				frappe.throw(_("Cannot change unit"))
    
		if strip(self.naming_series) =="" and strip(self.product_code) =="":
			frappe.throw(_("Please enter product code"))
   
		if self.is_inventory_product == False and self.is_new():
			self.opening_quantity = 0
   
		elif self.is_inventory_product and self.opening_quantity > 0 and not self.stock_location and self.is_new():
			frappe.throw(_("Please select stock location"))
			

		if strip(self.product_name_kh)=="":
			self.product_name_kh = strip(self.product_name_en)

		#validate uom conversion product price
		if self.is_inventory_product:
			for d in self.product_price:
				if d.unit != self.unit:
					if not check_uom_conversion(d.unit, self.unit):
							frappe.throw(_("There is no UoM conversion  from {} to {}".format( d.unit, self.unit)))


		#validate uom product recipe
		for d in self.product_recipe:
			if d.unit != d.base_unit:
				if not check_uom_conversion(d.base_unit, d.unit):
						frappe.throw(_("There is no UoM conversion for product {}-{} from {} to {}".format(d.product, d.product_name, d.base_unit, d.unit)))


		self.total_recipe_quantity = Enumerable(self.product_recipe).sum(lambda x: x.quantity)

		#generate combo menu to json and update to combo menu data 
		if self.is_combo_menu and self.product_combo_menus and self.use_combo_group==0:
			combo_menus = []
			for m in self.product_combo_menus:
				if m.unit != m.base_unit:
					if not check_uom_conversion(m.base_unit, m.unit):
							frappe.throw(_("There is no UoM conversion for product {}-{} from {} to {}".format(m.product, m.product_name, m.base_unit, m.unit)))

				combo_menus.append({
					"menu_name":m.name,
					"product_code":m.product,
					"product_name":m.product_name,
					"unit":m.unit,
					"quantity":m.quantity,
					"price":m.price,
					"photo":m.photo
				})
    
			self.combo_menu_data = json.dumps(combo_menus)

		if self.is_combo_menu and self.combo_groups and self.use_combo_group==1:
			combo_groups = []
			for m in self.combo_groups:
				combo_groups.append({
					"combo_group":m.combo_group,
					"pos_title":m.pos_title,
					"item_selection":m.item_selection,
					"menus":json.loads(m.combo_menu_data),
				})
			
			self.combo_group_data = json.dumps(combo_groups)

		
		# price = get_product_price(product=self, business_branch="SR Branch",portion="Normal", price_rule="Normal Rate", unit="Box" )
		# if price:
		# 	frappe.msgprint(str(price["cost"]))

		#check if portion price exists 
		if	len(self.product_price) > 0:
			self.price = Enumerable(self.product_price).min(lambda x: x.price)
   
		if not self.last_purchase_cost or self.last_purchase_cost == 0:
			self.last_purchase_cost = self.cost
   
		


	def autoname(self):
		if self.flags.ignore_autoname==True:
			return 

		from frappe.model.naming import set_name_by_naming_series, get_default_naming_series,make_autoname

		if strip(self.naming_series) !="" and strip(self.product_code) =="":
			set_name_by_naming_series(self)
			self.product_code = self.name		

		self.product_code = strip(self.product_code)
		self.name = self.product_code
		 
  
	def after_insert(self):
		if self.flags.ignore_after_insert==True:
			return 

		if self.is_inventory_product:
			if self.opening_quantity and self.opening_quantity>0:
				add_to_inventory_transaction(
					{
						"doctype":"Inventory Transaction",
						"transaction_date":datetime.now(),
						'transaction_type':"Product",
						"transaction_number":self.name,
						"product_code":self.name,
						"stock_location":self.stock_location,
						"in_quantity":self.opening_quantity,
						"price":self.cost,
						"note":"Opening Quantity",
						"has_expired_date":self.has_expired_date,
						"expired_date":self.expired_date,
						'note': 'Opening Quantity',
					}
				)


	def before_save(self):
		if self.disabled == 1:
			self.status = "Disabled"
		else:
			if self.has_variants == 1:
				self.status = "Template"

		if len(self.product_variants)>0:
			for a in self.product_variants:
				variant = frappe.db.sql("select count(name) count from `tabProduct` where product_code = '{0}'".format(a.current_variant_code),as_dict=1)
				if len(variant)>0:
					if variant[0].count > 0:
						insert_update_rename_variant(self,a,"update")
						#frappe.enqueue(insert_update_rename_variant,queue="short",self=self,a=a,action="update")
					else:
						insert_update_rename_variant(self,a,"insert")
						#frappe.enqueue(insert_update_rename_variant,queue="short",self=self,a=a,action="insert")
			frappe.msgprint(_("Add New Or Update Variant Will Be In The Background, It Can Take A Few Minutes."), alert=True)


		if self.is_new and self.opening_quantity > 0:
			opening_general_ledger_entry(self)
		if self.flags.ignore_before_save==True:
			return 
		prices = []
		if self.product_price:
			
			for p in self.product_price:
				prices.append({
					"price":p.price,
					'branch':p.business_branch or "",
					'price_rule':p.price_rule, 
					'portion':p.portion,
					'unit':p.unit, 
					'price_rule' : p.price_rule,
					"default_discount":p.default_discount
				})
		self.prices = json.dumps(prices)	
	
	def on_update(self):
		#
		for a in self.pos_menus:
			a.sort_order = self.sort_order
		frappe.clear_document_cache("Product",self.name)
		frappe.cache.delete_value("product_variant_" + self.name)
   
		
		
		if self.flags.ignore_on_update==True:
			return 
		add_product_to_temp_menu(self)
		# frappe.enqueue("epos_restaurant_2023.inventory.doctype.product.product.add_product_to_temp_menu", queue='short', self=self)
		


	def on_trash(self):
		if self.flags.ignore_on_trash==True:
			return 
		frappe.db.sql("delete from `tabTemp Product Menu` where product_code='{}'".format(self.name))
	
	@frappe.whitelist()
	def get_product_summary_information(self):
		stock_information = []

		stock_data =frappe.db.get_list('Stock Location Product',
					filters={
						'product_code': self.name
					},
					fields=['name','stock_location', 'quantity','unit',"expired_date", "has_expired_date"],
				)

		if stock_data:
			for d in stock_data:
				expired_date = "" if not d.has_expired_date  or not d.expired_date else frappe.format(d.expired_date,{"fieldtype":"Date"})
				stock_information.append({"name":d.name, "stock_location": d.stock_location, "quantity":d.quantity,"unit":d.unit,"expired_date":expired_date})
	

		return {
			"total_annual_sale":get_product_annual_sale(self),
			"stock_information":stock_information,
			"precision": frappe.db.get_default("float_precision"),
			
		}
	@frappe.whitelist()
	def generate_roundup(self):
		ra = []
		data = list(range(0,60))
		for a in data:
			ra.append({"base_value":a,"roundup_value":a})

		return ra
		
	@frappe.whitelist()
	def generate_variants(self):
		if validate_variant_value_changed(self) > 0:
			stored_variant = []
			if self.product_variants:
				for a in self.product_variants:
					stored_variant.append({
						"variant_code": a.variant_code,
						"current_variant_code": a.current_variant_code,
						"variant_name": a.variant_name,
						"variant_1": a.variant_1,
						"variant_2": a.variant_2,
						"variant_3": a.variant_3,
						"opening_qty": a.opening_qty,
						"cost": a.cost,
						"price": a.price
					})

			if not self.product_code:
				frappe.throw(_("Please enter product code first"))
			error = ""
			variant_1 = []
			variant_2 = []
			variant_3 = []

			values = []
			check_variant_1 =  [d.variant_value for d in self.variant_1_value]
			for a in check_variant_1:
				if a not in values:
					variant_1.append(a)
					values.append(a)
				else:
					error += ("Variant 1 Value {} Already Exist</br>".format(a))

			values = []
			check_variant_2 =  [d.variant_value for d in self.variant_2_value]
			for a in check_variant_2:
				if a not in values:
					variant_2.append(a)
					values.append(a)
				else:
					error += ("Variant 2 Value {} Already Exist</br>".format(a))

			values = []
			check_variant_3 =  [d.variant_value for d in self.variant_3_value]
			for a in check_variant_3:
				if a not in values:
					variant_3.append(a)
					values.append(a)
				else:
					error += ("Variant 3 Value {} Already Exist</br>".format(a))
			if error:
				frappe.throw(str(error))
			product_variants = []
			if variant_1 and not variant_2 and not variant_3:
				for v1 in variant_1:
					product_variants.append({
						"variant_code": "{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix")),
						"current_variant_code": "{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix")),
						"variant_name": "{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix")),
						"variant_1":v1,
						"opening_qty":0,
						"cost": self.cost,
						"price":self.price
					})
			elif variant_1 and  variant_2 and not variant_3:
				for v1, v2 in itertools.product(variant_1, variant_2):
					product_variants.append({
						"variant_code": "{}-{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix"),frappe.get_cached_value("Variant Code", v2,"code_prefix")),
						"current_variant_code": "{}-{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix"),frappe.get_cached_value("Variant Code", v2,"code_prefix")),
						"variant_name":"{}-{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix"),frappe.get_cached_value("Variant Code", v2,"code_prefix")),
						"variant_1":v1,
						"variant_2":v2,
						"opening_qty":0,
						"cost": self.cost,
						"price":self.price
					})
			else:
				for v1, v2,v3   in itertools.product(variant_1, variant_2, variant_3):
					product_variants.append({
						"variant_code": "{}-{}-{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix"),frappe.get_cached_value("Variant Code", v2,"code_prefix"),frappe.get_cached_value("Variant Code", v3,"code_prefix")),
						"current_variant_code": "{}-{}-{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix"),frappe.get_cached_value("Variant Code", v2,"code_prefix"),frappe.get_cached_value("Variant Code", v3,"code_prefix")),
						"variant_name": "{}-{}-{}-{}".format(self.name,frappe.get_cached_value("Variant Code", v1,"code_prefix"),frappe.get_cached_value("Variant Code", v2,"code_prefix"),frappe.get_cached_value("Variant Code", v3,"code_prefix")),
						"variant_1":v1,
						"variant_2":v2,
						"variant_3": v3,
						"opening_qty":0,
						"cost": self.cost,
						"price":self.price
					})
			for a in product_variants:
				for b in stored_variant:
					if b["variant_code"] == a["variant_code"]:
						a["opening_qty"] = b["opening_qty"]
						a["cost"] = b["cost"]
						a["price"] = b["price"]
			return product_variants
		else:
			return self.product_variants

def validate_variant_value_changed(self):
	changes = 0
	if (self.is_new() or 0) == 0:
		og_doc = frappe.get_doc('Product', self.name)
		og_variant_1_value = [item.variant_value for item in og_doc.get('variant_1_value')]
		og_variant_2_value = [item.variant_value for item in og_doc.get('variant_2_value')]
		og_variant_3_value = [item.variant_value for item in og_doc.get('variant_3_value')]
		og_product_variant = [item.variant_code for item in og_doc.get('product_variants')]
		new_variant_1_value = [item.variant_value for item in self.get('variant_1_value')]
		new_variant_2_value = [item.variant_value for item in self.get('variant_2_value')]
		new_variant_3_value = [item.variant_value for item in self.get('variant_3_value')]
		new_product_variants = [item.variant_code for item in self.get('product_variants')]
		if og_variant_1_value != new_variant_1_value:
			changes += 1
		if og_variant_2_value != new_variant_2_value:
			changes += 1
		if og_variant_3_value != new_variant_3_value:
			changes += 1
		if og_product_variant != new_product_variants:
			changes += 1
	return changes

def disable_variant(self):
	str_variant = []
	variants = frappe.db.sql("select name from `tabProduct` where variant_of = '{}'".format(self.name),as_dict=1)
	for a in self.product_variants:
		str_variant.append(a.variant_code)
	for a in variants:
		if a.name not in str_variant:
			transactions = frappe.db.sql("select count(name) count from `tabInventory Transaction` where product_code = '{}'".format(a.name),as_dict=1)
			if len(transactions)>0:
				if transactions[0].count>0:
					frappe.db.set_value('Product', a.name, {
						'status': 'Disabled',
						'disabled': 1,
						})
				else:
					frappe.delete_doc('Product', a.name)

def insert_update_rename_variant(self,a,action):
	disable_variant(self)
	if action == "update":
		name = a.current_variant_code
		if a.current_variant_code != a.variant_code:
			frappe.rename_doc('Product', a.current_variant_code, a.variant_code)
			name = a.variant_code
			a.current_variant_code = name
		p = frappe.get_doc("Product",name)
		p.revenue_group = self.revenue_group
		p.product_name_en = a.variant_name
		p.product_category = self.product_category
		p.revenue_group = self.revenue_group
		p.unit = self.unit
		p.cost = (self.cost if a.cost == 0 else a.cost)
		p.price = (self.price if a.price == 0 else a.price)
		p.status = "Variant"
		p.variant_of = self.name
		p.is_variant = 1
		p.variant_1 = a.variant_1
		p.variant_2 = a.variant_2
		p.variant_3 = a.variant_3
		p.disabled = 0
		p.save()
	else:
		p = frappe.new_doc("Product")
		p.is_inventory = 1
		p.opening_quantity = a.opening_qty
		p.revenue_group = self.revenue_group
		p.product_code = a.variant_code
		p.product_name_en = a.variant_name
		p.product_category = self.product_category
		p.revenue_group = self.revenue_group
		p.unit = self.unit
		p.cost = (self.cost if a.cost == 0 else a.cost)
		p.price = (self.price if a.price == 0 else a.price)
		p.status = "Variant"
		p.variant_of = self.name
		p.is_variant = 1
		p.variant_1 = a.variant_1
		p.variant_2 = a.variant_2
		p.variant_3 = a.variant_3
		p.insert()
	

def validate_default_accounts(self):
	branches = {row.business_branch for row in self.default_account}

	if len(branches) != len(self.default_account):
		frappe.throw(_("Cannot set multiple default account for one branch."))

@frappe.whitelist()
def get_product(barcode,business_branch=None,stock_location = None,price_rule=None, unit=None,portion = None,allow_sale=None,allow_purchase=None,is_inventory_product=None):
	try:
		frappe.flags.mute_messages = True
		filters = {"product_code":barcode,"disabled":0}
		if is_inventory_product == 1:
			filters["is_inventory_product"] = 1
		p = frappe.get_cached_doc("Product",filters,["*"])
		
		if allow_sale and not p.allow_sale:
			return {
				"status":404,
				"message":_("This product is not allow to sale")
			}
		
		if allow_purchase and not p.allow_purchase:
			return {
				"status":404,
				"message":_("This product is not allow to purchase")
			}
  
		if p :
			price = get_product_price(product=p,business_branch=business_branch, price_rule=price_rule,unit=unit or p.unit ,portion=portion  )
			tax_rule = None
			if p.tax_rule:
				tax_rule = frappe.get_doc("Tax Rule", p.tax_rule, cache = True)
			
			data = {
				"status":0,#success
				"product_code": p.product_code,
				"product_name_en":p.product_name_en,
				"unit":p.unit,
				"cost":price["cost"],
				"last_purchase_cost":p.last_purchase_cost,
				"price":price["price"],
				"allow_discount":p.allow_discount,
				"allow_free":p.allow_free,
				"allow_change_price":p.allow_change_price,
				"is_inventory_product":p.is_inventory_product,
				"tax_rule":p.tax_rule,
				"tax_rule_doc":tax_rule,
				"has_expired_date":p.has_expired_date

			}
			if p.has_expired_date and p.is_inventory_product and stock_location:
				data["expired_date"] = get_product_expired_date(p.name,stock_location)
				
			return data
		else:
			return {
				"status":404,
				"message":_("Product code {} is not exist".format(barcode))
			}
	except frappe.DoesNotExistError:
		return {
				"status":404,
				"message":_("Product code {} is not exist".format(barcode))
			}
		
	finally:
		frappe.flags.mute_messages = False

def get_product_expired_date(product_code, stock_location):
    sql = ("select min(expired_date) as expired_date from `tabStock Location Product` where product_code=%(product_code)s and stock_location=%(stock_location)s")
    data = frappe.db.sql(sql, {"stock_location":stock_location, "product_code":product_code},as_dict=1)
    return data[0]["expired_date"]
    
@frappe.whitelist()
def get_product_price(product=None,barcode=None,unit=None, business_branch=None,price_rule=None,portion=None):
	uom_conversion = 1
	if unit and product:
		if unit != product.unit:
			uom_conversion = get_uom_conversion(product.unit, unit)
	price = 0
	cost = 0
	if product:
		price = (product.price or 0) / uom_conversion
		cost = (product.cost or 0) / uom_conversion
		if product.product_price:
			data = Enumerable(product.product_price).where(lambda x: x.business_branch==(business_branch or x.business_branch) and x.price_rule==(price_rule or x.price_rule) and x.portion == (portion or x.portion) and x.unit == (unit or x.unit) )
			if data:
				if data[0]:
					price= data[0].price or 0
					cost= data[0].cost or 0
	else:
		p = frappe.get_doc("Product",{"product_code":barcode,"disabled":0},["*"])
		return get_product_price (product=p, unit=unit, business_branch=business_branch,portion=portion,price_rule=price_rule)
  
	return {"price":price,"cost":cost}


def get_product_annual_sale(self):
	year = datetime.now().strftime('%Y')

	#get branch for permission amount
	sql = "select sum(a.amount) from `tabSale Product` a inner join `tabSale` b on a.parent = b.name where year(b.posting_date) = {} and a.product_code = '{}'".format(year, self.name)
	data = frappe.db.sql(sql)
	if data:
		return data[0][0]
	return 0
@frappe.whitelist()
def get_product_cost_by_stock(product_code=None, stock_location=None):
	result = frappe.db.sql("select cost from `tabStock Location Product` where stock_location='{}' and product_code='{}'".format(stock_location, product_code), as_dict=1)
	last_cost = frappe.get_cached_value("Product",product_code, "last_purchase_cost")
	if result:
		result[0]["last_purchase_cost"] = last_cost
		return result[0]
	return {'cost':0,"last_purchase_cost":last_cost}

@frappe.whitelist()
def get_stock_location_product_info(product_code=None, stock_location=None):
	result = frappe.db.sql("select cost,expired_date from `tabStock Location Product` where stock_location='{}' and product_code='{}'".format(stock_location, product_code), as_dict=1)
	if result:
		return result[0]
	return {'cost':0}

def add_product_to_temp_menu(self):
	frappe.db.sql("delete from `tabTemp Product Menu` where product_code='{}'".format(self.name))
	if self.pos_menus and not self.disabled and self.allow_sale:
		printers = []
		for p in self.printers:
			printers.append({
					"printer":p.printer_name,
					"group_item_type":p.group_item_type,
					"ip_address":p.ip_address,
					"port":int(p.port or 0),
					"is_label_printer":p.is_label_printer,
					"usb_printing":p.usb_printing,
				})
	
		prices = []
		for p in self.product_price:
			prices.append({

					"price":p.price,
					'branch':p.business_branch or "",
					'price_rule':p.price_rule, 
					'portion':p.portion,
					  'unit':p.unit, 
					  'price_rule' : p.price_rule,
					  'default_discount':p.default_discount
					})
			
		#get product modifier
		mc0 = []
		mc1 = Enumerable(self.product_modifiers).select(lambda x: x.modifier_category).distinct()
		mc2 = [] #global modifier category



		# #get global modifier category
		global_modifier_product_categorie = frappe.get_all('Modifier Group Product Category',
								filters=[['product_category','=',self.product_category]],
								fields=['parent','name'],
								limit=200
							 )
		global_modifiers = []
		for gmpc in global_modifier_product_categorie:
			gmodifiers = frappe.get_doc('Modifier Group',gmpc.parent)
			for g in gmodifiers.modifiers:
				global_modifiers.append(g)
		
		if global_modifiers != []:
			mc2 = Enumerable(global_modifiers).select(lambda x: x.modifier_category).distinct()
		
		for mc in mc1:
			mc0.append(mc)
		for mc in mc2:
			mc0.append(mc)

		
		modifier_categories = Enumerable(mc0).select(lambda x: x).distinct()	
		modifiers = []


		## get modifier data
		for mc in modifier_categories:
			doc_category = frappe.get_doc("Modifier Category",mc)
			modifier_items = []	
			items = []			
			#global modifier group
			for m in global_modifiers:
				if m.modifier_category == mc:
					items.append({
						"name":m.name,
						"branch":m.business_branch or "" , 
						"prefix":m.prefix, 
						"modifier":m.modifier_code, 
						"value": str(m.business_branch or "") + str(m.prefix) + ''+str( m.modifier_code), 
						"price":m.price 
						})	
			
			#product modifier
			for m in self.product_modifiers:
				if m.modifier_category == mc:							
					items.append({
						"name":m.name,
						"branch":m.business_branch or "" , 
						"prefix":m.prefix, 
						"modifier":m.modifier_code, 
						"value":  str(m.business_branch or "") + str(m.prefix) + ''+str( m.modifier_code), 
						"price":m.price 
					})
			
			for i in items:	
				modifier_items.append({
					"name":i['name'],
					"branch":i['branch'], 
					"prefix":i['prefix'], 
					"modifier":i['modifier'], 
					"price": i['price'] 
				})

			modifiers.append({
				"category":mc,
				"is_required":doc_category.is_required,
				"is_multiple":doc_category.is_multiple,
				"items":modifier_items
			})
			
		## end get modifier data  



		for m in self.pos_menus:	 
			pos_menu = m.pos_menu
			pos_menu_paths = []
			while pos_menu:
				pos_menu_paths.insert(0,pos_menu)
				pos_menu = frappe.db.get_value('POS Menu', pos_menu, 'parent_pos_menu')  
			m.root_menu = pos_menu_paths[0]
			
			frappe.db.sql("update `tabProduct Menu` set root_menu='{}' where name='{}'".format(pos_menu_paths[0],m.name))  
			doc = frappe.get_doc({
							"pos_menu_id":m.name,
							'doctype': 'Temp Product Menu',
							'product_code': self.name,
							'pos_menu':m.pos_menu,
							'printers':json.dumps(printers),
							'prices':json.dumps(prices),
							'revenue_group':self.revenue_group,
							'modifiers':json.dumps(modifiers),
							'is_empty_stock_warning':m.is_empty_stock_warning,
							'discount_type': m.discount_type,
							'discount_value':m.discount_value,
							'sort_order':m.sort_order,
							'pos_note':self.pos_note
						})
			doc.insert() 


		## update to popular product in emenu
		sql_pop = """select name, parent from `tabeMenu Popular Products` where product_code = '{}'""".format(self.name)
		pop_docs = frappe.db.sql(sql_pop,as_dict=1)
		for pop in pop_docs:
			emenu = frappe.get_doc("eMenu",pop["parent"])	
			frappe.db.set_value('eMenu Popular Products', pop["name"], {
				'prices': json.dumps(prices),
				'modifiers': json.dumps(modifiers),				
			})

			product_menu = [ m for m in self.pos_menus if m.root_menu ==  emenu.default_root_menu ] 
			if len(product_menu)>0:
				m = product_menu[0] 
				frappe.db.set_value('eMenu Popular Products', pop["name"], {
					'is_empty_stock_warning': m.is_empty_stock_warning,
					'discount_type': m.discount_type,	
					'discount_value':m.discount_value		
				})				

		frappe.db.commit()


	update_fetch_from_field(self)

   
@frappe.whitelist()
def update_product_to_temp_product_menu():
	products = frappe.db.sql("select name from `tabProduct`", as_dict=1)
	for pro in products:
		doc = frappe.get_doc("Product", pro.name)
		
		add_product_to_temp_menu(doc)
	frappe.db.commit()
	return "Done"



@frappe.whitelist()
def assign_menu(products,menu):
	pos_menu_doc = frappe.get_doc("POS Menu",menu)
	for p in products.split(","):
		product = frappe.get_doc("Product",p)	 
		if len(product.pos_menus) ==0:
			# Create a new child document
			child_doc = frappe.new_doc("Product Menu")
			child_doc.pos_menu =menu 
			child_doc.pos_menu_name_kh= pos_menu_doc.pos_menu_name_kh
			# Add the child document to the parent document
			product.append("pos_menus", child_doc)
		else:
			result = [d for d in product.pos_menus if d.pos_menu== menu]
			
			if not result:				
				child_doc = frappe.new_doc("Product Menu")
				child_doc.pos_menu =menu 
				child_doc.pos_menu_name_kh= pos_menu_doc.pos_menu_name_kh
				# Add the child document to the parent document
				product.append("pos_menus", child_doc)	
		product.save()

	frappe.db.commit()

@frappe.whitelist()
def assign_printer(products,printer):
 
	printer_doc = frappe.get_doc("Printer",printer)
	for p in products.split(","):
		product = frappe.get_doc("Product",p)
	 
		if len(product.printers) ==0:
			# Create a new child document
			child_doc = frappe.new_doc("Product Printer")
			child_doc.printer =printer 
			child_doc.printer_name= printer_doc.printer_name
			# Add the child document to the parent document
			product.append("printers", child_doc)
		else:
			result = [d for d in product.printers if d.printer== printer]
			
			if not result:
				
				child_doc = frappe.new_doc("Product Printer")
				child_doc.printer =printer 
				child_doc.printer_name= printer_doc.printer_name
				# Add the child document to the parent document
				product.append("printers", child_doc)

			 
			 
		product.save()

	frappe.db.commit()

	#frappe.throw("u run assign pritner")

@frappe.whitelist()
def remove_printer(products,printer):
	for p in products.split(","):
		product = frappe.get_doc("Product",p)
		printers = product.get('printers')
		for row in printers:
			if row.printer == printer:
				printers.remove(row)
		product.save()

	frappe.db.commit()


@frappe.whitelist()
def clear_all_printer_from_product(products):
	for p in products.split(","):
		product = frappe.get_doc("Product",p)
		product.printers = []
		product.save()

	frappe.db.commit()

@frappe.whitelist()
def clear_all_menus_from_product(products):
	for p in products.split(","):
		product = frappe.get_doc("Product",p)
		product.pos_menus = []
		product.save()

	frappe.db.commit()


@frappe.whitelist()
def update_expire_date(data):
	data = json.loads(data)
	for d in data["stock_location_product"]:
		if "new_expired_date" in d and   d["new_expired_date"]:
			frappe.db.set_value("Stock Location Product",d["name"], "expired_date", d["new_expired_date"])
	frappe.db.commit()
	frappe.msgprint("Update expire date successfully")
 
def opening_general_ledger_entry(self):
	branch =  frappe.db.get_value('Stock Location',self.stock_location, 'business_branch')
	accounts =  frappe.db.get_value('Business Branch',branch, ['default_temporary_opening_account','default_inventory_account'], as_dict=1)
	docs = []
	doc = {
        "doctype":"General Ledger",
        "posting_date": datetime.today().strftime('%Y-%m-%d'),
        "account":accounts.default_inventory_account,
        "debit_amount":self.opening_quantity * self.cost,
        "voucher_type":"Item",
        "voucher_number":self.name,
        "business_branch": branch,
    }
	doc["remark"] = "Opening Stock On Product {0}\nAgainst Account {1}.".format(self.name,accounts.default_temporary_opening_account)
	docs.append(doc)
        
	doc = {
        "doctype":"General Ledger",
        "posting_date":datetime.today().strftime('%Y-%m-%d'),
        "account":accounts.default_temporary_opening_account,
        "credit_amount":self.opening_quantity * self.cost,
        "voucher_type":"Item",
        "voucher_number":self.name,
        "business_branch": branch,

    }
	doc["remark"] = "Opening Stock On Product {0}.\nAgainst Account {1}.".format(self.name,accounts.default_inventory_account)
	docs.append(doc)
	submit_general_ledger_entry(docs=docs)