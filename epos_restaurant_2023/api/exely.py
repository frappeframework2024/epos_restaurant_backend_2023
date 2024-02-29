import frappe

import requests
import json
from frappe.utils.data import getdate,add_to_date

@frappe.whitelist()
def search_guest(room="",guest_name="", guest_phone=""):
    if not room and not guest_name and not guest_phone:
        return []
    
    doc = frappe.get_doc("Exely Itegration Setting")
    
    url = doc.guest_api_endpoint

    headers = {'x-api-key': doc.api_key}
    params ={}
 
    if guest_name:
        params["guestName"] = guest_name
        
    if guest_phone:
        params["guestPhone"] = guest_phone
        
    if room:
        params["room"] = room
        


    response = requests.get(url, headers=headers, params=params)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = []
        
        raw= json.loads(response.text)
        for r in raw:
            doc={
                "guest_id":r["id"],
                "customer_name_en": "{} {}".format(r["firstName"],r["lastName"]),
                "phone_number": "/".join(r["phones"])
            }
            guest_info = frappe.db.sql("select name,customer_group from `tabCustomer` where exely_guest_id='{}' limit 1".format(r["id"]),as_dict=1)
            
            if len(guest_info)>0:
                guest_info = frappe.db.sql("select name,customer_group from `tabCustomer` where exely_guest_id='{}' limit 1".format(r["id"]),as_dict=1)
                doc["name"] = guest_info[0]["name"]
                doc["customer_group"] = guest_info[0]["customer_group"]
            else:
                guest = create_guest(doc)
                doc["name"] = guest.name
                doc["customer_group"] = guest.customer_group
                
            
            if "roomStays" in r:
                for s in r["roomStays"]:
                    doc["stay_room_id"]=s["id"]
                    doc["arrival"]=s["checkInDateTime"]
                    doc["departure"]=s["checkOutDateTime"]
                    doc["room_number"]=room
                    doc["status"]=s["status"]
                    doc["status_color"] = "green" if s["status"]=="New" else "red"
                    
                    
                    data.append(doc)
            else:
                data.append(doc)

        frappe.db.commit()  
        return data
    
        
    else:
        frappe.throw(f"{response.status_code} - {response.text}" ) 
        
def create_guest(data):
    doc = frappe.get_doc({
        "doctype":"Customer",
        "customer_name_en": data["customer_name_en"],
        "customer_group":"General",
        "exely_guest_id":data["guest_id"],
        "phone_number":data["phone_number"]
    }).insert()
    return doc

    
@frappe.whitelist()    
def submit_order_to_exely(doc_name):
    setting = frappe.get_doc("Exely Itegration Setting")
    sale = frappe.get_doc("Sale",doc_name)
    
    if sale:
        payment_method= "Cash"
        if len(sale.payment)>0:
            payment_type= sale.payment[0].payment_type
            pt = [d for d in setting.payment_types if d.epos_payment_type==payment_type]
            if len(pt)>0:
                payment_method = pt[0].exely_payment_type
                
        if  not payment_type:
            payment_method= "Cash"
            
        doc = {
            "roomStayId": sale.exely_room_stay_id,
            "guestId": sale.exely_guest_id,
            "services": get_service_detail(sale.sale_products),
            "paymentMethod":payment_method
        }
        
     
        # send to api
        url = setting.post_service_api_endpoint

        headers = {
                    'x-api-key': setting.api_key,
                    'Content-Type': 'application/json'
                }
        response = requests.post(url, data=json.dumps(doc),headers=headers)
        if response.status_code==200:
            raw= json.loads(response.text)
            frappe.db.sql("update `tabSale` set exely_transaction_id='{}' where name='{}'".format(raw["transactionId"],doc_name))
            frappe.db.commit()
        else:
            frappe.throw(str(response.text))

       
    #return doc

def get_service_detail(data):
    services = []
    currency = frappe.db.get_single_value("ePOS Settings","currency")
    for d in data:
        services.append({
            "name":"{}-{} ({})".format( d.product_code,d.product_name,d.quantity),
            "total":{
                "amount":d.amount,
                "currency":currency
            },
            "payment":{
                "amount":d.amount,
                "currency":currency
            },
            "vat":d.total_tax
        })
    return services


@frappe.whitelist()    
def cancel_order(transaction_id,comment):
    setting = frappe.get_doc("Exely Itegration Setting")
    url = setting.cancel_service_api_endpoint
    headers = {
                'x-api-key': setting.api_key,
                'Content-Type': 'application/json'
    }
    
    response = requests.delete(url,headers=headers, params= {"transactionId":transaction_id, "comment":comment})
    if response.status_code!=200:
        frappe.throw(str(response.text))

    
    #return doc
