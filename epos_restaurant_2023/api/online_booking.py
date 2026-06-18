import frappe
@frappe.whitelist()
def get_device_booking(device_uuid=None):
    sql ="""
        select * from `tabPOS Reservation` where device_uuid = %(device_uuid)s
        order by 
        creation desc
    """
    data = frappe.db.sql(sql,{"device_uuid":device_uuid},as_dict = 1)
    return data

@frappe.whitelist(methods="POST")
def create_booking(data):
    # frappe.throw("You already have booking on on date {0}".format(data.get("arrival_date")))

    data["doctype"] = "POS Reservation"
    data["reservation_status"] = "Pending"
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)
    return doc
    
@frappe.whitelist(methods="POST")
def cancel_booking(data):
    # {"device_uuid":"111","booking_id":"bnookingid":"reason":"reson" }
    if frappe.db.exists("POS Reservation",{"name":data.get("booking_id"),"device_uuid":data.get("device_uuid")}):
        doc = frappe.get_cached_doc("POS Reservation",data.get("booking_id"))
        doc.reservation_status = "Cancelled"
        doc.cancelled_note = data.get("reason")
        doc.save(ignore_permissions=True)

        return doc

    frappe.throw("No booking found")

  



