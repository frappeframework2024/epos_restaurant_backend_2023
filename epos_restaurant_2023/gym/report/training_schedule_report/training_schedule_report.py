# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

	validate(filters)

	report_data = []
	skip_total_row=False
	message=None
	report_data = []  
 
	return get_columns(filters), report_data, message, None, None,skip_total_row


def validate(filters):
	if not filters.business_branch:
		filters.business_branch = frappe.db.get_list("Business Branch",pluck='name')

def get_columns(filters):
	columns = []
	# {"label":"Product Category", "fieldname":"product_category","fieldtype":"Data", "align":"left","sql":"sp.product_category"},
	# 	{"label":"Product Code", "fieldname":"product_code","fieldtype":"Link","options":"Product", "align":"left","sql":"sp.product_code"},
	# 	{"label":"Product Name", "fieldname":"product_name","fieldtype":"Data", "align":"center","sql":"sp.product_name"},
	# 	{"label":"Total Invoice", "fieldname":"total_invoice","fieldtype":"INT", "align":"center","sql":"COUNT(DISTINCT s.name) as total_invoice"},
	# 	{"label":"Total Quantity Sold", "fieldname":"total_quantity","fieldtype":"INT","options":"Sale", "align":"center","sql":"sum(sp.quantity) as total_quantity"},
	# 	{"label":"Total Amount", "fieldname":"total_amount","fieldtype":"Currency", "align":"right","sql":"sum(sp.total_revenue) as total_amount"}
	
	return columns