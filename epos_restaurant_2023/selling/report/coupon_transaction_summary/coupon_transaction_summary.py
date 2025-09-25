# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
 
def execute(filters=None):
	columns = get_columns(filters)
	data = get_report_data(filters)
	report_summary = get_report_summary(filters,[d for d in data if d.get("is_total_row") ==1])
	chart_data = get_report_chart(filters,columns,[d for d in data if not d.get("is_total_row") ])

	return columns, data,None,chart_data,report_summary

def get_columns(filters):
	columns = [
		{"fieldname":"posting_date","label":_("Date"),"fieldtype":"Data","width":125},
		{"fieldname":"total_coupon_sold","label":_("Total Coupon Sold"),"fieldtype":"Int"},
		{"fieldname":"sold_coupon_amount","label":_("Sale Coupon Amount"),"fieldtype":"Currency"},
		{"fieldname":"top_up_amount","label":_("Top Up Amount"),"fieldtype":"Currency"},
		{"fieldname":"used_coupon_amount","label":_("Used Amount"),"fieldtype":"Currency"},
		{"fieldname":"redeem_amount","label":_("Redeem Amount"),"fieldtype":"Currency"},
		{"fieldname":"unused_amount","label":_("Unused Amount"),"fieldtype":"Currency"}
	]
	return columns

def get_report_data(filters):
	sql = """
		select 
			 DATE_FORMAT(posting_date, '%%d-%%m-%%Y') as posting_date,
			sum(transaction_type = 'Sale Coupon') as total_coupon_sold,
			sum(if(transaction_type='Sale Coupon', coupon_amount,0)) as sold_coupon_amount,
			sum(if(transaction_type='Top Up', coupon_amount,0)) as top_up_amount,
			sum(if(transaction_type = 'Used', coupon_amount,0)) as used_coupon_amount,
			sum(if(transaction_type='Redeem', coupon_amount,0)) as redeem_amount
		from `tabCoupon Transaction` 
		where
			posting_date between %(start_date)s and %(end_date)s and 
			coalesce(status,'') <> 'Deleted'    
			{additional_filter}		
		group by 
			posting_date
		order by posting_date
	"""

	additional_filter = ""
	if filters.pos_profile:
		additional_filter = " and pos_profile in %(pos_profile)s "

	if filters.business_branch:
		additional_filter =  additional_filter + " and business_branch in %(business_branch)s "


	sql = sql.format(additional_filter = additional_filter)
 
	
	data =  frappe.db.sql(sql,filters, as_dict = 1)
 
	unused_amount_data = get_unused_coupon_amount(filters)
	for d in data:
		unused_amount =  next((item for item in unused_amount_data if item.get("posting_date") == d.get("posting_date")), None)
		if unused_amount:
			d["unused_amount"] = unused_amount.get("unused_amount") or 0


	# add total row
	total_row = {
			"posting_date":"Total",
			"is_total_row":1,
		}
	for c in ["total_coupon_sold","sold_coupon_amount","top_up_amount","used_coupon_amount","redeem_amount","unused_amount"]:
		total_row[c] = sum([d.get(c) for d in data])
	data.append(total_row)

	return data



def get_unused_coupon_amount(filters):
	sql = """
		select 
			DATE_FORMAT(posting_date, '%%d-%%m-%%Y') as posting_date,
			sum(coupon_amount) as  unused_amount
		from `tabCoupon Transaction` 
		where
			posting_date between %(start_date)s and %(end_date)s and 
			coalesce(status,'') <> 'Deleted'    
			{additional_filter}		
		group by 
			posting_date
	"""

	additional_filter = ""
	if filters.pos_profile:
		additional_filter = " and pos_profile in %(pos_profile)s "

	if filters.business_branch:
		additional_filter =  additional_filter + " and business_branch in %(business_branch)s "


	sql = sql.format(additional_filter = additional_filter)
	
	return frappe.db.sql(sql,filters, as_dict = 1)


def get_report_summary(filters,data):
	if filters.show_summary==0:
		return None

	if not data:
		return None
	 
	return [
		{
		"value": data[0].get("total_coupon_sold"),
		"indicator": "Blue",
		"label": _("Total Coupon Sold"),
		"datatype": "Int",
		},
		{
		"value": data[0].get("sold_coupon_amount"),
		"indicator": "Green",
		"label": _("Sale Coupon Amount"),
		"datatype": "Currency",
		},
		{
		"value": data[0].get("top_up_amount"),
		"indicator": "Green",
		"label": _("Top Up Amount"),
		"datatype": "Currency",
		},
		
		{
		"value": data[0].get("used_coupon_amount"),
		"indicator": "Orange",
		"label": _("Used Coupon Amount"),
		"datatype": "Currency",
		},
		
		{
		"value": data[0].get("redeem_amount"),
		"indicator": "Red",
		"label": _("Redeem Amount"),
		"datatype": "Currency",
		},
		
		{
		"value": data[0].get("unused_amount"),
		"indicator": "Blue",
		"label": _("Unused Amount"),
		"datatype": "Currency",
		},
	]
	


def get_report_chart(filters,columns,data):
	if filters.chart_type == "None":
		return None
	chart_data = {
            "data": {
                "labels": [d.get("posting_date") for d in data],
				"datasets":[]
            },
            "type": filters.chart_type,
            
        }
	# add data set 
	for c in ["total_coupon_sold","sold_coupon_amount","top_up_amount","used_coupon_amount","redeem_amount","unused_amount"]:
		chart_data["data"]["datasets"].append(
                    {
                        "name": next((d for d in columns if d.get("fieldname") == c ),None).get("label"),
                        "values": [d.get(c) for d in data]
                    } 
		)
	frappe.msgprint(str(data))
	return chart_data