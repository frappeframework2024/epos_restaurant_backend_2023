import frappe

import requests
import json
from frappe.utils.data import getdate,add_to_date
from datetime import datetime
import pytz

@frappe.whitelist()
def search_guest(room="",guest_name="", guest_phone=""):
    if not room and not guest_name and not guest_phone:
        return []
    
    doc = frappe.get_doc("Exely Itegration Setting")
    
    url = doc.guest_api_endpoint

    headers = {'x-api-key': doc.api_key}
    params ={}
 
    if room:
        params["room"] = room
    else:
        params["room"] = ""
    
    if guest_name:
        params["guestName"] = guest_name
    else:
        params["guestName"] = ""
        
    if guest_phone:
        params["guestPhone"] = guest_phone
    else:
        params["guestPhone"] = ""


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
    payment_method = "Cash"
    payment_type = None
    if sale:
        if len(sale.payment)>0:
            payment_type= sale.payment[0].payment_type
            pt = [d for d in setting.payment_types if d.epos_payment_type==payment_type]
            if len(pt)>0:
                payment_method = pt[0].exely_payment_type

        if payment_type != "FOC":
            if not payment_type:
                payment_method= "Cash"

            local_time = datetime.fromisoformat(str(str((sale.posting_date).strftime("%Y-%m-%d")) + str(((sale.closed_date or datetime.now())).strftime("T%H:%M:%S+07:00"))))
            utc_time = local_time.astimezone(pytz.utc)
            doc = {
                "roomStayId": sale.exely_room_stay_id,
                "guestId": sale.exely_guest_id or setting.default_general_customer_id,
                "services": get_service_detail(sale),
                "paymentMethod":payment_method,
                "dateTime": str(utc_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
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
                sale = frappe.get_doc("Sale", doc_name)
                if sale.exely_transaction_id:
                    doc = frappe.get_doc({
                        'doctype': 'Comment',
                        'subject': 'Delete sale order',
                        "comment_type":"Info",
                        "reference_doctype":"Sale",
                        "reference_name":doc_name,
                        "content":"Old Exely Tran.Id: {}, New Exely Tran.Id: {}".format(sale.exely_transaction_id,raw["transactionId"] )
                    })
                    doc.insert()

                #log the transaction
                try:
                    doc = frappe.new_doc('Exely Logs')
                    doc.sale = sale.name
                    doc.exely_transaction_type = "Submit Order"
                    doc.exely_transaction_id = raw["transactionId"]
                    doc.grand_total = sale.grand_total
                    doc.submit()
                except:
                    pass
        

                frappe.db.sql("update `tabSale` set exely_transaction_id='{}' where name='{}'".format(raw["transactionId"],doc_name))
                frappe.db.commit()
            else:
                frappe.throw(str(response.text))
        else:
            try:
                doc = frappe.new_doc('Exely Logs')
                doc.sale = sale.name
                doc.exely_transaction_type = "Submit Order"
                doc.exely_transaction_id = raw["transactionId"]
                doc.grand_total = sale.grand_total
                doc.submit()
            except:
                pass

def get_service_detail(sale):
    services = []
    currency = frappe.db.get_single_value("ePOS Settings","currency")
    sale =  cal_adjustment(sale)
    for d in sale.sale_products:
        services.append({
            "name":"{}-{} ({})".format( d.product_code,d.product_name,d.quantity),
            "total":{
                "amount":round(d.total_revenue,2),
                "currency":currency
            },
            "payment":{
                "amount":round(d.total_revenue,2),
                "currency":currency
            },
            "vat":d.total_tax,
            "vatKind":"None"
        })
    return services

@frappe.whitelist()
def cal_adjustment(sale):
    item_amount = sum([round((d.total_revenue or 0),2) for d in sale.sale_products])
    diff = round((sale.grand_total-(item_amount or 0)),2)
    if diff != 0:
        for a in sale.sale_products : a.total_revenue = round((a.total_revenue or 0),2)
        sale.sale_products = sorted(sale.sale_products, key=lambda x: x.total_revenue,reverse=True)
        sale.sale_products[0].total_revenue = round(sale.sale_products[0].total_revenue,2) + diff
    return sale

@frappe.whitelist()    
def cancel_order(transaction_id,sale,comment):
    setting = frappe.get_doc("Exely Itegration Setting")
    url = setting.cancel_service_api_endpoint
    headers = {
                'x-api-key': setting.api_key,
                'Content-Type': 'application/json'
    }
    
    response = requests.delete(url,headers=headers, data=json.dumps( {"transactionId":transaction_id, "comment":comment}))
    if response.status_code!=200:
        frappe.throw(str(response.text))
        
    #log the transaction
    try:
        doc = frappe.new_doc('Exely Logs')
        doc.sale = sale
        doc.exely_transaction_type = "Cancel Order"
        doc.exely_transaction_id = transaction_id
        grand_total = frappe.db.get_value('Sale', sale, 'grand_total')
        doc.grand_total = grand_total
        doc.submit()
    except:
        pass
    
    #return doc
