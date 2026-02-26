# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_report_data(filters)
	summary = get_report_summary(filters, [d for d in data if d.get("is_total_row") == 1][0])
	if filters.show_summary:
		summary.insert(0,{
			"label": _("Total Coupons"),
					"value": len(data) -1,
					"datatype": "Int",
					"indicator": "Blue"
	})
	chart_data = get_report_chart(filters,[d for d in data if d.get("is_total_row") == 1][0])
	return columns, data,None,chart_data,summary





def get_columns():
	return [
		{"fieldname":"coupon","label":_("Coupon Number"),"fieldtype":"Data","align":"center"},
		{"fieldname":"sale","label":_("Sale #"),"fieldtype":"Data","align":"center","width":150},
		{"fieldname":"sale_date","label":_("Sale Date"),"fieldtype":"Date","align":"center"},
		{"fieldname":"sale_amount","label":_("Sale Amount"),"fieldtype":"Currency","align":"right"},
		{"fieldname":"top_up_amount","label":_("Top Up Amount"),"fieldtype":"Currency","align":"right"},
		{"fieldname":"used_amount","label":_("Used Amount"),"fieldtype":"Currency","align":"right"},
		{"fieldname":"redeem_amount","label":_("Redeem Amount"),"fieldtype":"Currency","align":"right"},
		{"fieldname":"balance","label":_("Balance"),"fieldtype":"Currency","align":"right"},
	]

def get_report_data(filters):
	sql="""
		select 
			coupon,
			sale,
			sale_date,
			coupon_value as sale_amount,
			top_up_coupon_value as top_up_amount,
			use_coupon_value as used_amount,
			redeem_coupon_value as redeem_amount,
			balance_coupon_value as balance
		from `tabCoupon Codes`
		where
			coalesce(sale,'') <> '' and 
			sale_date between %(start_date)s and %(end_date)s 

	
	"""
	if filters.show_coupons_have_balance:
		sql = sql + " and balance_coupon_value>0"

	sql = sql + " order by coupon"

	
	data =  frappe.db.sql(sql,filters,as_dict=1)

	total_row = {"coupon":_("Total"),"is_total_row":1}
	for c in ["sale_amount","top_up_amount","redeem_amount","used_amount","balance"]:
		total_row[c] = sum([d.get(c) for d in data])
	data.append(total_row)

	return data


def get_report_summary(filters,data):
	if not filters.show_summary :
		return None
	return [
            {
                "label": _("Sale Amount"),
                "value": data.get("sale_amount"),
                "datatype": "Currency",
                "indicator": "Blue"
            }, 

            {
                "label": _("Top Amount"),
                "value": data.get("top_up_amount"),
                "datatype": "Currency",
                "indicator": "Blue"
            }, 
            {
                "label": _("Used Amount"),
                "value": data.get("used_amount"),
                "datatype": "Currency",
                "indicator": "Orange"
            } ,
            {
                "label": _("Redeem Amount"),
                "value": data.get("used_amount"),
                "datatype": "Currency",
                "indicator": "Red"
            } ,
			 {
                "label": _("Balance"),
                "value": data.get("balance"),
                "datatype": "Currency",
                "indicator": "Green"
            } 


        ]


def get_report_chart(filters,data):
	if filters.chart_type == "None":
		return None

	chart_data = {
            "data": {
                "labels": [
                    "Coupon Sold"
                ],
                "datasets": [
                    {
                        "name": _("Coupon Amount"),
                        "values": [
                           data.get("coupon_amount")
                        ],
						
                    },
                    {
                        "name": _("Top Up Amount"),
                        "values": [
                            data.get("top_up_amount")
                        ]
                    },
                    {
                        "name": _("Used Amount"),
					 
                        "values": [
                           data.get("used_amount")
                        ]
                    },
                    {
                        "name": _("Redeem Amount"),
                        "values": [
                            data.get("redeem_amount")
                        ]
                    },
                    {
                        "name": _("Balance"),
                        "values": [
                            data.get("balance")
                        ]
                    }

                ]
            },
            "type": filters.chart_type,
            "lineOptions": {
                "regionFill": 1
            },
            "axisOptions": {
                "xIsSeries": 1
            }
        }

	return chart_data