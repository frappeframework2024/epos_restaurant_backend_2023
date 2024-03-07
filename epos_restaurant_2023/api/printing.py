import json
import frappe
from PIL import Image, ImageChops
from html2image import Html2Image
import numpy as np
import os
from frappe.www.printview import get_html_and_style
from frappe.utils import get_site_name
import base64
from frappe.utils import (
    nowdate,
    parse_val,
    is_html,
    add_to_date,
)
from escpos import *


def get_print_context(doc, sale_products= []):
    setting = frappe.get_doc("POS Config", frappe.db.get_value("POS Profile",doc.pos_profile, "pos_config"))
    return {"doc": doc,"sale_products": sale_products,"nowdate": nowdate, "frappe.utils": frappe.utils,"setting":setting,"frappe":frappe}


 
def trim(file_path):
    image = Image.open(file_path)
    # Load the image and convert it to RGB
    image = image.convert("RGB")

    # Get the pixel values as a numpy array
    pixels = np.array(image)

    # Define the color range for red and white
    red_min = np.array([200, 0, 0])
    red_max = np.array([255, 50, 50])
    white_min = np.array([240, 240, 240])
    white_max = np.array([255, 255, 255])

    # Create a mask for pixels that are red or white
    mask = np.logical_or(
        np.all(np.logical_and(pixels >= red_min, pixels <= red_max), axis=-1),
        np.all(np.logical_and(pixels >= white_min, pixels <= white_max), axis=-1)
    )

    # Find the bounding box of the white area
    coords = np.argwhere(~mask)
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0) + 1

    # Crop the image using the bounding box
    cropped = image.crop((x_min, y_min, x_max, y_max+30))

    # Save the cropped image
    cropped.save(file_path)
    

@frappe.whitelist(allow_guest=True)
def print_bill(station, name,template ):
    doc = frappe.get_doc("Sale", name)
    data_template,css,width,fixed_height = frappe.db.get_value("POS Receipt Template",template,["template","style","width","fixed_height"])
    html= frappe.render_template(data_template, get_print_context(doc))
    height = fixed_height
    if len(doc.sale_products) > 0:
        height += len(doc.sale_products) * 75
    return capture(html=html,css=css,height=height,width=width,imnage='{}_bill_image.png'.format(station))

 
@frappe.whitelist(allow_guest=True,methods="POST")
def print_kitchen_order(station, sale, products,printer): 
    if not frappe.db.exists("Sale",sale):
        return ""    
    doc_sale = frappe.get_doc("Sale", sale)
    data_template,css,width,fixed_height = frappe.db.get_value("POS Receipt Template","Kitchen Order",["template","style","width","fixed_height"])   
    html = frappe.render_template(data_template, get_print_context(doc=doc_sale,sale_products =  products))
    # return products  
    height = fixed_height
    if len(products) > 0:
        height += len(products) * 75 

    return capture(html=html,css=css,height=height,width=width,imnage='{}_{}_kitchen_order.png'.format(station,printer))
 
       


@frappe.whitelist(allow_guest=True)
def capture(height,width,html,css,imnage):
    chrome_path = "/usr/bin/google-chrome"
    # Set the CHROME_PATH environment variable
    os.environ['CHROME_PATH'] = chrome_path
    height = height 
    hti = Html2Image()
    hti.chrome_path=chrome_path
    hti.output_path =frappe.get_site_path() 
    hti.size=(width, height)

    hti.screenshot(html_str=html, css_str=css, save_as='{}'.format(imnage))   
    image_path = '{}/{}'.format(frappe.get_site_path(),imnage)    
    trim(image_path)
  

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        encoded_data = base64.b64encode(image_data).decode("utf-8")
    return encoded_data