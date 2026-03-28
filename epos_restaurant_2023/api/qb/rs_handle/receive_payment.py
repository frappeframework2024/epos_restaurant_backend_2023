import frappe

def handle_receive_payment_query(res):
    queue_id = res.get("requestID")
    status_code = res.get("statusCode")
    status_msg = res.get("statusMessage")

    # Check queue exists  
    existing = frappe.db.exists("Quickbooks Sync Queues", queue_id)
    if not existing:
        msg = f"Queue not found: {queue_id}"
        frappe.log_error(msg)
        print(msg)        
        return      
    
    queue = frappe.get_doc("Quickbooks Sync Queues", existing)

    # Avoid duplicate processing
    if queue.status == "Completed":
        return

    # Check for errors
    if status_code != "0":
        frappe.log_error(f"ReceivePaymentAdd Failed: {status_msg}")
        queue.status = "Error"
        queue.response_message = f"[{status_code}] {status_msg}"
        queue.save(ignore_permissions=True)
        return

    # Parse ReceivePaymentRet
    payment = res.find("ReceivePaymentRet")
    if not payment:
        queue.status = "Error"
        queue.response_message = "No ReceivePaymentRet found"
        queue.save(ignore_permissions=True)
        return

    txn_id = payment.findtext("TxnID")
    total_amount = float(payment.findtext("TotalAmount") or 0)
    deposit_account = payment.findtext("DepositToAccountRef/FullName") or ""

    # Parse applied invoices
    applied_invoices = []
    for applied in payment.findall("AppliedToTxnRet"):
        amount = (
            applied.findtext("PaymentAmount")
            or applied.findtext("Amount")
            or applied.findtext("AppliedAmount")
            or 0
        )
        
        applied_invoices.append({
            "TxnID": applied.findtext("TxnID"),
            "PaymentAmount": float(amount)
        })

    # Update queue with success info
    queue.status = "Completed"
    queue.response_message = (
        f"{status_msg}. TxnID={txn_id}, TotalPaid={total_amount}, "
        f"DepositedTo={deposit_account}, AppliedInvoices={applied_invoices}"
    )
    
    queue.save(ignore_permissions=True)