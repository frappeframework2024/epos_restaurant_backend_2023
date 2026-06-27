import frappe
from epos_restaurant_2023.api import sale
from epos_restaurant_2023.api.api import get_sale_list_table_badge
from epos_restaurant_2023.api.change_merge_table import on_merge_order 

@frappe.whitelist(methods=["POST"])
def get_sale_detail(sale_name):
    return sale.get_sale_detail(sale_name)


@frappe.whitelist(methods="POST")
def submit_order(data=None,print_request_bill=False):
    return sale.submit_order(data=data,print_request_bill=print_request_bill)

@frappe.whitelist(methods="POST")
def get_pending_order(data):
    return get_sale_list_table_badge(data)

@frappe.whitelist(methods=["POST","GET"])
def get_sale_product_printers(sale_products=None):
    
    if not sale_products:
        sale_products = {
      "name": "0b192cfffb",
      "owner": "pheakdey.micronet@gmail.com",
      "creation": "2026-06-23 09:18:52.420498",
      "modified": "2026-06-25 08:37:00.501410",
      "modified_by": "pheakdey.micronet@gmail.com",
      "docstatus": 0,
      "idx": 1,
      "product_code": "COM001",
      "product_name": "Test Combo",
      "product_name_kh": "Test Combo",
      "portion": "Unit",
      "product_group": "Food",
      "product_category": "Appetizer & Salad",
      "revenue_group": "Food",
      "kitchen_group_sort_order": 0,
      "pos_profile": "Main POS Profile",
      "unit": "Unit",
      "base_unit": "Unit",
      "base_price": 0,
      "coupon_value": 0,
      "total_coupon_value": 0,
      "quantity": 1,
      "deleted_quantity": 0,
      "crypto_able_amount": 0,
      "input_price": 0,
      "regular_price": 3,
      "price": 3,
      "modifiers_price": 0,
      "selling_price": 0,
      "sub_total": 3,
      "amount": 3,
      "discount_type": "Percent",
      "sale_discount_percent": 0,
      "discount": 0,
      "sale_discount_amount": 0,
      "discount_amount": 0,
      "total_discount": 0,
      "commission_01": 0,
      "commission_02": 0,
      "commission_03": 0,
      "commission_04": 0,
      "commission_05": 0,
      "is_park": 0,
      "is_redeem": 0,
      "rate_include_tax": 0,
      "total_tax": 0,
      "tax_1_rate": 0,
      "percentage_of_price_to_calculate_tax_1": 0,
      "calculate_tax_1_after_discount": 0,
      "taxable_amount_1": 0,
      "tax_1_amount": 0,
      "tax_2_rate": 0,
      "percentage_of_price_to_calculate_tax_2": 0,
      "calculate_tax_2_after_discount": 0,
      "calculate_tax_2_after_adding_tax_1": 0,
      "taxable_amount_2": 0,
      "tax_2_amount": 0,
      "tax_3_rate": 0,
      "percentage_of_price_to_calculate_tax_3": 0,
      "calculate_tax_3_after_discount": 0,
      "calculate_tax_3_after_adding_tax_1": 0,
      "calculate_tax_3_after_adding_tax_2": 0,
      "taxable_amount_3": 0,
      "tax_3_amount": 0,
      "total_revenue": 3,
      "default_income_account": "4710 - Food Revenue",
      "default_expense_account": "5110 - Cost of Goods Sold",
      "default_inventory_account": "1410 - Stock In Hand",
      "default_discount_account": "5001 - Sale Discount",
      "default_coupon_expense_account": "5006 - Marketing Expenses",
      "allow_discount": 1,
      "allow_free": 1,
      "allow_change_price": 1,
      "is_inventory_product": 0,
      "append_quantity": 1,
      "is_timer_product": 0,
      "is_free": 0,
      "is_combo_menu": 1,
      "use_combo_group": 1,
      "is_require_employee": 0,
      "delete_from_pos_require_password": 0,
      "move_from_sale_printed": 0,
      "allow_crypto_claim": 0,
      "is_open_product": 0,
      "is_delivered": 0,
      "backup_product_price": 0,
      "backup_modifier_price": 0,
      "sale_product_status": "Submitted",
      "menu_product_name": "8e0b19a0fe",
      "order_by": "Pheakdey",
      "order_time": "2026-06-23 16:47:35.947495",
      "time_stop": 0,
      "is_return": 0,
      "hide_in_kod": 0,
      "is_variant": 0,
      "coupon_markup_value": 0,
      "coupon_markup_percentage": 0,
      "cost": 0,
      "modifiers": "",
      "modifiers_data": "[]",
      "combo_menu": "***Starter***|PUMPKIN CUSTARD x1|***Main Course***|Motherboard x1, BEE FRIED RICE x1, Screen x1",
      "printers": "[{\"printer\": \"Cashier Printer\", \"group_item_type\": \"Printer cut by order\", \"ip_address\": \"192.168.10.161\", \"port\": 9100, \"is_label_printer\": 0, \"usb_printing\": 1}, {\"printer\": \"Kitchen Printer\", \"group_item_type\": \"Printer cut by order line\", \"ip_address\": \"192.168.10.161\", \"port\": 9100, \"is_label_printer\": 0, \"usb_printing\": 1}, {\"printer\": \"Bar Printer\", \"group_item_type\": \"Printer cut by order\", \"ip_address\": \"192.168.10.161\", \"port\": 9100, \"is_label_printer\": 0, \"usb_printing\": 1}]",
      "combo_menu_data": "[{\"menu_name\":\"c6247e08de\",\"product_code\":\"108\",\"product_name\":\"PUMPKIN CUSTARD\",\"unit\":\"Unit\",\"quantity\":1,\"price\":3,\"photo\":\"/files/img49436.whqc_1426x713q80.jpg\",\"selected\":true,\"group\":\"ME1 Starter\",\"group_title\":\"Starter\"},{\"menu_name\":\"4e380ea168\",\"product_code\":\"P0003\",\"product_name\":\"Motherboard\",\"product_name_kh\":\"Screen\",\"unit\":\"Unit\",\"quantity\":1,\"price\":80,\"photo\":None,\"selected\":true,\"group\":\"ME1 Main Course\",\"group_title\":\"Main Course\"},{\"menu_name\":\"b2125d60f4\",\"product_code\":\"104\",\"product_name\":\"BEE FRIED RICE\",\"product_name_kh\":\"បាយឆាសាច់គោ\",\"unit\":\"Unit\",\"quantity\":1,\"price\":6.5,\"photo\":\"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEHE9R69TjXr8Ix5ulXlmLyopkM0tC9Bz1P8LZuLdb7f9agowCjr31c6uf-Q&s\",\"selected\":true,\"group\":\"ME1 Main Course\",\"group_title\":\"Main Course\"},{\"menu_name\":\"06d86ada08\",\"product_code\":\"P0001\",\"product_name\":\"Screen\",\"product_name_kh\":\"Screen\",\"unit\":\"Unit\",\"quantity\":1,\"price\":100,\"photo\":None,\"selected\":true,\"group\":\"ME1 Main Course\",\"group_title\":\"Main Course\"}]",
      "temp_id": "0b192cfffb",
      "parent": "SINV2026-0866",
      "parentfield": "sale_products",
      "parenttype": "Sale",
      "doctype": "Sale Product"
    }
    if isinstance(sale_products,dict):
        sale_products = [sale_products]

    products = sale.get_products(sale_products)
    product_printers = sale.get_printer_by_product([x.get("product_code") for x in products])
    def get_printer_names(printers):
        _printers = []
        for p in printers:
            _printers.append(
                {
                    "printer": p ,
                    "printer_name": frappe.get_cached_value("Printer",p, "printer_name")
                })
        return _printers

    for pp in product_printers:
        _pro = next((p for p in products if p.get("product_code") == pp.get("product_code")), {})
        pp["printers"] = get_printer_names(pp.get("printer_ids").split(","))
        pp.update(_pro)

    return product_printers
    

