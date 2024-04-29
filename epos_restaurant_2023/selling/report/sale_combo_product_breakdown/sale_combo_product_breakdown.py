# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import json


def execute(filters=None):
	columns, data = [], []
	return get_column(filters), get_data(filters)


def get_data(filters):
	sql = """
		select
			0 as indent,
			s.name,
			s.custom_bill_number bill_number,
			sp.product_code,
			sp.product_name,
			sp.price,
			sp.quantity,
			sp.combo_menu_data,
			sp.amount,
			sp.is_combo_menu,
			1 is_group
		from `tabSale Product` sp inner join `tabSale` s on s.name = sp.parent
		where sp.is_combo_menu = 1 and s.docstatus = 1
	"""
	if filters.start_date and filters.end_date : 
		sql = sql + " and s.posting_date between %(start_date)s and %(end_date)s"
	report_data = []

	data = frappe.db.sql(sql,filters,as_dict=1)
	for sale in data:
		report_data.append(sale)
		if sale.combo_menu_data:
			combo_menu_data = json.loads(sale.combo_menu_data)
			
			total_combo_amount = sum([d["price"] * d["quantity"] * sale.quantity for d in combo_menu_data] or 0)
			combo_price = sale.price - sum([ d["price"] * d['quantity'] for d in combo_menu_data] or 0)
			report_data.append({"indent":1,"name":sale.product_name,"bill_number":"","is_group":1,"quantity":sale.quantity,"price":combo_price,"amount":sale.amount - total_combo_amount})
			for combo_menu_item in combo_menu_data:
				report_data.append({"indent":2,"name":"","bill_number":combo_menu_item['product_code'] + "-" + combo_menu_item['product_name'],"quantity":sale.quantity * combo_menu_item['quantity'],"price":combo_menu_item['price'],"amount":combo_menu_item['price'] * combo_menu_item['quantity'] * sale.quantity})
	return report_data

def get_column(filters):
	columns=[]
	columns.append({"label":"Name","fieldname":"name","fieldtype":"Link","options":"Sale","align":"left",'width':180})
	columns.append({"label":"Bill Number","fieldname":"bill_number","fieldtype":"Data","align":"left",'width':200})
	columns.append({"label":"Quantity","fieldname":"quantity","fieldtype":"INT","align":"center",'width':60})
	columns.append({"label":"Price","fieldname":"price","fieldtype":"Currency","align":"center",'width':100})
	columns.append({"label":"Total Amount","fieldname":"amount","fieldtype":"Currency","align":"center",'width':100})
	return columns