import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
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
	#run this to update parent_product_group in table sales invoice item

	report_data = []
	skip_total_row=False
	message=None
	data = get_report(filters)
	report_data = get_report_data(filters,data) 
	summary = get_summary_report(filters,data)
	report_chart = None
	if filters.chart_type !="None" and len(report_data)<=100:
		report_chart = get_report_chart(filters,data) 
	return get_columns(filters), report_data, message, report_chart, summary,skip_total_row
 
def validate(filters):

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:

			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))


def get_columns(filters):
	columns = [
		{'fieldname':'code','label':"Items",'fieldtype':'Data','align':'left','width':150},
		{'fieldname':'issue_date','label':"Date",'fieldtype':'Date','align':'center','width':150},
		{'fieldname':'expire_date','label':"Expire Date",'fieldtype':'Data','align':'center','width':150},
		{'fieldname':'amount','label':"Amount",'fieldtype':'Currency','align':'center','width':150},
		{'fieldname':'claim_amount','label':"Claim Amount",'fieldtype':'Currency','align':'center','width':150},
		{'fieldname':'balance','label':"Balance",'fieldtype':'Currency','align':'center','width':150},
		{'fieldname':'expired_balance','label':"Expired Balance",'fieldtype':'Currency','align':'center','width':150},
	]
	data = get_report(filters)

	return columns

def get_summary_report(filters,data):
	if filters.show_summary:
		return [
			{ "label":"Total Amount","value":sum([d['amount'] for d in data]),"datatype": "Currency","indicator":"green"},
			{ "label":"Total Claim Amount","value":sum([d['claim_amount'] for d in data]),"datatype": "Currency","indicator":"blue"},
			{ "label":"Balance","value":sum([d['balance'] for d in data]),"datatype": "Currency","indicator":"blue"},
			{ "label":"Expired Balance","value":sum([d['expired_balance'] for d in data]),"datatype": "Currency","indicator":"red"},
			
		]
def get_report(filters):
	sql = """
    select 
        1 as indent,
        b.code, 
        b.parent,
		b.expiry_date,
        if(ifnull(b.unlimited, '') = 1, 'Unlimited', DATE_FORMAT(b.expiry_date, '%%d-%%m-%%Y')) as expire_date,
        if(ifnull(b.unlimited, '') = 1, 0, b.balance) as expired_balance,
        b.unlimited,
        b.amount,
        a.issue_date,
        b.claim_amount,
        b.balance,
		a.member,
		c.customer_group,
        concat(a.member, '-', a.member_name) as member
    from `tabCash Coupon Items` b
    inner join `tabCash Coupon` a on a.name = b.parent
    inner join `tabCustomer` c on a.member = c.name
    where 
        a.issue_date between %(start_date)s and %(end_date)s
"""
	if filters.get('customer'):
		sql = sql + " and a.member in %(customer)s "
	if filters.get("customer_group"):
		sql = sql + " AND c.customer_group in %(customer_group)s"
	data = frappe.db.sql(sql, filters, as_dict=1)
	return data


def get_report_data(filters,data):
	report_data = []
	date = datetime.date.today()

	for e in data:
		if e['expiry_date'] and e['expiry_date'] < date and e['unlimited']==0:
			e['expired_balance'] = e.get('balance', 0) 
			e['balance'] = 0
		else:
			e['expired_balance'] = 0

	member = sorted(set({d['member'] for d in data}))
	
	for g in member:
		report_data.append({
			'indent':0,
			'code':g,
			'amount':sum([d['amount'] for d in data if d['member']==g]),
			'claim_amount':sum([d['claim_amount'] for d in data if d['member']==g]),
			'balance':sum([d['balance'] for d in data if d['member']==g]),
			'expired_balance':sum([d['expired_balance'] for d in data if d['member']==g])
		})

		report_data = report_data +  [d for d in data if d['member']==g]

	
	return report_data

 
def get_report_chart(filters, data):
    precision = frappe.db.get_single_value("System Settings", "currency_precision")
    
    columns = sorted(set(d['member'] for d in data))
    
    amounts = [0] * len(columns)
    claim_amounts = [0] * len(columns)
    balances = [0] * len(columns)
    expired_balances = [0] * len(columns)
    
    member_index = {member: index for index, member in enumerate(columns)}
    
    for d in data:
        member = d['member']
        index = member_index.get(member)
        if index is not None:
            amounts[index] += d.get('amount', 0)
            claim_amounts[index] += d.get('claim_amount', 0)
            balances[index] += d.get('balance', 0)
            expired_balances[index] += d.get('expired_balance', 0)

    datasets = [
        {
            "name": 'Amount',
            "values": [round(amount, int(precision)) for amount in amounts]
        },
        {
            "name": 'Claim Amount',
            "values": [round(claim_amount, int(precision)) for claim_amount in claim_amounts]
        },
        {
            "name": 'Balance',
            "values": [round(balance, int(precision)) for balance in balances]
        },
        {
            "name": 'Expired Balance',
            "values": [round(expired_balance, int(precision)) for expired_balance in expired_balances]
        }
    ]
    
    chart = {
        'data': {
            'labels': columns,
            'datasets': datasets
        },
        'type': filters.chart_type,
        "lineOptions": {
            "regionFill": 1,
        },
        'valuesOverPoints': 1,
        "axisOptions": {"xIsSeries": 1}
    }
    
    return chart
