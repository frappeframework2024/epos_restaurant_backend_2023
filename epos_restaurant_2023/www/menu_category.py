import frappe
import json


def get_context(context):
    context.no_cache = 1
    emenu = frappe.get_doc("eMenu", "emenu")
    context.emenu = emenu
    context.doc = frappe.get_doc("POS Menu", frappe.form_dict.menu_category)

    context.pos_menus = get_sub_menu(frappe.form_dict.menu_category)
    context.products = get_product(frappe.form_dict.menu_category)
    context.shortcut_menu = get_shortcut_menu()

    popular_products = []
    for d in emenu.popular_product:
        d.prices = json.loads(d.prices or "[]")
        popular_products.append(d)

    context.popular_products = popular_products


def get_sub_menu(parent_menu):
    sql = "select name,pos_menu_name_en,pos_menu_name_kh,if(coalesce(pos_menu_name_etc,'') = '',pos_menu_name_en,pos_menu_name_etc) pos_menu_name_etc,photo from `tabPOS Menu` where parent_pos_menu = %(parent_menu)s and disabled=0"
    data = frappe.db.sql(sql, {"parent_menu": parent_menu}, as_dict=1)
    return data


def get_product(menu):

    sql = """
        select 
            name,
            pos_menu,
            product_code,
            product_name_en,
            product_name_kh,
            coalesce(product_name_etc,product_name_en) product_name_etc,
            price,
            ifnull(photo,'files/no_image.jpg') as photo,
            prices,
            discount_value,
            discount_type,
            is_empty_stock_warning,
            description
        from `tabTemp Product Menu`
        where pos_menu =  %(menu)s
        order by sort_order
    """
    data = frappe.db.sql(sql, {"menu": menu}, as_dict=1)

    # Convert prices to JSON
    for item in data:
        item["prices"] = json.loads(item["prices"] or "[]")
    return data


def get_shortcut_menu():
    sql = "select name, shortcut_menu, parent_pos_menu from `tabPOS Menu` where shortcut_menu=1 and disabled=0"
    data = frappe.db.sql(sql, as_dict=1)
    return data
