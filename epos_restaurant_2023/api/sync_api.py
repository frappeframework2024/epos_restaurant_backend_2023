import json
import frappe
import requests

@frappe.whitelist()
def generate_init_data_sync_to_client(business_branch):
    
    #Generate Data to Data For Sync
    document_for_sync = frappe.db.get_all("Sync To Client Setting", fields=['document_type','sort_order'],order_by='sort_order asc')
    for data in document_for_sync:
        frappe.enqueue('epos_restaurant_2023.api.sync_api.insert_data_to_data_for_sync',document_type=data.document_type)
    return document_for_sync


def insert_data_to_data_for_sync(document_type):
    data_for_sync = frappe.get_all(document_type,fields=['name'],order_by='idx asc')
    for d in data_for_sync:
        doc = frappe.get_doc({
                'doctype': 'Data For Sync',
                'document_type':document_type,
                'document_name':d.name
            })
        doc.save()


@frappe.whitelist()
def sync_data_to_client():
    server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
    headers = {
                'Authorization': 'token fdad19c1e00297c:608a34efdd29106'
            }
    server_url = server_url + "api/resource/Data For Sync" + '?fields=["name","document_name","document_type"]&limit_page_length=100000000'
    response = requests.get(server_url,headers=headers)
    
    if response.status_code==200:
        data = json.loads(response.text)

    for d in data:
        frappe.enqueue('epos_restaurant_2023.api.sync_api.on_save',data = d)
    return data['data']

def on_save(data):
    server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
    headers = {
                'Authorization': 'token fdad19c1e00297c:608a34efdd29106'
            }
    server_url = server_url + f"api/resource/{data['document_type']}/{data['name']}"

    response = requests.get(server_url,headers=headers)
    data = json.loads(response.text)
    doc = frappe.get_doc(data['data'])
    doc.save()
    return data['data']
    