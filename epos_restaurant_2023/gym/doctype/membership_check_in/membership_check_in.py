# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import json
import frappe
from frappe.model.document import Document


class MembershipCheckIn(Document): 


	def on_submit(self): 
		for m in self.membership_check_in_item:			
			sql = """select count(`name`) as total_check_in from `tabMembership Check In Items` 
					where membership = '{}' 
					and docstatus = 1 """.format( m.membership)
			
		 
			exec = frappe.db.sql(sql, as_dict=1)
			# frappe.throw(str(exec))
			# frappe.throw(str(sql))
			if exec:
				count = (exec[0].total_check_in or 0)
				update = "update `tabMembership Check In Items` set check_in_number = {} where name ='{}'".format(count,m.name) 
				frappe.db.sql(update)

			#
			saving_crypto_customer(self, m.membership)


def saving_crypto_customer(self,membership ):
	sql = """select 
		count(name) as total_checked_in
	from `tabMembership Check In Items` m 
	where m.docstatus = 1
	-- and cast(m.creation as date) = %(check_in_date)s
	and m.membership = %(membership)s
	"""	
	docs = frappe.db.sql(sql,{"check_in_date":self.check_in_date,"membership":membership}, as_dict = 1)	
	
	if len( docs)>0:
		if docs[0]["total_checked_in"] <= 1:	
			default_crypto_amount_on_check_in = frappe.db.get_single_value("Check In Crypto Setting","default_crypto_amount_on_check_in")			
			update = """update `tabCustomer` c set c.total_crypto_on_check_in = c.total_crypto_on_check_in + {} where c.name = %(member)s""".format(default_crypto_amount_on_check_in)
			
			frappe.db.sql(update,{"member":self.member})

	frappe.db.sql("""update `tabCustomer` c 
			   set c.total_crypto_amount = c.total_crypto_on_check_in + c.total_crypto_on_register  + c.total_crypto_balance_expired,
			   c.total_crypto_balance = (c.total_crypto_on_check_in + c.total_crypto_on_register + c.total_crypto_balance_expired) - (c.total_crypto_claim + c.total_crypto_balance_expired)
			   where c.name = %(member)s""", {"member":self.member})				

	

	