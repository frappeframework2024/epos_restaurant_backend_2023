import json
import frappe
import requests
from py_linq import Enumerable
def get_context(context):
    context.no_cache = 1
    product =None
    emenu = frappe.get_doc("eMenu",frappe.form_dict.emenu_name) 
    if (frappe.form_dict.menu=="populars"):
        products =  [p for p in emenu.popular_product if p.product_code == frappe.form_dict.product_code ] 
        if len( products) >0 :
            product = products[0]
    else:
        product = frappe.get_doc("Temp Product Menu",frappe.form_dict.category)

    min_price = product.price or 0
    max_price = product.price or 0

    
    product_prices = json.loads(product.prices or "[]")    
    if len(product_prices)>0:
        min_price = Enumerable(product_prices).min(lambda x: x["price"] or 0)
        max_price = Enumerable(product_prices).max(lambda x: x["price"] or 0)

    product.update({
        "prices": product_prices
        }) 
    context.doc = product
    context.emenu = emenu
    context.min_price = min_price
    context.max_price = max_price