import frappe
from frappe import _
import urllib.parse
from epos_restaurant_2023.api.quickbook_intergration.api import (post_api,get_api, get_list)


@frappe.whitelist()
def get_product_autocomplete(name=None): 
    qb_query = "SELECT Name FROM Item ORDER BY Id ASC"
    if name:
        qb_query = "SELECT Name FROM Item WHERE Name LIKE '{}'  ORDER BY Id ASC ".format(urllib.parse.quote(("%{}%".format(name)))) 

    data = get_list(key="Item", max = 10, query=qb_query)
    return [d["Name"] for d in data]


@frappe.whitelist()
def get_product_by_name(name):
    query = "SELECT Id FROM Item Where Name ='{}'".format(name)
    data = get_list(key="Item", query=query)
    if len(data) > 0:
        return data[0]
    frappe.throw(_("Invalid Item"))


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



    