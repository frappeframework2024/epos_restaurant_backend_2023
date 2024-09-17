import frappe
import json

import frappe

def add_to_inventory_transaction(data):
    
    doc = frappe.get_doc(data)
    doc.insert()

@frappe.whitelist(allow_guest=True)
def get_product_qty(product,stock_location):
    qty = 0
    current_qtys = frappe.db.sql("select quantity from `tabStock Location Product` where product_code = '{0}' and stock_location = '{1}'".format(product,stock_location),as_dict=True)
    if len(current_qtys)>0:
        qty = current_qtys[0].quantity
    return qty

def update_product_quantity(stock_location,product_code, quantity,cost,doc):
    if doc:
        doc.quantity =(doc.quantity or 0) + (quantity or 0)
        if cost != None:
                doc.cost = ((doc.total_cost or 0) + cost*quantity) / (doc.quantity if doc.quantity>0 else 1)  
                
        doc.total_cost = (doc.cost or 0) * (doc.quantity or 0)
        doc.save()
      
    else:
        doc = frappe.get_doc({
					'doctype': 'Stock Location Product',
					'product_code': product_code,
					'stock_location':stock_location,
					'quantity':quantity or 0,
					'cost':cost or 0,
					'total_cost':(quantity or 0) * (cost or 0)
				})
        doc.insert() 
        
def get_stock_location_product(stock_location,product_code):
    data = frappe.db.sql("select name from `tabStock Location Product` where stock_location='{}' and product_code='{}'".format(stock_location, product_code), as_dict=1)
    if data:
            return frappe.get_doc("Stock Location Product", data[0].name)
    else:
        return None

@frappe.whitelist(allow_guest=True)
def get_uom_conversion(from_uom, to_uom):
    conversion =frappe.db.get_value('Unit of Measurement Conversion', {'from_uom': from_uom,"to_uom":to_uom}, ['conversion'], cache=True)
    
    return conversion or 1

@frappe.whitelist(allow_guest=True)
def get_bom_product_price(product_code):
    price = 0
    prices = frappe.db.sql("select price from `tabProduct Price` where parent = '{}' order by creation desc".format(product_code),as_dict=True)
    if len(prices) > 0:
        price = prices[0].price
    else:
        price = frappe.db.get_value('Product', product_code, 'price') 
    return price or 0

@frappe.whitelist(allow_guest=True)
def get_bom_product_cost(product_code):
    cost = 0
    costs = frappe.db.sql("select cost from `tabStock Location Product` where product_code = '{}' order by quantity desc".format(product_code),as_dict=True)
    if len(costs) > 0:
        cost = costs[0].cost
    else:
        cost = frappe.db.get_value('Product', product_code, 'cost') 
    return cost or 0


@frappe.whitelist(allow_guest=True)
def get_product_cost(stock_location, product_code):
    cost = 0
    if stock_location != "None":
        cost = frappe.db.get_value('Stock Location Product', {'stock_location':stock_location,"product_code":product_code}, ['cost'])
        if (cost or 0) == 0:
            cost =  frappe.db.get_value('Product',product_code, 'cost')
    else:
        cost = frappe.db.get_value('Product', product_code, 'cost')    
    return cost or 0

def check_uom_conversion(from_uom, to_uom):
    conversion =frappe.get_cached_value('Unit of Measurement Conversion', {'from_uom': from_uom,"to_uom":to_uom}, "conversion")
    return conversion

@frappe.whitelist(allow_guest=True)
def calculate_average_cost(product_code,stock_location,quantity=0,stock_value=0,doc_name=""):
    current_stock = frappe.db.sql("select cost,quantity,total_cost from `tabStock Location Product` where stock_location='{}' and product_code='{}'".format(stock_location, product_code), as_dict=1)
    
    current_qty = 0
    current_stock_cost = 0

    new_qty = float(quantity)
    new_stock_cost = float(stock_value)

    if current_stock:
        current_qty = float(current_stock[0]["quantity"])
        current_stock_cost = float(current_stock[0]["total_cost"])
    
    if doc_name != "":
        last_cost = frappe.db.sql("SELECT previous_cost cost FROM `tabInventory Transaction` where transaction_number = '{0}' and product_code = '{1}'".format(doc_name,product_code), as_dict=1)
        return last_cost[0].cost

    stock_cost = (current_stock_cost if current_stock_cost > 0 else 0) + new_stock_cost
    qty = (current_qty if current_qty > 0 else 0) + new_qty
    avc = stock_cost / qty

    return avc

@frappe.whitelist(allow_guest=True)
def get_last_inventory_transaction(product_code,stock_location,doc_name):
    data = frappe.db.sql("SELECT price FROM `tabInventory Transaction` where stock_location='{}' and product_code='{}' and transaction_number <> '{}' and docstatus = 0 order by creation desc limit 1".format(stock_location,product_code,doc_name), as_dict=1)
    if data:
       return data[0]["price"]
    else:
        return frappe.db.get_value('Product', {"name":product_code}, ['cost']) or 0
    
@frappe.whitelist(allow_guest=True)
def update_inventory_transaction_status(doc_name):
    frappe.db.sql("update `tabInventory Transaction` set docstatus = 2 where transaction_number = '{}'".format(doc_name))
    frappe.db.commit()