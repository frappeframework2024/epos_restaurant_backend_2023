# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import json
import frappe
from epos_restaurant_2023.api.security import aes_encrypt,get_aes_key,encode_base64,decode_base64,aes_decrypt
from frappe.model.document import Document


class FTPBackup(Document):
	def validate(self):
		# data ={"ftp_host":" ","ftp_user":" ","ftp_pass":" ,N{=;]hHA5&}4+oIyVd"}
		# encrypt=aes_encrypt(json.dumps(data),get_aes_key("@dmin$ESTC#"))
		# encrypt = encode_base64(encrypt)
		# frappe.msgprint(encrypt)
  
		pass
  
  
		# dycriptdata = self.ftp_auth_data
		# dycriptdata = decode_base64(dycriptdata)
		# dycriptdata =  aes_decrypt(dycriptdata, get_aes_key("@dmin$ESTC#"))
		# frappe.msgprint(dycriptdata)

 
 