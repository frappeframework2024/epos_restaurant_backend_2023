import frappe
from epos_restaurant_2023.api.qb.qbwc_helper import pretty_xml

## handle response customer
def handle_customer_query(res, company_name):
    request_id = res.get("requestID")
    status_code = res.get("statusCode")
    status_msg = res.get("statusMessage")

    # Check queue exists  
    existing = frappe.db.exists("Quickbooks Sync Queues", {"request_id": request_id})
    if not existing:
        msg = f"Queue not found: {request_id}"
        frappe.log_error(msg)
        print(msg)        
        return      
    
    queue = frappe.get_doc("Quickbooks Sync Queues", existing)

    # Avoid duplicate processing
    if queue.status == "Completed":
        return

    # ❌ Error handling
    if status_code != "0":
        frappe.log_error(f"CustomerQuery Failed: {status_msg}")
        queue.status = "Error"
        queue.response_message = f"[{status_code}] {status_msg}"
        queue.save(ignore_permissions=True)
        return

    # ✅ IMPORTANT: use .// to find nested nodes
    for d in res.findall(".//CustomerRet"):
        list_id = d.findtext("ListID")
        name = d.findtext("Name")
        full_name = d.findtext("FullName")   # 🔥 IMPORTANT
        edit_sequence = d.findtext("EditSequence")
        parent = d.findtext("ParentRef/FullName")

        if not list_id:
            continue

        # Check existing
        existing = frappe.db.exists("Quickbooks Data", {
            "qb_list_id": list_id,
            "data_type": "Customer"
        })

        if existing:
            doc = frappe.get_doc("Quickbooks Data", existing)
        else:
            doc = frappe.new_doc("Quickbooks Data")

        # Save raw XML
        data_xml_str = pretty_xml(d)

        # Map fields
        doc.qb_list_id = list_id
        doc.code = full_name
        doc.data_type = "Customer"
        doc.qb_company = company_name
        doc.qb_edit_sequence = edit_sequence        
        # doc.qb_full_name = full_name          # 🔥 useful
        # doc.parent_customer = parent          # 🔥 hierarchy
        doc.qb_raw_xml = data_xml_str

        doc.save(ignore_permissions=True)

    # ✅ Update queue
    queue.status = "Completed"
    queue.response_message = status_msg
    queue.save(ignore_permissions=True)

