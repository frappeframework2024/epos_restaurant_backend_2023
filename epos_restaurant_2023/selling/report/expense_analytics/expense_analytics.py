import frappe
from frappe import _
from frappe.utils import date_diff,add_months, add_days
from frappe.utils.data import strip
import datetime

def execute(filters=None): 
	validate(filters)
	report_data = []
	skip_total_row=False
	message=None
	if filters.get("parent_row_group"):
		report_data = get_report_group_data(filters)
		skip_total_row = True
	else:
		report_data = get_report_data(filters) 
	report_chart = None
	if filters.chart_type !="None" and len(report_data)<=100:
		report_chart = get_report_chart(filters,report_data) 
	return get_columns(filters), report_data, message, report_chart, get_report_summary(report_data,filters),skip_total_row

def get_report_summary(data,filters):
	report_summary=[]
	if filters.parent_row_group==None:
		if not filters.is_ticket:
			report_summary =[{"label": filters.row_group ,"value":len(data)}]
	fields = get_report_field(filters)
	for f in fields:
		value=sum(d["total_" + f["fieldname"]] for d in data if d["indent"]==0)
		report_summary.append({"label":"{}".format(f["label"]),"value":value,"datatype": f["fieldtype"],"indicator":f["indicator"]})

	return  report_summary

def validate(filters):
	if not filters.business_branch:
		filters.business_branch = frappe.db.get_list("Business Branch",pluck='name') 

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))

	if filters.row_group and filters.parent_row_group:
		if(filters.row_group == filters.parent_row_group):
			frappe.throw("Parent row group and row group can not be the same")
 
def get_columns(filters):	
	columns = []
	columns.append({'fieldname':'row_group','label':filters.row_group,'fieldtype':'Data',"options":"Sale",'align':'left','width':150})
	if filters.row_group == "Expense Code":
		columns.append({'fieldname':'expense_name','label':"Expense Name",'fieldtype':'Data','align':'left','width':250})
	if filters.column_group !="None" and filters.row_group not in ["Date","Month","Year"]:
		for c in get_dynamic_columns(filters):
			columns.append(c)
	return columns

def get_dynamic_columns(filters):
	fields = get_fields(filters)
	report_fields = get_report_field(filters)
	columns=[]
	for f in fields:
		for rf in report_fields:
			columns.append({
				'fieldname':f["fieldname"] + "_" + rf["fieldname"],
				'label': f["label"] + " "  + rf["short_label"],
				'fieldtype':rf["fieldtype"],
				'precision': rf["precision"],
				'align':rf["align"],
				'width':100
				}
			)
	return columns

def get_report_field(filters):
	fields = []
	fields.append({"label":"Amount", "short_label":"", "fieldname":"amount","fieldtype":"Currency","indicator":"Red","precision":None, "align":"right","chart_color":"#2E7D32","sql_expression":"SUM(a.amount)"})
	return fields

