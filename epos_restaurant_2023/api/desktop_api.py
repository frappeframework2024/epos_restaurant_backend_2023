import numpy as np
import json
from PIL import Image
from epos_restaurant_2023.api.product import get_product_by_menu
from epos_restaurant_2023.api.api import get_system_settings
from epos_restaurant_2023.api.printing import (
    get_print_context, 
    print_bill,
    print_kitchen_order,
    print_waiting_slip,
    print_voucher_invoice,
    print_from_print_format
    )
import frappe
@frappe.whitelist()
def dome():
    return print_from_print_format(data = {
                "action" : "print_report",                
                "doc": "Working Day",
                "name":"WD2024-0008",
                "print_format": "Working Day Sale Summary",
                "pos_profile":"Main POS Profile",
                "outlet":"Main Outlet",
                "letterhead":"Downtown Letterhead"
            })

@frappe.whitelist(allow_guest=True)
def get_bill_template_api(name,template, reprint=0):
    if not frappe.db.exists("Sale",name):
        return ""    
    doc = frappe.get_doc("Sale", name) 
    data_template,css = frappe.db.get_value("POS Receipt Template",template,["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc,reprint))
    return {"html":html,"css":css}    

## WINDOW SERVER PRINTING GENERATE HTML
@frappe.whitelist(allow_guest=True, methods="POST")
def get_bill_template(name,template, reprint=0):
    if not frappe.db.exists("Sale",name):
        return ""    
    doc = frappe.get_doc("Sale", name) 
    data_template,css = frappe.db.get_value("POS Receipt Template",template,["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc,reprint))
    return {"html":html,"css":css}


## print waiting slip
@frappe.whitelist(allow_guest=True,methods='POST')
def get_waiting_slip_template(name):
    if not frappe.db.exists("Sale",name):
        return ""    
    doc = frappe.get_doc("Sale", name)
    data_template,css = frappe.db.get_value("POS Receipt Template","Waiting Slip",["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc))
    return {"html":html,"css":css}


@frappe.whitelist(allow_guest=True, methods="POST")
def get_voucher_template(name):
    if not frappe.db.exists("Voucher",name):
        return ""    
    doc = frappe.get_doc("Voucher", name) 
    working_day = frappe.get_doc("Working Day",doc.working_day)

    doc.pos_profile = working_day.pos_profile
    data_template,css = frappe.db.get_value("POS Receipt Template","Voucher Reciept",["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc))
    return {"html":html,"css":css}


@frappe.whitelist(allow_guest=True,methods='POST')
def get_kot_template(sale, printer_name, products): 
    if not frappe.db.exists("Sale",sale):
        return ""    
    doc_sale = frappe.get_doc("Sale", sale)
    _products = products
    if type(products) is str:
        _products  = json.loads(products)
    data_template,css = frappe.db.get_value("POS Receipt Template","Kitchen Order",["template","style"])   
    html = frappe.render_template(data_template, get_print_context(doc=doc_sale,sale_products = _products,printer_name=printer_name))    
    return {"html":html,"css":css}


## get Sticker Lable 
@frappe.whitelist(allow_guest=True,methods='POST')
def get_lable_order_template(sale, printer_name, products): 
    if not frappe.db.exists("Sale",sale):
        return ""    
    doc_sale = frappe.get_doc("Sale", sale)
    _products = products
    if type(products) is str:
        _products  = json.loads(products)
    data_template,css = frappe.db.get_value("POS Receipt Template","Lable Sticker",["template","style"])   
    html = frappe.render_template(data_template, get_print_context(doc=doc_sale,sale_products = _products,printer_name=printer_name))    
    return {"html":html,"css":css}

## print waiting slip
@frappe.whitelist(allow_guest=True,methods='POST')
def get_wifi_template(password):    
    data_template,css = frappe.db.get_value("POS Receipt Template","WiFi",["template","style"]) 
    html= frappe.render_template(data_template, {"password":password})
    return {"html":html,"css":css}

## print report Print Format
@frappe.whitelist(allow_guest=True,methods='POST')
def get_report_from_print_format_template(data):    
    return print_from_print_format(data,is_html=True)

@frappe.whitelist(allow_guest=True)
def get_working_day_info(name,pos_profile):
    result = []

    working_day = frappe.get_doc("Working Day",name)
    exch = frappe.db.sql("select exchange_rate,exchange_rate_input,from_currency,to_currency from `tabCurrency Exchange` where docstatus = 1 and posting_date <= '{}' and from_currency <> to_currency order by posting_date  desc limit 1".format(working_day.posting_date),as_dict=1)
    main = frappe.get_doc("Currency",frappe.db.get_default("currency"))
    second = frappe.get_doc("Currency",frappe.db.get_default("second_currency"))
 
    result.append({
            "categroy":'working_day_info',
            'title':'Working Day',
            'value': working_day.name
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Business Branch',
            'value': working_day.business_branch
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Outlet',
            'value': working_day.outlet
        })
    result.append({
            "categroy":'working_day_info',
            'title':'POS Profile',
            'value': pos_profile
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Created Date',
            'value': working_day.creation
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Opened By',
            'value': frappe.get_doc("User", working_day.owner).full_name
        })
    result.append({
        "categroy":'working_day_info',
        'title':'Status',
        'value': "Opened" if working_day.is_closed == 1 else "Closed"
    })
    result.append({
        "categroy":'working_day_info',
        'title':'Closed Date',
        'value': frappe.format(working_day.modified,{'fieldtype':'Datetime'})
    })
    result.append({
        "categroy":'working_day_info',
        'title':'Closed By',
        'value': frappe.get_doc("User", working_day.modified_by).full_name
    })
    result.append({
        "categroy":'working_day_info',
        'title':'Exchange Rate',
        'value':  (frappe.utils.fmt_money(1,currency=exch[0].from_currency, precision = main.custom_currency_precision)) + " = " + frappe.utils.fmt_money(exch[0].exchange_rate_input,currency=exch[0].to_currency, precision=second.custom_currency_precision)
    })

    sale_transactions = frappe.db.sql("""
    select sale_type, count(name) as total_transaction, count(name) as total_display from `tabSale` where working_day = '{0}' and docstatus = 1 and is_foc=0 and pos_profile = '{1}' group by sale_type
    union 
    select 'FOC' as sale_type, count(name) as total_transaction, count(name) as total_display from `tabSale` where working_day = '{0}' and docstatus = 1 and is_foc=1 
    union
    select 'Voucher Claim' as sale_type,count(name) as total_transaction,count(name) as total_voucher_claim from `tabSale Payment` where working_day = '{0}' and docStatus = 1
    union
    select 'Voucher Top Up' as sale_type,count(name) as total_transaction,count(name) as total_voucher_claim from `tabVoucher` where working_day = '{0}' and docStatus = 1
    union
    select 'Void Transaction' as sale_type, 0 as total_transaction, count(name) as total_display from `tabSale` where working_day = '{0}' and docstatus = 2
    union
    select 'Total Guest Cover' as sale_type, 0 as total_display, sum(guest_cover) as total_transaction from `tabSale` where working_day = '{0}'""".format(working_day.name,pos_profile),as_dict=1)
    for a in sale_transactions:
        result.append({
            "categroy":'sale_transactions',
            'title': a["sale_type"],
            'value': str(a["total_transaction"])
        })

    sale_transactions = frappe.db.sql("""select 
    coalesce(sum(if(is_foc=0,sub_total,0)),0) as `Sub Total`,
    coalesce(sum(if(is_foc=0,total_discount,0)),0) as `Total Discount`,
    coalesce(sum(if(is_foc=0,tax_1_amount,0)),0) as `Tax 1`,
    coalesce(sum(if(is_foc=0,tax_2_amount,0)),0) as `Tax 2`,
    coalesce(sum(if(is_foc=0,tax_3_amount,0)),0) as `Tax 3`,
    coalesce(sum(if(is_foc = 1,grand_total,0)),0) as `Total FOC Amount`,
    coalesce(sum(if(is_foc = 0,grand_total,0)),0) as `Grand Total`,
    coalesce(sum(commission_amount),0) as `Total Commission Amount`
    from `tabSale` where working_day = '{0}' and docstatus = 1 and pos_profile = '{1}'""".format(working_day.name,pos_profile),as_dict=1)
    for k in sale_transactions[0].keys():
        result.append({
            "categroy":'sale_summary',
            'title':k,
            'value': frappe.utils.fmt_money(sale_transactions[0][k],currency=main.name, precision=main.custom_currency_precision)
        })
     
    sale_by_revenue_group = frappe.db.sql("""
    select 
        revenue_group,
        coalesce(sum(sp.quantity)) as total_qty,
        coalesce(sum(total_revenue)) as amount 
    from `tabSale Product` sp
        inner join tabSale s on s.name = sp.parent
    where 
        s.working_day = '{0}' and 
        s.is_foc=0 and 
        s.docstatus = 1 and
        s.pos_profile = '{1}'
    group by revenue_group
    union
    select
        'Voucher Top Up' revenue_group,
        count(name) as total_qty,
        coalesce(sum(actual_amount)) as amount
    from `tabVoucher`
    where working_day = '{0}' and docstatus=1
    """.format(working_day.name,pos_profile),as_dict=1)
    for a in sale_by_revenue_group:
        result.append({
            "categroy":'sale_by_revenue_group',
            'title': a["revenue_group"],
            'value': str(a["total_qty"])+"/"+frappe.utils.fmt_money(a["amount"],currency=main.name, precision=main.custom_currency_precision)
        })

    foc_by_revenue_group = frappe.db.sql("""
    select revenue_group,
    sum(total_revenue) as amount 
    from `tabSale Product` sp
    inner join tabSale s on s.name = sp.parent
    where s.working_day = '{0}' and s.is_foc=1 and s.docstatus=1 and
    s.pos_profile = '{1}' group by revenue_group""".format(working_day.name,pos_profile),as_dict=1)
    for a in foc_by_revenue_group:
        result.append({
            "categroy":'foc_by_revenue_group',
            'title': a["revenue_group"],
            'value': frappe.utils.fmt_money(a["amount"],currency=main.name, precision=main.custom_currency_precision)
        })
    
    payment_breakdown = frappe.db.sql("""
    select 
        payment_type,
        currency,
        currency_precision,
        exchange_rate,
        sum(fee_amount) as fee_amount ,
        sum(input_amount) as input_amount ,
        sum(payment_amount) as payment_amount
    from `tabSale Payment`
    where working_day = '{0}' and docstatus = 1 and pos_profile = '{1}'
    group by 
        payment_type,
        currency,
        currency_precision,
        exchange_rate""".format(working_day.name,pos_profile),as_dict=1)
    for a in payment_breakdown:
        result.append({
            "categroy":'payment_breakdown',
            'title': a["payment_type"],
            'value': frappe.utils.fmt_money(a["input_amount"] + (a["fee_amount"] * a["exchange_rate"]),currency=a["currency"],precision=a["currency_precision"])
        })
    if(sum(c["payment_amount"] for c in payment_breakdown)>0):
        result.append({
                "categroy":'payment_breakdown',
                'title': "Total Payment Amount",
                'value': frappe.utils.fmt_money(sum(c["payment_amount"] for c in payment_breakdown),currency=main.name, precision=main.custom_currency_precision)+"\n"+frappe.utils.fmt_money(sum(c["payment_amount"] for c in payment_breakdown)* exch[0].exchange_rate, currency=second.name, precision=second.custom_currency_precision)
            })

    voucher_payments = frappe.db.sql("""
    select sum(input_amount) as input_amount,
    sum(payment_amount) as payment_amount,
    payment_type,
    currency 
    from `tabVoucher Payment` 
    where working_day = '{}' and docstatus=1 GROUP BY 
	payment_type, currency """.format(working_day.name),as_dict=1) 
    for a in voucher_payments:
        custom_currency_precision= frappe.db.get_value("Currency",a["currency"],"custom_currency_precision")
        result.append({
            "categroy":'voucher_payments',
            'title': a["payment_type"],
            'value': frappe.utils.fmt_money(a["input_amount"],currency=a["currency"],precision=custom_currency_precision)
        })

    on_account = frappe.db.sql("""
    select 
        payment_type,
        sum(input_amount) as input_amount ,
        sum(amount) as payment_amount 
        from `tabSale` a
        inner join `tabPOS Sale Payment` b on b.parent = a.name
        where working_day = '{0}' and a.pos_profile = '{1}' and payment_type='On Account'
    group by
        payment_type""".format(working_day.name,pos_profile),as_dict=1)
    for a in on_account:
        custom_currency_precision= frappe.db.get_value("Currency",a["currency"],"custom_currency_precision")
        result.append({
            "categroy":'on_account',
            'title': a["payment_type"],
            'value': frappe.utils.fmt_money(a["input_amount"] + (a["fee_amount"] * a["exchange_rate"]),currency=a["currency"],precision=a["currency_precision"])
    })
    if(sum(c["payment_amount"] for c in on_account)>0):
        result.append({
                "categroy":'on_account',
                'title': "Total On Account",
                'value': frappe.utils.fmt_money(sum(c["payment_amount"] for c in on_account),currency=main.name, precision=main.custom_currency_precision)
            })
    
    return {"working_day":result}

@frappe.whitelist(allow_guest=True)
def cashier_shift_info(name,pos_profile):
    result = []

    cashier_shift = frappe.get_doc("Cashier Shift",name)
    exch = frappe.db.sql("select exchange_rate,exchange_rate_input,from_currency,to_currency from `tabCurrency Exchange` where docstatus = 1 and posting_date <= '{}' and from_currency <> to_currency order by posting_date  desc limit 1".format(working_day.posting_date),as_dict=1)
    main = frappe.get_doc("Currency",frappe.db.get_default("currency"))
    second = frappe.get_doc("Currency",frappe.db.get_default("second_currency"))

    result.append({
            "categroy":'cashier_shift_info',
            'title':'Working Day',
            'value': cashier_shift.working_day
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Business Branch',
            'value': working_day.business_branch
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Outlet',
            'value': working_day.outlet
        })
    result.append({
            "categroy":'working_day_info',
            'title':'POS Profile',
            'value': pos_profile
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Created Date',
            'value': working_day.creation
        })
    result.append({
            "categroy":'working_day_info',
            'title':'Opened By',
            'value': frappe.get_doc("User", working_day.owner).full_name
        })
    result.append({
        "categroy":'working_day_info',
        'title':'Status',
        'value': "Opened" if working_day.is_closed == 1 else "Closed"
    })
    result.append({
        "categroy":'working_day_info',
        'title':'Closed Date',
        'value': frappe.format(working_day.modified,{'fieldtype':'Datetime'})
    })
    result.append({
        "categroy":'working_day_info',
        'title':'Closed By',
        'value': frappe.get_doc("User", working_day.modified_by).full_name
    })
    result.append({
        "categroy":'working_day_info',
        'title':'Exchange Rate',
        'value':  (frappe.utils.fmt_money(1,currency=exch[0].from_currency, precision = main.custom_currency_precision)) + " = " + frappe.utils.fmt_money(exch[0].exchange_rate_input,currency=exch[0].to_currency, precision=second.custom_currency_precision)
    })


    return {"cashier_shift":result}