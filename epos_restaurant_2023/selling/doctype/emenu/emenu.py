# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import json
import frappe
from py_linq import Enumerable
from frappe.website.website_generator import WebsiteGenerator

class eMenu(WebsiteGenerator):
	def get_context(self, context):
		 
		filter={}
		filter["pos_menu"] = [d.menu for d in self.pos_menu_selections]
		data = []
		if filter["pos_menu"]:
			sql ="""
				select 
					name,
					pos_menu,
					product_code,
					product_name_en,
					product_name_kh,
					price,
					ifnull(photo,'files/no_image.jpg') as photo,
					prices,
					discount_value,
					discount_type,
					is_empty_stock_warning,
					description
				from `tabTemp Product Menu`
				where pos_menu in %(pos_menu)s
				order by sort_order
			"""
			data = frappe.db.sql(sql,filter,as_dict=1)

			# Convert prices to JSON
			for item in data:
				item['prices'] = json.loads(item['prices'] or '[]')
 

		context.no_cache = not  (self.enable_cache or 0)
		context.products = data 
		popular_products = [] 
		for d in self.popular_product:
			d.prices = json.loads(d.prices or '[]') 
			popular_products.append(d)

		context.popular_products = popular_products

	def validate(self):
		for pop in  self.popular_product:		
			prices = []	
			pop.modifiers = []
			pop.prices = []
			if frappe.db.exists("Product", pop.product_code): 
				product = frappe.get_doc("Product",pop.product_code)
				if len(product.product_price)>0:
					for p in product.product_price:
						prices.append({
								"price":p.price,
								'branch':p.business_branch or "",
								'price_rule':p.price_rule, 
								'portion':p.portion,
								'unit':p.unit, 
								'price_rule' : p.price_rule,
								'default_discount':p.default_discount
							})
						
				pop.modifiers = json.dumps(get_product_modifier(product))
				pop.prices= json.dumps(prices)

				##  
				product_menu = [ m for m in product.pos_menus if m.root_menu ==  self.default_root_menu ] 
				if len(product_menu)>0:
					m = product_menu[0] 
					pop.is_empty_stock_warning = m.is_empty_stock_warning
					pop.discount_type = m.discount_type
					pop.discount_value = m.discount_value
				

def get_product_modifier(product):
	#get product modifier
	mc0 = []
	mc1 = Enumerable(product.product_modifiers).select(lambda x: x.modifier_category).distinct()
	mc2 = [] #global modifier category
	
	# #get global modifier category
	global_modifier_product_categorie = frappe.get_all('Modifier Group Product Category',
							filters=[['product_category','=',product.product_category]],
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
		for m in product.product_modifiers:
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

	return modifiers
			
		## end get modifier data
