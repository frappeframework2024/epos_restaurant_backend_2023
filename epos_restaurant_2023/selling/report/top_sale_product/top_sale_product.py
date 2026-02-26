import frappe
from frappe.utils import date_diff,today 
from frappe.utils.data import strip
from frappe import _
from py_linq import Enumerable

def execute(filters=None): 
	validate(filters)
	#run this to update parent_product_group in table sales invoice item
	
	report_data = []
	skip_total_row=False
 
	
	report_data = get_report_data(filters) 

	return get_columns(filters), report_data, None, None,skip_total_row
 
def validate(filters):
	if not filters.business_branch:
		filters.business_branch = frappe.db.get_list("Business Branch",pluck='name')
	if not filters.top or filters.top < 0:
		frappe.throw(_('Invalid top row'))
	if not filters.outlet:
		filters.outlet = frappe.db.get_list("Outlet",filters={
        'business_branch': ['In', ','.join(filters.business_branch)]
    },pluck='name')
  

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))


 
def get_columns(filters):
	return [
		{"label":"Product Category", "fieldname":"product_category","fieldtype":"Data", "align":"left","sql":"sp.product_category"},
		{"label":"Product Code", "fieldname":"product_code","fieldtype":"Link","options":"Product", "align":"left","sql":"sp.product_code"},
		{"label":"Product Name", "fieldname":"product_name","fieldtype":"Data", "align":"center","sql":"sp.product_name"},
		{"label":"Total Invoice", "fieldname":"total_invoice","fieldtype":"INT", "align":"center","sql":"COUNT(DISTINCT s.name) as total_invoice"},
		{"label":"Total Quantity Sold", "fieldname":"total_quantity","fieldtype":"INT","options":"Sale", "align":"center","sql":"sum(sp.quantity) as total_quantity"},
		{"label":"Total Amount", "fieldname":"total_amount","fieldtype":"Currency", "align":"right","sql":"sum(sp.total_revenue) as total_amount"}
		
	]
 
 
def selected_column(filters):
	query_field=[]
	for c in get_columns(filters):
		query_field.append(c['sql'])
	return ",".join(query_field)

def get_conditions(filters,group_filter=None):
	conditions=''

	if filters.get('start_date') : start_date = filters.start_date
	if filters.get('end_date') : end_date = filters.end_date
	
	if filters.get('start_date') and filters.get('end_date'):
		conditions = " s.posting_date between '{}' AND '{}'".format(start_date,end_date)
		conditions += " AND s.business_branch in %(business_branch)s"
	else:
		conditions += " s.business_branch in %(business_branch)s"

	if filters.outlet:
		conditions += " AND s.outlet in %(outlet)s"
	conditions += " AND s.docstatus = 1 AND s.is_foc = 0"
	return conditions

def get_report_data(filters):
	sql = """select  
			{0}
			FROM `tabSale Product` AS sp
			inner join `tabSale` s on s.name = sp.parent
			WHERE {1}
			group by 
				sp.product_category,
				sp.product_code,
				sp.product_name 
			{3}
			LIMIT {2}
		
	""".format(selected_column(filters),get_conditions(filters),filters.top,get_order_by(filters))	
	# frappe.throw(sql)
	data = frappe.db.sql(sql,filters, as_dict=1)

	return data

def get_order_by(filters):
	if filters.order_by == "Sale Amount":
		return "order by total_amount DESC"
	if filters.order_by == "Quantity Sold":
		return "order by total_quantity DESC"