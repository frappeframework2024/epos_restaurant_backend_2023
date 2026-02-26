import frappe

def get_context(context):
    frappe.local.response["type"] = "json"
    frappe.local.response["message"] = "OK"