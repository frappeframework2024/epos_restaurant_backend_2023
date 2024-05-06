import os
import uuid
from html2image import Html2Image
import numpy as np
import base64
import subprocess
import platform 
from PIL import Image
import frappe
import json
import time
from escpos.printer import Network
from epos_restaurant_2023.api.printing import (
    get_print_context, 
    print_from_print_format,
    )
 


def html_to_image(height,width,html,css,path,image):    
    if not os.path.exists(path):
        os.makedirs(path)
        os.chmod(path, 0o777)
    hti = Html2Image()    
    hti.output_path = path
    hti.size=(int(width), height)
    css += """body{
        background:white !important;
    }"""  
    hti.screenshot(html_str=html, css_str=css, save_as='{}'.format(image))   
    image_path = '{}/{}'.format(path,image)    
    trim(image_path)
    return image_path

def trim(file_path):
    image = Image.open(file_path)
    image = image.convert("RGB")
    pixels = np.array(image)
    red_min = np.array([200, 0, 0])
    red_max = np.array([255, 50, 50])
    white_min = np.array([240, 240, 240])
    white_max = np.array([255, 255, 255])
    mask = np.logical_or(
        np.all(np.logical_and(pixels >= red_min, pixels <= red_max), axis=-1),
        np.all(np.logical_and(pixels >= white_min, pixels <= white_max), axis=-1)
    )
    coords = np.argwhere(~mask)
    y_min, x_min = coords.min(axis=0)      
    y_max, x_max = coords.max(axis=0)
    cropped = image.crop((x_min, y_min, x_max, y_max+30))
    cropped.save(file_path)

