import frappe
from epos_restaurant_2023.api.qb.qbwc_helper import pretty_xml
from frappe.model.naming import make_autoname

## handle response invoice add
def handle_invoice_query(res):
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
        frappe.log_error(f"InvoiceAdd  Failed: {status_msg}")
        queue.status = "Error"
        queue.response_message = f"[{status_code}] {status_msg}"
        queue.save(ignore_permissions=True)
        return

    
     # Parse InvoiceRet
    invoice = res.find("InvoiceRet")
    if not invoice:
        queue.status = "Error"
        queue.response_message = "No InvoiceRet found"
        queue.save(ignore_permissions=True)
        return
    
    txn_id = invoice.findtext("TxnID")
    balance_remaining = float(invoice.findtext("BalanceRemaining") or 0)

    ## update currency queues
    queue.status = "Completed"
    queue.response_message = status_msg
    queue.save(ignore_permissions=True)
    
    
    # If invoice has balance, create ReceivePayment queue
    if balance_remaining > 0 :                
        doc = frappe.new_doc("Quickbooks Sync Queues")
        doc.action = "Add"
        doc.request_id = txn_id
        doc.status = "Pending"
        doc.action_type = "Sale Payment"
        doc.business_branch = queue.business_branch
        doc.code = make_autoname("QBRP.-.#####")
        doc.insert()
    
    frappe.db.commit()
        



