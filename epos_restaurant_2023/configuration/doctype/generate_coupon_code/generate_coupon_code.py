# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from frappe.model.document import bulk_insert
from epos_restaurant_2023.utils import encrypt_aes_base64
from frappe.model.document import Document


class GenerateCouponCode(Document):

	def before_submit(self):
		self.encrypt_key = None
		self.encrypt_iv = None
	             

		# 1. Collect all coupon numbers from child table
		coupons = [c.coupon_number for c in self.coupon_codes]

		# 2. Check existing coupons
		existing = frappe.db.get_all(
			"Coupon Codes",
			filters=[{"coupon": ["in", coupons]}, {"coupon_status":"Unused"}],
			fields=["coupon"]
		)
		existing_coupons = {d["coupon"] for d in existing}

		# 3. Filter new coupons
		new_coupons = [c for c in self.coupon_codes if c.coupon_number not in existing_coupons]


		if not new_coupons:
			frappe.msgprint("No new coupons to insert")
			return

		docs = [] 
		import uuid
		from frappe.utils import now
		for c in new_coupons:			
			doc = {
				"doctype":"Coupon Codes",
				"reference_doctype":"Generate Coupon Code",
				"reference_name":self.name,
				"coupon": c.coupon_number,
				"coupon_url":c.coupon_number_url or "",
				"coupon_status":"Unused",
				"name": str(uuid.uuid4()),
				"owner": frappe.session.user,
				"creation":now()
			}		
			docs.append(doc)		
		bulk_insert("Coupon Codes", get_record(docs=docs) , chunk_size=10000)


def get_record(docs):  
    for d in docs:
        doc = frappe.get_doc(d)      
        yield doc
        


@frappe.whitelist()
def generate_button(param): 
	p = json.loads(param)
	data  =[]
	for number in range(p.get( "start_number",0), p.get("end_number",0)):
		encrypted_b64 = encrypt_aes_base64(str(number))
		item = {"coupon_number":str(number), "coupon_encrypt":encrypted_b64}

		if  p.get("prefix_url","") != "":
			item["coupon_url"] = p.get("prefix_url","") + encrypted_b64
		
		data.append(item)


	return data



 