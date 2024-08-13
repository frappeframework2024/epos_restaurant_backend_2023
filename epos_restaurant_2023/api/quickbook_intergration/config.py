import frappe
from flask import Flask, request, redirect
import requests
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

@frappe.whitelist(methods="POST")
def get_auth():
    abc()
    auth_code = request.args.get('code')
    # auth_client.get_bearer_token(auth_url, realm_id = doc.realm_id)

    return ""
 
def abc():
    doc = frappe.get_doc('ePOS Settings')
    auth_client = AuthClient(
        doc.client_id, #“client_id”,
        doc.client_secret, #“client_secret”,
        "http://192.168.10.19:1216", #“redirect_uri”,
        doc.environment
    )

    scopes = [
        Scopes.ACCOUNTING,
        # Scopes.PAYMENT,
        Scopes.OPENID,
        # Scopes.PROFILE,
        # Scopes.EMAIL,
        # Scopes.PHONE,
        # Scopes.ADDRESS
    ]

    auth_url = auth_client.get_authorization_url(scopes)   
    return redirect(auth_url) 