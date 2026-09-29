# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockLocationProduct(Document):
	def validate(self):
       existed = frappe.db.sql("""select 
                        name 
                        from `tabStock Location Product` 
                        where product_code = %(code)s and 
                        stock_location = %(stock)s and 
                        business_branch = %(branch)s""",
                        {"code":doc.product_code,"stock":doc.stock_location,"branch":doc.business_branch},as_dict=1)
        if existed:
            frappe.throw("Product <b>"+doc.product_code+"</b> for stock location <b>"+doc.stock_location+"</b> already existed")

@frappe.whitelist()
def get_stock_location_product(stock_location=None, product_code = None):
    blank_data = {"cost":0,'quantity':0}
    if stock_location and product_code:
        data = frappe.get_value('Stock Location Product', {"stock_location": stock_location, "product_code": product_code}, ['quantity', 'cost'], as_dict=1)
        return data if data else blank_data
    return blank_data