import frappe
from frappe import _
from frappe.utils import getdate
from epos_restaurant_2023.api.share.utils import api_rate_limit, api_error,api_response

@frappe.whitelist()
@api_rate_limit(limit=10, seconds=60*2)
def get(**args):  
    if  frappe.request.method != "POST":      
        return api_error(_("Method Not Allowed"),405)  
    
    p = {k.strip(): v for k, v in args.items()}  
    p.pop("cmd",None)
    
    limit = p.get("limit",20) or 20
    limit_start = p.get("limit_start",0)
    
    filters = {
        "disabled":0
    }
    
    
    # get product all 
    batch_size = 100
    start = limit_start
    all_products = []
    while True:
        products = frappe.get_all(
            "Product",
            fields=["name"],
            filters=filters,
            order_by="sort_order asc",
            limit_start=start,
            limit_page_length=batch_size
        )

        if not products:
            break

        all_products.extend(products)    
        if len(products) >= batch_size:            
            start += batch_size       
        else:
            start += len(products) 
        break
        
    
    result = []
    for product in all_products:
        p = frappe.get_doc("Product", product.name)
        # result.append(p)
        result.append(_prepare_product(p))
        
    
    
    return api_response(result,start)


def _prepare_product(product):
    p = product
    prices = []
    modifiers = []
    if not p.product_price:
        prices = [{
            "portion":"Normal",
            "unit":p.unit,
            "price":p.price
        }]
    else:
        prices = [{
            "portion":pp.portion,
            "unit":pp.unit,
            "price":pp.price
        } for pp in p.product_price]
        
    if p.product_modifiers:
        modifiers = [{
            "group": pm.modifier_category,
            "prefix":pm.prefix,
            "modifier_name":pm.modifier_code,
            "price":pm.price
        } for pm in p.product_modifiers]
        
    product_json = {
        "id":p.name,
        "product_code":p.product_code,
        "product_name":p.product_name_en,
        "category":p.product_category,
        "revenue":p.revenue_group,
        "base_unit":p.unit,
        "rate_include_tax":p.rate_include_tax,
        "is_open_product":p.is_open_product,
        "is_inventory":p.is_inventory_product,
        "allow_discount":p.allow_discount,
        "prices": prices,
        "modifiers":modifiers,
        "is_pos_menu":len(p.pos_menus) > 0,
        "sort": p.sort_order,        
    }
    
    return product_json


