import frappe
from frappe import _

@frappe.whitelist()
def get_cashier_shift_summary_inrormation(cashier_shift):
    shift_doc = frappe.get_cached_doc("Cashier Shift", cashier_shift)
    return {
        "shift_doc":shift_doc,
        "exchange_rate":get_exchange_rate(shift_doc.posting_date),
       
    }


@frappe.whitelist()
def get_sale_summary(cashier_shift):
    sql ="""
        select 
            sale_type,
            sum(if(sale_type in ('Sale Coupon','Top Up'), 1,0)) as total_bill,
            sum(if(sale_type='Sale Coupon', total_quantity,0)) as total_coupon,
            sum(sub_total) as sub_total,
            sum(total_discount) as total_discount,
            sum(grand_total) as total_amount,
            sum(total_coupon_value) as coupon_value
        from `tabSale`
        where
            docstatus = 1 and 
            cashier_shift = %(cashier_shift)s
        group by
            sale_type
    """
    data = frappe.db.sql(sql,{"cashier_shift":cashier_shift},as_dict=1)
    
    return_data = []
    for t in ["Sale Coupon","Top Up","Redeem"]:
        tran = [d for d in data if d.get("sale_type") == t]
        if tran:
            return_data.append(tran[0])
        else:
            return_data.append({"sale_type":t})
    return return_data

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


