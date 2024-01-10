import json
import time
import frappe
import base64
from py_linq import Enumerable
from frappe.utils import today, add_to_date
import datetime
from frappe import _
import pandas as pd
from frappe.utils.data import add_to_date
from epos_restaurant_2023.inventory.inventory import get_uom_conversion

@frappe.whitelist()
def get_timer_product_estimate_price_test():
    sale_product = {
        "name":"01f2e92b0f",
        "product_code": "T001",
        "time_in":"2024-01-09 10:03:32",
        "time_out":"2024-01-09 15:52:55",
        "parent":"SO2024-0075"
    }
    return get_timer_product_estimate_price(sale_product)

@frappe.whitelist(methods="POST")
def get_timer_product_estimate_price(sale_product):
    data = get_timer_product_breakdown(sale_product)
    return sum([d["amount"] for d in data])


@frappe.whitelist(methods="POST")
def get_timer_product_breakdown(sale_product):

    data = get_times(sale_product)
    
    product = frappe.get_doc("Product", sale_product["product_code"])
    sale_doc = frappe.get_doc("Sale", sale_product["parent"])

    #round up  time
    for d in data:
        # round up time
        round_up = ([int(x.roundup_value) for x in product.roundup_list if str(x.base_value) == str(d["total_minute"])  ]) 
        d["minute_round_up"] = d["total_minute"] if len(round_up) == 0 else max(round_up)
        # price 
        if len(product.product_price)>0:
            # return product.product_price
            prices = [x for x in product.product_price  if int(d["hour"])>=int(x.start_time) and int(d["hour"])<=int(x.end_time) and x.price_rule == sale_doc.price_rule ]
            if len(prices)>0:
                d["price"]  = prices[0].price
                d["unit"] = prices[0].unit
                d["uom_conversion"] = get_uom_conversion(product.unit,prices[0].unit)
            else:
                d["unit"] = product.unit
                d["price"] = product.price or 0
                d["uom_conversion"] = 1
            
        else:
            d["unit"] = product.unit
            d["price"] = product.price or 0
            d["uom_conversion"] = 1

        d["amount"] = d["minute_round_up"] * d["uom_conversion"] * d["price"]


    return data



 


def get_times(sale_product):
    times = []
    time_in = datetime.datetime.strptime(sale_product["time_in"], "%Y-%m-%d %H:%M:%S")
    time_out = datetime.datetime.strptime(sale_product["time_out"], "%Y-%m-%d %H:%M:%S")

    while time_in<= time_out:
        times.append(
            { 
            "time_in": time_in.replace(minute=00, second=00),
            "time_out": add_to_date(time_in,hours=1).replace(minute=0, second=0)
        }
        )

        time_in = add_to_date(time_in, hours = 1)
       
  
    if len(times)> 0:
        times[0]["time_in"] = datetime.datetime.strptime(sale_product["time_in"], "%Y-%m-%d %H:%M:%S").replace(second=0)
        times[len(times)-1]["time_out"] = datetime.datetime.strptime(sale_product["time_out"], "%Y-%m-%d %H:%M:%S").replace(second=0)
    
    for d in times:
        time_in = datetime.datetime.strptime(str(d["time_in"]), "%Y-%m-%d %H:%M:%S")
        time_out = datetime.datetime.strptime(str(d["time_out"]), "%Y-%m-%d %H:%M:%S")
       
        d["total_minute"] =  int((time_out - time_in).total_seconds() / 60)
        d["hour"] = time_in.hour


    return times

 