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
def station_license(device_id):
    doc = frappe.db.get_list('POS Station',
        filters={
            'disabled': 0,
            'device_id':device_id
        },
        fields=["name","license"],
        as_list=False
    )
    if doc:
        return {"name":doc[0].name,"license":doc[0].license}
    else:
        return {"name":None,"license":None}