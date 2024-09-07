import frappe
from frappe import _
from epos_restaurant_2023.api.quickbook_intergration.api import (post_api,get_api, get_list)


@frappe.whitelist() 
def get_all():
    query = "SELECT * FROM Item ORDER BY Id"
    return get_list(key="Item", query=query)



@frappe.whitelist(allow_guest=True, methods="GET")
def get_query(table,query): 
    return get_list(key=table, query=query)


@frappe.whitelist(allow_guest=True, methods="GET")
def create_item(data): 
    resp = post_api("item",headers={"Content-Type":"application/json"}, body=data)
    return resp.json()



    