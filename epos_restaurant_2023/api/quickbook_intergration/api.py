

import frappe
from frappe import _
import requests
from epos_restaurant_2023.api.quickbook_intergration.config import (refresh_token)
import base64
import json

@frappe.whitelist() 
def post_api(endpoint, params=None, body=None):
    setting = frappe.get_doc('QuickBooks Configuration') 
    base_url = "https://sandbox-quickbooks.api.intuit.com/v3"
    if setting.environment != "sandbox":
        base_url = base_url.replace("sandbox-","")

    headers = {
        'Authorization': 'Bearer {}'.format(setting.access_token),
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        resp = requests.post("{}/{}".format(base_url, endpoint), params=params, headers=headers, data=body)  
        return resp
    except requests.exceptions.HTTPError as http_err:
        frappe.throw(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        frappe.throw(f"Connection error occurred: {conn_err}")  # e.g., DNS failure, refused connection
    except requests.exceptions.Timeout as timeout_err:
        frappe.throw(f"Timeout error occurred: {timeout_err}")  # e.g., request timed out
    except requests.exceptions.RequestException as req_err:
        frappe.throw(f"An error occurred: {req_err}")  # Catch all other exceptions
    except Exception as e:
        frappe.throw(f"An unexpected error occurred: {e}")


@frappe.whitelist() 
def get_api(endpoint, params= None, body = None):
    setting = frappe.get_doc('QuickBooks Configuration') 
    base_url = "https://sandbox-quickbooks.api.intuit.com/v3"
    if setting.environment != "sandbox":
        base_url = base_url.replace("sandbox-","") 
    headers = {
        'Authorization': 'Bearer {}'.format(setting.access_token),
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        resp = requests.get("{}/{}".format(base_url, endpoint), params=params, headers=headers, data=body)  
        resp.raise_for_status()
        return resp
    except requests.exceptions.HTTPError as http_err:
        frappe.throw(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        frappe.throw(f"Connection error occurred: {conn_err}")  # e.g., DNS failure, refused connection
    except requests.exceptions.Timeout as timeout_err:
        frappe.throw(f"Timeout error occurred: {timeout_err}")  # e.g., request timed out
    except requests.exceptions.RequestException as req_err:
        frappe.throw(f"An error occurred: {req_err}")  # Catch all other exceptions
    except Exception as e:
        frappe.throw(f"An unexpected error occurred: {e}")


@frappe.whitelist()
def check_authorization():
    check = refresh_token()
    if check["status"]==1:
        return {"status": 1, "msg":"Authorized"}
    else:
        return  {
            "status":0,
            "msg":"Unauthorized: The refresh token may be invalid or expired."
        }

    

def update_after_diconnected(setting):
    setting.refresh_token = None
    setting.access_token = None
    setting.realm_id = None
    setting.is_connected = 0
    setting.save()
    frappe.db.commit()


@frappe.whitelist() 
def get_company_information(realm_id):
    resp = get_api("company/{0}/companyinfo/{0}".format(realm_id))
    if resp.status_code in [200,201]:
        return resp.json()
    
    return None

@frappe.whitelist() 
def get_by_query(query):   
    doc = frappe.get_doc("QuickBooks Configuration")
    resp = get_api("company/{0}/query".format(doc.realm_id), params={"query":query})
    if resp.status_code in [200,201]:
        return resp.json()
    
    return None

@frappe.whitelist() 
def qb_get_list_payment_methods():
    doc = frappe.get_doc("QuickBooks Configuration")
    params ={
        "query":"select Name,Type, Id  from PaymentMethod where active = true"
    }
    resp = get_api("company/{0}/query".format(doc.realm_id), params=params)
    if resp.status_code in [200,201]:
        return resp.json()["QueryResponse"]["PaymentMethod"]
    
    return None



@frappe.whitelist() 
def qb_get_list_products(name = None):
    doc = frappe.get_doc("QuickBooks Configuration")
    conn = ""
    if name:
        conn =  "WHERE Name LIKE '%{}%'".format(name)
    params ={
        "query":"SELECT * FROM Item {}".format(conn)
    }
    resp = get_api("company/{0}/query".format(doc.realm_id), params=params)
    if resp.status_code in [200,201]:
        return resp.json()["QueryResponse"]
    
    return None