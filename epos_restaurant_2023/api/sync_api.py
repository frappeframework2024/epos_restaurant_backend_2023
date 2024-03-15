import json
import frappe
import requests

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
def get_data_for_sync():
    frappe.db.sql('Update `tabData For Sync` set is_synced = 1')
    data = frappe.db.get_all('Data For Sync',fields=['document_name', 'name','document_type'],filters={
        'is_synced': 1
    })
    frappe.db.sql('Delete From `tabData For Sync` where is_synced=1')
    return data

@frappe.whitelist()
def sync_data_to_client():
    server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
    headers = {
                'Authorization': 'token fdad19c1e00297c:608a34efdd29106'
            }
    server_url = server_url + "api/method/epos_restaurant_2023.api.sync_api.get_data_for_sync"
    response = requests.get(server_url,headers=headers)
    
    if response.status_code==200:
        data_for_sync = json.loads(response.text)
        data_for_sync = data_for_sync['message']
        doctype_for_sync = frappe.db.sql('select document_type,total_record_per_sync from `tabSync To Client Setting` order by idx',as_dict=1)
        for d in doctype_for_sync:
            filter_data = list(filter(lambda x: x["document_type"] == d.document_type,data_for_sync))
            
            small_arrays = [filter_data[i:i+d.total_record_per_sync] for i in range(0, len(data_for_sync), d.total_record_per_sync)]
            if len(small_arrays) > 0:
                
                frappe.enqueue('epos_restaurant_2023.api.sync_api.on_save',data=small_arrays) 
    else:
        return response.text

def on_save(data):
   
    server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
    headers = {
                'Authorization': 'token fdad19c1e00297c:608a34efdd29106'
            }
    for d in data:
        if len(d)> 0:
            for row in d:
                server_url = server_url + f"api/resource/{row['document_type']}/{row['document_name']}"
                response = requests.get(server_url,headers=headers)
                if response.status_code==200:
                    response_data = json.loads(response.text)
                    
                    if frappe.db.exists(row['document_type'],row['document_name']):
                        row = response_data['data']
                        doc = frappe.get_doc(row)
                        doc.save()
                    else:
                        row = response_data['data']
                        row["__newname"] = row["name"]
                        doc = frappe.get_doc(row)
                        doc.insert(ignore_permissions=True, ignore_links=True)
                    return doc
                else:
                    return response.raw
    