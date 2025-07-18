import frappe
import json
# jinja filter list

@frappe.whitelist()
def unique(value):
    return set(value)

@frappe.whitelist()
def format_currency(value):
    return frappe.format(value, {"fieldtype": "Currency"})

@frappe.whitelist()
def format_second_currency(value):
     
    currency =  frappe.get_cached_value("ePOS Settings",None,"second_currency")
  
    precision = frappe.get_cached_value("Currency",currency,"custom_currency_precision")
    return frappe.utils.fmt_money(value,  currency =  currency, precision = precision )

@frappe.whitelist()
def to_json(value):
   
    if not value:
        return None
    try:
        return json.loads(value)
    except:
        return None



# jinja method 
def get_total(value, fieldname):
    return sum([d.get(fieldname) for d in value])

def get_total(value, fieldname):
    return sum([d.get(fieldname) for d in value])



def get_exchange_rate(date):
    from_currency = frappe.get_cached_value("ePOS Settings",None,"currency")
    to_currency = frappe.get_cached_value("ePOS Settings",None,"second_currency")
    currecy_data = frappe.db.sql("select exchange_rate from `tabCurrency Exchange` where posting_date<=%(posting_date)s and from_currency = %(from_currency)s and to_currency = %(to_currency)s order by creation desc limit 1",
        {
            "posting_date": date,
            "from_currency":from_currency,
            "to_currency":to_currency
        },as_dict=1)
    if currecy_data:
        return currecy_data[0].exchange_rate
    else:
        return 1

@frappe.whitelist()
def get_combo_product_by_kitchen_group(value=None):
    # value is param contain product como item list
    
 
    for p in value:
        p["kitchen_group"] = frappe.get_cached_value("Product",p.get("product_code"),"kitchen_group") or "Not Set"

    # get sorted kitchen group 
    sql = "select name as kitchen_group from `tabKitchen Group` where name in %(names)s order by sort_order"
    kitchen_group = frappe.db.sql(sql,{"names":[d.get("kitchen_group") for d in value]}, as_dict=1)

    for k in kitchen_group:
        k["products"] =[d for d in value if d.get("kitchen_group") == k.get("kitchen_group")]

    # handle with not set kitchen group
    if len([d for d in value if d.get("kitchen_group" == "Not Set")])>0:
            
        not_set_kitchen_group = {
                "kitchen_group":"Not Set", 
                "products":[d for d in value if d.get("kitchen_group") == "Not Set"]

        } 
        kitchen_group.append(not_set_kitchen_group)
    
    return kitchen_group







    
    
     