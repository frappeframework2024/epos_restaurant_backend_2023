import frappe

def execute(filters=None): 
	validate(filters)
	report_data = []
	skip_total_row=False
	report_data = get_report_data(filters) 
	return get_columns(filters), report_data, None, None, None,skip_total_row
 
def validate(filters):
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
	if filters.row_group and filters.parent_row_group:
		if(filters.row_group == filters.parent_row_group):
			frappe.throw("Parent row group and row group can not be the same")
 
def get_columns(filters):
	return [
		{"label":"Expense", "fieldname":"expense","fieldtype":"Link","options":"Expense","align":"left","width":200},
		{"label":"Date",  "fieldname":"posting_date","fieldtype":"Date", "align":"center","width":150},
		{"label":"Branch", "fieldname":"business_branch","fieldtype":"Data","align":"center","width":150},
		{"label":"Payment Type", "fieldname":"payment_type","fieldtype":"Data","align":"center","width":200},
		{"label":"Expense Amount", "fieldname":"expense_amount","fieldtype":"Currency","align":"right","width":150},
		{"label":"Payment Amount", "fieldname":"payment_amount","fieldtype":"Currency","align":"right","width":150}
	]
 
def get_conditions(filters):
	conditions = " b.docstatus = 1 "
	conditions += " AND b.posting_date between '{}' AND '{}'".format(filters.start_date,filters.end_date)
	if filters.get("payment_type_group"):
		conditions += " AND c.payment_type_group in %(payment_type_group)s"
	if filters.get("payment_type"):
		conditions += " AND a.payment_type in %(payment_type)s"
	if filters.get("expense"):
		conditions += " AND a.parent = %(expense)s"
	if filters.get("business_branch"):
		conditions += " AND b.business_branch in %(business_branch)s"
	return conditions

def get_report_data(filters):
	sql = """select  
			b.posting_date,
			b.business_branch,
			a.parent as expense,
			a.payment_type,
			b.total_amount as expense_amount,
			(a.amount * a.exchange_rate) as payment_amount
		FROM `tabExpense Payments` AS a
		inner join `tabExpense` as b on a.parent = b.name
		inner join `tabPayment Type` as c on a.payment_type = c.name
		WHERE
			{}
	""".format(get_conditions(filters))	
	data = frappe.db.sql(sql,filters, as_dict=1)
	return data