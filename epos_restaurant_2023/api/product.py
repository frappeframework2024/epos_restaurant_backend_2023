import re
import string

import frappe
import json
from frappe.utils.response import json_handler
from datetime import datetime, timedelta
from epos_restaurant_2023.inventory.inventory import get_uom_conversion
from functools import lru_cache
from py_linq import Enumerable

def convert_to_safe_key(text):
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove special characters
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove whitespace from beginning and end and replace remaining spaces with underscores
    text = text.strip().replace(" ", "_")
    
    return text


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
            
            menu_products = get_temp_menu_products(d.name,mobile=mobile)
            for m in menu_products:
                menus.append(m)
        
        menu_products = get_temp_menu_products(root_menu,mobile=mobile)
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
        
        for m in get_temp_menu_products(d.name,mobile=mobile):
            menus.append(m)       
        
    return menus


def get_temp_menu_products(parent_menu,mobile=0):     
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
                allow_crypto_claim,
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
                    "allow_crypto_claim":p.allow_crypto_claim,
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
                    "append_quantity": p.append_quantity,
                    "is_require_employee":p.is_require_employee,
                    "modifiers_data": json.dumps(([pr.business_branch,pr.modifier_category,pr.prefix,pr.modifier_code,pr.price] for pr in p.product_modifiers),default=json_handler),
                    "is_empty_stock_warning":0,
                    "rate_include_tax":p.rate_include_tax,
                    "pos_note":p.pos_note
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
                        "allow_crypto_claim":product.allow_crypto_claim,
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
                        "append_quantity": product.append_quantity,
                        "is_require_employee":product.is_require_employee,
                        "revenue_group":product.revenue_group,
                        "modifiers_data": json.dumps(([pr.business_branch,pr.modifier_category,pr.prefix,pr.modifier_code,pr.price] for pr in product.product_modifiers),default=json_handler),
               
                        "is_empty_stock_warning":0,
                        "rate_include_tax":product.rate_include_tax,
                        "pos_note":product.pos_note
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
    product = frappe.get_cached_doc("Product",product_code)
    uom_conversion = 1 if get_uom_conversion(product.unit, unit) == 0 or get_uom_conversion(product.unit, unit) is None else get_uom_conversion(product.unit, unit)
    stock_location_products = frappe.db.sql("SELECT count(*) count FROM `tabStock Location Product` WHERE product_code = '{0}'".format(product_code),as_dict=1)
   
    if stock_location_products:
        if stock_location_products[0].count>0:
            doc = frappe.db.sql("SELECT cost/{2} cost,quantity*{2} quantity FROM `tabStock Location Product` WHERE product_code = '{0}' AND stock_location = '{1}' order by modified desc limit 1".format(product_code,stock_location,uom_conversion),as_dict=1)
            if doc or len(doc)>0:
                doc[0]["last_purchase_cost"] = product.last_purchase_cost
                return doc[0]
            else:
                 return {"cost":0,"quantity":0}
        else:
            doc = frappe.db.sql("SELECT cost/{1} cost,0 quantity FROM `tabProduct` WHERE product_code = '{0}' limit 1".format(product_code,uom_conversion),as_dict=1)
            doc[0]["last_purchase_cost"] = product.last_purchase_cost
            return doc[0]
    else:
            doc = frappe.db.sql("SELECT cost/{1} cost,0 quantity FROM `tabProduct` WHERE product_code = '{0}' limit 1".format(product_code,uom_conversion),as_dict=1)
            doc[0]["last_purchase_cost"] = product.last_purchase_cost
            return doc[0]
        
def get_product_category(category):
    if cached_value := frappe.cache.get_value("product_category_by_category_name_" + category):
        return cached_value
    
    sql="select name, name as name_en, product_category_name_kh as name_kh, parent_product_category as parent, photo, text_color, background_color, show_in_pos_shortcut_menu as shortcut_menu, allow_sale,'menu' as type, '' as price_rule from `tabProduct Category` where parent_product_category=%(category)s and allow_sale=1"
    data = frappe.db.sql(sql, {"category":category},as_dict=1)
    frappe.cache.set_value("product_category_by_category_name_" + convert_to_safe_key(category), data)
    return data             

