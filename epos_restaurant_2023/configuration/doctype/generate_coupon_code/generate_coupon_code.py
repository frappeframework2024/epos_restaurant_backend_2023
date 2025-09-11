# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

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
		
		for c in new_coupons:
			frappe.get_doc({
				"doctype": "Coupon Codes",
				"coupon": c.coupon_number,
				"coupon_status": "Unused",
				"coupon_url": c.coupon_number_url or ""

			}).insert(ignore_permissions=True)
		frappe.db.commit() 

		



@frappe.whitelist()
def generate_button(param): 
	p = json.loads(param)
	data  =[]
	for number in range(p.get( "start_number",0), p.get("end_number",0)):
		encrypted_b64 = encrypt_aes_base64(str(number), p.get("key",""), p.get("iv",""))
		item = {"coupon_number":str(number), "coupon_encrypt":encrypted_b64}

		if  p.get("prefix_url","") != "":
			item["coupon_url"] = p.get("prefix_url","") + encrypted_b64
		
		data.append(item)


	return data




def encrypt_aes_base64(plain_text: str, key: str, iv: str) -> str:
    # convert key and iv from str -> bytes
    key_bytes = key.encode("utf-8")
    iv_bytes = iv.encode("utf-8")

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    ct_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(ct_bytes).decode("utf-8")


