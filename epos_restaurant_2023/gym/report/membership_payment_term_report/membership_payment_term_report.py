# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
 
	return columns, data

def get_columns(filters):
	columns = []

	columns.append({"label":"Doc. #", "fieldname":"name","fieldtype":"Link","options":"Membership", "align":"center","width":120})
	columns.append({"label":"Register",  "fieldname":"posting_date","fieldtype":"Date", "align":"center","width":120})
	columns.append({"label":"Code", "fieldname":"customer","fieldtype":"Data","align":"left","width":100})
	columns.append({"label":"Member", "fieldname":"member_name","fieldtype":"Data","align":"left","width":150})
	columns.append({"label":"Member Type", "fieldname":"customer_group","fieldtype":"Data","align":"left","width":150})
	columns.append({"label":"Gender", "fieldname":"gender","fieldtype":"Data","align":"center","width":70})
	columns.append({"label":"Membership Option", "fieldname":"membership_type","fieldtype":"Data","align":"left","width":250})
	columns.append({"label":"Price", "fieldname":"price","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"Discount", "fieldname":"total_discount","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"Grand Total", "fieldname":"grand_total","fieldtype":"Currency","align":"right","width":100})
	columns.append({"label":"Payment Term", "fieldname":"payment_term","fieldtype":"Long Text","align":"left","width":350})

	return columns

def get_data(filters):
    sql = """
    select 	
		m.`name`,
		m.posting_date,
		m.customer,
		c.customer_group,
		m.gender,
		m.member_name, 
		m.membership_type,
		m.price,
		m.total_discount,
		m.grand_total,
		m.start_date,
		m.end_date as expiry_date,
		(select GROUP_CONCAT(CONCAT(' - Payment Date: ', pt.payment_date, ', Amount: $', FORMAT(pt.payment_amount,2), if(coalesce(pt.note,'')='','', concat( 'Note: ', coalesce(pt.note,'')) ) ,'' ) SEPARATOR '\n')  from `tabMembership Payment Term` pt where pt.parent = m.name order by pt.payment_date, pt.idx) as payment_term
	from `tabMembership` m
	inner join `tabCustomer` c on m.customer = c.`name`
	where 1 = 1
		and m.docstatus = 1
		and m.posting_date BETWEEN %(start_date)s and %(end_date)s
    """
    if filters.customer_group:
        sql += " and c.customer_group in %(customer_group)s"
    data = frappe.db.sql(sql, {
        "start_date":filters.start_date, 
        "end_date":filters.end_date, 
        "customer_group":filters.customer_group
    }, as_dict=True)
    
    return data