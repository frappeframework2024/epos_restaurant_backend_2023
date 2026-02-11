
from frappe import _
import frappe
import requests
import time
import hashlib
import hmac
import base64
from datetime import datetime, timezone
import json
from epos_restaurant_2023.api.api import get_estc_connection
## status code = 422  is invalid data

@frappe.whitelist(allow_guest=True)
def aba_generate_qr(**params):
    if  frappe.request.method != "POST":        
        frappe.local.response.update({
            "staus_code":"405",
            "message": _("Invalid request method"),
            "http_status_code": 405 
        }) 
        return

    p = {k.strip(): v for k, v in params.items()}  
    p.pop("cmd",None)



    conn =  get_estc_connection() 
    if not conn.get("estc_central_rul", None) :
        staus_code = 422
        frappe.local.response.update({
            "staus_code":f"{staus_code}",
            "message": _("The 'estc_central_url' is not configured in site settings. Please contact your system administrator."),
            "http_status_code": staus_code 
        }) 
        return
    

    estc_central_rul = conn.get("estc_central_rul", None) or ""
    url = f"{estc_central_rul}/api/method/estc.api.payway.aba_generate_qr"

    # Make POST request
    ## verify=False is equivalent to CURLOPT_SSL_VERIFYPEER=false
    response = requests.post(url, json=p, verify=False) 
    try:
        data = response.json() 
    except Exception:
        data = {}   

    #success request
    if(response.status_code in [200,201]):  
        from epos_restaurant_2023.api.qr import generate_qr
        _data =  data.get("message") or {}
        qr_string = _data.get("qr_string",None) or ""
        currency = p.get("currency",None) or ""
        qr_image_custom = None
        qr_image = (p.get("image",None) or False)
        if qr_image == False:
            qr_image_custom = generate_qr(data= qr_string,size=6, use_logo=True,currency=currency, image_base64=True)
        
        _data.pop("qr_string", None)       
        response = {
            **_data, 
            "qr_image_custom": qr_image_custom
        } 
        
        if qr_image == True :
            response.pop("qr_image_custom",None)

        frappe.local.response.update(response) 


        return
    

    #fails request
    status_code = data.get("status_code",None) or response.status_code

    update_response = {
        "staus_code":status_code,
        **data,
        "http_status_code": response.status_code
    }
    frappe.local.response.update(update_response) 

    create_error_log(params=p, error=update_response)
    return 
     

def create_error_log(params, error):
    frappe.enqueue(
            "epos_restaurant_2023.api.payway.create_error_log_enqueue", # python function or a module path as string
            queue="short", # one of short, default, long
            job_name="create_payway_integration_log", # specify a job name
            # enqueue_after_commit=True,
            params = params,
            error = error
        )

@frappe.whitelist()   
def create_error_log_enqueue(params, error):
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
def update_payway_tranaction_id_on_callback_success(tran):
    frappe.enqueue(
            "epos_restaurant_2023.api.payway.update_payway_tranaction_id_on_callback_success_enqueue", # python function or a module path as string
            queue="short", # one of short, default, long
            job_name="update_payway_tranaction_id_on_callback_success_enqueue", # specify a job name
            enqueue_after_commit=True,
            tran = tran
        )
    # return update_payway_tranaction_id_on_callback_success_enqueue(tran)

@frappe.whitelist() 
def update_payway_tranaction_id_on_callback_success_enqueue(tran):
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