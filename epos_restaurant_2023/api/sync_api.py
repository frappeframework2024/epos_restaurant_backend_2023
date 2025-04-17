import json
import frappe
import requests
import re
from frappe.utils import password,cstr

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
        server_url = server_url + "/api/method/epos_restaurant_2023.api.sync_api.get_data_for_sync"
       
        response = requests.get(server_url,headers=headers,json={"business_branch": setting.current_client_branch})
        
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
    for d in data:
        frappe.rename_doc(doctype,d['old_name'],d['name'])
    frappe.db.commit()

@frappe.whitelist()
def get_file(file_name):
    import base64
    file_name = (file_name or "").replace("/private","").replace("/files/","")
    if frappe.db.exists("File", {"file_name": file_name}):
        return
    setting = frappe.get_doc("ePOS Sync Setting")
    headers = {
                "Authorization": f"token {setting.access_token}",
                "Content-Type":"application/json"
            }
    server_url = setting.server_url + "/api/method/epos_restaurant_2023.api.sync_api.get_file_from_server"
    response = requests.post(server_url,headers=headers,json={"file_name":file_name})
    if response.status_code == 200:
        data = json.loads(response.text)
        content = base64.b64decode(data["message"])
        doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "content": content,
            "is_private": 0
        })
        doc.flags.ignore_validate = True
        doc.flags.ignore_insert = True
        doc.flags.ignore_after_insert = True
        doc.flags.ignore_on_update = True
        doc.flags.ignore_before_submit = True
        doc.flags.ignore_on_submit = True
        doc.flags.ignore_on_cancel = True
        doc.insert(ignore_permissions=True,ignore_links=True)
        frappe.db.commit()
        return "success"
    else:
        return response.text

@frappe.whitelist()
def get_file_from_server(file_name):
    import base64
    if frappe.db.exists("File", {"file_name": file_name}):
        doc = frappe.get_doc("File", {"file_name":file_name})
        file_path = doc.get_full_path()
        encoded = None
        with open(file_path, 'rb') as f : encoded = base64.b64encode(f.read()).decode()
        return (encoded or "")
    else:
        return "No File Exist"

def on_save(doc):
    doc["__newname"] = doc["name"]
    meta = frappe.get_meta(doc['doctype'])
    for f in [d for d in  meta.fields if d.fieldtype=='Attach Image']:
        if doc.get(f.fieldname):
            frappe.enqueue("epos_restaurant_2023.api.sync_api.get_file", queue='short',file_name=doc[f.fieldname]) 
            # get_file(doc[f.fieldname])
            # if doc[f.fieldname] and not is_url(doc[f.fieldname]):
            #     doc[f.fieldname] = "{}{}".format(frappe.db.get_single_value("ePOS Sync Setting","server_url") ,doc[f.fieldname])
            
    doc = frappe.get_doc(doc)
    if doc.flags.disable_generate_data_for_sync:
        return
    doc.flags.ignore_validate = True
    doc.flags.ignore_insert = True
    doc.flags.ignore_after_insert = True
    doc.flags.ignore_on_update = True
    doc.flags.ignore_before_submit = True
    doc.flags.ignore_on_submit = True
    doc.flags.ignore_on_cancel = True
    
    delete_doc(doc.doctype,doc.name)
    
    doc.insert(ignore_permissions=True, ignore_links=True)
    if doc.doctype == "User":
        set_user_password(doc.name,doc.new_password)

    

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
    frappe.db.sql("delete from  `tab{}` where name in %(data)s".format(doctype),data)
    meta = frappe.get_meta(doctype)

    for child in [d for d in meta.fields if d.fieldtype=="Table"]:
        frappe.db.sql("delete from `tab{0}` where parent='{1}'".format(child.options,doctype))
        
   



# *******************SERVER API**************************
@frappe.whitelist()
def generate_init_data_sync_to_client():
    setting = frappe.get_doc("ePOS Sync Setting")
    if setting.enable==1:
        for d in setting.sync_to_client:
            for bus in setting.sync_business_branches:
                sql = """Insert Into `tabData For Sync` (business_branch,name,document_name,document_type) select  '{1}',UUID(),a.name,'{0}' from `tab{0}` as a""".format(d.document_type,bus.business_branch)
                frappe.db.sql(sql)
            frappe.db.commit()


    

@frappe.whitelist()
def get_data_for_sync(business_branch=None):
    setting = frappe.get_doc("ePOS Sync Setting")
    if business_branch:
        frappe.db.sql("Update `tabData For Sync` set is_synced = 1")
        frappe.db.commit()
        data = frappe.db.sql( "select distinct document_type, document_name,is_deleted,is_renamed,old_name  from `tabData For Sync` where is_synced=1 order by creation",as_dict=1) 
    else:
        frappe.db.sql("Update `tabData For Sync` set is_synced = 1 where business_branch='{}'".format(business_branch))
        frappe.db.commit()
        data = frappe.db.sql( "select distinct document_type, document_name,is_deleted,is_renamed,old_name  from `tabData For Sync` where is_synced=1 and business_branch='{}' order by creation".format(business_branch),as_dict=1) 
    
    
    
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
    if doctype == "User":
        for d in names:
            if frappe.db.exists(doctype,d):
                doc = frappe.get_doc(doctype,d)
                doc.new_password = get_password(doc.name)
                data.append(doc)
    else:
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

def get_password(name):
    username =  frappe.get_doc("User",name).username
    employee =  frappe.db.sql("select name from `tabEmployee` where username = '{0}'".format(username),as_dict=1)
    str_password = password.get_decrypted_password("Employee", employee[0].name, fieldname="encrypt_password",raise_exception=False)
    return str_password

def set_user_password(user, password):
    from frappe.utils.password import update_password
    update_password(user=user, pwd=password)
    frappe.db.commit()


def is_url(url):
    # Regular expression pattern to match URLs
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    # Check if the given string matches the URL pattern
    if url_pattern.match(url):
        return True
    else:
        return False
    
@frappe.whitelist()
def testMe():
    import os

    file_path = "/foder/f2/files/beer-heineken-blonde-french-5-33-cl.jpg"
    file_name = os.path.basename( file_path)

    return send_image_to_public_site( 
        {"doctype":"Product",
         "name":"B001",
         "url":"/files/beer-heineken-blonde-french-5-33-cl29c1b0.jpg",
            "file_name": file_name
         }
    )

@frappe.whitelist()
def send_image_to_public_site(data):
    import base64
    import requests
    from frappe.utils.file_manager import get_file_path
    setting = frappe.get_doc("ePOS Sync Setting")
    image_path = get_file_path(data.get("url"))
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    data["filedata_base64"] = encoded_string
    
    response = requests.post(
        "http://webmonitor.inccloudserver.com:7117/api/method/epos_restaurant_2023.api.sync_api.upload_image",
        json={"data":data},
        # headers={
        #     "Authorization": f'token {setting.access_token}'
        # }
        headers={
            "Authorization": f'token b84df842943ec01:744075e4def9080'
        }
    )
    result = None
    if response.ok:
        result =  response.json()
    else:
        result =  (response.status_code,response.text)


    try:
        result =  response.json()
    except Exception as e:
        result =  str(e)
    
    return result

 
    

@frappe.whitelist(allow_guest=True)
def upload_image(data):
    import base64
    from frappe.utils.file_manager import save_file
    doc = frappe.get_doc(data.get("doctype"), data.get("name"))
    file = save_file(data.get("file_name"), base64.b64decode(data.get("filedata_base64")), doc.doctype, doc.name)
    doc.photo = file.file_url
    doc.save(ignore_permissions=True)
    return {"status": "success", "file_url": file}