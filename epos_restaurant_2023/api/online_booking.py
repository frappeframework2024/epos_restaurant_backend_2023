import frappe
@frappe.whitelist()
def get_device_booking(device_uuid=None):
    data = frappe.db.sql("select * from `tabRestaurant Booking`",as_dict = 1)
    return data