def get_fields(filters):
	daily_label = "date_format(date,'%d/%m')"
	start_date = datetime.datetime.strptime(filters.start_date, "%Y-%m-%d").date()
	end_date = datetime.datetime.strptime(filters.end_date, "%Y-%m-%d").date()
	if start_date.month == end_date.month and start_date.year == end_date.year:
		daily_label = "date_format(date,'%d')"
	sql=""
	if filters.column_group=="Daily":
		sql = """
			select 
				concat('col_',date_format(date,'%d_%m')) as fieldname, 
				{2} as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{0}' and '{1}'
			group by
				concat('col_',date_format(date,'%d_%m')) , 
				date_format(date,'%d')  	
		""".format(filters.start_date, filters.end_date,daily_label)
	elif filters.column_group =="Monthly":
		sql = """
			select 
				concat('col_',date_format(date,'%m_%Y')) as fieldname, 
				date_format(date,'%b/%y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%m_%Y')) , 
				date_format(date,'%b %y')  	
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Weekly":
		sql = """
			select 
				concat('col_',date_format(date,'%v_%Y')) as fieldname, 
				concat('WK ',date_format(date,'%v/%y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%v_%Y')), 
				concat('WK ',date_format(date,'%v %y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Quarterly":
		sql = """
			select 
				concat('col_',QUARTER(date)) as fieldname, 
				concat('Q',QUARTER(date),' ',date_format(date,'%y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',QUARTER(date)),
				concat('Q',QUARTER(date),' ',date_format(date,'%y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Half Yearly":
		sql = """
			select 
				concat('col_',if(month(date) between 1 and 6,'jan_jun','jul_dec'),date_format(date,'%y')) as fieldname, 
				concat(if(month(date) between 1 and 6,'Jan-Jun','Jul-Dec'),' ',date_format(date,'%y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',if(month(date) between 1 and 6,'jan_jun','jul_dec'),date_format(date,'%y')), 
				concat(if(month(date) between 1 and 6,'Jan-Jun','Jul-Dec'),' ',date_format(date,'%y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Yearly":
		sql = """
			select 
				concat('col_',date_format(date,'%Y')) as fieldname, 
				date_format(date,'%Y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%Y')),
				date_format(date,'%Y')
		""".format(filters.start_date, filters.end_date)
	fields = frappe.db.sql(sql,as_dict=1)
	return fields
 
def get_conditions(filters,group_filter=None):
	conditions = "b.docstatus = 1"
	if(group_filter!=None):
		conditions += " and {} ='{}'".format(group_filter["field"],group_filter["value"].replace("'","''").replace("%","%%"))
	conditions += " AND b.posting_date between '{}' AND '{}'".format(filters.start_date, filters.end_date)
	if filters.get("expense_category"):
		conditions += " AND a.expense_category in %(expense_category)s"
	conditions += " AND b.business_branch in %(business_branch)s"
	return conditions

def get_report_data(filters,parent_row_group=None,indent=0,group_filter=None):
	row_groups = [d["fieldname"] for d in get_row_groups() if d["label"]==filters.row_group]
	row_group = "a.expense_category"
	if len(row_groups)>0:
		row_group = row_groups[0]
	else:
		row_group = "a.expense_category"
	if(parent_row_group!=None):
		row_groups = [d["fieldname"] for d in get_row_groups() if d["label"]==parent_row_group]
		if len(row_groups)>0:
			row_group = row_groups[0]
	sql = "select {} as row_group, {} as indent ".format(row_group, indent)
	report_fields = get_report_field(filters)
	if filters.column_group != "None":
		fields = get_fields(filters) 
		for f in fields:
			sql = strip(sql)
			if sql[-1]!=",":
				sql = sql + ','
			for rf in  report_fields:
				sql_expression = str(rf["sql_expression"]).lower().replace("sum","")
				sql = sql +	"sum(if(b.posting_date between '{}' AND '{}',{},0)) as '{}_{}',".format(f["start_date"],f["end_date"],sql_expression,f["fieldname"],rf["fieldname"])
	for rf in report_fields:
		sql = strip(sql)
		if sql[-1]==",":
			sql = sql[0:len(sql)-1]
		sql = sql + " ,{} AS 'total_{}' ".format(rf["sql_expression"],rf["fieldname"])
	extra_fields = ""
	if (filters.row_group == "Expense Code" and indent == 1) or (filters.row_group == "Expense Code" and (filters.parent_row_group or "") == ""):
		extra_fields = ",a.expense_name"
	sql = sql + extra_fields + """
		FROM `tabExpense Item` AS a
			INNER JOIN `tabExpense` b on b.name = a.parent
		WHERE
			{0}
		GROUP BY 
		{1}{2}
	""".format(get_conditions(filters,group_filter), row_group,extra_fields)
	data = frappe.db.sql(sql,filters, as_dict=1)
	return data
 
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

def get_report_chart(filters,data):
	columns = []
	dataset = []
	colors = []
	report_fields = get_report_field(filters)

	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
			columns.append(f["label"])
		for rf in report_fields:
			dataset_values = []
			for f in fields:
				dataset_values.append(sum(d["{}_{}".format(f["fieldname"],rf["fieldname"])] for d in data if d["indent"]==0))
			dataset.append({'name':rf["label"],'values':dataset_values})
			colors.append(rf["chart_color"])
	else:
		for d in data:
			if d["indent"] ==0:
				columns.append(d["row_group"])
	chart = {
		'data':{
			'labels':columns,
			'datasets':dataset
		},
		"type": filters.chart_type,
		"lineOptions": {
			"regionFill": 1,
		},
		"axisOptions": {"xIsSeries": 1},
	}
	return chart

def get_row_groups():
	return [
		{
			"fieldname":"a.expense_category",
			"label":"Expense Category",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"b.business_branch",
			"label":"Business Branch",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"a.expense_code",
			"label":"Expense Code",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"b.employee_name",
			"label":"Expense By",
			"parent_row_group_filter_field":"row_group"
		},
	]