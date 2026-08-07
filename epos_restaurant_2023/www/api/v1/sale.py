import frappe

def get_context(context):
    frappe.response["message"] = {
        "status": "success",
        "hello": "world"
    }