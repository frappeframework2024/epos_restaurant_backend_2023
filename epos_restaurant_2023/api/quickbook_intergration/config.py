import frappe
from frappe import _
import requests
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
import base64
import json


@frappe.whitelist(allow_guest=True)
def auth_client():
    doc = frappe.get_doc('QuickBooks Configuration')    
    auth_client = AuthClient(
        client_id= doc.client_id, 
        client_secret= doc.client_secret,
        redirect_uri= doc.redirect_url,
        environment= doc.environment,
        realm_id= doc.realm_id
    )
    return auth_client

@frappe.whitelist()
def connect_quickbooks(): 
    scopes = [
        Scopes.ACCOUNTING,
    ]
    auth_url = auth_client().get_authorization_url(scopes)   
    return auth_url


@frappe.whitelist(methods="POST")
def exchange_authorization_code(params):
    _param = json.loads(params)
    doc = frappe.get_doc('QuickBooks Configuration')   
    response = request_bearer_token_api(doc, grant_type="authorization_code",auth_code=_param["code"])
    
    if response.status_code  in [200,201]:   
        resp = response.json()  
        doc.realm_id = int(_param["realm_id"])
        doc.connected = 1
        doc.refresh_token = resp["refresh_token"]
        doc.access_token = resp["access_token"]
        doc.save()
        frappe.db.commit()


        ## get company
        from epos_restaurant_2023.api.quickbook_intergration.api import get_company_information
        qb_company = get_company_information(_param["realm_id"])
        if qb_company:
            setting = frappe.get_doc('QuickBooks Configuration')  
            setting.qb_company_name = qb_company["CompanyInfo"]["CompanyName"]
            setting.save()
            frappe.db.commit()            

        return "connected"
    
    doc.refresh_token = None
    doc.access_token = None
    doc.realm_id = None
    doc.is_connected = 0
    doc.save()
    frappe.db.commit()
    return frappe.throw(response.json()["error"])


@frappe.whitelist()   
def refresh_token(refresh_token = None):
    doc = frappe.get_doc('QuickBooks Configuration')
    if not refresh_token:
        refresh_token = doc.refresh_token

    if not refresh_token:
        doc.refresh_token = None
        doc.access_token = None
        doc.connected = 0
        doc.qb_company_name = None
        doc.realm_id = 0
        doc.save()
        frappe.db.commit()
        return {
            "status":0,
            "msg":_("The refresh token is invalid")
        }
    response = request_bearer_token_api(doc, grant_type="refresh_token",refresh_token=refresh_token)
    
    if response.status_code  in [200,201]:
        resp = response.json()  
        doc.connected = 1      
        doc.refresh_token = resp["refresh_token"]
        doc.access_token = resp["access_token"]
        doc.save()
        frappe.db.commit()
        return {
            "status":1,
            "expires_in":resp["expires_in"],
            "x_refresh_token_expires_in":resp["x_refresh_token_expires_in"],
            "access_token": resp["access_token"]
        }  

    msg =   response.json()["error"]  
    doc.refresh_token = refresh_token 
    if response.status_code in [400,401]:
        doc.refresh_token = None 
        msg = "Unauthorized: The refresh token may be invalid or expired"
       


    doc.access_token = None
    doc.connected = 0
    doc.realm_id = 0
    doc.qb_company_name = None
    doc.save()
    frappe.db.commit()

    return {
        "status":0,
        "msg":  msg
    }
   



def request_bearer_token_api(doc, grant_type = "refresh_token", refresh_token = None, auth_code = None):
    url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
    authorization = "{}:{}".format(doc.client_id, doc.client_secret)
    byte_string  = authorization.encode('utf-8')
    base64_encoded  = base64.b64encode(byte_string)
    base64_string = base64_encoded.decode('utf-8') 
    headers = {
        'Authorization': 'Basic {}'.format(base64_string),
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body={
        "grant_type": grant_type
    }
    if grant_type == "refresh_token":
        body.update({"refresh_token":refresh_token})
    else:
        body.update({
            "code":auth_code,
            "redirect_uri":doc.redirect_url
        })
        
    return requests.post(url, headers=headers, data=body)