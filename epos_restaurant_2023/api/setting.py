import frappe
import json
@frappe.whitelist(methods="POST" )
def get_settings():
   
   data = {}
   data["currency_precision"] = frappe.get_cached_value("System Settings",None, "currency_precision")  or 2
   data["float_precision"] =  frappe.get_cached_value("System Settings",None, "float_precision")  or 2


   return data
