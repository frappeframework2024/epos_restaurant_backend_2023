

import frappe
# from intuitlib.client import AuthClient
# from intuitlib.enums import Scopes
from epos_restaurant_2023.api.quickbook_intergration.config import (get_auth)

@frappe.whitelist( methods="POST")
def create_invoice(param):
    return  get_auth()