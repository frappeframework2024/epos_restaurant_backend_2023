import frappe
@frappe.whitelist()
def hello(value):
    return  "Hello World!==" + str(value)
@frappe.whitelist()
def get_jinja_filters():
    return {
        "hello": hello
        }
