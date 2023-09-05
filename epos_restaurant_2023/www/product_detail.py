import frappe
def get_context(context):
 
    product = frappe.get_doc("Product",frappe.form_dict.product_code)
    context.doc = product