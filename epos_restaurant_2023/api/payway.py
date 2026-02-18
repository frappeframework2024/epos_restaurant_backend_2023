
from frappe import _
import frappe
import requests
from datetime import datetime, timezone
from epos_restaurant_2023.api.api import get_estc_connection
from epos_restaurant_2023.helpers.payway_helper import (create_error_log_enqueue)


## status code = 422  is invalid data
@frappe.whitelist()
def aba_generate_qr(**params):
    if  frappe.request.method != "POST":        
        frappe.local.response.update({
            "status_code":"405",
            "message": _("Invalid request method"),
            "http_status_code": 405 
        }) 
        return

    p = {k.strip(): v for k, v in params.items()}  
    p.pop("cmd",None)

    # "lifetime":5, //5min ~ default None mean 30days
    p["lifetime"] = 5

    conn =  get_estc_connection() 
    if not conn.get("estc_central_url", None) :
        status_code = 422
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": _("The 'estc_central_url' is not configured in site settings. Please contact your system administrator."),
            "http_status_code": status_code 
        }) 
        return    

    estc_central_url = conn.get("estc_central_url", None) or ""
    url = f"{estc_central_url}/api/method/estc.api.payway.aba_generate_qr"

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
        "status_code":status_code,
        **data,
        "http_status_code": response.status_code
    }
    frappe.local.response.update(update_response) 

    #create error log enqueue
    create_error_log_enqueue(params=p, error=update_response)
    return 
   
