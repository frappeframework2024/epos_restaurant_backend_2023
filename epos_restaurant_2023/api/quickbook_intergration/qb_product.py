import frappe
from frappe import _
from epos_restaurant_2023.api.quickbook_intergration.api import (post_api,get_api, get_list)


@frappe.whitelist() 
def get_all():
    query = "SELECT * FROM Item ORDER BY Id"
    return get_list(key="Item", query=query)

@frappe.whitelist(allow_guest=True, methods="POST")
def create_item():
    body ={
        "Name": "Sample Item",
        "Type": "Inventory",
        "IncomeAccountRef": {
            "value": "1",
            "name": "Sales"
        },
        "ExpenseAccountRef": {
            "value": "456",
            "name": "Expenses"
        },
        "AssetAccountRef": {
            "value": "789",
            "name": "Inventory Asset"
        },
        "QtyOnHand": 100,
        "UnitPrice": 20.00
        }

    resp = post_api("item",body=body)
    return resp.json()
