
import frappe
import json
from frappe.utils.response import json_handler
from datetime import datetime, timedelta
from epos_restaurant_2023.inventory.inventory import get_uom_conversion
@frappe.whitelist(allow_guest=True)
def get_product_by_menu(root_menu="", mobile = 0):
    if root_menu=="":
        return []
    else:
        menus = []
        sql = """select 
                    name,
                    pos_menu_name_en as name_en,
                    pos_menu_name_kh as name_kh,
                    parent_pos_menu as parent,
                    photo,
                    text_color,
                    background_color,
                    shortcut_menu,
                    price_rule,
                    photo,
                    'menu' as type,
                    1 as type_index,
                    sort_order
                from `tabPOS Menu` 
                where 
                    parent_pos_menu='{}' and
                    disabled = 0 
                order by sort_order, name
                """.format(root_menu)
        data = frappe.db.sql(sql,as_dict=1)
        
        for d in data:
            menus.append(d)
            child_menus = get_child_menus(d.name, mobile=mobile)
            
            for m in child_menus:
                menus.append(m)
            
            menu_products = get_products(d.name,mobile=mobile)
            for m in menu_products:
                menus.append(m)
        
        menu_products = get_products(root_menu,mobile=mobile)
        for m in menu_products:
                menus.append(m)
             
        return menus

def get_child_menus(parent_menu, mobile= 0):
    menus = []
    menus.append({"type":"back","parent":parent_menu})
    sql = """select 
                name,
                pos_menu_name_en as name_en,
                pos_menu_name_kh as name_kh,
                parent_pos_menu as parent,
                photo,
                text_color,
                background_color,
                shortcut_menu,
                price_rule,
                'menu' as type,
                2 as type_index,
                sort_order
            from `tabPOS Menu` 
            where 
                parent_pos_menu='{}' and
                disabled = 0 
            order by sort_order, name
            """.format(parent_menu)
    data = frappe.db.sql(sql,as_dict=1)
    for d in data:        
        menus.append(d)
        child_menus = get_child_menus(d.name,mobile=mobile)
        for m in child_menus:
            menus.append(m)
        
        for m in get_products(d.name,mobile=mobile):
            menus.append(m)       
        
    return menus


def get_products(parent_menu,mobile=0):     
    sql = """select 
                name as menu_product_name,
                product_code as name,
                product_name_en as name_en,
                product_name_kh as name_kh,
                '{0}' as parent,
                price,
                unit,
                allow_discount,
                allow_change_price,
                allow_free,
                is_open_product,
                is_inventory_product,
                is_require_employee,
                is_timer_product,
                is_open_price,
                prices,
                printers,
                modifiers,
                photo,
                'product' as type,
                3 as type_index,
                append_quantity,
                is_combo_menu,
                use_combo_group,
                combo_menu_data,
                combo_group_data,
                tax_rule,
                sort_order,
                tax_rule_data,
                revenue_group,
                sort_order,
                is_empty_stock_warning,
                rate_include_tax
            from  `tabTemp Product Menu` 
            where 
                pos_menu='{0}' 
            order by sort_order
            """.format(parent_menu)
    data = frappe.db.sql(sql,as_dict=1)
   
    return data


@frappe.whitelist()
def get_product_variants(parent):
    data  = frappe.db.sql("select name from `tabProduct Variants` where parent='{}'".format(parent),as_dict=1)
    if data :
        return data


