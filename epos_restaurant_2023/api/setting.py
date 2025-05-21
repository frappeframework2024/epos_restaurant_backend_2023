import frappe
import json
@frappe.whitelist(methods="POST" )
def get_settings():
   
   data = {}
   data["currency_precision"] = frappe.get_cached_value("System Settings",None, "currency_precision")  or 2
   data["float_precision"] =  frappe.get_cached_value("System Settings",None, "float_precision")  or 2
   data["app_name"] =  frappe.get_cached_value("ePOS Settings",None, "epos_app_name")
   data["app_logo"] =  frappe.get_cached_value("ePOS Settings",None, "epos_logo") 
   data["currency"] =  frappe.get_cached_value("ePOS Settings",None, "currency") 

   currency = frappe.get_cached_doc("Currency", data["currency"])
   data["currency_symbol"] ="$"
   data["symbol_on_right"] = 0
   if currency:
       data["currency_symbol"] = currency.symbol
       data["symbol_on_right"] = currency.symbol_on_right
       


   return data
