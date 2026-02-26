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
		{'fieldname':'sale_coupon','label':"Items",'fieldtype':'Data','align':'left','width':150},
		{'fieldname':'posting_date','label':"Date",'fieldtype':'Date','align':'center','width':150},
		{'fieldname':'limit_visit','label':"Limit Visit",'fieldtype':'Int','align':'center','width':150},
		{'fieldname':'visited_count','label':"Visited Count",'fieldtype':'Int','align':'center','width':150},
		{'fieldname':'price','label':"Price",'fieldtype':'Currency','align':'center','width':150},
		{'fieldname':'discount_value','label':"Price",'fieldtype':'Currency','align':'center','width':150},
		{'fieldname':'grand_total','label':"Grand Total",'fieldtype':'Currency','align':'center','width':150},
		{'fieldname':'total_payment_amount','label':"Total Payment",'fieldtype':'Currency','align':'center','width':150},
		{'fieldname':'payment_balance','label':"Balance",'fieldtype':'Currency','align':'center','width':150},
	]
	data = get_report(filters)

	return columns

def get_summary_report(filters,data):
	if filters.show_summary:
		return [
			{ "label":"Total Price","value":sum([d['price'] for d in data]),"datatype": "Currency","indicator":"green"},
			{ "label":"Total Discount","value":sum([d['discount_value'] for d in data]),"datatype": "Currency","indicator":"green"},
			{ "label":"Grand Total","value":sum([d['grand_total'] for d in data]),"datatype": "Currency","indicator":"blue"},
			{ "label":"Total Payment","value":sum([d['total_payment_amount'] for d in data]),"datatype": "Currency","indicator":"blue"},
			{ "label":"Balance","value":sum([d['payment_balance'] for d in data]),"datatype": "Currency","indicator":"blue"},
			
		]
def get_report(filters):
	sql1=''
	join=''
	if filters.get("member_type")==['Member']:
		sql1 = ",c.name as customer,c.customer_group"
		join = "inner join `tabCustomer` c on b.member = c.name"
	sql = """
    select 

		b.name as sale_coupon,
		b.visited_count,
		concat(b.visited_count,'/',b.limit_visit) as visited,
		b.limit_visit,
		b.price,
		b.discount_value,
		b.grand_total,
		a.payment_type,
		IFNULL(b.member, '') AS member, 
		b.member_name,
		CONCAT(IFNULL(b.member, ''), IF(b.member IS NOT NULL, '-', ''), b.member_name) AS member_code,  
		b.total_payment_amount,
		b.payment_balance,
		a.name,
		b.member_type
		{}
	from `tabSales Coupon Payment` a
	inner join `tabSale Coupon` b on a.sale_coupon = b.name
    {}
    where 
        b.posting_date between %(start_date)s and %(end_date)s and
		a.docstatus = 1
""".format(sql1,join)
	if  filters.get("member_type") == ['Member']:
	
		sql = sql + " and b.member_type in %(member_type)s"
		if filters.get('customer'):
			
			sql = sql + " and b.member in %(customer)s "
		if filters.get("customer_group"):
			sql = sql + " AND c.customer_group in %(customer_group)s"
	if filters.get("member_type"):
		sql = sql + " and b.member_type in %(member_type)s"
	# frappe.throw(sql)
	data = frappe.db.sql(sql, filters, as_dict=1)
	return data


def get_report_data(filters,data):
	report_data = []
	# frappe.throw(str([d['member'] for d in data]))
	member = sorted(set({d['member_code'] for d in data}))
	individual = sorted(set({d['member_type'] for d in data}))
	if filters.get('member_type'):
		for i in individual:
			report_data.append({
				'indent':0,
				'sale_coupon':i,
				'limit_visit':sum([d['limit_visit'] for d in data if d['member_type']==i]),
				'visited_count':sum([d['visited_count'] for d in data if d['member_type']==i]),
				'price':sum([d['price'] for d in data if d['member_type']==i]),
				'discount_value':sum([d['discount_value'] for d in data if d['member_type']==i]),
				'grand_total':sum([d['grand_total'] for d in data if d['member_type']==i]),
				'total_payment_amount':sum([d['total_payment_amount'] for d in data if d['member_type']==i]),
				'payment_balance':sum([d['payment_balance'] for d in data if d['member_type']==i]),
			})
			for g in [m['member_code'] for m in data if m['member_type']==i]:
				report_data.append({
					'indent':1,
					'sale_coupon':g,
					'limit_visit':sum([d['limit_visit'] for d in data if d['member_code']==g and d['member_type']==i]),
					'visited_count':sum([d['visited_count'] for d in data if d['member_code']==g and d['member_type']==i]),
					'price':sum([d['price'] for d in data if d['member_code']==g and d['member_type']==i]),
					'discount_value':sum([d['discount_value'] for d in data if d['member_code']==g and d['member_type']==i]),
					'grand_total':sum([d['grand_total'] for d in data if d['member_code']==g and d['member_type']==i]),
					'total_payment_amount':sum([d['total_payment_amount'] for d in data if d['member_code']==g and d['member_type']==i]),
					'payment_balance':sum([d['payment_balance'] for d in data if d['member_code']==g and d['member_type']==i]),
				})

				report_data = report_data +  [d.update({"indent":2}) or d for d in data if d['member_code']==g and d['member_type']==i]

	else:
		for g in member:
				report_data.append({
					'indent':0,
					'sale_coupon':g,
					'limit_visit':sum([d['limit_visit'] for d in data if d['member_code']==g]),
					'visited_count':sum([d['visited_count'] for d in data if d['member_code']==g]),
					'price':sum([d['price'] for d in data if d['member_code']==g]),
					'discount_value':sum([d['discount_value'] for d in data if d['member_code']==g]),
					'grand_total':sum([d['grand_total'] for d in data if d['member_code']==g]),
					'total_payment_amount':sum([d['total_payment_amount'] for d in data if d['member_code']==g]),
					'payment_balance':sum([d['payment_balance'] for d in data if d['member_code']==g]),
				})

				report_data = report_data +  [d.update({"indent":1}) or d for d in data if d['member_code']==g]
	return report_data

 
def get_report_chart(filters, data):
    precision = frappe.db.get_single_value("System Settings", "currency_precision")
    
    columns = sorted(set(d['member_code'] for d in data))
    
    price = [0] * len(columns)
    discount_value = [0] * len(columns)
    grand_total = [0] * len(columns)
    total_payment = [0] * len(columns)
    payment_balance = [0] * len(columns)
    
    member_index = {member: index for index, member in enumerate(columns)}
    
    for d in data:
        member = d['member_code']
        index = member_index.get(member)
        if index is not None:
            price[index] += d.get('price', 0)
            discount_value[index] += d.get('discount_value', 0)
            grand_total[index] += d.get('grand_total', 0)
            total_payment[index] += d.get('total_payment_amount', 0)
            payment_balance[index] += d.get('payment_balance', 0)

    datasets = [
        {
            "name": 'Price',
            "values": [round(p, int(precision)) for p in price]
        },
        {
            "name": 'Discount',
            "values": [round(d, int(precision)) for d in discount_value]
        },
        {
            "name": 'Grand Total',
            "values": [round(g, int(precision)) for g in grand_total]
        },
        {
            "name": 'Payment Amount',
            "values": [round(p, int(precision)) for p in total_payment]
        },
        {
            "name": 'Payment Balance',
            "values": [round(e, int(precision)) for e in payment_balance]
        },
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
