import json
import frappe
import requests


# ********************Client API *********************

# this method for for schedult task
@frappe.whitelist()
def get_all_data_for_sync_from_server():
    setting = frappe.get_doc("ePOS Sync Setting")
    if setting.enable==1 and   setting.server_url and setting.current_client_branch:
        server_url = setting.server_url
        headers = {
                    'Authorization': f'token {setting.access_token}'
                }
        server_url = server_url + "/api/method/epos_restaurant_2023.api.sync_api.get_data_for_sync?business_branch=" + setting.current_client_branch
       
        response = requests.get(server_url,headers=headers)
        
        if response.status_code==200:
            data_for_sync = json.loads(response.text)
            data_for_sync = data_for_sync['message']
            for d in data_for_sync:
                submit_sync_data_to_rq_job(d) 
        else:
            return response.text


def submit_sync_data_to_rq_job(data):
    for d in data["update"]:
        frappe.enqueue('epos_restaurant_2023.api.sync_api.get_sync_data_from_server',doctype=data["doctype"],data=d)
    
    # delete sync data 
    if data["delete"]:
        frappe.enqueue('epos_restaurant_2023.api.sync_api.delete_sync_data',doctype=data["doctype"],data=data["delete"])

    # rename
    if data["rename"]:
        frappe.enqueue('epos_restaurant_2023.api.sync_api.rename_sync_data',doctype=data["doctype"],data=data["rename"])

 

@frappe.whitelist()
def get_sync_data_from_server(doctype, data):
    setting = frappe.get_doc("ePOS Sync Setting")
    headers = {
                'Authorization': f'token {setting.access_token}'
            }
    server_url = setting.server_url + "/api/method/epos_restaurant_2023.api.sync_api.get_doctype_data"
    response = requests.post(server_url,headers=headers,json={"doctype":doctype, "names":data})
    if response.status_code == 200:
        data = json.loads(response.text)
        data = data["message"]
        for doc in data:
            if doc.get("business_branch"):
                if doc["business_branch"] == setting.current_client_branch:
                    on_save(doc)
            else:
                on_save(doc)
            
        frappe.db.commit()

@frappe.whitelist()
def rename_sync_data(doctype, data):
    setting = frappe.get_doc("ePOS Sync Setting")
    headers = {
                'Authorization': f'token {setting.access_token}'
            }
    server_url = setting.server_url + "/api/method/epos_restaurant_2023.api.sync_api.get_doctype_for_rename"
    response = requests.post(server_url,headers=headers,json={"doctype":doctype, "data":data})
    if response.status_code == 200:
        data = json.loads(response.text)
        data = data["message"]
        for doc in data:
            if doc['doc'].get("business_branch"):
                if doc['doc']["business_branch"] == setting.current_client_branch:
                    on_rename(doc)
            else:
                on_rename(doc)
        frappe.db.commit()


def on_save(doc):
    doc["__newname"] = doc["name"]
    doc = frappe.get_doc(doc)
    doc.flags.ignore_validate = True
    doc.flags.ignore_insert = True
    doc.flags.ignore_after_insert = True
    doc.flags.ignore_on_update = True
    doc.flags.ignore_before_submit = True
    doc.flags.ignore_on_submit = True
    doc.flags.ignore_on_cancel = True
    
    delete_doc(doc.doctype,doc.name)
    doc.insert(ignore_permissions=True, ignore_links=True)


def on_rename(doc):
    doc.flags.ignore_validate = True
    doc.flags.ignore_insert = True
    doc.flags.ignore_after_insert = True
    doc.flags.ignore_on_update = True
    doc.flags.ignore_before_submit = True
    doc.flags.ignore_on_submit = True
    doc.flags.ignore_on_cancel = True
    
    frappe.rename_doc(doc['doc']['doctype'],doc['old_name'],[doc['doc']['doctype']])
    

def delete_doc(doctype,name):
    frappe.db.sql("delete from `tab{}` where name='{}'".format(doctype,name))
    meta = frappe.get_meta(doctype)

    for child in [d for d in meta.fields if d.fieldtype=="Table"]:
        frappe.db.sql("delete from `tab{}` where parent='{}'".format(child.options,name))
    frappe.db.commit()

@frappe.whitelist()
def delete_sync_data(doctype,data):
    frappe.db.sql("delete from  `tab{}` where name in %(names)s")
    meta = frappe.get_meta(doctype)

    for child in [d for d in meta.fields if d.fieldtype=="Table"]:
        frappe.db.sql("delete from `tab{}` where parent='{}'".format(child.options,name))
        
   



# *******************SERVER API**************************
@frappe.whitelist()
def generate_init_data_sync_to_client(business_branch):
    if business_branch == "" or not business_branch:
        frappe.throw('Invalid Business Branch')
    setting = frappe.get_doc("ePOS Sync Setting")
    if setting.enable==1:
        for d in setting.sync_to_client:
            
            sql = """Insert Into `tabData For Sync` (business_branch,name,document_name,document_type) select  '{1}',UUID(),a.name,'{0}' from `tab{0}` as a""".format(d.document_type,business_branch)
            frappe.db.sql(sql)
        frappe.db.commit()


    

@frappe.whitelist()
def get_data_for_sync(business_branch):
    setting = frappe.get_doc("ePOS Sync Setting")
    frappe.db.sql("Update `tabData For Sync` set is_synced = 1 where business_branch='{}'".format(business_branch))
    frappe.db.commit()
    data = frappe.db.sql( "select distinct document_type, document_name,is_deleted,is_renamed,old_name  from `tabData For Sync` where is_synced=1 and business_branch='{}'".format(business_branch),as_dict=1) 
    
    return_data = []
    sync_doctypes = set([d["document_type"] for d in data])
    for dt in setting.sync_to_client:
        if dt.document_type in sync_doctypes:
            client_doctype = {"doctype":dt.document_type}
            # update data 
            breakdown_data =[d["document_name"] for d in data if d["document_type"] == dt.document_type and d["is_deleted"]==0 and d['is_renamed'] == 0]
             
            
            client_doctype["update"] =[breakdown_data[i:i+dt.total_record_per_sync] for i in range(0, len(breakdown_data), dt.total_record_per_sync)]
            client_doctype["delete"] =set([d["document_name"] for d in data if d["document_type"] == dt.document_type and d["is_deleted"]==1])
            client_doctype["rename"] =[dict({'name':d["document_name"],'old_name':d["old_name"]}) for d in data if d["document_type"] == dt.document_type and d["is_renamed"]==1] or []
            return_data.append(client_doctype)
    frappe.db.sql("delete from `tabData For Sync` where is_synced=1 and business_branch='{}'".format(business_branch))       
    frappe.db.commit()
    return return_data
      
@frappe.whitelist(methods="POST")
def get_doctype_data(doctype,names):
    data = []
    for d in names:
        if frappe.db.exists(doctype,d):
            data.append(frappe.get_doc(doctype,d))
    return data


@frappe.whitelist(methods="POST")
def get_doctype_for_rename(doctype,data):
    data = []
    for d in data:
        if frappe.db.exists(doctype,d['name']):
            data.append({'old_name':d['old_name'],'doc':frappe.get_doc(doctype,d)})
    return data