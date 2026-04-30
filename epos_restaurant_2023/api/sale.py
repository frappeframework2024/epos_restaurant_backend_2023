import frappe 

@frappe.whitelist(methods="POST")
def submit_order(data):
    if not data.get("doc").get("name"):
        frappe.get_doc(data.get("doc")).insert()

    frappe.db.commit()
    
