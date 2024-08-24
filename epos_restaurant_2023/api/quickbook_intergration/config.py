import frappe
from frappe import _
from flask import Flask, redirect, request, session
import requests
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
import base64
import json

@frappe.whitelist(methods="POST")
def get_auth(): 
    # auth_code = request.args.get('code')
    return get_authorization_url()
 
def auth_client():
    doc = frappe.get_doc('ePOS Settings')
    auth_client = AuthClient(
        client_id= doc.client_id, 
        client_secret= doc.client_secret,
        redirect_uri= "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl",
        environment= doc.environment,
        realm_id=9341452865879148
    )
    return auth_client

@frappe.whitelist(allow_guest=True)
def get_token():
    doc = frappe.get_doc('ePOS Settings')
    token = auth_client().get_bearer_token("BB117243872909XrGLtTMoZfUFpAYtS7IWVUsbp7zvL8zMyBXZ",realm_id=9341452865879148)

    return token


def get_authorization_url(): 
    scopes = [
        Scopes.ACCOUNTING,
        Scopes.PAYMENT,
        Scopes.OPENID,
        Scopes.PROFILE,
        Scopes.EMAIL,
        Scopes.PHONE,
        Scopes.ADDRESS
    ]
    auth_url = auth_client().get_authorization_url(scopes)   
    return auth_url

    

    # return auth_url
    auth = auth_client.get_bearer_token("AB11724300524kaYUKOfs36IWPWUi9RySS2sh4NOT1Dig9DE4j", realm_id = doc.realm_id)

    return     auth
 

app = Flask(__name__)
@app.route('/qb-authorize')
@frappe.whitelist(allow_guest=True)
def quickbooks_authorize():
    auth_url = get_authorization_url()
    return redirect(auth_url)

@app.route('/qb-callback')
@frappe.whitelist(allow_guest=True)
def quickbooks_callback():
    auth_code = request.args.get('code')
    if not auth_code:
        return "Error: No authorization code received.", 400
        
    try:
        auth_client().get_bearer_token(auth_code)
        access_token = auth_client().access_token
        return "Authorization successful! Access token obtained.", 200
    
    except Exception as e:
        return f"Error obtaining access token: {e}", 400

@frappe.whitelist(allow_guest=True)   
def refresh_token(refresh_token = None):
    doc = frappe.get_doc('ePOS Settings')
    if not refresh_token:
        refresh_token = doc.refresh_token

    if not refresh_token:
        return frappe.throw(_("Invalid Refresh Token"))
    
    url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
    authorization = "{}:{}".format(doc.client_id, doc.client_secret)
    byte_string  = authorization.encode('utf-8')
    base64_encoded  = base64.b64encode(byte_string)
    base64_string = base64_encoded.decode('utf-8') 
    headers = {
        'Authorization': 'Basic {}'.format(base64_string),
        'Accept': 'application/json'
    }
    body={
        "grant_type":"refresh_token",
        "refresh_token":refresh_token
    }
    response = requests.post(url, headers=headers, data=body)
    if response.status_code  in [200,201]:
        resp = json.loads(response.text)

        
        doc.refresh_token = resp["refresh_token"]
        doc.access_token = resp["access_token"]
        doc.save()
        frappe.db.commit()

        return json.loads(response.text )
    return frappe.throw(json.loads(response.text)["error"])
   