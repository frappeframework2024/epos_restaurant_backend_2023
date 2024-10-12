# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from passlib.hash import pbkdf2_sha256

class ResetData(Document):
	def validate(self):
			if self.stored_password is None or self.stored_password == "" : 
				self.stored_password = self.password
			if self.stored_password is None or self.stored_password == "":
				frappe.throw("Please Enter Password")
			else:
				user = frappe.db.sql("select password from __Auth where name ='Administrator' and doctype='User' and fieldname='password'",as_dict=True)
				if not pbkdf2_sha256.verify(self.stored_password, user[0].password):
					frappe.throw("Wrong Password")

	def on_submit(self):
		if self.transaction_type == "Reset Database":
			frappe.call('epos_restaurant_2023.install.reset_database')
		elif self.transaction_type == "Reset Sale Transaction":
			frappe.call('epos_restaurant_2023.install.reset_sale_transaction')
		else:
			frappe.msgprint("?")
		
		naming_series = []
		naming_series = frappe.db.sql("select distinct pos_bill_number_prefix as naming from `tabPOS Config`", as_dict=1)
		naming_series = naming_series + frappe.db.sql("select distinct waiting_number_prefix as naming from `tabPOS Profile`",as_dict=1)
		series =[]
		for d in naming_series:
			if d["naming"]:
				string = d["naming"]
				date = frappe.utils.nowdate()
				year = date.split("-")[0]
				year_short = year[-2:]
				month = date.split("-")[1]
				naming = string.replace('.', '').replace('YYYY', year).replace('yyyy', year).replace('YY', year_short).replace('yy', year_short).replace('MM', month).replace('#', '')
				series.append(naming)
		
		frappe.db.sql("update `tabSeries` set current=  0 where name in %(format)s", {"format":[d for d in series]} )

	def on_update(self):
		frappe.db.sql("""update `tabReset Data` set stored_password = '' where docstatus = 1 and name = '{0}'""".format(self.name))
		self.reload()
		

	