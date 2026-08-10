import frappe
from frappe import _
from frappe.utils import getdate
from frappe.rate_limiter import rate_limit
from epos_restaurant_2023.api.share.utils import api_rate_limit,api_error,api_response

@frappe.whitelist()
@api_rate_limit(limit=10, seconds=60*2)
def get(**args):  
    if  frappe.request.method != "POST":      
        return api_error(_("Method Not Allowed"),405)  
    
    p = {k.strip(): v for k, v in args.items()}  
    p.pop("cmd",None)
    
    limit = p.get("limit",20) or 20
    name = p.get("id",None)
    shifts = p.get("shifts",[])
    
    posting_date = p.get("posting_date", None)
    if not posting_date:
        frappe.local.response.update({
            "message": _("Posting Date is required"),
            "http_status_code": 422
        })
        return
    
    try:
        posting_date = getdate(posting_date)
    except Exception as e:
        return api_error(_("Posting Date must be a valid date"), 422)

    
    filters = {
         "docstatus": 1,
         "posting_date": posting_date,         
    }
    
    if name:
        filters.update({"name":name})
    
    if shifts:
        filters.update({
            "shift_name":["in", shifts]
        })
    
    sales = frappe.get_all("Sale", 
                            fields=["name"], 
                            filters=filters,                            
                            order_by="posting_date asc", limit=limit)
    
    result = []
    for g in sales:
        sale = frappe.get_doc("Sale", g.name)
        result.append({
            "sale_info":{
                "id": sale.name,
                "invoice_number": sale.custom_bill_number,
                "total_guest":sale.guest_cover,
                "customer_id": sale.customer,
                "customer_name": sale.customer_name,
                "posting_date":sale.posting_date,
                "shift": sale.shift_name,
                "rate_include_tax":sale.rate_include_tax,
                "total_quantity":sale.total_quantity,
                "total_discount":sale.total_discount,
                "total_tax":sale.total_tax,
                "total_amount": sale.grand_total,
                "closed_by":sale.closed_by,
                "closed_date":sale.closed_date,
            },
            "payments":_get_sale_payments(sale),
            "sale_products": _get_sale_products(sale),
            
        })
        
        
    return api_response(result)

def _get_sale_products(sale):
    sale_products = []
    for d in sale.sale_products:
        price = (d.price or 0) + (d.modifiers_price or 0)
        subtotal = d.quantity * price
        discount_type = d.discount_type or "Percent"
        discount = 0.0
        if d.sale_discount_percent == 0 and d.sale_discount_amount > 0:
            discount_type = "Amount"
            
        if d.sale_discount_percent > 0 :
            discount = d.sale_discount_percent
            
        if d.discount_type == "Percent" and d.discount > 0:
            discount = d.discount
        
        if d.discount_type == "Amount":
            discount = d.total_discount
            
        sale_products.append({
            "id": d.name,            
            "product_code": d.product_code,
            "product_name": d.product_name,
            "portion": d.portion,
            "modifiers": d.modifiers,            
            "unit": d.unit,           
            "quantity": d.quantity,
            "price": price,
            "sub_total": subtotal,
            "total_amount": subtotal - (d.total_discount or 0), 
            "discount_type": discount_type,
            "discount_value": discount,
            "discount_amount": d.total_discount or 0,
            "rate_include_tax": d.rate_include_tax or 0,
            "tax_amount":d.total_tax or 0,
            "is_free": d.is_free or 0,
            "is_return": d.is_return or 0,
            "allow_discount":d.allow_discount,
            "note": d.note or "",
             "product_category":d.product_category,
            "revenue_group":d.revenue_group,
        },)
        
    return sale_products

def _get_sale_payments(sale):
    payments = []
    for d in sale.payment:
        payments.append({
            "id": d.name,
            "payment_type": d.payment_type,
            "payment_type_group": d.payment_type_group,
            "input_amount": d.input_amount,
            "amount": d.amount,
            "exchange_rate": d.exchange_rate
        })
        
    return payments

