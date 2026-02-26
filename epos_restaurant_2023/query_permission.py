import frappe
def get_employee_permission(user):
    if user != "Administrator":
        return "(`tabEmployee`.employee_name not in ('Pheakdey','Test'))"

# def product_filters(filters):
#     return "(`tabProduct`.status not in ('Variant','Disabled'))"
