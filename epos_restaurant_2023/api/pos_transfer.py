import json
import frappe
from frappe import _

@frappe.whitelist()
def pos_transfer(sales):
    sales = json.loads(sales)
    submitted = []
    for sale in sales:
        docstatus,custom_is_sent,posting_date = frappe.db.get_value("Sale", sale, ["docstatus","custom_is_sent","posting_date"])
        if docstatus == 1 and (custom_is_sent or 0) == 0:
            submitted.append({"name":sale,"posting_date":posting_date})
    submitted =  sorted(submitted, key=lambda x: x["posting_date"])
    batch = []
    items = []
    for a in submitted:
        doc = frappe.get_doc("Sale", a.get("name"))
        items.extend([item.product_code for item in doc.sale_products])
        batch.append(doc.as_dict())
        if len(batch) == 10:
            validate_products(items)
            send_to_receiver(batch)
            batch = []
    if batch:
        validate_products(items)
        send_to_receiver(batch)
    names = [b.get("name") for b in submitted]
    if names:
        frappe.db.sql("""
            UPDATE `tabSale`
            SET custom_is_sent = 1
            WHERE name IN ({})
        """.format(", ".join(["%s"] * len(names))), tuple(names))
    frappe.db.commit()
    frappe.msgprint("All Transfer")
        
@frappe.whitelist()
def validate_products(items):
    import requests
    setting = frappe.get_doc("POS Transfer Setting")
    url = "{0}/api/method/epos_restaurant_2023.api.pos_transfer.receive_from_sender".format(setting.receiver_url)
    headers = {
        "Authorization": "token {0}".format(setting.access_token)
    }
    items = json.dumps(items, default=str)
    try:
        response = requests.post(url, headers=headers, json={"items": items})
        if response.status_code != 200:
            result = response.json()
            message = result.get("exception", "")
            frappe.msgprint(_("Error: {0}").format(message.split(": ", 1)[1]))
    except Exception as e:
        frappe.throw("An error occurred while validating products on receiver: {0}".format(str(e)))

@frappe.whitelist()
def validate_product_on_receiver(items=""):
    if items:
        items = json.loads(items)
        for a in items:
            if frappe.db.exists("Product", a):
                continue
            else:
                frappe.throw(_("Product {0} does not exist on receiver.").format(a))
   
@frappe.whitelist()
def send_to_receiver(data):
    data = json.dumps(data, default=str)
    import requests
    setting = frappe.get_doc("POS Transfer Setting")
    url = "{0}/api/method/epos_restaurant_2023.api.pos_transfer.receive_from_sender".format(setting.receiver_url)
    headers = {
        "Authorization": "token {0}".format(setting.access_token)
    }
    try:
        response = requests.post(url, headers=headers, json={"sales": data})
        if response.status_code != 200:
            result = response.json()
            message = result.get("exception", "")
            frappe.msgprint(_("Error: {0}").format(message.split(": ", 1)[1]))
    except Exception as e:
        frappe.throw("An error occurred while sending data to receiver: {0}".format(str(e)))

@frappe.whitelist()
def receive_from_sender(sales=""):
    if sales:
        sales = json.loads(sales)
        for sale in sales:
            existing = frappe.db.sql("select name from `tabSale` where custom_original_name='{0}'".format(sale["name"]),as_dict=1)
            if existing:
                frappe.throw("Sale {} already existed".format(sale["name"]))
            else:
                original_name = sale.get("name")
                original_bill_number = sale.get("custom_bill_number")
                sale["name"] = ""
                doc = frappe.get_doc(sale)
                doc.custom_original_name = original_name
                doc.custom_original_bill_number = original_bill_number
                doc.insert()
                doc.submit()

# add custom fields in Sale for both site
#Is Sent type Check
#Original Name type Data
#Original Bill Number type Data

#create new single doctype name "POS Transfer Setting" for both site
#Receiver URL type Data example http://192.168.10.143:1213
#Access Token type Data example c7988962eef0dcc:08118204bd27952


#add this is sale_list.js
# onload(listview) {
#         listview.page.add_action_item(__('POS Transfer'), () => {
#             const selected = listview.get_checked_items();
#             if (!selected.length) {
#                 frappe.msgprint(__('Please select at least one sale.'));
#                 return;
#             }
#             frappe.confirm(
#                 __('Are you sure you want to transfer {0} selected sales?', [
#                     selected.length
#                 ]),
#                 () => {
#                     // User confirms
#                     frappe.call({
#                         method: 'epos_restaurant_2023.api.pos_transfer.pos_transfer',
#                         args: {
#                             sales: selected.map(row => row.name)
#                         },
#                         freeze: true,
#                         freeze_message: __('Transferring...'),
#                         callback(r) {
#                             if (!r.exc) {
#                                 listview.refresh();
#                             }
#                         }
#                     });
#                 },
#                 () => {
#                     // User cancels; do nothing
#                 }
#             );
#         });
#     }