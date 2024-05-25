import frappe
import json

def update_fetch_from_field(self):
    data_for_updates = []
    condiction_keys = [
        {
            "key":"product_code",
            "doctypes":["eMenu Popular Products"]
        }
    ]
	
    updated_data = {}

    if self.has_value_changed("product_name_en"):	
        updated_data["product_name_en"] = self.product_name_en
        data_for_updates.append({"doctype":"eMenu Popular Products","update_field":"product_name_en=%(product_name_en)s"})
        
    # if product name kh changed
    if self.has_value_changed("product_name_kh"):	
        updated_data["product_name_kh"] = self.product_name_kh
        data_for_updates.append({"doctype":"eMenu Popular Products","update_field":"product_name_kh=%(product_name_kh)s"})
    
    #if photo changed
    if self.has_value_changed("photo"):
        updated_data["photo"] = self.photo
        data_for_updates.append({"doctype":"eMenu Popular Products","update_field":"photo=%(photo)s"})
        
    # if description changed
    if self.has_value_changed("description"):	
        updated_data["description"] = self.description         
        data_for_updates.append({"doctype":"eMenu Popular Products","update_field":"description=%(description)s"})

    # if is empty stock change
    if self.has_value_changed("is_empty_stock_warning"):
        updated_data["is_empty_stock_warning"] = self.is_empty_stock_warning         
        data_for_updates.append({"doctype":"eMenu Popular Products","update_field":"is_empty_stock_warning=%(is_empty_stock_warning)s"})
        
    # if price is changed
    if self.has_value_changed("price"):	
        updated_data["price"] = self.price 
        data_for_updates.append({"doctype":"eMenu Popular Products","update_field":"price=%(price)s"})
        
    # if product_price changed
    if self.has_value_changed("product_price"):	
        prices = '[]'
        if self.product_price:
            prices = json.dumps( 
                                [
                                    {"price":d.price, "branch":d.business_branch, "price_rule":d.price_rule, "portion":d.portion, "unit": d.unit, "default_discount":d.default_discount or 0}
                                    for d in self.product_price
                                ]
                            )
        updated_data["prices"] = prices 
        data_for_updates.append({"doctype":"eMenu Popular Products","update_field":"prices=%(prices)s"})

        
    if data_for_updates:
        for d in set([x["doctype"] for x in data_for_updates]):
            key = [f["key"] for f in condiction_keys if d in f["doctypes"]]
            
            key = "product" if not key else key[0]

            sql="update `tab{}` set {} where {}='{}'".format(
                d,
                ",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
                key,
                self.name
            )
           
            frappe.db.sql(sql,updated_data)