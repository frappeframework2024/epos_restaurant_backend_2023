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
    sync_response = []
    for s in sale_list:
        sale_product_list = frappe.db.get_all("Sale Product",fields=["product_code","product_name","qb_product_id","price","quantity"],filters={
            'parent': s.name
        })
        # Build Object to json for request\
        invoice = Invoice()
        invoice.DocNumber = s.custom_bill_number or s.name
        if s.qb_customer_id != "NONE" and s.qb_customer_id:
            invoice.CustomerRef = CustomerRef(value=s.qb_customer_id)
        else:
            qb_customer_id = frappe.db.get_value('Customer', s.customer, 'qb_customer_id')
            invoice.CustomerRef = CustomerRef(value=qb_customer_id)
            if invoice.CustomerRef.value == "NONE":
                qb_conf = frappe.get_doc("QuickBooks Configuration")
                invoice.CustomerRef = CustomerRef(value=qb_conf.default_customer_id)

        sale_products = [d['product_name'] for d in sale_product_list if not d['qb_product_id']]
        if len(sale_products) > 0:
            sync_response.append({"sale_id":s['custom_bill_number'] or s['name'],"qb_id":"NONE","message":','.join(sale_products) + ' has not mapped to yet.'} )
        else:
            for sale_product in sale_product_list:
                if sale_product.qb_product_id:
                    invoice.Line.append(LineItem(
                            Amount=sale_product.quantity * sale_product.price,
                            Description=sale_product.product_name,
                            SalesItemLineDetail=SalesItemLineDetail(
                                item_ref=sale_product.qb_product_id or "",
                                qty=sale_product.quantity,
                                unit_price=sale_product.price,
                                discount_rate=0,
                            )
                        ))
            if s.total_discount > 0:
                invoice.Line.append(LineItem(
                            DetailType='DiscountLineDetail',
                            Amount=s['total_discount'],
                            Description=sale_product.product_name,
                            DiscountLineDetail=DiscountLineDetail(percent_base=False)
                        ))
                
        if len(invoice.Line) >0:
            # return json.loads(dump(invoice))
            resp = post_api("invoice",headers={'Content-Type': 'application/json'}, body= json.loads(dump(invoice)))
            if resp.ok:
                sync_response.append({"sale_id":s['custom_bill_number'] or s['name'],"qb_id":resp.json()["Invoice"]["Id"],"message":f'Success'})
                frappe.db.set_value("Sale",s.name,'qb_invoice_id',resp.json()["Invoice"]["Id"])
                frappe.db.commit()
            else:
                sync_response.append({"sale_id":s['name'],"qb_id":resp.json(),"message":resp.status_code})

    return sync_response
    # return resp.json()


def dump(data):
    return json.dumps(data,default=lambda o: o.__dict__, indent=4)

@frappe.whitelist(allow_guest=True, methods="GET")
def create_payment(data): 
    resp = post_api("invoice",headers={"Content-Type":"application/json"}, body=data)
    return resp.json()


@dataclass
class ItemRef:
    value: str=''

@dataclass
class SalesItemLineDetail:
    def __init__(self,unit_price,qty,discount_rate,item_ref):
        self.UnitPrice = unit_price
        self.Qty = qty
        self.DiscountRate = discount_rate or 0
        self.ItemRef = ItemRef(value=item_ref)

    ItemRef: ItemRef = field(default_factory=ItemRef)
    UnitPrice: float = 0
    Qty: int = 0
    DiscountRate: Optional[float] = None  # Optional if some entries don't have DiscountRate

@dataclass
class LineItem:
    DetailType: str = 'SalesItemLineDetail'
    Amount: float = 0
    Description: str = ''
    SalesItemLineDetail: Optional[SalesItemLineDetail]= None # type: ignore
    DiscountLineDetail: Optional[DiscountLineDetail] = None# type: ignore

@dataclass
class CustomerRef:
    value: str = ''

@dataclass
class Invoice:
    Line: List[LineItem] = field(default_factory=list)
    TxnDate: str=''
    DocNumber: str = ''
    CustomerRef: CustomerRef=field(default_factory=CustomerRef) # type: ignore


@dataclass
class DiscountAccountRef:
    def __init__(self,_value):
        self.value = _value
    value:str
@dataclass
class DiscountLineDetail:
    def __init__(self,discount_ref=None,percent_base=False,discount_percent=0):
        self.PercentBased=percent_base
        self.DiscountAccountRef=discount_ref
        self.DiscountPercent=discount_percent
    PercentBased:bool
    DiscountPercent:float
    DiscountAccountRef:Optional[DiscountAccountRef] # type: ignore

