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

	if filters.get("parent_row_group"):
		report_data = get_report_group_data(filters)
		message="Enable <strong>Parent Row Group</strong> making report loading slower. Please try  to select some report filter to reduce record from database "
		skip_total_row = True
	else:
		report_data = get_report_data(filters) 
	report_chart = None

	 


	# columns, report data , message, report chart, report summary, skip total row
	return get_columns(filters), report_data, message, report_chart, [],skip_total_row


	# columns, data = [], []
	# return columns, data




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
def get_columns(filters):
	columns = []
	_row_group = [d for d in get_row_groups() if d["label"] ==filters.row_group ][0]["fieldname"]
	
	# frappe.throw(str(_row_group)) 

	## append columns
	columns.append({'fieldname':_row_group,'label':filters.row_group,'fieldtype':'Data','align':'left','width':250})

	## generate dynamic columns
	if filters.row_group not in ["Date","Month","Year"]:
		for c in get_dynamic_columns(filters):
			columns.append(c) 
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
		fields.append({"label":"Product","short_label":"Product Category", "fieldname":"product_name","fieldtype":"Data","indicator":"Grey", "align":"left","chart_color":"#FF8A65","sql_expression":"product_name"})

	if filters.row_group != "Product Category" and filters.row_group != "Product Group" and filters.row_group != "Stock Location" and filters.row_group != "Business Branch":
		fields.append({"label":"Product Category","short_label":"Product Category", "fieldname":"product_category","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65","sql_expression":"product_category"})
	
	if filters.row_group != "Business Branch":
		fields.append({"label":"Business Branch","short_label":"Business Branch", "fieldname":"business_branch","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65","sql_expression":"business_branch"})
	
	if filters.row_group != "Stock Location" and filters.row_group != "Business Branch":
		fields.append({"label":"Stock Location","short_label":"Stock Location", "fieldname":"stock_location","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65","sql_expression":"stock_location"})
	
	if filters.row_group == "Product":
		fields.append({"label":"Unit","short_label":"Unit", "fieldname":"stock_unit","fieldtype":"Data","indicator":"Grey", "align":"left","precision":2,"chart_color":"#FF8A65","sql_expression":"a.stock_unit"})
	fields.append({"label":"Quantity on Hand","short_label":"QOH", "fieldname":"prev_on_hand","fieldtype":"Float","indicator":"Grey","precision":8, "align":"right","chart_color":"#FF8A65","sql_expression":"SUM(a.quantity_on_hand)"})
	
	
	
	return fields


## on get report group data
def get_report_group_data(filters):
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
def get_report_data(filters,parent_row_group=None,indent=0,group_filter=None):
	row_group = [d["fieldname"] for d in get_row_groups() if d["label"]==filters.row_group][0]

	# if(parent_row_group!=None):
		# row_group = [d["fieldname"] for d in get_row_groups() if d["label"]==parent_row_group][0]

	data = get_sql_data(filters,row_group)

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
		conditions += " AND a.product_group in %(product_group)s"

	if filters.get("product_category"):
		conditions += " AND a.product_category in %(product_category)s"
 
	
	conditions += " AND a.business_branch in %(business_branch)s"

	conditions += " AND a.stock_location in %(stock_location)s"
	
	return conditions




# on get sql data	
def get_sql_data(filters,row_group): 
	_group_by = """a.product_code,
 		a.product_name, 
		a.stock_unit,
		a.product_category,
 		a.product_group, 
		a.stock_location,
		a.business_branch"""
	
	if row_group == "product_category":
		_group_by = """a.product_category,
 		a.product_group, 
		a.stock_location,
		a.business_branch"""
	elif row_group == "product_group":
		_group_by = """a.product_group, 
		a.stock_location,
		a.business_branch"""
	elif row_group == "stock_location":
		_group_by = """a.stock_location,
		a.business_branch"""
	elif row_group =="":
		_group_by = """a.business_branch"""

	_filter =  get_filter_condition(filters)
	##query prev on hand quantity
	sql = """with inventory_transaction as(
				select 
					a.product_code,
					a.product_name, 
					a.stock_unit,
					a.product_category,
					a.product_group,
					a.business_branch,
					a.stock_location,		
					max(a.creation) as _max_creation,
					max(a.transaction_date) as _max_transaction
				from `tabInventory Transaction` AS a 
				where {1} 
					and a.transaction_date < '{2}'
				group by 
					a.product_code,
					a.product_name, 
					a.stock_unit,
					a.product_category,
					a.product_group,
					a.business_branch,
					a.stock_location	
			)
			, b as(
				select	
					{0},
					sum((select x.balance from `tabInventory Transaction` x where x.creation = a._max_creation and x.stock_location = a.stock_location )) as prev_on_hand
				from inventory_transaction a
				group by 
					{0}
				union
				select 
					{0}, 
					0 as prev_on_hand
				from `tabInventory Transaction` a 
				where {1}
					and a.transaction_date between '{2}' and '{3}'
				group by 
					{0}
			)select
					{0}, 
					sum(a.prev_on_hand)  as prev_on_hand
			from b as a
			group by
					{0}""".format(_group_by, _filter, filters.start_date, filters.end_date )
	
	doc = frappe.db.sql(sql,filters, as_dict=1)

	# ## get current filter
	# sql2 = """select 
	# 	{0},
	# 	0 as prev_on_hand,
	# 	0 as balance,
	# 	if(a.transaction_type = 'Sale', sum(a.in_quantity-a.out_quantity),0) as sale,
	# 	if(a.transaction_type = 'Folio Transaction', sum(a.in_quantity-a.out_quantity),0) as folio_transaction,
	# 	sum(a.in_quantity) as in_quantity,
	# 	sum(a.out_quantity) as out_quantity		
	# from `tabInventory Transaction` a
	# where 1=1 {1}
	# 	and a.transaction_date between '{2}' and '{3}' 
	# group by 
	# 	{0} 
	# """.format(_group_by, _filter, filters.start_date, filters.end_date)
	# # frappe.throw(str(doc))
	# doc2 = frappe.db.sql(sql2,filters, as_dict=1)
	
	return doc

# get sql filter condition
def get_filter_condition(filters):
	conditions = " 1 = 1 " 
	if filters.get("product_group"):
		conditions += " AND a.product_group in %(product_group)s"

	if filters.get("product_category"):
		conditions += " AND a.product_category in %(product_category)s"
	
	conditions += " AND a.business_branch in %(business_branch)s"

	conditions += " AND a.stock_location in %(stock_location)s"
	
	return conditions
 