@frappe.whitelist()
def get_products(category ='All Product Categories',product_code=None,keyword=None , limit = 20, page=1, order_by='product_code',order_by_type='asc', include_product_category=0,price_rule="Normal"):
    sql="""
        select 
            name as menu_product_name,
            name,
            product_name_en as name_en,
            product_name_kh as name_kh,
            product_category as parent,
            price,
            unit,
            allow_crypto_claim,
            allow_discount,
            allow_change_price,
            allow_free,
            is_open_product,
            is_inventory_product,
            photo,
            append_quantity,
            is_combo_menu,
            use_combo_group,
            combo_menu_data,
            combo_group_data,
            is_open_price,
            is_timer_product,
            rate_include_tax,
            tax_rule,
            revenue_group,
            prices,
            sort_order,
            has_variants,
            '[]' as printers,
            '[]' as modifiers,
            '' as price_rule,
            'product' as type,
            variant_of,
            is_variant
            
        from `tabProduct`
        where
            (
                disabled=0 and 
                allow_sale=1 and 
                is_variant=if(%(product_code)s!='',is_variant, 0)
            ) 
    """

 
    
    if category!= 'All Product Categories':
        sql = sql + " and product_category in %(product_categories)s"
    if product_code:
        sql = sql + " and name = %(product_code)s "
        
    if keyword:
        sql = sql + " and name like %(keyword)s or product_name_en like %(keyword)s and product_name_kh like %(keyword)s"
    
    sql = sql + " order by %(order_by)s %(order_by_type)s"
    sql = sql + " LIMIT %(limit)s OFFSET %(start)s;"
   
    filter = {
        "product_categories": get_product_category_with_children(category),
        "product_code":product_code or "",
        "limit":int(limit),
        "start": (int(page)-1) * (int(limit) + 1),
        "order_by":order_by,
        "order_by_type":order_by_type
        
    }
    if keyword:
        filter["keyword"]='%{}%'.format(keyword)
     
    data = frappe.db.sql(sql,filter,as_dict=1)
    
    # todo 
    # get  product price
    # get product modifier
    # get printers
    
    for  d in data:
        d["printer"] = json.dumps( get_product_printers(d["name"]))

        d["modifiers"] = json.dumps( get_product_modifiers(d["name"]))
        
        if d["variant_of"]  and d["is_variant"] ==1:
            d["selected_variant"] = get_selected_variant(d["name"],d["variant_of"]) 
        # get_default_price
        product_prices = json.loads(d["prices"])
        if product_prices:
            default_price =  get_default_product_price(price_rule, product_prices)
            d["unit"] = default_price["unit"]
            d["portion"] = default_price["portion"]
            d["price"] = default_price["price"]
    
    if int(include_product_category) ==1:
        return {"products":data,"categories":get_product_category(category)}
    else:
        return {"products":data}
            


def get_default_product_price(price_rule="Normal", prices=None):
    # will update to support branch later
    default_price = [p for p in prices if p["price_rule"] == price_rule]
    if  default_price:
        default_price = default_price[0]
    if not default_price:
        default_price = prices[0]
    return default_price



@frappe.whitelist(methods="POST")
def get_product_by_variant(variant,product_code):
    sql ="""
        select variant_code from `tabProduct Variants` 
        where 
            parent = %(product_code)s and
            coalesce(variant_1,'') = if(%(variant_1)s ='', coalesce(variant_1,''),%(variant_1)s) and 
            coalesce(variant_2,'') = if(%(variant_2)s ='', coalesce(variant_2,''),%(variant_2)s) and 
            coalesce(variant_3,'') = if(%(variant_3)s ='', coalesce(variant_3,''),%(variant_3)s)  
        limit 1
    """
    filter = {
        "product_code":product_code
    }
    
    filter["variant_1"] = '' if not  "variant_1" in variant else variant["variant_1"]["variant_value"]
        
    filter["variant_2"] = '' if not "variant_2" in variant else variant["variant_2"]["variant_value"]

    filter["variant_3"] = '' if not "variant_3" in variant else  variant["variant_3"]["variant_value"]
 
        
    data = frappe.db.sql(sql,filter,as_dict = 1)

    if data:
       
        product_data = get_products(product_code=data[0]["variant_code"], limit=1, page=1,include_product_category=0)
        
        if product_data:
            if product_data["products"]:
                product = product_data["products"][0]
                
                return product 
    
    frappe.throw("This selected product variant is not available in the system")
        
 


