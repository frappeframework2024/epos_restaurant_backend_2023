import frappe
import requests
import json
@frappe.whitelist()
def generate_data_for_sync_record(doc, method=None, *args, **kwargs):
    if doc.doctype != "Data For Sync":
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

            if doc.doctype in [d.document_type for d in setting.sync_to_server]:
                if doc.doctype in [d.document_type for d in setting.sync_to_server if d.event == 'on_update']:
                    frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=doc)
            
                # frappe.db.commit()
@frappe.whitelist()
def generate_data_for_sync_record_on_delete(doc, method=None, *args, **kwargs):
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_client]:
            frappe.db.sql("delete from `tabData For Sync` where document_type='{}' and document_name='{}'".format(doc.doctype,doc.name))
            if doc.get("business_branch"):
                frappe.get_doc({
                            "doctype":"Data For Sync",
                            "business_branch":doc.business_branch,
                            "document_type":doc.doctype,
                            "document_name":doc.name,
                            "is_deleted":1
                        }).insert(ignore_permissions=True)
            else:
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
def generate_data_for_sync_record_on_rename(doc ,method=None, *args, **kwargs):
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable == 1:
        doc_name = {'old_name': args[0], 'name': args[1]}
        frappe.db.sql("delete from `tabData For Sync` where document_type='{}' and document_name='{}' ".format(doc.doctype,doc.name))
        if doc.get("business_branch"):
            frappe.get_doc({
                        "doctype":"Data For Sync",
                        "business_branch":doc.business_branch,
                        "document_type":doc.doctype,
                        "old_name":doc_name['old_name'],
                        "document_name":doc_name['name'],
                        "is_renamed":1
                    }).insert(ignore_permissions=True)
        else:
            for b in setting.sync_business_branches:
                if not frappe.db.exists("Data For Sync",{"business_branch":b.business_branch,"document_type":doc.doctype,"document_name":doc.name}):
                    frappe.get_doc({
                        "doctype":"Data For Sync",
                        "business_branch":b.business_branch,
                        "document_type":doc.doctype,
                        "old_name":doc_name['old_name'],
                        "document_name":doc_name['name'],
                        "is_renamed":1
                    }).insert(ignore_permissions=True)
            
@frappe.whitelist()
def sync_data_to_server_on_submit(doc, method=None, *args, **kwargs):
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_server if d.event == 'on_submit']:
            doctype = [d for d in setting.sync_to_server if d.event == 'on_submit' and d.document_type==doc.doctype][0] 
            frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=doc,extra_action=doctype.extra_action or [])   

@frappe.whitelist()
def sync_data_to_server_on_cancel(doc, method=None, *args, **kwargs):
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_server if d.event == 'on_cancel']:
            doctype = [d for d in setting.sync_to_server if d.event == 'on_cancel' and d.document_type==doc.doctype][0] 
            frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=doc,extra_action=doctype.extra_action or [])    
            

 
                          
@frappe.whitelist()
def sync_data_to_server(doc,extra_action):
    server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
    token = frappe.db.get_single_value('ePOS Sync Setting','access_token')
    headers = {
                'Authorization': 'token {}'.format(token),
                "Content-Type":"application/json"
            }
    server_url = server_url + "/api/method/epos_restaurant_2023.api.utils.save_sync_data"

    response = requests.post(server_url,headers=headers,json={"doc":frappe.as_json(doc),"extra_action":extra_action })
    if response.status_code==200:
        meta = frappe.get_meta(doc.doctype)
        if len([d for d in meta.fields if d.fieldname=="is_synced"]>0):
            frappe.db.sql("update `tab{}` set is_synced = 1 where name = '{}'".format(doc.doctype,doc.name))
            frappe.db.commit()
    return response.text
     
    
    
    

@frappe.whitelist(methods="POST")
def save_sync_data(doc,extra_action=None):
    
    doc = json.loads(doc)
    doc["__newname"] = doc["name"]
    doc = frappe.get_doc(doc) 
    sql = "update `tab{}` set creation='{}', owner='{}', modified='{}', modified_by='{}' where name='{}'".format(doc.doctype, doc.creation,doc.owner, doc.modified, doc.modified_by,doc.name)
    doc.flags.ignore_validate = True
    doc.flags.ignore_insert = True
    doc.flags.ignore_after_insert = True
    doc.flags.ignore_on_update = True
    doc.flags.ignore_before_submit = True
    doc.flags.ignore_on_submit = True
    doc.flags.ignore_on_cancel = True
    doc.flags.ignore_before_update_after_submit = True
    
    if frappe.db.exists(doc.doctype, doc.name):
        doc.save(ignore_permissions=True)
    else:  
        doc.insert(ignore_permissions=True, ignore_links=True)
    
    if extra_action:
        for action in json.loads(extra_action) :
            frappe.enqueue(action, queue='short', self=doc)
        
    
    frappe.db.sql(sql)
    frappe.db.commit()

    
@frappe.whitelist()
def ping():
    return "pong"

