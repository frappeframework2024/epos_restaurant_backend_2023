import json
import time
import frappe
import base64
from py_linq import Enumerable
from frappe.utils import today, add_to_date
from datetime import datetime, timedelta
import calendar
from dateutil import relativedelta
from frappe import _


@frappe.whitelist(allow_guest=True)
def station_license(device_id,platform="Windows",business_branch=None): 
    if device_id=="Demo":
        doc = None
        if not frappe.db.exists("POS Station","Demo"):
            business_branch = frappe.db.sql("select name from `tabBusiness Branch` limit 1",as_dict=1)[0]["name"]
            doc= frappe.get_doc({"name":"Demo","owner":"Administrator","creation":"2024-03-19 20:04:27.312125","modified":"2024-03-19 20:04:27.312125","modified_by":"Administrator","docstatus":0,"idx":0,"station_name":"Demo",
                                "business_branch":business_branch,
                                "platform":"Web","device_id":"Demo","license":"","is_used":0,"is_order_station":0,"disabled":0,"show_button_print_bill":1,"show_button_cancel_print_bill":1,"show_start_close_working_day":1,"show_start_close_cashier_shift":1,"show_button_pos_reservation":1,"show_button_customer_display":1,"show_option_payment":1,"show_option_quick_pay":1,"show_sale_more_action_menu":1,"show_reference_button_in_more_menu":1,"show_button_commission":1,"show_button_change_price_on_order_station":0,"show_keypad_in_sale_screen":0,"show_deleted_sale_product_in_sale_screen":0,"show_button_change_sale_type":0,"show_park_button":0,"show_top_up":1,"show_setting_menu":0,"show_button_resend":0,"show_wifi_button":1,"doctype":"POS Station","station_printers":[{"name":"982e4cd655","owner":"Administrator","creation":"2024-02-28 09:18:51.397289","modified":"2024-03-19 20:04:27.312125","modified_by":"Administrator","docstatus":0,"idx":1,"printer":"bd0509fedc","printer_name":"Cashier Printer","ip_address":"192.168.10.80","port":9100,"group_item_type":"Printer cut by order","cashier_printer":1,"is_label_printer":0,"parent":"Demo","parentfield":"station_printers","parenttype":"POS Station","doctype":"Station Printers"},{"name":"f6a44d03d8","owner":"Administrator","creation":"2024-02-28 09:18:51.397289","modified":"2024-03-19 20:04:27.312125","modified_by":"Administrator","docstatus":0,"idx":2,"printer":"7c240a1581","printer_name":"Kitchen Printer","ip_address":"192.168.10.80","port":9100,"group_item_type":"Printer cut by order","cashier_printer":0,"is_label_printer":0,"parent":"Demo","parentfield":"station_printers","parenttype":"POS Station","doctype":"Station Printers"},{"name":"776aa0f1a3","owner":"Administrator","creation":"2024-02-28 09:18:51.397289","modified":"2024-03-19 20:04:27.312125","modified_by":"Administrator","docstatus":0,"idx":3,"printer":"8f07b425c5","printer_name":"Bar Printer","ip_address":"192.168.10.80","port":9100,"group_item_type":"Printer cut by order","cashier_printer":0,"is_label_printer":0,"parent":"Demo","parentfield":"station_printers","parenttype":"POS Station","doctype":"Station Printers"}],"__last_sync_on":"2024-03-19T13:04:32.196Z"}) 
            doc.insert(ignore_permissions=True, ignore_links=True)
            frappe.db.commit()
        else:
            doc=frappe.get_doc("POS Station","Demo")
        return {"name":"Demo","license":doc.license,"platform":doc.platform,"is_used":0}
    
    if not platform: 
        filters = {
            'disabled': 0,
            'device_id':device_id
            }
    else:
        filters = {
                'disabled': 0,
                'device_id':device_id,
                'platform':platform
                }
        if business_branch:
            filters.update({'business_branch':business_branch})
        else:
            pass
            
    # frappe.throw(str(filters))

    doc = frappe.db.get_list('POS Station',
        filters=filters,
        fields=["name","license","platform","is_used"],
        as_list=False
    )
    
    
    
    if doc:
        return {"name":doc[0].name,"license":doc[0].license,"platform":doc[0].platform,"is_used":doc[0].is_used}
    else:
        return {"name":None,"license":None,"platform":None,"is_used":None}
    
@frappe.whitelist(allow_guest=True)
def start_config_pos():
    pass

@frappe.whitelist(allow_guest=True)
def test():
    return "ToDo Test"
