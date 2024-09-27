import frappe
from frappe import _
import urllib.parse
from epos_restaurant_2023.api.quickbook_intergration.api import (post_api,get_api, get_list)


@frappe.whitelist()
def get_customer_autocomplete(name=None): 
    qb_query = "SELECT DisplayName FROM Customer ORDER BY Id ASC"
    if name:
        qb_query = "SELECT DisplayName FROM Customer WHERE DisplayName LIKE '{}'  ORDER BY Id ASC ".format(urllib.parse.quote(("%{}%".format(name)))) 

    data = get_list(key="Customer", max = 10, query=qb_query)
    return [d["DisplayName"] for d in data]

@frappe.whitelist()
def get_customer_by_name(name):
    query = "SELECT Id FROM Customer Where DisplayName ='{}'".format(name)
    data = get_list(key="Customer", query=query)
    if len(data) > 0:
        return data[0]
    frappe.throw(_("Invalid Customer"))

@frappe.whitelist() 
def get_customer_types():
    query = "SELECT * FROM CustomerType"
    return get_list(key="CustomerType", query=query)





