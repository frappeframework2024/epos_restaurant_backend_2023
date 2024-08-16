import frappe
from flask import Flask, request, redirect
import requests
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

@frappe.whitelist(methods="POST")
def get_auth(): 
    # auth_code = request.args.get('code')


    return abc()
 
def abc():
    doc = frappe.get_doc('ePOS Settings')
    auth_client = AuthClient(
        doc.client_id, #“client_id”,
        doc.client_secret, #“client_secret”,
        # "http://webmonitor.inccloudserver.com:1216", #“redirect_uri”,
        "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl",
        doc.environment
    )

    scopes = [
        Scopes.ACCOUNTING,
        Scopes.PAYMENT,
        Scopes.OPENID,
        Scopes.PROFILE,
        Scopes.EMAIL,
        Scopes.PHONE,
        Scopes.ADDRESS
    ]


    auth_url = auth_client.get_authorization_url(scopes)   

    return auth_url

    

    # return auth_url
    auth = auth_client.get_bearer_token("AB11723523901QeyxOVyYfLaVZcdxvgeAz6OKl3pWts97ToLJN", realm_id = doc.realm_id)

    return     auth