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

	return get_columns(filters, report_data), report_data, None, None, get_report_summary(report_data,filters),skip_total_row
 
def validate(filters):
	if not filters.business_branch:
		filters.business_branch = frappe.db.get_list("Business Branch",pluck='name')
  
	if not filters.outlet:
		filters.outlet = frappe.db.get_list("Outlet",pluck='name')
  

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:

			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))



	if filters.row_group and filters.parent_row_group:
		if(filters.row_group == filters.parent_row_group):
			frappe.throw("Parent row group and row group can not be the same")
 
def get_columns(filters,data):
	total_commission_amount = Enumerable(data).sum(lambda x: x.commission_amount or 0)
	columns = []
	columns.append({"label":"Doc. #", "fieldname":"name","fieldtype":"Link","options":"Sale", "align":"center","width":250})	
	columns.append({"label":"Date",  "fieldname":"posting_date","fieldtype":"Date", "align":"center",})
	columns.append({"label":"Branch", "fieldname":"business_branch","fieldtype":"Data","align":"left","width":120})
	columns.append({"label":"Outlet", "fieldname":"outlet","fieldtype":"Data","align":"left"})
	columns.append({"label":"Customer", "fieldname":"customer_name","fieldtype":"Data","align":"left","width":150})
	columns.append({"label":"Tbl #", "fieldname":"tbl_number","fieldtype":"Data","align":"left"})
	columns.append({"label":"Guest Cover", "fieldname":"guest_cover","fieldtype":"Data","align":"center","width":50})
	columns.append({"label":"QTY", "fieldname":"total_quantity","fieldtype":"Float","precision":2, "align":"center","width":75})
	columns.append({"label":"Sub Total", "fieldname":"sub_total","fieldtype":"Currency","align":"right"})
	columns.append({"label":"Discount", "fieldname":"total_discount","fieldtype":"Currency","align":"right","width":100})
	if total_commission_amount > 0:
		columns.append({"label":"Commission", "fieldname":"commission_amount","fieldtype":"Currency","align":"right","width":100})

	columns.append({"label":"Net Sale", "fieldname":"net_sale","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"Tax", "fieldname":"total_tax","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"Revenue", "fieldname":"grand_total","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"Gross Profit", "fieldname":"profit","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"Cost", "fieldname":"total_cost","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"User", "fieldname":"created_by","fieldtype":"Data"})
	columns.append({"label":"Status", "fieldname":"status","fieldtype":"Data","width":100})

	return columns
	
 
 
 


 
def get_conditions(filters,group_filter=None):
	conditions = " 1 = 1"
	start_date = filters.start_date
	end_date = filters.end_date
 
	if not filters.include_foc:
		conditions += " and a.is_foc=0 "

	conditions += " and a.posting_date between '{}' AND '{}'".format(start_date,end_date)

	if filters.get("product_group"):
		conditions += " AND a.product_group in %(product_group)s"

	if filters.get("product_category"):
		conditions += " AND a.product_category in %(product_category)s"

	if filters.get("customer_group"):
		conditions += " AND a.customer_group in %(customer_group)s"
  
	if filters.get("customer"):
		conditions += " AND a.customer = %(customer)s"
 
	conditions += " AND a.business_branch in %(business_branch)s"
	conditions += " AND a.outlet in %(outlet)s"

	if filters.get("pos_profile"):
		conditions += " AND a.pos_profile in %(pos_profile)s"

	if filters.get("show_only_cancelled") == 1:
		conditions += " AND a.docstatus = 2"
	else:
		if filters.get("show_cancelled") == 1:
			conditions += " AND a.docstatus in (1,2)"
		else:
			conditions += " AND a.docstatus = 1"
	
	return conditions

def get_report_data(filters,parent_row_group=None,indent=0,group_filter=None):
	
	sql = """select  
			a.name as sale_id,
			CASE 
        		WHEN coalesce(a.custom_bill_number,'') = '' THEN a.name
        		ELSE CONCAT(coalesce(a.custom_bill_number,''), ' (', a.name, ')')
    		END AS name,
			a.tbl_number,
			a.posting_date,
			a.business_branch,
			a.outlet,
			a.stock_location,
			concat(a.customer ,'-',a.customer_name) as customer_name,
			total_quantity,
			a.sub_total,
			a.total_discount,
			a.grand_total,
			a.total_cost,
			a.commission_amount,
			a.sub_total - a.total_discount - a.commission_amount as net_sale,
			a.profit,
			a.total_tax,
			a.created_by,
			a.guest_cover,
			if(a.docstatus=1, if(a.is_foc = 1, 'FOC', 'Paid'),'Cancelled') status
	FROM `tabSale` AS a
		WHERE
			{}
		
	""".format(get_conditions(filters,group_filter))	
	 
	data = frappe.db.sql(sql,filters, as_dict=1)

	return data
 

def get_report_summary(data,filters):
	report_summary = [] 
	if filters.show_summary:
		total_commission_amount = Enumerable(data).sum(lambda x: x.commission_amount or 0)
		report_summary.append({"label":_("Quantity"),"value":Enumerable(data).sum(lambda x: x.total_quantity or 0),"indicator":"gray"})	
		report_summary.append({"label":_("Sub Total"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.sub_total or 0)),"indicator":"gray"})	
		report_summary.append({"label":_("Discount"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_discount or 0)),"indicator":"gray"})	
		if total_commission_amount > 0:	
			report_summary.append({"label":_("Commission"),"value":frappe.utils.fmt_money(total_commission_amount),"indicator":"red"})		

		report_summary.append({"label":_("Net Sale"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.net_sale or 0)),"indicator":"blue"})	
		report_summary.append({"label":_("Tax"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_tax or 0)),"indicator":"gray"})	
			
		report_summary.append({"label":_("Revenue"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.grand_total or 0)),"indicator":"red"})
		report_summary.append({"label":_("Cost"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_cost or 0)),"indicator":"red"})
			
		report_summary.append({"label":_("Gross Profit"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.profit or 0)),"indicator":"green"})	

	return report_summary