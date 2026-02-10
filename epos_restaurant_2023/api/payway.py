
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
        qr_image_custom = generate_qr(data= qr_string,size=6, use_logo=True,currency=currency, image_base64=True)
        

        _data.pop("qr_string", None)       
        response = {
            **_data, 
            "qr_image_custom": qr_image_custom
        }   
        frappe.local.response.update(response) 
        return
    

    #fails request
    status_code = data.get("status_code",None) or response.status_code
    frappe.local.response.update({
        "staus_code":status_code,
        **data,
        "http_status_code": response.status_code
    }) 
    return 
     
