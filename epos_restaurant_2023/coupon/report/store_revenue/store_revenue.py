import frappe
from frappe import _
from frappe.utils import add_months, add_days
import datetime

def execute(filters=None): 
	if filters.filter_based_on =="Fiscal Year":
		if not filters.from_fiscal_year:
			filters.from_fiscal_year = datetime.date.today().year
		
		filters.start_date = '{}-01-01'.format(filters.from_fiscal_year)
		filters.end_date = '{}-12-31'.format(filters.from_fiscal_year) 
	elif filters.filter_based_on =="This Month":
		filters.start_date = datetime.date.today().replace(day=1)
		filters.end_date =add_days(  add_months(filters.start_date ,1),-1)
		 
	validate(filters)

	report_data = get_report_data(filters) 
	report_chart = None
	if filters.chart_type !="None" and len(report_data)<=100:
		report_chart = get_report_chart(filters,report_data) 
	return get_columns(filters), report_data, "", report_chart, get_report_summary(report_data,filters),0
 
def validate(filters):
	if not filters.business_branch:
		filters.business_branch = frappe.db.get_list("Business Branch",pluck='name')
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))

def get_columns(filters):	
	columns = []
	if filters.group_by == "Station":
		columns.append({"label":"Station","fieldname":"pos_profile","fieldtype":"Data","align":"left",'width':200})
	elif filters.group_by == "Coupon Number":
		columns.append({"label":"Coupon Number","fieldname":"coupon_number","fieldtype":"Data","align":"left",'width':150})
	elif filters.group_by == "Posting Date":
		columns.append({"label":"Posting Date","fieldname":"posting_date","fieldtype":"Date","align":"left",'width':150})
	elif filters.group_by == "Hour":
		columns.append({"label":"Hour","fieldname":"number","fieldtype":"Data","align":"center",'width':100})
	else:
		columns.append({"label":"Device","fieldname":"pos_station","fieldtype":"Data","align":"left",'width':150})
	columns.append({"label":"Transactions","fieldname":"transactions","fieldtype":"Data","align":"center",'width':120})
	columns.append({"label":"Amount","fieldname":"actual_amount","fieldtype":"Currency","align":"center",'width':150})
	return columns
 
def get_conditions(filters):
	conditions = " where"
	if filters.group_by == "Hour":
		conditions = " and"
	conditions += " coalesce(transaction_type,'Use')='Use'"
	start_date = filters.start_date
	end_date = filters.end_date
	conditions += " AND coalesce(posting_date,now()) between '{}' AND '{}'".format(start_date,end_date)
	conditions += " AND business_branch in %(business_branch)s"
	if filters.get("pos_profile"):
		conditions += " AND pos_profile in %(pos_profile)s"
	if filters.get("pos_station"):
		conditions += " AND pos_station in %(pos_station)s"
	return conditions

def get_report_data(filters):
	join = ""
	group_by = get_field(filters)
	if group_by == "number":
		join = "right join `tabNumbers` b on b.number = hour(a.creation)"
	sql = """
	SELECT 
	{1},
	coalesce(truncate(abs(sum(a.actual_amount)),4),0) actual_amount,
	coalesce(count(a.name),0) transactions
	FROM `tabCoupon Transaction` a
	{2}
	{0}
	group by {1}
	""".format(get_conditions(filters),group_by,join)
	data = frappe.db.sql(sql,filters, as_dict=1)
	return data
 
def get_report_group_data(filters):
	parent = get_report_data(filters)
	data=[] 
	for p in parent:
		data.append(p)
	return data

def get_report_summary(data,filters):
	report_summary=[]
	if filters.show_summary:
		report_summary =[{"label": filters.group_by ,"value":len(data)}]
		fields = get_report_field(filters)
		for f in fields:
			value = "{:.2f}".format(sum(d[f["fieldname"]] for d in data))
			report_summary.append({"label":"{}".format(f["label"]),"value":value,"indicator":f["indicator"]})
	return  report_summary

def get_report_chart(filters, data):
    columns = []
    colors = []
    field = get_field(filters)
    columns = list({d[field] for d in data})  # Use set for uniqueness
    report_fields = get_report_field(filters)
    datasets = []
    for rf in report_fields:
        dataset_values = []
        for col in columns:
            value = sum(d[rf["fieldname"]] for d in data if d[field] == col)
            dataset_values.append(value)
        datasets.append({
            'name': rf["label"],
            'values': dataset_values
        })
        colors.append(rf["chart_color"])
    chart = {
        'data': {
            'labels': columns,
            'datasets': datasets
        },
        "type": filters.chart_type,
        "lineOptions": {
            "regionFill": 1,
        },
        "axisOptions": {"xIsSeries": 1}
    }
    return chart

def get_field(filters):
	field = "pos_profile"
	if filters.group_by == "Coupon Number":
		field = "coupon_number"
	elif filters.group_by == "Device":
		field = "pos_station"
	elif filters.group_by == "Posting Date":
		field = "posting_date"
	elif filters.group_by == "Hour":
		field = "number"
	else:
		field = "pos_profile"
	return field

def get_report_field(filters):
	fields = []
	fields.append({"label":"Amount","short_label":"Amt.", "fieldname":"actual_amount","fieldtype":"Currency","indicator":"gray","precision":2,"chart_color":"#FF8A65"})
	return fields