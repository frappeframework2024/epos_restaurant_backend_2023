import frappe
from frappe import _
import urllib.parse
from epos_restaurant_2023.api.quickbook_intergration.api import ( get_list,get_api)

@frappe.whitelist()
def get_payment_type_autocomplete():
    query = "SELECT Name FROM PaymentMethod ORDER BY Id ASC"
    data = get_list(key="PaymentMethod", query=query)
    return [p["Name"] for p in data]

@frappe.whitelist()
def get_payment_type_by_name(name):
    query = "SELECT Name,Type,Active,Id FROM PaymentMethod Where Name ='{}'".format(name)
    data = get_list(key="PaymentMethod", query=query)
    if len(data) > 0:
        return data[0]
    frappe.throw(_("Invalid QB Payment Method"))