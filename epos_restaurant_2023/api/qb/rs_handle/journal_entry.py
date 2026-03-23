import frappe
from epos_restaurant_2023.api.qb.qbwc_helper import pretty_xml

## handle response add journal 
def handle_journal_entry_add(res):
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
    
    # duplicate processing
    if queue.status == "Completed":
        return

    if status_code == "0":
        txn = res.find("JournalEntryRet")
        queue.status = "Completed"
        queue.qb_txn_id = txn.findtext("TxnID") if txn is not None else None
        queue.qb_edit_sequence = txn.findtext("EditSequence") if txn is not None else None
        queue.qb_txn_number = txn.findtext("TxnNumber") if txn is not None else None
        queue.response_message = status_msg

    else:
        queue.status = "Error"
        queue.response_message = f"[{status_code}] {status_msg}"

    queue.save(ignore_permissions=True)