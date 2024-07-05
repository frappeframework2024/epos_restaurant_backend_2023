from functools import lru_cache
import frappe
import json 

@lru_cache(maxsize=128)
def get_doctype_value_cache(doctype,doc_name, fieldname):
    if doc_name:
        return frappe.db.get_value(doctype,doc_name,fieldname)
    else:
        return frappe.db.get_single_value(doctype,fieldname)


@lru_cache(maxsize=128)
def get_doc_cache(doctype,doc_name):
    return frappe.get_doc(doctype,doc_name)

   
@lru_cache(maxsize=128)
def get_cache_data(doctype,docname,fields):
    data= frappe.db.sql("select {} from `tab{}` where name=%(name)s".format(",".join(fields.split(",")),doctype),{"name":docname},as_dict=1 )
    if data:
        return data[0]
    return None


@lru_cache(maxsize=128)
def get_default_account_from_pos_config(params):
    sql = """
            select 
                revenue_group, 
                default_income_account,
                default_expense_account 
            from `tabPOS Config Default Account` 
            where
                parent = %(pos_config)s and 
                revenue_group in %(revenue_groups)s and 
                business_branch = %(business_branch)s
            """
   
    data = frappe.db.sql(sql, json.loads(params),as_dict=1)
    return data

@lru_cache(maxsize=128)
def get_default_account_from_revenue_group(params):
    sql = """
            select 
                parent as revenue_group, 
                default_income_account,
                default_expense_account 
            from `tabRevenue Group Default Account` 
            where
                parent in %(revenue_groups)s and 
                business_branch = %(business_branch)s
            """
    data = frappe.db.sql(sql, json.loads(params),as_dict=1)
    return data