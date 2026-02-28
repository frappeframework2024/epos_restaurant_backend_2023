#~app/epos_restaurant_2023/epos_restaurant_2023/helpers/payway_helper.py

from frappe import _
import frappe
import requests
from epos_restaurant_2023.api.api import get_estc_connection
from datetime import datetime, timezone,timedelta
from frappe.utils import now_datetime,pretty_date



def validate_on_refund_transaction(param):
    p = param
    tran_id = p.get("tran_id")
    sql = """select name from `tabSale Payment` where aba_pay_transaction = %(tran_id)s"""
    docs = frappe.db.sql(sql,{"tran_id":tran_id}, as_dict=True)
    #Check if the transaction is older than 1 hour
    transactions = []
    for d in docs:
        doc = frappe.get_doc("Sale Payment", d.name)
        if not (doc.creation + timedelta(hours=1) < now_datetime()):
            transactions.append({
                "tran_id": doc.aba_pay_transaction,
                "timeago":pretty_date(doc.creation),
                "creation":doc.creation,
                "now":now_datetime()
            })  
            
    if len(transactions)  <= 0:
        frappe.local.response.update({
            "status_code":f"{404}",
            "message": "The transaction is more than 1 hour not allow to refund",
            "http_status_code": 404
        })
        return  
    
    return transactions

#method refund payment enqueue job
def aba_refund_payment_enqueue(param,sale_doc):
    frappe.enqueue(
        "epos_restaurant_2023.helpers.payway_helper.on_aba_refund_payment", # python function or a module path as string
        queue="short", # one of short, default, long
        job_name="aba_refund_payment", # specify a job name
        param = param,
        sale_doc = sale_doc
    )
    
    return {
        "status": "queued",
        "message": "Refund is being processed"
    }
    

# refund payment
def on_aba_refund_payment(param, sale_doc=None):
    p =  param
    transtions = validate_on_refund_transaction(param=p)
    if not transtions:
        return

    conn =  get_estc_connection()
    if not  conn.get("estc_payway_socket_server_url",None):
        status_code = 404
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message":"This feature is currently unavailable.",
            "http_status_code": status_code
        })
        return

    if not conn.get("estc_central_url", None) :
        status_code = 422
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": "The 'estc_central_url' is not configured in site settings. Please contact your system administrator.",
            "http_status_code": status_code
        })
        return


    estc_central_url = conn.get("estc_central_url", None) or ""
    url = f"{estc_central_url}/api/method/estc.api.payway.aba_refund_payment"


    t = transtions[0]
    # Make POST request
    ## verify=False is equivalent to CURLOPT_SSL_VERIFYPEER=false
    p["tran_id"] = t.get("tran_id")
    response = requests.post(url, json=p, verify=False)
    try:
        data = response.json()
    except Exception :
        data = {}

    status_code = response.status_code
    if status_code not in [200,201]:
        frappe.log_error(
            frappe.as_json(data),
            "REFUND FAILED"
        )
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": data.get("message"),
            "http_status_code": status_code
        })
        return
    
    if sale_doc:  
        if p.get("refunded_type",None) == "Manual":
            sale_doc.db_set({
                "sale_status":"Closed - Refunded",
                "sale_status_color":"#EC864B"
            },update_modified=False)
         
        note = "{}: {}".format((p.get("refunded_type",None) or ""), (p.get("refunded_note",None) or ""))
        doc_comment = frappe.get_doc({
            'doctype': 'Comment',
            'subject': 'ABA generate KHQR',
            "comment_type":"Info",
            "reference_doctype":"Sale",
            "reference_name":sale_doc.name,
            "comment_by":p.get("refunded_by"),
            "custom_note":note,
            "content":note
        })
        doc_comment.insert(ignore_permissions=True)

    return data


    


@frappe.whitelist()
def create_error_log_enqueue(params, error):
    frappe.enqueue(
            "epos_restaurant_2023.helpers.payway_helper.create_error_log", # python function or a module path as string
            queue="short", # one of short, default, long
            job_name="create_payway_integration_log", # specify a job name
            # enqueue_after_commit=True,
            params = params,
            error = error
        )

@frappe.whitelist()   
def create_error_log(params, error):
    try: 
        #remove key
        error.pop("http_status_code",None)
        #create logs
        doc = frappe.new_doc("PayWay Error Logs")
        doc.request_params =frappe.as_json(params)
        doc.error_message = frappe.as_json(error)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title="PayWay Error Logs",
            message=frappe.get_traceback()
        )

@frappe.whitelist(allow_guest=True) 
def update_payway_tranaction_id_on_callback_success_enqueue(tran):
    frappe.enqueue(
            "epos_restaurant_2023.helpers.payway_helper.update_payway_tranaction_id_on_callback_success", # python function or a module path as string
            queue="short", # one of short, default, long
            job_name="update_payway_tranaction_id_on_callback_success", # specify a job name
            enqueue_after_commit=True,
            tran = tran
        )
    # return update_payway_tranaction_id_on_callback_success_enqueue(tran)

@frappe.whitelist() 
def update_payway_tranaction_id_on_callback_success(tran):
    (tran.get("response") or {}).pop("temp_tran_id",None)
    update_sql = """
        UPDATE `tabSale`
        SET payment_transaction = CONCAT(
            IFNULL(payment_transaction, ''),
            %(tran)s
        )
        WHERE name = %(invoice_id)s
    """
    filters = {"tran":frappe.as_json(tran), "invoice_id":  (tran.get("response") or {}).get("invoice_id") }
    frappe.db.sql(update_sql,filters)
    frappe.db.commit()

    return "update success"

