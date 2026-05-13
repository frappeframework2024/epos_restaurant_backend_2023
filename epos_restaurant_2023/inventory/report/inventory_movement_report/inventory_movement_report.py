# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import json
import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
from datetime import datetime, date 

def execute(filters=None):
 

	if filters.filter_based_on =="Fiscal Year":
		# if not filters.from_fiscal_year:
			filters.from_fiscal_year = datetime.today().year
			
			filters.start_date = '{}-01-01'.format(filters.from_fiscal_year)
			filters.end_date = '{}-12-31'.format(filters.from_fiscal_year) 


	elif filters.filter_based_on =="This Month": 
		filters.start_date = str(date.today().replace(day=1))
		filters.end_date =add_days(  add_months(filters.start_date ,1),-1)
	
	 
	validate(filters)


	report_data = []
	skip_total_row=False
	message=None
	report_fields =  []

	if filters.get("parent_row_group"):
		report_data = get_report_group_data(filters,report_fields)
		message="Enable <strong>Parent Row Group</strong> making report loading slower. Please try  to select some report filter to reduce record from database "
		skip_total_row = True
	else:
		report_data = get_report_data(filters,report_fields =report_fields) 
	report_chart = None
 
	return get_columns(filters,report_fields=report_fields), report_data, message, report_chart, [],skip_total_row
 



## on validate filter
def validate(filters):
	if not filters.business_branch:
		filters.business_branch = frappe.db.get_list("Business Branch",pluck='name')  
	
	if not filters.stock_location:
		filters.stock_location = frappe.db.get_list("Stock Location",pluck='name')

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:

			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))

	
	if filters.column_group=="Daily":
		n = date_diff(filters.end_date, filters.start_date)
		if n>31:
			frappe.throw("Date range cannot greater than 30 days")

	if filters.row_group and filters.parent_row_group:
		if(filters.row_group == filters.parent_row_group):
			frappe.throw("Parent row group and row group can not be the same")


## on get columns report
def get_columns(filters,report_fields):
	columns = []
	_row_group = [d for d in get_row_groups() if d["label"] ==filters.row_group ][0]["fieldname"]
	
	# frappe.throw(str(_row_group)) 

	## append columns
	if filters.row_group == "Product":
		columns.append({"label":"Code","short_label":"Code", "fieldname":"product_code","fieldtype":"Link","options":"Product","indicator":"Grey",'width':120, "align":"left","chart_color":"#FF8A65"})

	columns.append({'fieldname':_row_group,'label':filters.row_group,'fieldtype':'Data','align':'left','width':250})

	## generate dynamic columns
	if filters.row_group not in ["Date","Month","Year"]:
		for c in get_dynamic_columns(filters):
			columns.append(c) 

	# for g in report_fields:
	# 	if g.fieldtype=='Link' and g.link_field_doctype:
	# 		columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":"Link","options":g.link_field_doctype,"precision":g.report_precision,"align": g.align })
	# 	else:
		# columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"precision":g.report_precision,"align": g.align })
	
	columns.append({"fieldname":"purchase_order","label":_("PO"),"width":100,"fieldtype":"Float","precision":4,"align": "right" })
	columns.append({"fieldname":"sale","label":_("Sale"),"width":100,"fieldtype":"Float","precision":4,"align": "right" })
	columns.append({"fieldname":"other_in","label":_("Other In"),"width":100,"fieldtype":"Float","precision":4,"align": "right" })
	columns.append({"fieldname":"other_out","label":_("Other Out"),"width":100,"fieldtype":"Float","precision":4,"align": "right" })
   
	columns.append({"label":_("Balance"),"short_label":_("Balance"), "fieldname":"balance","fieldtype":"Float","indicator":"Grey","precision":4, "align":"right","chart_color":"#FF8A65"})
	return columns



## on get row group
def get_row_groups():
	return [
		{
			"fieldname":"product_name",
			"label":"Product"
		},
		{
			"fieldname":"product_category",
			"label":"Product Category",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"product_group",
			"label":"Product Group",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"business_branch",
			"label":"Business Branch",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"stock_location",
			"label":"Stock Location",
			"parent_row_group_filter_field":"row_group"
		}
	]


## on get dynamic columns
def get_dynamic_columns(filters):
	#static report field
	report_fields = get_report_field(filters)
	columns=[]
	for rf in report_fields:
		columns.append({
			'fieldname': rf["fieldname"],
			'label': rf["short_label"],
			'fieldtype':rf["fieldtype"],
			'precision': rf["precision"]or 0,
			'align':rf["align"]}
		)
		

	return columns


