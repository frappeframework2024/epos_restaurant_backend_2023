# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt


import frappe


def execute(filters=None):
	columns = get_report_columns(filters)
	data = get_report_data(filters)
	return columns, data

def get_report_columns(filters):
    columns = [
		{"fieldname":"product_code","label":"Product Code","fieldtype":"Link","options":"Product","align":"left","width":"150"},
		{"fieldname":"product_name", "label":"Product Name","align":"left","width":"250"},
		{"fieldname":"product_group", "label":"Product Group", "align":"left","width":"200"},
		{"fieldname":"product_category", "label":"Category", "align":"left","width":"200"},
		{"fieldname":"stock_location","label":"Warehouse","width":"150"}
    ]
    if filters.show_none_stock_product:
        columns.append(
            {"fieldname":"is_inventory_product","label":"Inventory Product","fieldtype":"Check","width":"150", "align":"center"}
        )
    columns = columns +[
		{"fieldname":"quantity","label":"Quantity", "fieldtype":"Float","align":"center","width":"80"},
		{"fieldname":"reorder_level","label":"Re-order Level", "fieldtype":"Float","align":"center"},
		{"fieldname":"unit","label":"Unit","width":"80"},
		{"fieldname":"cost","label":"Cost", "fieldtype":"Currency","width":100},
		{"fieldname":"total_cost","label":"Total Cost", "fieldtype":"Currency","width":"150"},
		{"fieldname":"expired_date","label":"Expired Date", "fieldtype":"Date"},
		{"fieldname":"expired_date_in_day","label":"Expired In", "fieldtype":"Int","align":"center"}
	]
    return columns

def get_report_data(filters):
    sql = """
		select slp.*,
			datediff(slp.expired_date,now()) as expired_date_in_day,
            coalesce(pc.name,'') as product_group,
            p.is_inventory_product
		from `tabProduct` p
        left join `tabStock Location Product` slp on slp.product_code = p.name
        left join `tabProduct Category` pc on pc.name = slp.product_category
		where
			1=1   
    """
    if not filters.show_none_stock_product:
        sql = sql + " and coalesce(p.is_inventory_product,0) = 1"
    if filters.business_branch:
        sql= sql + " and business_branch in %(business_branch)s "
    
    if filters.stock_location:
        sql= sql + " and  stock_location in %(stock_location)s "
    
    if filters.vendor:
        sql= sql + " and  vendor in %(vendor)s "

    if filters.product_category:
        sql= sql + " and  product_category = %(product_category)s "
        
    if filters.product_group and not filters.product_category:
        filters.product_groups = get_product_category_by_product_group(filters.product_group)
        sql= sql + " and  slp.product_category in %(product_groups)s "

    if filters.show_product_option=="Product With Zero Stock":
        sql = sql + " and quantity=0"
    elif filters.show_product_option=="Product to Order":
        sql = sql + " and quantity<=reorder_level"
    elif filters.show_product_option=="Product With Stock":
        sql = sql + " and (quantity>0 or quantity>reorder_level)"
    elif filters.show_product_option=="Product With Negative Stock":
        sql = sql + " and quantity<0"
    elif filters.show_product_option=="Product Expired":
        sql = sql + " and coalesce(expired_date,'')!='' and has_expired_date = 1 and expired_date<=now()"    
    elif filters.show_product_option=="Product Expired Within Day":
        if (filters.expired_day or 0) ==0:
            frappe.throw("Please enter expired within day")
        sql = sql + " and coalesce(expired_date,'')!='' and has_expired_date = 1 and datediff(expired_date,now()) between 0 and %(expired_day)s"
        
        
    data = frappe.db.sql(sql,filters,as_dict=1)
   
    
    if filters.order_by:
        sql= sql + " order by {} {}".format( get_order_by_field(filters), filters.order_by_type)
            
  
    return data

def get_order_by_field(fitlers):
    data = ["Product Name","Product Code","Category","Quantity","Expired Date"]
    key = ["product_name","product_code","product_category","quantity","expired_date"]
    return key[data.index(fitlers.order_by)]



def  get_product_category_by_product_group(parent):
    sql="""
        WITH RECURSIVE hierarchy AS (
            SELECT
                name,
                parent_product_category
            FROM
                `tabProduct Category`
            WHERE
                name = %(parent)s
             UNION ALL
            SELECT
                t.name as account,
                t.parent_product_category
                
            FROM
                `tabProduct Category` t
            JOIN
                hierarchy h ON t.parent_product_category = h.name
           
        )
        SELECT
            name
        FROM
            hierarchy

    """
    data = frappe.db.sql(sql,{"parent":parent},as_dict=1)
    return [d.get("name") for d in data]

    
    