def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]

    result = subprocess.run(command, stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8')
    if "Request timed out." in output or "100% packet loss" in output:
        return False # "NOT CONNECTED"
    return True #"CONNECTED"

def on_print(file_path, printer, delete_file = 1):
    if printer: 
        if ping(printer["ip_address"]):         
            try:
                printer_obj = Network(printer["ip_address"]) 
                printer_obj.open()
                ## crop image base on height buffer size  
                im = Image.open(file_path)
                _image = im
                # printer_obj.image(im) 
                _width,_height = im.size
                # _width = 590
    
                crop_height = 200
                init_crop_height = 0 
                h = _height 
                while _height > crop_height: 
                    im = _image
                    box = (0, init_crop_height, _width, int( crop_height+init_crop_height))
                    crop_image = im.crop(box)
                    printer_obj.image(crop_image)                 
                    init_crop_height += int(crop_height)
                    _height -= crop_height
                    time.sleep(0.1)
                    if _height <=  crop_height: 


                        break

                if _height>0:
                    box = (0, int(init_crop_height), _width, int(_height+init_crop_height)) 
                    crop_image = im.crop(box)
                    printer_obj.image(crop_image) 
                    time.sleep(0.1)

                printer_obj.text(" ")           
                printer_obj.cut()
                printer_obj.close()

                if delete_file == 1:
                    if os.path.isfile(file_path):
                        os.remove(file_path)

            except OSError as e:
                frappe.throw(str(e))
            finally:
                pass


            
@frappe.whitelist(methods="POST")
def print_all_bill_to_network_printer(data):
    print_data = []
    for d in data:
        doc = frappe.get_doc("Sale",d["name"])
        doc.sale_status = 'Bill Requested'
        doc.save()
        print_data.append(d)
    frappe.db.commit()

    for d in print_data:
        print_bill_to_network_printer(d) 

    return True


## quick pay print bill
@frappe.whitelist(methods="POST")
def print_all_bill_quick_pay_to_network_printer(data):
    print_data = []
    for s in data:
        doc =  frappe.get_doc('Sale',s['name'])
        doc.append ('payment', {
                'payment_type':s['payment_type'],
                'input_amount':doc.grand_total,
                'amount':doc.grand_total
            })          

        doc.docstatus = 1
        doc.sale_status = 'Closed'
        doc.save()
        print_data.append(s)
    frappe.db.commit()

    ## print
    for d in print_data:
        print_bill_to_network_printer(d) 
 
    return True


# @frappe.whitelist(allow_guest=True,methods='POST') 
@frappe.whitelist(methods="POST")
def print_bill_to_network_printer(data):     
    frappe.enqueue("epos_restaurant_2023.api.network_printing_api.print_bill_to_network_printer_queue",data=data,queue="short")
    
# @frappe.whitelist(allow_guest=True)
def print_bill_to_network_printer_queue(data):
    # time.sleep(0.2)
    if not frappe.db.exists("Sale",data["name"]):
        return ""  
    doc = frappe.get_doc("Sale", data["name"]) 
    data_template,css,width,fixed_height,item_height = frappe.db.get_value("POS Receipt Template",data["template_name"],["template","style","width","fixed_height","item_height"])
    html= frappe.render_template(data_template, get_print_context(doc,data["reprint"]))

    img_name = str(uuid.uuid4())+".PNG"
    path = frappe.get_site_path()+"/file/receipt/"
    height = fixed_height
    if len(doc.sale_products) > 0:
        height += (len(doc.sale_products) * item_height)
    file_path = html_to_image(height,int(width),html,css,path,img_name)

    if data["action"] == "print_invoice":
        for i in range(data["print_setting"]["print_invoice_copies"]):
            time.sleep(0.05)
            on_print(file_path=file_path,printer= data["printer"], delete_file=0)

    elif data["action"] == "print_receipt":
        for i in range(data["print_setting"]["print_receipt_copies"]):
            time.sleep(0.05)
            on_print(file_path=file_path,printer= data["printer"], delete_file=0)

    ## delete file after print        
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except OSError as e:
        frappe.throw(str(e))

        
   
# @frappe.whitelist(allow_guest=True,methods="POST")
@frappe.whitelist(methods="POST")
def print_kot_to_network_printer(data):  
    frappe.enqueue("epos_restaurant_2023.api.network_printing_api.print_kot_to_network_printer_enque",data=data,queue="short")
    
## KOT Printing
# @frappe.whitelist(allow_guest=True,methods="POST")

def print_kot_to_network_printer_enque(data):     
    sale = data["sale"]
    if not frappe.db.exists("Sale",sale["name"]):
        return "" 
    doc_sale = frappe.get_doc("Sale", sale["name"])   
    data_template,css,width,fixed_height,item_height = frappe.db.get_value("POS Receipt Template","Kitchen Order",["template","style","width","fixed_height","item_height"])   
    template ={
        "data_template":data_template,
        "css":css,
        "width":int(width),
        "fixed_height":fixed_height,
        "item_height":item_height
    }
    time.sleep(0.5)
    on_kot_print(data=data,sale=doc_sale, template=template)

### print kot by print 
def on_kot_print(data,sale,template):
    for p in data["printers"]:
        _on_kot_print(template=template, station=p["station"], printer=p["printer"], sale=sale,sale_products=p["products"])

### print kot with con
def _on_kot_print(template ,  station, printer,sale, sale_products): 
    is_label_printer = printer["is_label_printer"] or 0 
    group_item_type = printer["group_item_type"] or "Printer cut by order"
    path = frappe.get_site_path()+"/file/"
    if is_label_printer == 1:
        data_template,css,width,fixed_height,item_height = frappe.db.get_value("POS Receipt Template","Lable Sticker",["template","style","width","fixed_height","item_height"])   
        for sp in sale_products:
            _sp = json.loads(json.dumps(sp))
            quantity = _sp["quantity"]
            sp["quantity"] = 1
            _sale_products = []
            _sale_products.append(sp)

            for i in range(quantity):                
                html = frappe.render_template(data_template, get_print_context(doc=sale,sale_products = _sale_products,printer_name=printer["printer_name"]))
                img_name = "{}_{}.PNG".format(station,str(uuid.uuid4()) )                          
                height =  fixed_height + item_height                    
                file_path = html_to_image(height,int(width),html,css,path,img_name)  
                time.sleep(0.2)
                on_print(file_path, printer) 
    else:
        height =  template["fixed_height"] or 500
        if group_item_type == "Printer cut by order":
            img_name = "{}_{}_{}.PNG".format(station,printer["printer_name"],str(uuid.uuid4()))             
            if len(sale_products) > 0:
                height += len(sale_products) * (template["item_height"] or 70)
            
            html = frappe.render_template(template["data_template"], get_print_context(doc=sale,sale_products = sale_products,printer_name=printer["printer_name"]))
            file_path = html_to_image(height ,int(template["width"]),html,template["css"],path,img_name)  
            time.sleep(0.2)
            on_print(file_path, printer)  

        elif group_item_type == "Printer cut by order line":        
            height +=  (template["item_height"] or 70)
            for sp in sale_products:
                _sale_products = []
                _sale_products.append(sp)
                img_name = "{}_{}_{}.PNG".format(station,printer["printer_name"],str(uuid.uuid4())) 
                html = frappe.render_template(template["data_template"], get_print_context(doc=sale,sale_products = _sale_products,printer_name=printer["printer_name"]))
                file_path = html_to_image(height ,int(template["width"]),html,template["css"],path,img_name)  
                time.sleep(0.2)
                on_print(file_path, printer)  

        elif group_item_type == "Printer cut by order quantity":
            height +=  (template["item_height"] or 70)
            for sp in sale_products:
                _sp = json.loads(json.dumps(sp))
                quantity = _sp["quantity"]
                sp["quantity"] = 1                
                _sale_products = []
                _sale_products.append(sp)

                for i in range(quantity):   
                    img_name = "{}_{}_{}.PNG".format(station,printer["printer_name"],str(uuid.uuid4())) 
                    html = frappe.render_template(template["data_template"], get_print_context(doc=sale,sale_products = _sale_products,printer_name=printer["printer_name"]))
                    file_path = html_to_image(height ,int(template["width"]),html,template["css"],path,img_name)  
                    time.sleep(0.2)
                    on_print(file_path, printer)    

## end KOT printing


## Print Waiting Number
@frappe.whitelist(methods="POST")
def print_waiting_number_to_network_printer(data):
    frappe.enqueue("epos_restaurant_2023.api.network_printing_api.print_waiting_number_to_network_printer_enque",data=data,queue="short")

# @frappe.whitelist(allow_guest=True,methods="POST")
def print_waiting_number_to_network_printer_enque(data):
    if not frappe.db.exists("Sale",data["name"]):
        return ""    
    doc = frappe.get_doc("Sale", data["name"])
    data_template,css,width,fixed_height,item_height = frappe.db.get_value("POS Receipt Template","Waiting Slip",["template","style","width","fixed_height","item_height"])
    html= frappe.render_template(data_template, get_print_context(doc))
    img_name = str(uuid.uuid4())+".PNG"
    path = frappe.get_site_path()+"/file/"
    height = fixed_height
    if len(doc.sale_products) > 0:
        height += (len(doc.sale_products) * item_height)
         
    file_path = html_to_image(height,int(width),html,css,path,img_name)
    ## onProcess Print
    time.sleep(0.2)
    on_print(file_path, data["printer"])
     
## Print Voucher Slip
@frappe.whitelist(methods="POST")
def print_voucher_to_network_printer(data):
    frappe.enqueue("epos_restaurant_2023.api.network_printing_api.print_voucher_to_network_printer_enque",data=data,queue="short")

# @frappe.whitelist(allow_guest=True,methods="POST")
def print_voucher_to_network_printer_enque(data):
    if not frappe.db.exists("Voucher",data["name"]):
        return ""    
    doc = frappe.get_doc("Voucher", data["name"]) 
    working_day = frappe.get_doc("Working Day",doc.working_day)

    doc.pos_profile = working_day.pos_profile
    data_template,css ,width,fixed_height,item_height= frappe.db.get_value("POS Receipt Template","Voucher Reciept",["template","style","width","fixed_height","item_height"])
    html= frappe.render_template(data_template, get_print_context(doc))
    height = fixed_height + item_height
    img_name = str(uuid.uuid4())+".PNG"
    path = frappe.get_site_path()+"/file/"

    file_path = html_to_image(height,int(width),html,css,path,img_name)
    time.sleep(0.2)
    on_print(file_path, data["printer"])


# @frappe.whitelist(allow_guest=True,methods="POST")
@frappe.whitelist(methods="POST")
def print_wifi_to_network_printer(data):
    data_template,css,width,fixed_height,item_height = frappe.db.get_value("POS Receipt Template","WiFi",["template","style","width","fixed_height","item_height"]) 
    html= frappe.render_template(data_template, {"password":data["password"]})
    height = fixed_height + item_height
    img_name = str(uuid.uuid4())+".PNG"
    path = frappe.get_site_path()+"/file/"

    file_path = html_to_image(height,width,html,css,path,img_name)
    time.sleep(0.2)
    on_print(file_path, data["printer"])

# Print report
@frappe.whitelist(methods="POST")
def print_report_to_network_printer(data):
    if data:
        frappe.enqueue("epos_restaurant_2023.api.network_printing_api.print_report_to_network_printer_enque",data=data,queue="short")

# @frappe.whitelist(allow_guest=True,methods="POST")
def print_report_to_network_printer_enque(data):
    if data:
        result = print_from_print_format(data,is_html=True)
        img_name = str(uuid.uuid4())+".PNG"
        path = frappe.get_site_path()+"/file/"

        file_path = html_to_image(result["height"],result["width"],result["html"],result["css"],path,img_name)
        time.sleep(0.2)
        on_print(file_path, data["printer"])

