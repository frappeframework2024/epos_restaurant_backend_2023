import frappe
from epos_restaurant_2023.api.qb.qbwc_helper import pretty_xml

## handle response payment type
def handle_payment_method_query(res,company_name):
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

    if status_code != "0":
        frappe.log_error(f"PaymentMethodQuery Failed: {status_msg}")
        queue.status = "Error"
        queue.response_message = f"[{status_code}] {status_msg}"
        queue.save(ignore_permissions=True)
        return

    # Process Payment Methods
    for pm in res.findall("PaymentMethodRet"):
        list_id = pm.findtext("ListID")
        name = pm.findtext("Name")
        edit_sequence = pm.findtext("EditSequence")
        
        if not list_id:
            continue

        existing = frappe.db.exists("Quickbooks Data",  {
                "qb_list_id": list_id,
                "data_type": "Payment Type"
            })
        
        if existing:
            doc = frappe.get_doc("Quickbooks Data", existing)
        else:
            doc = frappe.new_doc("Quickbooks Data")

        # Save raw XML if needed
        pm_xml_str = pretty_xml(pm) 
        
        doc.qb_list_id = list_id
        doc.code = name
        doc.data_type = "Payment Type"
        doc.qb_company = company_name    
        doc.qb_edit_sequence = edit_sequence
        doc.qb_raw_xml = pm_xml_str
        
        doc.save(ignore_permissions=True)

    # Update queue
    queue.status = "Completed"
    queue.response_message = status_msg
    queue.save(ignore_permissions=True)



