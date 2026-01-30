
import frappe
import requests
import time
import hashlib
import hmac
import base64
from datetime import datetime, timezone
import json

@frappe.whitelist(allow_guest=True)
def aba_generate_qr(**param):
    p = {k.strip(): v for k, v in param.items()}  

    #get param
    amount = p.get("payment_amount", 0.0) or 0.0
    currency = p.get("currency","KHR") or "KHR" 
    merchant_id = 'estccomputer'
    api_key = '2e075214-f54a-4c66-b940-a242d38d0bfd'

    # API URL
    url = "https://checkout-sandbox.payway.com.kh/api/payment-gateway/v1/payments/generate-qr"

    # Request parameters
    request_time = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    tran_id = "estc" + str(int(time.time())) 
    payment_option = "abapay_khqr"
    purchase_type = "purchase"
    qr_image_template = "template3_color"
    callback_url = "aHR0cHM6Ly82NmMyZjEyYWQwNTcwMDllZTliZTZjYTIubW9ja2FwaS5pby9BUEkvcHVzaGJhY2stbm90aWZpY2F0aW9uL3B1cmNoYXNl"
    custom_fields = base64.b64encode(
                        json.dumps({
                            "my_custom_field": "this my custom field"
                        }).encode("utf-8")
                    ).decode("utf-8") 

    # Generate hash
    hash_string = f"{request_time}{merchant_id}{tran_id}{amount}{purchase_type}{payment_option}{callback_url}{currency}{custom_fields}{qr_image_template}"

    hash_bytes = hmac.new(api_key.encode(), hash_string.encode(), hashlib.sha512).digest()
    hash_base64 = base64.b64encode(hash_bytes).decode()

    # Prepare request payload
    request_params = {
        "req_time": request_time,
        "merchant_id": merchant_id,
        "tran_id": tran_id,
        "amount": amount,
        "payment_option": payment_option,
        "currency": currency,
        "qr_image_template": qr_image_template,
        "purchase_type": purchase_type,
        "callback_url": callback_url,
        "custom_fields":custom_fields,
        "hash": hash_base64
    }

    # Make POST request
    response = requests.post(url, json=request_params, verify=False)  # verify=False is equivalent to CURLOPT_SSL_VERIFYPEER=false
    try:
        data = response.json() 
    except Exception:
        data = {} 
 

    if(response.status_code in [200,201]): 
        data.pop("status", None)
        data.pop("amount", None)
        data.pop("currency", None)
        return data
    else:
        frappe.local.response.http_status_code = response.status_code
        message = (data.get("status") or {}).get("message") or ""
        
        frappe.throw(message, frappe.ValidationError) 


@frappe.whitelist(allow_guest=True)
def aba_payment_callback(**data):
    param = {k.strip(): v for k, v in data.items()}  
    from epos_restaurant_2023.custom_socket_client import emit_event
    emit_event("ABAPayWay",data=param)
    return "success"
    