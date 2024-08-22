import frappe
from flask import Flask, redirect, request, session
import requests
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

@frappe.whitelist(methods="POST")
def get_auth(): 
    # auth_code = request.args.get('code')
    return get_authorization_url()
 
def auth_client():
    doc = frappe.get_doc('ePOS Settings')
    auth_client = AuthClient(
        doc.client_id, 
        doc.client_secret,
        "http://localhost:10800",
        doc.environment
    )
    return auth_client

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
    auth = auth_client.get_bearer_token("AB11723523901QeyxOVyYfLaVZcdxvgeAz6OKl3pWts97ToLJN", realm_id = doc.realm_id)

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