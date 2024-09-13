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
        invoice = InvoiceModel()
        invoice.DocNumber = s.custom_bill_number or s.name
        if s.qb_customer_id != "NONE" and s.qb_customer_id:
            invoice.CustomerRef = CustomerRefModel(value=s.qb_customer_id)
        else:
            qb_customer_id = frappe.db.get_value('Customer', s.customer, 'qb_customer_id')
            invoice.CustomerRef = CustomerRefModel(value=qb_customer_id)
            if invoice.CustomerRef.value == "NONE":
                qb_conf = frappe.get_doc("QuickBooks Configuration")
                invoice.CustomerRef = CustomerRefModel(value=qb_conf.default_customer_id)

        sale_products = [d['product_name'] for d in sale_product_list if not d['qb_product_id']]
        if len(sale_products) > 0:
            sync_response.append({"sale_id":s['custom_bill_number'] or s['name'],"qb_id":"NONE","message":','.join(sale_products) + ' has not mapped to yet.'} )
        else:
            for sale_product in sale_product_list:
                if sale_product.qb_product_id:
                    invoice.Line.append(LineItemModel(
                            Amount=sale_product.quantity * sale_product.price,
                            Description=sale_product.product_name,
                            SalesItemLineDetail=SalesItemLineDetailModel(
                                item_ref=sale_product.qb_product_id or "",
                                qty=sale_product.quantity,
                                unit_price=sale_product.price,
                                discount_rate=0
                            )
                        ))
            if s.total_discount > 0:
                invoice.Line.append(LineItemModel(
                            DetailType='DiscountLineDetail',
                            Amount=s['total_discount'],
                            Description=sale_product.product_name,
                            DiscountLineDetail=DiscountLineDetailModel(percent_base=False)
                        ))

        if len(invoice.Line) >0:
            # return json.loads(dump(invoice))
            resp = post_api("invoice",headers={'Content-Type': 'application/json'}, body= json.loads(dump(invoice)))
            if resp.ok:
                sync_response.append({"sale_id":s['custom_bill_number'] or s['name'],"qb_id":resp.json()["Invoice"]["Id"],"message":f'Success'})
                frappe.db.set_value("Sale",s.name,'qb_invoice_id',resp.json()["Invoice"]["Id"])
                frappe.db.commit()
                frappe.enqueue("epos_restaurant_2023.api.quickbook_intergration.qb_invoice.post_payment_qb_queue",qb_invoice_id=resp.json()["Invoice"]["Id"],sale_id=s.name,qb_customer_id=resp.json()["Invoice"]["CustomerRef"]["value"])
            else:
                sync_response.append({"sale_id":s['name'],"qb_id":resp.json(),"message":resp.status_code})

    return sync_response
    # return resp.json()




@frappe.whitelist()
def post_payment_qb_queue(sale_id,qb_invoice_id,qb_customer_id):
    # Prepare Data to post
    payment = PaymentModel()
    
    # Posting Payment on Invoice
    response_message = []
    payment_list = frappe.db.get_list("Sale Payment",filters={"sale":sale_id,"docstatus":1},fields=['name','sale','posting_date','payment_amount'])
    for p in payment_list:
        payment.TotalAmt = p.payment_amount
        payment.TxnDate = str(p.posting_date)
        payment.PaymentMethodRef = PaymentMethodRefModel(value=3)
        payment.CustomerRef = CustomerRefModel(value=qb_customer_id)
        payment_line= PaymentLineModel()
        payment_line.Amount=p.payment_amount
        payment_line.LinkedTxn.append(LinkedTxnModel(TxnId=qb_invoice_id,TxnType='Invoice'))
        payment.Line.append(payment_line)
        payment_response=post_api("payment",headers={'Content-Type': 'application/json'}, body= json.loads(dump(payment)))
    return response_message.append(payment_response.json())


@frappe.whitelist()
def get_qb_mapped_payment_type(payment_type):
    qb_conf = frappe.get_doc("QuickBooks Configuration")
    qb_payment_type_id = [d.qb_payment_type_id for d in qb_conf.payment_method_mapping if d.pos_payment_type == payment_type]
    if len(qb_payment_type_id) > 0:
        qb_payment_type_id = qb_payment_type_id[0]
    else:
        qb_payment_type_id = qb_conf.default_qb_payment_type_id
    return qb_conf


@frappe.whitelist(allow_guest=True, methods="GET")
def create_payment(data):
    resp = post_api("invoice",headers={"Content-Type":"application/json"}, body=data)
    return resp.json()

def dump(data):
    return json.dumps(data,default=lambda o: o.__dict__, indent=4)

@dataclass
class ItemRefModel:
    value: str=''

@dataclass
class SalesItemLineDetailModel:
    def __init__(self,unit_price,qty,discount_rate,item_ref):
        self.UnitPrice = unit_price
        self.Qty = qty
        self.DiscountRate = discount_rate or 0
        self.ItemRef = ItemRefModel(value=item_ref)

    ItemRef: ItemRefModel = field(default_factory=ItemRefModel)
    UnitPrice: float = 0
    Qty: int = 0
    DiscountRate: Optional[float] = None  # Optional if some entries don't have DiscountRate


@dataclass
class DiscountAccountRefModel:
    def __init__(self,_value):
        self.value = _value
    value:str
@dataclass
class DiscountLineDetailModel:
    def __init__(self,discount_ref=None,percent_base=False,discount_percent=0):
        self.PercentBased=percent_base
        self.DiscountAccountRef=discount_ref
        self.DiscountPercent=discount_percent
    PercentBased:bool
    DiscountPercent:float
    DiscountAccountRef:Optional[DiscountAccountRefModel]

@dataclass
class LineItemModel:
    DetailType: str = 'SalesItemLineDetail'
    Amount: float = 0
    Description: str = ''
    SalesItemLineDetail: Optional[SalesItemLineDetailModel]= None # type: ignore
    DiscountLineDetail: Optional[DiscountLineDetailModel] = None# type: ignore

@dataclass
class CustomerRefModel:
    value: str = ''

@dataclass
class InvoiceModel:
    Line: List[LineItemModel] = field(default_factory=list)
    TxnDate: str=''
    DocNumber: str = ''
    CustomerRef: CustomerRefModel=field(default_factory=CustomerRefModel) # type: ignore


@dataclass
class LinkedTxnModel:
    TxnId:str=''
    TxnType:str=''
@dataclass
class PaymentLineModel:
    Amount:float = 3
    LinkedTxn: List[LinkedTxnModel]=field(default_factory=list)

@dataclass
class PaymentMethodRefModel:
    value:str=''

@dataclass
class PaymentModel:
    TotalAmt:float = 0.0
    TxnDate:str=''
    CustomerRef: CustomerRefModel=field(default_factory=CustomerRefModel)
    PaymentMethodRef: PaymentMethodRefModel=field(default_factory=PaymentMethodRefModel)
    Line:List[PaymentLineModel]=field(default_factory=list)

