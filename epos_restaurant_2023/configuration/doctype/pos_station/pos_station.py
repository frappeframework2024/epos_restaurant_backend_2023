# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests

from epos_restaurant_2023.api.api import get_estc_connection,has_internet
from frappe.model.document import Document

class POSStation(Document):

	def validate(self):
		pass


	@frappe.whitelist()
	def on_refresh_license(self):

		if not self.device_id :
			frappe.throw(_("Device ID is required."))


		if not has_internet():
			frappe.throw(_("The server is not connected to the internet."))


		conn = get_estc_connection()

		bus = frappe.get_doc("Business Branch", self.business_branch)
 
		if not bus.property_code:
			frappe.throw(_("Property code is not configured in the system."))

		estc_central_url = conn.get("estc_central_url", None) or ""
		url = f"{estc_central_url}/api/method/estc.api.api.get_device_license"

		request_param = {
			"property_code":bus.property_code, #required
			"platform":self.platform, # required
			"request_code": self.device_id, #required
			"device_name": self.name
		}

		# Make POST request
		## verify=False is equivalent to CURLOPT_SSL_VERIFYPEER=false
		response = requests.post(url, json=request_param, verify=False)  
		try:
			resp = response.json() 
		except Exception:
			resp = {}   
		license_code = (resp.get("data",None) or {}).get("license_code",None) or "" 
		
		if license_code and license_code != "Inactive License":
			# self.license = license_code
			return license_code

		return ""


