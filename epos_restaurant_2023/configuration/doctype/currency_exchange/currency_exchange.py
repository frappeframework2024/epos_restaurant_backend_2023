# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CurrencyExchange(Document):
	def validate(self):
		if self.exchange_rate_input <= 0 or self.change_exchange_rate_input <= 0:
			frappe.throw("Input values cannot less than or equal zero.")
		
		if  frappe.db.get_default("currency") == self.from_currency:
			self.exchange_rate = self.exchange_rate_input
			self.change_exchange_rate = self.change_exchange_rate_input
		else:
			if frappe.db.get_default("exchange_rate_main_currency") == self.from_currency and    frappe.db.get_default("currency")  != frappe.db.get_default("exchange_rate_main_currency"):
				self.exchange_rate = 1/ self.exchange_rate_input
				self.change_exchange_rate = 1/self.change_exchange_rate_input
		
		if self.from_currency == self.to_currency:
			self.exchange_rate_input = 1
			self.exchange_rate = 1

			## change exchange rate 
			self.change_exchange_rate_input = 1
			self.change_exchange_rate = 1

	def on_submit(self):
		currency = self.to_currency
		if frappe.db.get_default("exchange_rate_main_currency") == self.from_currency and    frappe.db.get_default("currency")  != frappe.db.get_default("exchange_rate_main_currency"):
			currency = self.from_currency

		# update payment type  exchange rate
		sql_payment_type = "update `tabPayment Type` set exchange_rate = {}, change_exchange_rate = {} where currency='{}'".format(self.exchange_rate,self.change_exchange_rate,currency)
		frappe.db.sql(sql_payment_type)		

		#update to pos config payment type exchange rate
		sql_config_payment_type = "update `tabPOS Config Payment Type` set exchange_rate = {},change_exchange_rate = {} where currency='{}'".format(self.exchange_rate,self.change_exchange_rate,currency)
		frappe.db.sql(sql_config_payment_type)

@frappe.whitelist()
def get_current_exchange_rate(posting_date="",base="",quotes=""):
	from datetime import datetime
	settings = frappe.get_doc("ePOS Settings")
	now = datetime.now()
	diff = (now - datetime.strptime(settings.last_get_exchange_rate, "%Y-%m-%d %H:%M:%S.%f")).seconds
	if diff > 10:
		settings.last_get_exchange_rate = now
		settings.save()
		if (posting_date or "") != "" and (base or "") != "" and (quotes or "") != "":
			import requests
			url = "https://api.frankfurter.dev/v2/rates?date={0}&base={1}&quotes={2}".format(posting_date,base,quotes)
			response = requests.get(url)
			result = response.json()
			return {"rate":result[0].get("rate")}
		else:
			return {"rate":0}
	else:
		frappe.throw("Please wait 10 second")