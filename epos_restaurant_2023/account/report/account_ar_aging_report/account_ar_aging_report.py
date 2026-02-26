# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_report_columns(filters)
 
	report_data = get_report_data(filters)
	summary = None if not filters.show_summary else get_report_summary([d for d in report_data if "is_total_row" in d and d["is_total_row"]==1])
	chart = None if not filters.show_chart else get_report_chart([d for d in report_data if "is_total_row" in d and d["is_total_row"]==1])
	return columns,report_data,None, chart,summary,

def get_report_columns(filters):
    columns=[
		{"fieldname":"name", "label":_("Customer #"),"fieldtype":"Link","options":"Customer","align":"center","width":150},
		{"fieldname":"customer_name", "label":_("Customer Name"),"width":200},
		{"fieldname":"phone_number", "label":_("Phone"),"align":"left","width":150},
		{"fieldname":"amount_current_day", "label":_("Current"), "fieldtype":"Currency","align":"right","width":125 },
		{"fieldname":"amount_30_day", "label":_("30 Days"), "fieldtype":"Currency","align":"right", "width":125 },
		{"fieldname":"amount_60_day", "label":_("60 Days"), "fieldtype":"Currency","align":"right", "width":125 },
		{"fieldname":"amount_90_day", "label":_("90 Days"), "fieldtype":"Currency","align":"right", "width":125 },
		{"fieldname":"amount_120_plus_day", "label":_("120+ Days"), "fieldtype":"Currency","align":"right", "width":125 },
		{"fieldname":"balance", "label":_("Balance"), "fieldtype":"Currency","align":"right", "width":125 },
	]
    
    return columns

def get_report_data(filters):
	sql = """
		select 
			name ,
			customer_name_en as customer_name,
			 
			phone_number,
   			0 as balance
		from `tabCustomer` 
	"""
	if filters.customer:
		sql = sql + "  where  name = %(customer)s"

	report_data =  frappe.db.sql(sql, filters,as_dict =1)

	# get gl data
	general_ledger_data = get_general_ledger_data(filters)
	exist_customers = list(set([d["customer"] for d in general_ledger_data]))
	report_data = [d for d in report_data if d["name"] in exist_customers]
  
	range_data =[
		{"fieldname":"amount_current_day", "min":0,"max":1},
		{"fieldname":"amount_30_day", "min":1,"max":31},
		{"fieldname":"amount_60_day", "min":31,"max":61},
		{"fieldname":"amount_90_day", "min":61,"max":91},
		{"fieldname":"amount_120_plus_day", "min":91,"max":10000000},
	]

	for c in report_data:
		for r in range_data:
			c[r["fieldname"]] = sum([d["amount"] for d in general_ledger_data if d["customer"] == c["name"] and d["day"] in range(r["min"],r["max"]) ])	
			c["balance"] = c["balance"] + c[r["fieldname"]] 

	total_row = {
		"is_total_row":1,
		"name":"Total",

	}
	for r in range_data:
		total_row[r["fieldname"]] = sum([d[r["fieldname"]] for d in report_data if r["fieldname"] in d])	
	total_row["balance"] = sum([d["balance"] for d in report_data if "balance" in d])	
	report_data.append(total_row)
	return report_data

def get_report_summary(data):
	if not data:
		return None
	else:
		data = data[0]
	 
		return [
			{"label":"Current","color":"green",  "datatype": "Currency", "value":data["amount_current_day"]},
			{"label":"30 Days", "color":"blue", "datatype": "Currency", "value":data["amount_30_day"]},
			{"label":"60 Days", "color":"yello", "datatype": "Currency", "value":data["amount_60_day"]},
			{"label":"90 Days", "color":"orange", "datatype": "Currency", "value":data["amount_90_day"]},
			{"label":"120+ Days",  "color":"red", "datatype": "Currency", "value":data["amount_120_plus_day"]},
			
			
		]


def get_general_ledger_data(filters):
	sql="""
		select 
			a.party as customer,
			DATEDIFF(%(date)s,a.posting_date) as day,
			sum(a.debit_amount-a.credit_amount) as amount
		from `tabGeneral Ledger` a
		inner join `tabChart Of Account` b on b.name = a.account

		where 
			b.account_type = 'Receivable' and 
			a.party_type = 'Customer' and 
			
			a.business_branch = %(business_branch)s and 
			a.posting_date <= %(date)s 
		
	"""
	if filters.customer:
		sql = sql + " and a.party =%(customer)s"

	sql = sql + """
		group by
			a.party,
			DATEDIFF(%(date)s,a.posting_date)
		having sum(a.debit_amount-a.credit_amount)  != 0
	"""
 
	return frappe.db.sql(sql, filters, as_dict=1)



def get_report_chart(data):
	if not data:
		return None
	else:
		data = data[0]
		chart_data = []
		chart_data.append(data["amount_current_day"])
		chart_data.append(data["amount_30_day"])
		chart_data.append(data["amount_60_day"])
		chart_data.append(data["amount_90_day"])
		chart_data.append(data["amount_120_plus_day"])
		chart =  {'data':
					{
						'labels':[_('Current'),_("30 Days"),_("60 Days"),_("90 Days"),_("120+ Days")],
						'datasets':[
									{'values':chart_data,},

								]
					},
					'type':'percentage'
				}
		return chart
