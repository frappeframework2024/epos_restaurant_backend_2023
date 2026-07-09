import frappe
@frappe.whitelist()
def get_device_booking(device_uuid=None):
    sql ="""
        select * from `tabPOS Reservation` where device_uuid = %(device_uuid)s
        order by 
        arrival_date desc
    """
    data = frappe.db.sql(sql,{"device_uuid":device_uuid},as_dict = 1)
    return data

@frappe.whitelist(methods="POST")
def create_booking(data):
    # frappe.throw("You already have booking on on date {0}".format(data.get("arrival_date")))
    data["doctype"] = "POS Reservation"
    data["reservation_status"] = "Pending"
    data["guest"] = get_customer_id(data)
    data["property"] =  "ESTC HOTEL 6"

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

def get_customer_id(data):  
    sql = "select distinct guest from `tabPOS Reservation` where device_uuid=%(device_uuid)s and coalesce(guest,'')!='' limit 1"
    guest_data = frappe.db.sql(sql,{"device_uuid":data.get("device_uuid")},as_dict = 1)
    if len(guest_data)>0:
        return guest_data[0].get("guest")
    
    if not frappe.db.exists("Customer Group","Online Customer"):
        frappe.get_doc({"doctype":"Customer Group","customer_group_en":"Online Customer","customer_group_kh":"Online Customer"}).insert(ignore_permissions=True)
    
    doc = frappe.get_doc({
        "doctype":"Customer",
        "customer_group": "Online Customer",
        "customer_name_en": data.get("guest_name"),
        "phone_number":data.get("phone_number")
    }).insert(ignore_permissions=True)

    return doc.name


  



