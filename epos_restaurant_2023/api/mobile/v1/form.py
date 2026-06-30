import frappe



def get_customer_form():
    meta = frappe.get_meta("Customer")
    return {
  "doctype": "Customer",
  "title": "Customer",
"fields":meta.get("fields"),
  "layout": [
    {
      "type": "section",
      "label": "Photo",
      "icon": "photo",
      "fields": ["photo"]
    },
    {
      "type": "section",
      "label": "General Information",
      "icon": "badge",
      "fields": ["customer_code", "customer_name_en", "gender", "date_of_birth"]
    },
    {
      "type": "section",
      "label": "Company",
      "icon": "business",
      "fields": ["company_name", "customer_group"]
    },
    {
      "type": "section",
      "label": "Contact",
      "icon": "phone",
      "fields": ["phone_number"]
    },
    {
      "type": "section",
      "label": "Address",
      "icon": "location",
      "fields": ["country", "province", "address"]
    },
    
  ]
}


FORMS = {
    "Customer": get_customer_form()
}

@frappe.whitelist()
def get_form(doctype):
    return FORMS[doctype]
