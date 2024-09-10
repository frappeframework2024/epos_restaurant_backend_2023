import frappe
from frappe import _
import urllib.parse
from epos_restaurant_2023.api.quickbook_intergration.api import (post_api, get_list)
import json
from dataclasses import dataclass,field
from typing import List, Optional



@frappe.whitelist(allow_guest=True, methods="GET")
def create_invoice(cashier_shift): 
    sql_sale = "select name,total_discount,customer,customer_name,posting_date,custom_bill_number,qb_customer_id from `tabSale` where cashier_shift = %(cashier_shift)s and docstatus = 1"
    sale_list = frappe.db.sql(sql_sale,{"cashier_shift":cashier_shift},as_dict = 1)
    # for s in sale_list:
    #     sale_product_list = frappe.db.get_all("Sale Product",,filters={
    #         'parent': s.name
    #     })
        
    resp = post_api("invoice",headers={"Content-Type":"application/json"}, body=data)
    return resp.json()

@frappe.whitelist(allow_guest=True, methods="GET")
def create_payment(data): 
    resp = post_api("invoice",headers={"Content-Type":"application/json"}, body=data)
    return resp.json()




@dataclass
class ItemRef:
    value: str

@dataclass
class SalesItemLineDetail:
    def __init__(self, detail_type,unit_price,qty,discount_rate):
        self.DetailType = detail_type
        self.UnitPrice = unit_price
        self.Qty = qty
        self.DiscountRate = discount_rate
    ItemRef: ItemRef
    UnitPrice: float = 0
    Qty: int = 0
    DiscountRate: Optional[float] = None  # Optional if some entries don't have DiscountRate

@dataclass
class LineItem:
    DetailType: str = 'SalesItemLineDetail'
    Amount: float = 0
    Description: str = ''
    SalesItemLineDetail: SalesItemLineDetail=field(default_factory=SalesItemLineDetail) # type: ignore

@dataclass
class CustomerRef:
    value: str = ''

@dataclass
class Invoice:
    Line: List[LineItem] = field(default_factory=list)
    TxnDate: str=''
    DocNumber: str = ''
    CustomerRef: CustomerRef=field(default_factory=CustomerRef) # type: ignore





