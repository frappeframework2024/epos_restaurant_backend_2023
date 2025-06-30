import frappe
from frappe import _

@frappe.whitelist()
def get_cashier_shift_summary_inrormation(cashier_shift):
    shift_doc = frappe.get_cached_doc("Cashier Shift", cashier_shift)
    return {
        "shift_doc":shift_doc,
        "exchange_rate":get_exchange_rate(shift_doc.posting_date),
        "transactions":get_transactions(cashier_shift)
    }


def get_transactions(cashier_shift):
    sql ="""
        select 
            count(s.sale_type == 'Sale Coupon') as total_sale_coupon,
        from `tabSale` s
        where
            cashier_shift = %(cashier_shift)s and
            docstatus = 1 
    """
    data = frappe.db.sql(sql,{"cashier_shift":cashier_shift},as_dict=1)
    data = data[0]
    return [
        {"label":"Sale Coupon","value": data.get("total_sale_coupon")}
    ]

def  get_exchange_rate(date):
    currency, second_currency = frappe.get_cached_value("ePOS Settings",None,["currency","second_currency"])
    sql="""
        select 
            exchange_rate 
        from `tabCurrency Exchange` 
        where 
            posting_date <= %(date)s and 
            docstatus = 1  and 
            from_currency = %(currency)s and 
            to_currency = %(second_currency)s
        order by 
        creation desc limit 1
    
    """
    data = frappe.db.sql(sql,{"date":date,"currency":currency,"second_currency":second_currency},as_dict=1)

    if data:
        return data[0].exchange_rate
    
    return 1
