
from frappe import _
import frappe
import requests
from datetime import datetime, timezone
from epos_restaurant_2023.api.api import get_estc_connection
from epos_restaurant_2023.helpers.payway_helper import (
    create_error_log_enqueue,
    on_aba_refund_payment
)


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
    status_code = 422
    
    # check if sale already close
    sale_name = (p.get("response",None) or  {}).get("invoice_id",None) or ""
    if not frappe.db.exists("Sale", sale_name):
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": _("This sale is invalid. Please reload the system and generate the QR code again."),
            "http_status_code": status_code
        })
        
        return
    doc_sale = frappe.get_doc("Sale",sale_name)
    if doc_sale.docstatus == 1:
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": _("Payment for this sale has already been settled. Please leave this screen and reload the system."),
            "http_status_code": status_code
        })
        return 
    if (doc_sale.aba_transaction_id or "") != "" and (doc_sale.aba_transaction_id or "") != p.get("tran_id"):
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": _("A KHQR is already being generated for this sale. Please reload the system and try again."),
            "http_status_code": status_code
        })
        return 
    
    
    doc_sale.db_set("aba_transaction_id", p.get("tran_id"),update_modified=False)       
    doc_comment = frappe.get_doc({
        'doctype': 'Comment',
        'subject': 'ABA generate KHQR',
        "comment_type":"Info",
        "reference_doctype":"Sale",
        "reference_name":doc_sale.name,
        "comment_by":"",
        "custom_note":"ABA generate KHQR",
        "content":"ABA generate KHQR with amount {} {} on PayWay transaction id: {}".format(p.get("payment_amount"), p.get("currency"), p.get("tran_id"))
    })
    doc_comment.insert(ignore_permissions=True)       
        

    # "lifetime":5, //5min ~ default None mean 30days
    p["lifetime"] = 5 ## overrride lifetime of qr

    ## validate sale payment
    if len(p.get("sale_payments",None) or []) <=0:        
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": _("Payment must not be empty."),
            "http_status_code": status_code 
        }) 
        return   


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
   

# close transaction as cancel qr
@frappe.whitelist()
def aba_close_transaction(**param):
#    { 
#     "property_code": "", # required
#     "pos_config": "", # required
#     "invoice_id": "" # required
# }
   
    if  frappe.request.method != "POST":        
        frappe.local.response.update({
            "status_code":"405",
            "message": _("Invalid request method"),
            "http_status_code": 405 
        }) 
        return
    
    p = {k.strip(): v for k, v in param.items()}  
    p.pop("cmd",None)
    
    sale_name = p.get("invoice_id",None) or ""
    doc_sale = frappe.get_doc("Sale",sale_name)
    if doc_sale.docstatus == 0: 
        doc_sale.db_set("aba_transaction_id", "",update_modified=False)


    conn =  get_estc_connection() 
    if not conn.get("estc_payway_socket_server_url",None):
        return "This feature is currently unavailable."
    
    if not conn.get("estc_central_url", None) :
        status_code = 422
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": _("The 'estc_central_url' is not configured in site settings. Please contact your system administrator."),
            "http_status_code": status_code 
        }) 
        return    

    estc_central_url = conn.get("estc_central_url", None) or ""
    url = f"{estc_central_url}/api/method/estc.api.payway.aba_close_transaction"
 

    # Make POST request
    ## verify=False is equivalent to CURLOPT_SSL_VERIFYPEER=false
    response = requests.post(url, json=p, verify=False) 
     
    try:
        data = response.json() 
    except Exception:
        data = {}  
    
    status_code = response.status_code
    if status_code not in [200,201]:
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": data,
            "http_status_code": status_code 
        }) 
        return
    
    return data