@frappe.whitelist(methods=["POST","GET"])
def submit_resend_to_printer(doc=None,data=None):
    if not doc:
        doc = frappe.get_cached_doc("Sale","SINV2026-0895")
    if not data:
        data = [
            {
                "printer_ids": "8f07b425c5,8018f3cb27",
                "product_code": "108",
                "printers": "8f07b425c5,8018f3cb27",
                "product_name": "PUMPKIN CUSTARD",
                "quantity": 1.0,
                "price": 3,
                "order_by": "Pheakdey",
                "order_time": "2026-06-25 15:48:34.123778"
            },
            {
                "printer_ids": "9cbb0df8a3,7c240a1581,bd0509fedc",
                "product_code": "COM001",
                "printers": "9cbb0df8a3,7c240a1581,bd0509fedc",
                "product_name": "Test Combo",
                "quantity": 1.0,
                "price": 0.0,
                "unit": "Unit",
                "note": None,
                "portion": None,
                "modifiers": "",
                "order_by": "Pheakdey",
                "order_time": "2026-06-25 15:48:34.123778"
            },
            {
                "printer_ids": "8018f3cb27,7c240a1581",
                "product_code": "P0001",
                "printers": "8018f3cb27,7c240a1581",
                "product_name": "Screen",
                "quantity": 1.0,
                "price": 100,
                "order_by": "Pheakdey",
                "order_time": "2026-06-25 15:48:34.123778"
            },
            {
                "printer_ids": "8018f3cb27,7c240a1581",
                "product_code": "P0002",
                "printers": "8018f3cb27,7c240a1581",
                "product_name": "Frame",
                "quantity": 1.0,
                "price": 50,
                "order_by": "Pheakdey",
                "order_time": "2026-06-25 15:48:34.123778"
            },
            {
                "printer_ids": "7c240a1581,bd0509fedc",
                "product_code": "P0003",
                "printers": "7c240a1581,bd0509fedc",
                "product_name": "Motherboard",
                "quantity": 1.0,
                "price": 80,
                "order_by": "Pheakdey",
                "order_time": "2026-06-25 15:48:34.123778"
            }
            ]
    return sale.submit_resend_product_to_printer(doc,data)
    
@frappe.whitelist(methods=["POST"])
def merge_bill(source_doc_name,target_doc_name):
    data = on_merge_order(old_sale = source_doc_name, new_sale = target_doc_name)
    return data.get("data")