def get_product_variant(product_code):
    # we clear this cache when save product 
    if cached_value := frappe.cache.get_value("product_variant_" + product_code):
        return cached_value
    
    doc = frappe.get_cached_doc("Product", product_code)
    variants = []
    if doc.variant_1_name:
        variants.append({"variant_name":doc.variant_1_name, "variants":[{"variant":d.variant_value} for d in doc.variant_1_value]})
    
    if doc.variant_2_name:
        variants.append({"variant_name":doc.variant_2_name, "variants":[{"variant":d.variant_value} for d in doc.variant_2_value]})
    
    if doc.variant_3_name:
        variants.append({"variant_name":doc.variant_3_name, "variants":[{"variant":d.variant_value} for d in doc.variant_3_value]})
    
    frappe.cache.set_value("product_variant_" + product_code, variants)
    return variants

def get_product_printers(product_code):
    # we clear this cache when save product 
    if cached_value := frappe.cache.get_value("product_printer_" + product_code):
        return cached_value
    
    doc = frappe.get_cached_doc("Product", product_code)
    printers = []
    for p in doc.printers:
            printers.append({
                    "printer":p.printer_name,
                    "group_item_type":p.group_item_type,
                    "ip_address":p.ip_address,
                    "port":int(p.port or 0),
                    "is_label_printer":p.is_label_printer,
                    "usb_printing":p.usb_printing,
                })
    
    frappe.cache.set_value("product_printer_" + product_code, printers)
    return printers

def get_selected_variant(product_code, variant_of):
    # we clear this cache when save product 
    if cached_value := frappe.cache.get_value("selected_variant_" + product_code):
        return cached_value

    variant = {}
    variant_1_name  =frappe.get_cached_value("Product", variant_of, "variant_1_name" ) 
    if variant_1_name:
        variant["variant_1"] = {"variant_name": variant_1_name, "variant_value": frappe.get_cached_value("Product", product_code, "variant_1") }
    
    
    variant_2_name  =frappe.get_cached_value("Product", variant_of, "variant_2_name" ) 
    if variant_2_name:
        variant["variant_2"] = {"variant_name": variant_2_name, "variant_value": frappe.get_cached_value("Product", product_code, "variant_2") }
    
    
    
    variant_3_name  =frappe.get_cached_value("Product", variant_of, "variant_3_name" ) 
    if variant_3_name:
        variant["variant_3"] = {"variant_name": variant_3_name, "variant_value": frappe.get_cached_value("Product", product_code, "variant_3") }
    
    frappe.cache.set_value("selected_variant_" + product_code, variant)
    return variant



