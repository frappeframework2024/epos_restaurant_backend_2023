import frappe
import json
from epos_restaurant_2023.api.api import get_current_cashier_shift
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
            data["working_day"] = get_working_day(pos_profile.name)
            data["cashier_shift"] = get_current_cashier_shift(pos_profile.name)  
        return data

@frappe.whitelist()
def get_working_day(pos_profile):

    sql="select name,pos_profile,posting_date from `tabWorking Day` where pos_profile = %(pos_profile)s and is_closed=0 order by creation desc limit 1"
    working_day = frappe.db.sql(sql,{"pos_profile":pos_profile},as_dict=True)
    if working_day:
        return working_day[0]
    else:
        return None
@frappe.whitelist()
def get_exchange_rate():
    
    main_currency = frappe.get_cached_value("ePOS Settings",None, "currency")
    exchange_rate_main_currency = frappe.get_cached_value("ePOS Settings",None, "exchange_rate_main_currency")

    second_currency = frappe.get_cached_value("ePOS Settings",None, "second_currency")
    if exchange_rate_main_currency == second_currency:
        second_currency  = main_currency
    
    exchange_rate = frappe.db.sql("""select 
                                        posting_date,
                                        exchange_rate,
                                        exchange_rate_input,
                                        change_exchange_rate,
                                        change_exchange_rate_input 
                                    from `tabCurrency Exchange` 
                                    where docstatus=1 
                                    and from_currency= %(from_currency)s
                                    and to_currency=%(to_currency) s
                                    order by posting_date desc
                                    limit 1""",{
                                        "from_currency":main_currency,
                                        "to_currency":second_currency,
                                    }, as_dict= 1)
    return exchange_rate


@frappe.whitelist()
def get_print_format(pos_profile):
    #get default print format
    profile = frappe.get_cached_doc("POS Profile", pos_profile)
    _pos_print_format = frappe.get_list("POS Print Format Setting",fields=[
        "name",
        "business_branch",
        "title",
        "print_format_doc_type",
        "pos_receipt_template",
        "invoice_template_by_seat_number",
        "print_format",
        "print_report_name",
        "sort_order",
        "show_in_pos_report",
        "show_in_pos",
        "print_invoice_copies", 
        "print_receipt_copies",
        "pos_invoice_file_name",
        "pos_receipt_file_name", 
        "receipt_height",
        "receipt_width",
        "receipt_margin_top",
        "receipt_margin_left",
        "receipt_margin_right",
        "receipt_margin_bottom",
        "show_in_pos_closed_sale",
        "report_options"],order_by="sort_order asc")
    
    _pos_print_format_data = []
    for p in _pos_print_format:
        if (p.business_branch or '') == '' or p.business_branch == profile.business_branch:
            pf = frappe.get_doc("Print Format", p.print_format)
            _data = {
                "name":p.print_format,
                "title":p.title,
                "doc_type":pf.doc_type,
                "pos_receipt_template":p.pos_receipt_template,
                "invoice_template_by_seat_number":p.invoice_template_by_seat_number,
                "print_report_name":p.print_report_name,
                "default_print_language":pf.default_print_language,
                "show_in_pos_report":p.show_in_pos_report,
                "show_in_pos":p.show_in_pos,
                "print_invoice_copies":p.print_invoice_copies, 
                "print_receipt_copies":p.print_receipt_copies,
                "pos_invoice_file_name":p.pos_invoice_file_name,
                "pos_receipt_file_name":p.pos_receipt_file_name, 
                "receipt_height":p.receipt_height, 
                "receipt_width":p.receipt_width,
                "receipt_margin_top":p.receipt_margin_top, 
                "receipt_margin_left":p.receipt_margin_left,
                "receipt_margin_right":p.receipt_margin_right,
                "receipt_margin_bottom":p.receipt_margin_bottom,
                "show_in_pos_closed_sale":p.show_in_pos_closed_sale,
                "report_options":p.report_options,
                "business_branch":p.business_branch or "",
                "sort_order":p.sort_order,
            }
            _pos_print_format_data.append(_data)



 

    default_pos_receipt=None
    if _pos_print_format_data:
        _receipt_setting = list(filter(lambda x: x["name"] == profile.default_pos_receipt,_pos_print_format_data))
        if _receipt_setting:
            default_pos_receipt = _receipt_setting[0]

 
    #get report list   
    reports = _pos_print_format_data
    return reports