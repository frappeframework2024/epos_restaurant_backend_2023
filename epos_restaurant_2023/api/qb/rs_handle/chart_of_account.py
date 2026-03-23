import frappe
from epos_restaurant_2023.api.qb.qbwc_helper import pretty_xml

## handle response chart of account
def handle_account_query(res,company_name):
    request_id = res.get("requestID")
    status_code = res.get("statusCode")
    status_msg = res.get("statusMessage")
    
    iterator_id = res.get("iteratorID")
    remaining = int(res.get("iteratorRemainingCount") or 0)
    
    
    # Check queue exists  
    existing = frappe.db.exists("Quickbooks Sync Queues", {"request_id": request_id})
    if not existing:
        msg = f"Queue not found: {request_id}"
        frappe.log_error(msg)
        print(msg)        
        return      
    
    queue = frappe.get_doc("Quickbooks Sync Queues", existing)
    
         
    # duplicate processing
    if queue.status == "Completed":
        return
    
    if status_code != "0":
        frappe.log_error(f"AccountQuery Failed: {status_msg}")
        queue.status = "Error"
        queue.response_message = f"[{status_code}] {status_msg}"
        queue.save(ignore_permissions=True)        
        return

    for acc in res.findall("AccountRet"):
        list_id = acc.findtext("ListID")
        name = acc.findtext("Name")
        full_name = acc.findtext("FullName")
        number = acc.findtext("AccountNumber")
        edit_sequence = acc.findtext("EditSequence")

        if not list_id:
            continue

        # Check if exists
        existing = frappe.db.exists("Quickbooks Data", {
            "qb_list_id": list_id,
            "data_type": "Chart Of Account"
        })

        if existing:
            doc = frappe.get_doc("Quickbooks Data", existing)
        else:
            doc = frappe.new_doc("Quickbooks Data")
            
        acc_xml_str = pretty_xml(acc)
        
        doc.qb_list_id = list_id
        doc.code = full_name
        doc.chart_of_account_full_name = full_name
        doc.data_type = "Chart Of Account"        
        doc.qb_raw_xml = acc_xml_str    
        doc.qb_company = company_name    
        doc.qb_edit_sequence = edit_sequence
        doc.description = f"{number}~{name}"        
        doc.save(ignore_permissions=True)
     
    
   
   
   # 🔁 Handle iterator (IMPORTANT)
    if remaining > 0:
        # Update current queue
        queue.iterator_id = iterator_id
        queue.remaining_count = remaining
        queue.status = "Pending"
        queue.response_message = f"Remaining: {remaining}"
        queue.save(ignore_permissions=True)

        # ➕ Create next queue
        new_queue = frappe.new_doc("Quickbooks Sync Queues")
        new_queue.request_id = queue.name  # same request chain
        new_queue.iterator_id = iterator_id
        new_queue.status = "Pending"
        new_queue.action = "Chart Of Account"
        new_queue.save(ignore_permissions=True)

    else:
        # ✅ Completed
        queue.status = "Completed"
        queue.response_message = "All accounts synced"
        queue.save(ignore_permissions=True)
        