## on get report field
def get_report_field(filters): 
	fields = []

	if filters.row_group != "Product" and filters.row_group != "Product Category" and filters.row_group != "Product Group" and filters.row_group != "Stock Location" and filters.row_group != "Business Branch":
		fields.append({"label":"Product","short_label":"Product", "fieldname":"product_name","fieldtype":"Data","indicator":"Grey", "align":"left","chart_color":"#FF8A65"})

	if filters.row_group != "Product Category" and filters.row_group != "Product Group" and filters.row_group != "Stock Location" and filters.row_group != "Business Branch":
		fields.append({"label":"Product Category","short_label":"Product Category", "fieldname":"product_category","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65"})
	
	if  filters.row_group != "Product Group" and filters.row_group != "Stock Location" and filters.row_group != "Business Branch":
		fields.append({"label":"Product Group","short_label":"Product Group", "fieldname":"product_group","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65"})

	if filters.row_group != "Business Branch":
		fields.append({"label":"Business Branch","short_label":"Business Branch", "fieldname":"business_branch","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65"})
	
	if filters.row_group != "Stock Location" and filters.row_group != "Business Branch":
		fields.append({"label":"Stock Location","short_label":"Stock Location", "fieldname":"stock_location","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65"})
	
	if filters.row_group == "Product":
		fields.append({"label":"Unit","short_label":"Unit", "fieldname":"stock_unit","fieldtype":"Data","indicator":"Grey", "align":"left","precision":2,"chart_color":"#FF8A65"})
	fields.append({"label":"Quantity on Hand","short_label":"QOH", "fieldname":"prev_on_hand","fieldtype":"Float","indicator":"Grey","precision":4, "align":"right","chart_color":"#FF8A65"})
	 
	return fields


## on get report group data
def get_report_group_data(filters,report_fields=None):
	parent = get_report_data(filters, filters.parent_row_group, 0)
	data=[] 

	for p in parent:		 
		p["is_group"] = 1
		data.append(p)

		row_group = [d for d in get_row_groups() if d["label"]==filters.parent_row_group][0]
		children = get_report_data(filters, None, 1, group_filter={"field":row_group["fieldname"],"value":p[row_group["parent_row_group_filter_field"]]})
		for c in children:
			data.append(c)
	return data


## on get report data
def get_report_data(filters,parent_row_group=None,indent=0,group_filter=None, report_fields=None):
	row_group = [d["fieldname"] for d in get_row_groups() if d["label"]==filters.row_group][0] 

	data = get_sql_data(filters) 

	return data


## on get condition
def get_conditions(filters,group_filter=None):
	conditions = " 1 = 1 "
	start_date = filters.start_date
	end_date = filters.end_date


	if(group_filter!=None):		 
		conditions += " and {} ='{}'".format(group_filter["field"],group_filter["value"].replace("'","''").replace("%","%%"))

	conditions += " AND a.transaction_date between '{}' AND '{}'".format(start_date,end_date)

	if filters.get("product_group"):
		conditions += " AND coalesce(a.product_group,'None Group') in %(product_group)s"

	if filters.get("product_category"):
		conditions += " AND a.product_category in %(product_category)s"
 
	
	conditions += " AND a.business_branch in %(business_branch)s"

	conditions += " AND a.stock_location in %(stock_location)s"
	
	return conditions




# on get sql data	
def get_sql_data(filters): 
	limit_page_length=100     
	business_branch_filter = filters.get("business_branch") or []
	stock_location_filter = filters.get("stock_location") or []
 
	product_group_filter = filters.get("product_group") or []
	product_category_filter = filters.get("product_category") or []

	# -------------------------
	# BUSINESS BRANCH
	# -------------------------
	business_filters = {}
	if business_branch_filter:
		business_filters["name"] = ["in", business_branch_filter]
  
	business_branchs = frappe.get_all(
		"Business Branch",
		filters=business_filters,
		pluck="name",
		limit_page_length=limit_page_length,
	)
 
	# -------------------------
	# STOCK LOCATION
	# -------------------------
	s_location_filters = {
		"business_branch":["in", business_branchs]
	}
	if stock_location_filter:
		s_location_filters["name"] = ["in",stock_location_filter]
  
	stock_locations = frappe.get_all(
		"Stock Location",
		filters=s_location_filters,
		pluck="name",
		limit_page_length=limit_page_length,
	)	 
  
 
	# -------------------------
	# PRODUCT GROUPS
	# -------------------------
	if product_group_filter:
		product_groups = frappe.get_all(
			"Product Category",
			filters={
				"is_group": 1,
				"name": ["in", product_group_filter]
			},
			pluck="name",
    		limit_page_length=limit_page_length
		)
	else:
		product_groups = frappe.get_all(
			"Product Category",
			filters={"is_group": 1},
			pluck="name",
			limit_page_length=limit_page_length,
		)

	# -------------------------
	# PRODUCT CATEGORIES
	# -------------------------
	category_filters = {
		"is_group": 0,
		"parent_product_category": ["in", product_groups]
	}

	# only apply if user selected categories
	if product_category_filter:
		category_filters["name"] = ["in", product_category_filter]

	product_categories = frappe.get_all(
		"Product Category",
		filters=category_filters,
		pluck="name",
		limit_page_length=limit_page_length
	) 
 
	_filters = {
		"business_branch": ",".join(business_branchs) ,
		"start_date": filters.get("start_date"),
		"end_date": filters.get("end_date"),
		"stock_location": ",".join(stock_locations),
		"product_category": ",".join(product_categories)
	} 
 
	data = frappe.db.sql("""
		call sp_get_inventory_movement_report(
			%(business_branch)s,
			%(start_date)s,
			%(end_date)s,
			%(stock_location)s,
			%(product_category)s
		)
		""", _filters, as_dict=True)
    
	 
	return data


# get sql filter condition
def get_filter_condition(filters):
	conditions = " 1 = 1 " 
	if filters.get("product_group"):
		conditions += " AND coalesce(a.product_group,'None Group') in %(product_group)s"

	if filters.get("product_category"):
		conditions += " AND a.product_category in %(product_category)s"
	
	conditions += " AND a.business_branch in %(business_branch)s"

	conditions += " AND a.stock_location in %(stock_location)s"
	
	return conditions
 

