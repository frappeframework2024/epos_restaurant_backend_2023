from epos_restaurant_2023.api.product import (
    get_product_by_menu as _get_product_by_menu,
    get_products as _get_products,
    get_product_option as _get_product_option,
    get_product_by_variant as _get_product_by_variant,
    get_product_detail_information as _get_product_detail_information,
) 
import frappe

@frappe.whitelist(methods="POST")
def get_product_by_menu(root_menu="",sort_order_by="product_name_en",sort_menu_order_by='name' ):

    return _get_product_by_menu(root_menu=root_menu,
                                mobile = 0,
                                sort_order_by=sort_order_by,
                                sort_menu_order_by=sort_menu_order_by )



@frappe.whitelist(methods="POST")
# @frappe.whitelist(allow_guest=True)
def get_products(category ='All Product Categories',product_code=None,keyword=None , limit = 20, page=1, order_by='product_code',order_by_type='asc', include_product_category=0,price_rule="Normal"):

    return _get_products(
            category =category,
            product_code=product_code,
            keyword=keyword , 
            limit = limit, 
            page=page, 
            order_by=order_by,
            order_by_type=order_by_type, 
            include_product_category=include_product_category,
            price_rule=price_rule
        )


@frappe.whitelist(methods="POST") 
def get_product_option(product_code="", business_branch="", price_rule="Normal"):
    return _get_product_option(
            product_code=product_code,
            business_branch=business_branch, 
            price_rule=price_rule
        )

@frappe.whitelist(methods="POST") 
def get_product_by_variant(variant,product_code):
    return _get_product_by_variant(
            variant=variant,
            product_code=product_code,
        )


@frappe.whitelist(methods="POST") 
def get_product_detail_information(product_code):
    return _get_product_detail_information(
        product_code=product_code
    )