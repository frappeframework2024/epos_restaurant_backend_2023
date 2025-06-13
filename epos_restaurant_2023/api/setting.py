import frappe
import json
@frappe.whitelist(methods="POST" )
def get_settings(station_name=None):

    data = {}
    data["currency_precision"] = frappe.get_cached_value("System Settings",None, "currency_precision")  or 2
    data["float_precision"] =  frappe.get_cached_value("System Settings",None, "float_precision")  or 2
    data["app_name"] =  frappe.get_cached_value("ePOS Settings",None, "epos_app_name")
    data["app_logo"] =  frappe.get_cached_value("ePOS Settings",None, "epos_logo") 
    data["currency"] =  frappe.get_cached_value("ePOS Settings",None, "currency") 
    data["second_currency"] =  frappe.get_cached_value("ePOS Settings",None, "second_currency") 

    currency = frappe.get_cached_doc("Currency", data["currency"])
    data["currency_symbol"] =currency.symbol
    data["currency_precision"] =currency.custom_currency_precision 
    data["symbol_on_right"] = currency.symbol_on_right
    data["currency_format"] = currency.custom_pos_currency_format 
    # second currency
    second_currency = frappe.get_cached_doc("Currency", data["second_currency"])
    data["second_currency_symbol"] =second_currency.symbol
    data["second_currency_precision"] =second_currency.custom_currency_precision 
    data["second_symbol_on_right"] = second_currency.symbol_on_right
    data["second_currency_format"] = second_currency.custom_pos_currency_format 


    data["allow_login_multiple_site"] = 1
    if currency:
        data["currency_symbol"] = currency.symbol
        data["symbol_on_right"] = currency.symbol_on_right
        

        # if station_name pass we get more data like pos profile
        if station_name:
            pos_profile = frappe.get_cached_doc("POS Profile", frappe.get_cached_value("POS Station",station_name,"pos_profile"))
            data["pos_profile"] = pos_profile
            data["allow_login_multiple_site"] = frappe.get_cached_value("POS Station",station_name,"allow_login_multiple_site")
            
            
        return data