@frappe.whitelist()
def get_product_by_barcode(barcode):
    #step 1 check barcard in tabProduct if have product return 
    #step 2 if product not exist check barcode from product price if exist retrun
    # step 3 both not exist then throw product not exist    
    #check if barcode have in product
    data  = frappe.db.sql("select name from `tabProduct` where name='{0}' or product_code_2='{0}' or product_code_3='{0}'".format(barcode),as_dict=1)
    
    if data:
            if data[0].name:
                p = frappe.get_doc('Product', data[0].name)
                price = p.price or 0
                if p.product_price:
                    product_price = [d for d in p.product_price if d.unit == p.unit]
                    if product_price:
                        price = product_price[0].price
                        
                return {
                    "menu_product_name": barcode,
                    "name": p.name,
                    "name_en": p.product_name_en,
                    "name_kh": p.product_name_kh,
                    "parent": p.product_category,
                    "price": price,
                    "unit": p.unit,
                    "allow_discount": p.allow_discount,
                    "allow_change_price": p.allow_change_price,
                    "allow_free": p.allow_free,
                    "is_open_product": p.is_open_product,
                    "is_inventory_product": p.is_inventory_product,
                    "is_timer_product":p.is_timer_product,
                    "is_open_price":p.is_open_price,
                    "prices":p.prices,
                    "printers":json.dumps(([pr.printer,pr.group_item_type] for pr in p.printers),default=json_handler),
                    "modifiers": "[]",
                    "photo": p.photo,
                    "type": "product",
                    "revenue_group":p.revenue_group,
                    "append_quantity": 1,
                    "is_require_employee":p.is_require_employee,
                    "modifiers_data": json.dumps(([pr.business_branch,pr.modifier_category,pr.prefix,pr.modifier_code,pr.price] for pr in p.product_modifiers),default=json_handler),
                    "sort_order":p.sort_order,
                    "is_empty_stock_warning":p.is_empty_stock_warning,
                    "rate_include_tax":p.rate_include_tax
                }
            else:
                frappe.throw("Item No Name?")
                
    else:
        
        data  = frappe.db.sql("select name,price,unit,parent from `tabProduct Price` where barcode='{}'".format(barcode),as_dict=1)
        if data:
            product = frappe.get_doc('Product', data[0].parent)
            return {
                        "menu_product_name": product.name,
                        "name": product.name,
                        "name_en": product.product_name_en,
                        "name_kh": product.product_name_kh,
                        "parent": product.product_category,
                        "price": data[0].price,
                        "unit": data[0].unit,
                        "allow_discount": product.allow_discount,
                        "allow_change_price": product.allow_change_price,
                        "allow_free": product.allow_free,
                        "is_open_product": product.is_open_product,
                        "is_open_price": product.is_open_price,
                        "is_timer_product": product.is_timer_product,
                        "is_inventory_product": product.is_inventory_product,
                        "prices":'[]',#we return empty array because tis barcode is product price barcode
                        "printers":json.dumps(([pr.printer,pr.group_item_type] for pr in product.printers),default=json_handler),
                        "modifiers": "[]",
                        "photo": product.photo,
                        "type": "product",
                        "append_quantity": 1,
                        "is_require_employee":product.is_require_employee,
                        "revenue_group":product.revenue_group,
                        "modifiers_data": json.dumps(([pr.business_branch,pr.modifier_category,pr.prefix,pr.modifier_code,pr.price] for pr in product.product_modifiers),default=json_handler),
                        "sort_order":product.sort_order,
                        "is_empty_stock_warning":p.is_empty_stock_warning,
                        "rate_include_tax":p.rate_include_tax
                    }
        

    frappe.throw("Product Code {} Not Found".format(barcode))
    
@frappe.whitelist(methods="POST")
def get_product_price_by_price_rule(products, business_branch, price_rule="Normal Rate"):
    for p in products:
        doc = frappe.get_doct("Product",p)
        # check product price by price rule and branch
        price = max([d.price for d in doc.product_price if d.business_branch==business_branch and price_rule==d.price_rule]) or 0
        #check product by price rule
        if price==0:
            price = max([d.price for d in doc.product_price if price_rule==d.price_rule]) or 0
            
        #get price by product
        if price==0:
            price = doc.price   
        p["price"] = price
        
    return products

@frappe.whitelist()
def get_product_detail_information(product_code):
    doc = frappe.get_doc("Product",product_code)
    inventory = frappe.db.sql("select stock_location,unit,quantity,reorder_level from `tabStock Location Product` where product_code='{}'".format(product_code),as_dict=1)
    
    return {"product":doc,"invenotry":inventory}

@frappe.whitelist()
def get_currenct_cost(product_code="",stock_location="",unit=""):
    if product_code == "" or stock_location == "" or unit == "":
        return {"cost":0,"quantity":0}
    product = frappe.get_doc("Product",product_code)
    uom_conversion = 1 if get_uom_conversion(product.unit, unit) == 0 or get_uom_conversion(product.unit, unit) is None else get_uom_conversion(product.unit, unit)
    stock_location_products = frappe.db.sql("SELECT count(*) count FROM `tabStock Location Product` WHERE product_code = '{0}'".format(product_code),as_dict=1)
   
    if stock_location_products:
        if stock_location_products[0].count>0:
            doc = frappe.db.sql("SELECT cost/{2} cost,quantity*{2} quantity FROM `tabStock Location Product` WHERE product_code = '{0}' AND stock_location = '{1}' order by modified desc limit 1".format(product_code,stock_location,uom_conversion),as_dict=1)
            if doc or len(doc)>0:
                return doc[0]
            else:
                 return {"cost":0,"quantity":0}
        else:
            doc = frappe.db.sql("SELECT cost/{1} cost,0 quantity FROM `tabProduct` WHERE product_code = '{0}' limit 1".format(product_code,uom_conversion),as_dict=1)
            return doc[0]
    else:
            doc = frappe.db.sql("SELECT cost/{1} cost,0 quantity FROM `tabProduct` WHERE product_code = '{0}' limit 1".format(product_code,uom_conversion),as_dict=1)
            return doc[0]