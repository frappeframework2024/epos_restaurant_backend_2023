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
def station_license(device_id,platform=None): 
    if not platform:
        filters = {
            'disabled': 0,
            'device_id':device_id,
            'platform':platform
            }
    else:
        filters = {'disabled': 0,
            'device_id':device_id
            }
    doc = frappe.db.get_list('POS Station',
        filters=filters,
        fields=["name","license","platform"],
        as_list=False
    )
    if doc:
        return {"name":doc[0].name,"license":doc[0].license,"platform":doc[0].platform}
    else:
        return {"name":None,"license":None,"platform":None}
    
@frappe.whitelist(allow_guest=True)
def start_config_pos():
    pass

@frappe.whitelist(allow_guest=True)
def test():
    return "ToDo Test"
