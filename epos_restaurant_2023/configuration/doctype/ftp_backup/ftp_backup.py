# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import json
import frappe
from epos_restaurant_2023.api.security import aes_encrypt,get_aes_key,encode_base64,decode_base64,aes_decrypt
from frappe.model.document import Document


class FTPBackup(Document):
	def before_save(self):
		self.message = ""

 
 