# check transaction of qr
@frappe.whitelist()
def aba_check_transaction(**param):
    # **param = 
    #     { 
    #     "tran_id": "",
    #     "property_code": "",
    #     "pos_config": "",
    #     "response": {
    #         "pos_profile": "",
    #         "station_name": "",
    #         "invoice_id": "",
    #         "temp_tran_id": ""
    #     }
    # }

    if  frappe.request.method != "POST":        
        frappe.local.response.update({
            "status_code":"405",
            "message": _("Invalid request method"),
            "http_status_code": 405 
        }) 
        return
    
    p = {k.strip(): v for k, v in param.items()}  
    p.pop("cmd", None)
    conn =  get_estc_connection() 
    if not conn.get("estc_payway_socket_server_url",None):
        return "This feature is currently unavailable."
    
    if not conn.get("estc_central_url", None) :
        status_code = 422
        frappe.local.response.update({
            "status_code":f"{status_code}",
            "message": _("The 'estc_central_url' is not configured in site settings. Please contact your system administrator."),
            "http_status_code": status_code 
        }) 
        return  
    
    
    estc_central_url = conn.get("estc_central_url", None) or ""
    url = f"{estc_central_url}/api/method/estc.api.payway.aba_check_transaction"

    # Make POST request
    ## verify=False is equivalent to CURLOPT_SSL_VERIFYPEER=false
    response = requests.post(url, json=p, verify=False)
    try:
        data = response.json() 
    except Exception :
        data = {}    

    frappe.local.response.update({ 
            "message": data.get("message",None),
            "http_status_code": response.status_code
    }) 
    return




@frappe.whitelist()
def aba_refund_payment(**param):      
    # **param = {
    #     "invoice_id":"" , //required
    #     "refunded_by":"Mr.ABC", //optional
    #     "refunded_note":"Wrong Payment", //optional
    #     "refunded_type":"Manual" //reqired:  Manual, Edit Invoice, Delete Invoice
    # }  
   
    
    if  frappe.request.method != "POST":
        frappe.local.response.update({
                "status_code":"405",
                "message": _("Invalid request method"),
                "http_status_code": 405
            })
        return
    
    p = {k.strip(): v for k, v in param.items()}
    p.pop("cmd", None)
    
    
    if not p.get("invoice_id"):
        frappe.local.response.update({
            "status_code":"405",
            "message": _("Invalid Sale"),
            "http_status_code": 405
        })
        return
    sale_name = p.get("invoice_id")
    if not frappe.db.exists("Sale",sale_name):
        frappe.local.response.update({
            "status_code":"405",
            "message": _("Invalid Sale"),
            "http_status_code": 405
        })
        return 
    
    sale_doc = frappe.get_doc("Sale",sale_name)
    if not sale_doc.aba_transaction_id or sale_doc.sale_status == "Closed - Refunded":
        frappe.local.response.update({
            "status_code":"404",
            "message": _("No payment transaction available to refund."),
            "http_status_code": 404
        })
        return
    
    
        
    property_code = frappe.get_value("Business Branch", sale_doc.business_branch,"property_code") or ""
    if property_code:
        pos_config = frappe.get_value("POS Profile", sale_doc.pos_profile,"pos_config") or ""   
        refund_param = {
            "tran_id":sale_doc.aba_transaction_id,
            "property_code":property_code, 
            "pos_config":pos_config, 
            "refunded_by":p.get("refunded_by"), 
            "refunded_note":p.get("refunded_note"), 
            "refunded_type":p.get("refunded_type",None) or "Manual"
        }
        
        # p = {
        #     "tran_id":"" , //required
        #     "property_code":"", //required
        #     "pos_config":"", //required
        #     "refunded_by":"Mr.ABC", //optional
        #     "refunded_note":"Wrong Payment", //optional
        #     "refunded_type":"Manual" //reqired:  Manual, Edit Invoice, Delete Invoice
        # }  
        
        data = on_aba_refund_payment(param=refund_param, sale_doc=sale_doc)
        if not data:
            return
        
        frappe.local.response.update({
            "status_code":"200",
            "message": data.get("message"),
            "http_status_code": 200
        })
        return 
    

    frappe.local.response.update({
        "status_code":"200",
        "message": _("No payment transaction available to refund."),
        "http_status_code": 200
    })
    return


    