def get_product_modifiers(product_code):
    # we clear this cache when save product 
    if cached_value := frappe.cache.get_value("product_modifier_" + product_code):
        return cached_value
    
    #get product modifier
    doc = frappe.get_cached_doc("Product",product_code)
    
    mc0 = []
    mc1 = Enumerable(doc.product_modifiers).select(lambda x: x.modifier_category).distinct()
    mc2 = [] #global modifier category



    # #get global modifier category
    global_modifier_product_categorie = get_global_modifier_by_category(doc.product_category)
    
    global_modifiers = []
    for gmpc in global_modifier_product_categorie:
        gmodifiers = frappe.get_cached_doc('Modifier Group',gmpc.parent)
        for g in gmodifiers.modifiers:
            global_modifiers.append(g)
    
    if global_modifiers != []:
        mc2 = Enumerable(global_modifiers).select(lambda x: x.modifier_category).distinct()
    
    for mc in mc1:
        mc0.append(mc)
    for mc in mc2:
        mc0.append(mc)

    
    modifier_categories = Enumerable(mc0).select(lambda x: x).distinct()	
    modifiers = []


    ## get modifier data
    for mc in modifier_categories:
        doc_category = frappe.get_cached_doc("Modifier Category",mc)
        modifier_items = []	
        items = []			
        #global modifier group
        for m in global_modifiers:
            if m.modifier_category == mc:
                items.append({
                    "name":m.name,
                    "branch":m.business_branch or "" , 
                    "prefix":m.prefix, 
                    "modifier":m.modifier_code, 
                    "value": str(m.business_branch or "") + str(m.prefix) + ''+str( m.modifier_code), 
                    "price":m.price 
                    })	
        
        #product modifier
        for m in doc.product_modifiers:
            if m.modifier_category == mc:							
                items.append({
                    "name":m.name,
                    "branch":m.business_branch or "" , 
                    "prefix":m.prefix, 
                    "modifier":m.modifier_code, 
                    "value":  str(m.business_branch or "") + str(m.prefix) + ''+str( m.modifier_code), 
                    "price":m.price 
                })
        
        for i in items:	
            modifier_items.append({
                "name":i['name'],
                "branch":i['branch'], 
                "prefix":i['prefix'], 
                "modifier":i['modifier'], 
                "price": i['price'] 
            })

        modifiers.append({
            "category":mc,
            "is_required":doc_category.is_required,
            "is_multiple":doc_category.is_multiple,
            "items":modifier_items
        })
        
    frappe.cache.set_value("product_modifier_" + product_code, modifiers)
    return modifiers

   
def get_global_modifier_by_category(category):
    if cached_value := frappe.cache.get_value("global_modifier_group_" + category.replace(" ","_")):
        return cached_value
    
    data =frappe.get_all('Modifier Group Product Category',
                            filters=[['product_category','=',category]],
                            fields=['parent','name'],
                            limit=200
                            )
    
    frappe.cache.set_value("global_modifier_group_" +  convert_to_safe_key(category),data )
    return data


@frappe.whitelist()
def  get_product_category_with_children(parent_category='All Product Categories'):
    if cached_value := frappe.cache.get_value("product_category_with_children_" + parent_category):
        return cached_value
    sql="""
        WITH RECURSIVE hierarchy AS (
            SELECT
                name as product_category,
                parent_product_category
            FROM
                `tabProduct Category`
            WHERE
                name = %(parent_category)s and 
                allow_sale = 1
            UNION ALL
            SELECT
                t.name as product_category,
                t.parent_product_category
            FROM
                `tabProduct Category` t
            JOIN
                hierarchy h ON t.parent_product_category = h.product_category
        )
        SELECT
            product_category
        FROM
            hierarchy

    """
    data =  frappe.db.sql(sql,{"parent_category":parent_category,},as_dict=1)
    frappe.cache.set_value("product_category_with_children_" + convert_to_safe_key(parent_category),data )
    return [d["product_category"] for d in data]


@frappe.whitelist()
def get_product_option(product_code="", business_branch="", price_rule="Normal"):
    if cached_value := frappe.cache.get_value(f"product_option_{product_code}_{price_rule}"):
        return cached_value
    
    
    doc = frappe.get_cached_doc("Product", product_code)
    
    data = {"name":doc.name, "product_name_en": doc.product_name_en, "product_name_kh":doc.product_name_kh,"is_variant":doc.is_variant, "variant_of":doc.variant_of}
    
    if (doc.photo):
        data["photo"] = doc.photo
    else:
        if doc.variant_of:
            data["photo"] = frappe.get_cached_value("Product", doc.variant_of,"photo")
            
    if doc.product_price:
        data["prices"] = [{"price":d.price, "unit":d.unit, "portion":d.portion} for d in doc.product_price if (not d.business_branch  and    d.price_rule == price_rule) or (d.business_branch==business_branch and d.price_rule==price_rule ) ]
    if not "prices" in data:
        data["prices"] = [{"price":doc.price,"unit":doc.unit, "portion":doc.unit}]
    
    if data["prices"]:
        data["prices"][0]["selected"] = True
    
    if doc.has_variants:
        data["variants"] =  get_product_variant(doc.name)
    elif doc.variant_of :
        data["variants"] =  get_product_variant(doc.variant_of)
    
    
    
    
    
    frappe.cache.set_value(f"product_option_{product_code}_{price_rule}",data )
    return data

