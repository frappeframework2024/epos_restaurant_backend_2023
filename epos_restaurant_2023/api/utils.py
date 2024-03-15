import frappe
import requests
@frappe.whitelist()
def generate_data_for_sync_record(doc, method=None, *args, **kwargs):
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_client]:
            for b in setting.sync_business_branches:
                if not frappe.db.exists("Data For Sync",{"business_branch":b.business_branch,"document_type":doc.doctype,"document_name":doc.name}):
                    frappe.get_doc({
                        "doctype":"Data For Sync",
                        "business_branch":b.business_branch,
                        "document_type":doc.doctype,
                        "document_name":doc.name
                    }).insert(ignore_permissions=True)
                # frappe.db.commit()
@frappe.whitelist()
def generate_data_for_sync_record_on_delete(doc, method=None, *args, **kwargs):
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_client]:
            frappe.db.sql("delete from `tabData For Sync` where document_type='{}' and document_name='{}'".format(doc.doctype,doc.name))
            for b in setting.sync_business_branches:
                if not frappe.db.exists("Data For Sync",{"business_branch":b.business_branch,"document_type":doc.doctype,"document_name":doc.name}):
                    frappe.get_doc({
                        "doctype":"Data For Sync",
                        "business_branch":b.business_branch,
                        "document_type":doc.doctype,
                        "document_name":doc.name,
                        "is_deleted":1
                    }).insert(ignore_permissions=True)
            

@frappe.whitelist()
def sync_data_to_server_on_submit(doc, method=None, *args, **kwargs):
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_server if d.event == 'on_submit']:
            frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=doc)        
            

           
@frappe.whitelist()
def sync_data_to_server(doc):
     
    server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
    token = frappe.db.get_single_value('ePOS Sync Setting','access_token')
    headers = {
                'Authorization': 'token {}'.format(token)
            }
    server_url = server_url + "api/method/epos_restaurant_2023.api.utils.save_sync_data"
    response = requests.get(server_url,headers=headers,data=doc)
    if response.status_code ==200:
        pass
    #   can be update is sync = true
    
    
    

@frappe.whitelist(methods="POST")
def save_sync_data(doc):
    doc = frappe.get_doc(doc)
    doc.flags.ignore_validate = True
    doc.flags.ignore_insert = True
    doc.flags.ignore_update = True
    
    if frappe.db.exists(doc.doctype, doc.name):
        doc.save()
    else:  
        doc.insert()
        
    

    
@frappe.whitelist()
def ping():
    return "pong"

