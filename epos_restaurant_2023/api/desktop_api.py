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
            'value': frappe.format(working_day.creation,{'fieldtype':'Datetime'})
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

    close_cashier = frappe.db.sql("""
    select count(name) as total_shift  from `tabCashier Shift`
    where working_day='{}'""".format(working_day.name),as_dict=1)
    result.append({
            "categroy":'sale_transactions',
            'title': "Total Cashier Shift",
            'value': str(close_cashier[0].total_shift)
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
    result.append({
            "categroy":'sale_transactions',
            'title': "# Transactions",
            'value': str(sum(a.total_transaction for a in sale_transactions))
        })
    for a in sale_transactions:
        if a["total_display"]>0:
            result.append({
                "categroy":'sale_transactions',
                'title': a["sale_type"],
                'value': str(a["total_display"])
            })

    sale_summary = frappe.db.sql("""select 
    coalesce(sum(if(is_foc=0,sub_total,0)),0) as `Sub Total`,
    coalesce(sum(if(is_foc=0,total_discount,0)),0) as `Total Discount`,
    coalesce(sum(if(is_foc=0,sub_total,0)),0)- coalesce(sum(if(is_foc=0,total_discount,0)),0)-  coalesce(sum(commission_amount),0) `Total Net Sale`,
    coalesce(sum(if(is_foc=0,tax_1_amount,0)),0) as `Tax 1`,
    coalesce(sum(if(is_foc=0,tax_2_amount,0)),0) as `Tax 2`,
    coalesce(sum(if(is_foc=0,tax_3_amount,0)),0) as `Tax 3`,
    coalesce(sum(if(is_foc = 1,grand_total,0)),0) as `Total FOC Amount`,
    coalesce(sum(if(is_foc = 0,grand_total,0)),0)-coalesce(sum(commission_amount),0) as `Total Sale Revenue`,
    coalesce(sum(commission_amount),0) as `Total Commission Amount`
    from `tabSale` where working_day = '{0}' and docstatus = 1 and pos_profile = '{1}'""".format(working_day.name,pos_profile),as_dict=1)
    for k in sale_summary[0].keys():
        if sale_summary[0][k]>0:
            result.append({
                "categroy":'sale_summary',
                'title':k,
                'value': frappe.utils.fmt_money(sale_summary[0][k],currency=main.name, precision=main.custom_currency_precision)
            })
     
    sale_by_revenue_group = frappe.db.sql("""
    select 
        revenue_group,
        coalesce(sum(sp.quantity),0) as total_qty,
        coalesce(sum(total_revenue),0) as amount 
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
        coalesce(sum(actual_amount),0) as amount
    from `tabVoucher`
    where working_day = '{0}' and docstatus=1
    """.format(working_day.name,pos_profile),as_dict=1)
    for a in sale_by_revenue_group:
        if a["amount"]>0:
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
        if a["amount"]>0:
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
    exch = frappe.db.sql("select exchange_rate,exchange_rate_input,from_currency,to_currency from `tabCurrency Exchange` where docstatus = 1 and posting_date <= '{}' and from_currency <> to_currency order by posting_date  desc limit 1".format(cashier_shift.posting_date),as_dict=1)
    main = frappe.get_doc("Currency",frappe.db.get_default("currency"))
    second = frappe.get_doc("Currency",frappe.db.get_default("second_currency"))

    result.append({
            "categroy":'cashier_shift_info',
            'title':'Working Day',
            'value': cashier_shift.working_day
        })
    result.append({
            "categroy":'cashier_shift_info',
            'title':'Cashier Shift',
            'value': cashier_shift.name
        })
    result.append({
            "categroy":'cashier_shift_info',
            'title':'Business Branch',
            'value': cashier_shift.business_branch
        })
    result.append({
            "categroy":'cashier_shift_info',
            'title':'Outlet',
            'value': cashier_shift.outlet
        })
    result.append({
            "categroy":'cashier_shift_info',
            'title':'POS Profile',
            'value': pos_profile
        })
    result.append({
            "categroy":'cashier_shift_info',
            'title':'Created Date',
            'value': frappe.format(cashier_shift.creation,{'fieldtype':'Datetime'})
        })
    result.append({
            "categroy":'cashier_shift_info',
            'title':'Opened By',
            'value': frappe.get_doc("User", cashier_shift.owner).full_name
        })
    result.append({
        "categroy":'cashier_shift_info',
        'title':'Status',
        'value': "Opened" if cashier_shift.is_closed == 1 else "Closed"
    })
    result.append({
        "categroy":'cashier_shift_info',
        'title':'Closed Date',
        'value': frappe.format(cashier_shift.modified,{'fieldtype':'Datetime'})
    })
    result.append({
        "categroy":'cashier_shift_info',
        'title':'Closed By',
        'value': frappe.get_doc("User", cashier_shift.modified_by).full_name
    })
    result.append({
        "categroy":'cashier_shift_info',
        'title':'Exchange Rate',
        'value':  (frappe.utils.fmt_money(1,currency=exch[0].from_currency, precision = main.custom_currency_precision)) + " = " + frappe.utils.fmt_money(exch[0].exchange_rate_input,currency=exch[0].to_currency, precision=second.custom_currency_precision)
    })

    sale_transactions = frappe.db.sql("""
    select  sale_type, count(name) as total_transaction , count(name) as total_display from `tabSale` 
    where cashier_shift = '{0}' and docstatus = 1 and is_foc=0 group by sale_type
    union 
    select  'FOC', count(name) as total_transaction, count(name) as total_display from `tabSale` where cashier_shift = '{0}' and docstatus = 1 and is_foc=1
    union
    select   'Total Guest Cover' as sale_type, 0 as total_display, sum(guest_cover)  as total_transaction from `tabSale` 
    where cashier_shift = '{0}' and docstatus = 1 """.format(cashier_shift.name),as_dict=1)
    result.append({
        "categroy":'sale_transactions',
        'title': "# Cash Float",
        'value': str(sum(a.total_transaction for a in sale_transactions))
    })
    sale_transactions_cash_float = frappe.db.sql("""
    SELECT currency,input_amount,currency_precision,payment_method FROM `tabCashier Shift Cash Float` WHERE payment_type_group='Cash' AND parent='{0}'""".format(cashier_shift.name),as_dict=1)
    for a in sale_transactions_cash_float:
        if a["input_amount"]>0:
            result.append({
                "categroy":'sale_transactions',
                'title': a["payment_method"],
                'value': frappe.utils.fmt_money(a["input_amount"],currency=a["currency"],precision=a["currency_precision"])
            })
    result.append({
        "categroy":'sale_transactions',
        'title': "# Transactions",
        'value': str(sum(a.total_transaction for a in sale_transactions))
    })
    for a in sale_transactions:
        if a["total_display"]>0:
            result.append({
                "categroy":'sale_transactions',
                'title': a["sale_type"],
                'value': str(a["total_display"])
            })

    cash_float = frappe.db.sql("""
    SELECT 
    currency,
    input_amount,
    currency_precision,
    input_close_amount,
    close_amount,
    system_close_amount,
    different_amount 
    FROM `tabCashier Shift Cash Float` 
    WHERE payment_type_group='Cash' AND parent='{0}'""".format(cashier_shift.name),as_dict=1)
    if cash_float:
        for a in cash_float:
            result.append({
                "categroy":'cash_drawer',
                'title': 'Starting Amount' + '(' + a["currency"] + ')',
                'value': frappe.utils.fmt_money(a["input_amount"],currency=a["currency"],precision=a["currency_precision"])
            })
    cash_drawer_transactions = frappe.db.sql("""
    select 
        ct.transaction_status,
        ct.currency,
        ct.symbol,
        c.custom_currency_precision,
    sum(ct.input_amount) as total_amount
    from `tabCash Transaction` ct
    inner join `tabCurrency` c on c.name = ct.currency
    where cashier_shift = '{}'
    group by
        ct.transaction_status,
        ct.currency,
        ct.symbol,
        c.custom_currency_precision""".format(cashier_shift.name),as_dict=1)
    if cashier_shift.total_opening_amount>0:
        result.append({
            "categroy":'cash_drawer',
            'title': 'Total Opening Amount',
            'value': frappe.utils.fmt_money(cashier_shift.total_opening_amount,currency=main.name, precision= main.custom_currency_precision)
        })
    if cash_drawer_transactions:
        for a in cash_drawer_transactions:
            result.append({
                "categroy":'cash_drawer',
                'title': a["transaction_status"]+'('+a["currency"]+')',
                'value': frappe.utils.fmt_money(a["total_amount"],currency=a["currency"],  precision= a["custom_currency_precision"])
            })
    cash_sale = frappe.db.sql("""select sum(payment_amount) as payment_amount from `tabSale Payment` where cashier_shift = '{}' and payment_type_group='Cash'""".format(cashier_shift.name),as_dict=1)
    result.append({
        "categroy":'cash_drawer',
        'title': 'Total Cash Sale'+'('+frappe.db.get_default("currency")+')',
        'value': frappe.utils.fmt_money(cash_sale[0].payment_amount,currency=main.name,  precision= main.custom_currency_precision)
    })
    for a in cash_float:
        result.append({
            "categroy":'cash_drawer',
            'title': 'Close Amount' + '(' + a["currency"] + ')',
            'value': frappe.utils.fmt_money(a["input_close_amount"],currency=a["currency"],  precision= a["currency_precision"])
        })
    result.append({
        "categroy":'cash_drawer',
        'title': 'Total Closed Amount'+'('+frappe.db.get_default("currency")+')',
        'value': frappe.utils.fmt_money(sum(a.close_amount for a in cash_float),currency=main.name, precision= main.custom_currency_precision)
    })
    result.append({
        "categroy":'cash_drawer',
        'title': 'Expected Cash',
        'value': frappe.utils.fmt_money(sum(a.system_close_amount for a in cash_float),currency=main.name, precision= main.custom_currency_precision)
    })
    result.append({
        "categroy":'cash_drawer',
        'title': 'Different Amount'+'('+frappe.db.get_default("currency")+')',
        'value': frappe.utils.fmt_money(sum(a.different_amount for a in cash_float),currency=main.name, precision= main.custom_currency_precision)
    })
    sale_summary = frappe.db.sql("""
    select 
    coalesce(sum(if(is_foc=0,sub_total,0)),0) as `Sale Sub Total`,
    coalesce(sum(if(is_foc=0,total_discount,0)),0) as `Total Discount`,
    coalesce(sum(if(is_foc = 0,grand_total,0)),0) as `Total Net Sale`,
    coalesce(sum(if(is_foc=0,tax_1_amount,0)),0) as `Tax 1`,
    coalesce(sum(if(is_foc=0,tax_2_amount,0)),0) as `Tax 2`,
    coalesce(sum(if(is_foc=0,tax_3_amount,0)),0) as `Tax 3`,
    coalesce(sum(if(is_foc = 0,grand_total,0)),0)-coalesce(sum(commission_amount),0) as `Total Sale Revenue`,
    coalesce(sum(changed_amount),0) as `Total Change Amount`,
    coalesce(sum(if(is_foc = 1,grand_total,0)),0) as `Total FOC Amount`,
    coalesce(sum(commission_amount),0) as `Commission Amount`
    from `tabSale`
    where cashier_shift = '{}' and docstatus=1""".format(cashier_shift.name),as_dict=1)
    for k in sale_summary[0].keys():
        if sale_summary[0][k]>0:
            result.append({
                "categroy":'sale_summary',
                'title':k,
                'value': frappe.utils.fmt_money(sale_summary[0][k],currency=main.name, precision=main.custom_currency_precision)
            })

    sale_by_revenue_group = frappe.db.sql("""
    select 
    revenue_group,
    sum(total_revenue) as amount ,
    coalesce(sum(quantity),0) as total_qty
    from `tabSale Product` sp
    inner join tabSale s on s.name = sp.parent
    where s.cashier_shift = '{}' and s.is_foc=0 and s.docstatus=1 and sp.docstatus=1
    group by revenue_group""".format(cashier_shift.name),as_dict=1)
    for a in sale_by_revenue_group:
        result.append({
            "categroy":'sale_by_revenue_group',
            'title': a["revenue_group"],
            'value': str(a["total_qty"])+"/"+frappe.utils.fmt_money(a["amount"],currency=main.name, precision=main.custom_currency_precision)
        })
    
    foc_revenue_group = frappe.db.sql("""
    select 
    revenue_group,
    sum(total_revenue) as amount,
    coalesce(sum(quantity),0) as total_qty
    from `tabSale Product` sp
    inner join tabSale s on s.name = sp.parent
    where s.cashier_shift = '{}' and s.is_foc=1
    group by revenue_group""".format(cashier_shift.name),as_dict=1)
    if foc_revenue_group:
        for a in foc_revenue_group:
            result.append({
                "categroy":'foc_revenue_group',
                'title': a["revenue_group"],
                'value': str(a["total_qty"])+"/"+frappe.utils.fmt_money(a["amount"],currency=main.name, precision=main.custom_currency_precision)
            })
    
    voucher_payments = frappe.db.sql("""
    select 
    sum(input_amount) as input_amount,
    payment_type,currency 
    from `tabVoucher Payment` 
    where cashier_shift = '{}' 
    GROUP BY payment_type,currency """.format(cashier_shift.name),as_dict=1)
    if voucher_payments:
        for a in voucher_payments:
            custom_currency_precision= frappe.db.get_value("Currency",a["currency"],"custom_currency_precision")
            result.append({
                "categroy":'voucher_payments',
                'title': a["revenue_group"],
                'value': frappe.utils.fmt_money(a["input_amount"],currency=a["currency"],precision=custom_currency_precision)
            })
    
    payment_breakdown = frappe.db.sql("""
    select 
        payment_type,
        symbol,
        exchange_rate,
        currency,
        currency_precision,
        coalesce(sum(fee_amount),0) as fee_amount,
        coalesce(sum(input_amount),0) as input_amount ,
        coalesce(sum(payment_amount),0) as payment_amount 
    from `tabSale Payment`
    where cashier_shift = '{}'
    group by
        symbol,
        exchange_rate,
        currency,
        currency_precision,
        payment_type""".format(cashier_shift.name),as_dict=1)
    for a in payment_breakdown:
        result.append({
            "categroy":'payment_breakdown',
            'title': a["payment_type"],
            'value': frappe.utils.fmt_money(a["input_amount"] + (a["fee_amount"] * a["exchange_rate"]),currency=a["currency"],precision=a["currency_precision"])
        })
    sale_tip = frappe.db.sql("""
    select 
    coalesce(sum(tip_amount),0) as tip_amount
    from `tabSale`
    where cashier_shift = '{}'
    """.format(cashier_shift.name),as_dict=1)
    if sum(a.tip_amount for a in sale_tip)>0:
        result.append({
            "categroy":'payment_breakdown',
            'title': 'Tip Amount',
            'value': frappe.utils.fmt_money(sum(a.tip_amount for a in sale_tip), currency=main.name, precision=main.custom_currency_precision)
        })
    result.append({
        "categroy":'payment_breakdown',
        'title': 'Total Payment',
        'value': frappe.utils.fmt_money(sum(a.payment_amount+a.fee_amount for a in payment_breakdown), currency=main.name, precision=main.custom_currency_precision)+' = '+
                 frappe.utils.fmt_money(sum(a.payment_amount+a.fee_amount for a in payment_breakdown)* exch[0].exchange_rate, currency=second.name, precision=second.custom_currency_precision)
    })

    revenue_cash_transaction = frappe.db.sql("""
    select 
        ct.transaction_status, 
        ct.input_amount,
        ct.amount,
        ct.payment_type, 
        ct.note,
        ct.symbol
    from `tabCash Transaction` ct
    where 
        ct.cashier_shift = '{}'
    """.format(cashier_shift.name),as_dict=1)
    revenue_sale_transactions = frappe.db.sql("""
    select 
        payment_type,
        symbol,
        sum(input_amount) as input_amount ,
        sum(fee_amount) as fee_amount ,
        sum(payment_amount) as payment_amount 
    from `tabSale Payment`
    where cashier_shift = '{}'
    group by
        symbol,
        payment_type""".format(cashier_shift.name),as_dict=1)
    result.append({
    "categroy":'total_revenue',
    'title': 'Total Revenue',
    'value': frappe.utils.fmt_money(cashier_shift.total_opening_amount + sum(a.payment_amount+a.fee_amount for a in revenue_sale_transactions)+sum(a.amount if a.transaction_status == "Cash In" else 0 for a in revenue_cash_transaction)-sum(a.amount if a.transaction_status == "Cash Out" else 0 for a in revenue_cash_transaction), currency=main.name, precision=main.custom_currency_precision)+' = '+
             frappe.utils.fmt_money((cashier_shift.total_opening_amount + sum(a.payment_amount+a.fee_amount for a in revenue_sale_transactions)+sum(a.amount if a.transaction_status == "Cash In" else 0 for a in revenue_cash_transaction)-sum(a.amount if a.transaction_status == "Cash Out" else 0 for a in revenue_cash_transaction))* exch[0].exchange_rate, currency=second.name, precision=second.custom_currency_precision)
    })

    on_account = frappe.db.sql("""
    select 
        payment_type,
        currency_symbol,
        sum(input_amount) as input_amount ,
        sum(amount) as payment_amount 
        from `tabSale` a
        inner join `tabPOS Sale Payment` b on b.parent = a.name
        where cashier_shift = '{}' and payment_type='On Account'
    group by
        currency_symbol,
        payment_type""".format(cashier_shift.name),as_dict=1)
    if sum(a.payment_amount for a in on_account)>0:
        result.append({
        "categroy":'on_account',
        'title': 'Total On Account'+'('+frappe.db.get_default("currency")+')',
        'value': frappe.format_value(sum(a.payment_amount for a in on_account),"Currency")
        })

    return {"cashier_shift":result}