import frappe

# jinja filter list

@frappe.whitelist()
def unique(value):
    return set(value)

@frappe.whitelist()
def format_currency(value):
    return frappe.format(value, {"fieldtype": "Currency"})

@frappe.whitelist()
def format_second_currency(value):
    currency = frappe.get_cached_value("ePOS Settings",None,"second_currency")
    precision = frappe.get_cached_value("Currency",currency,"custom_currency_precision")
    return frappe.format(value, {"fieldtype": "Currency", "currency": currency,"precision":precision})


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
    
    
     