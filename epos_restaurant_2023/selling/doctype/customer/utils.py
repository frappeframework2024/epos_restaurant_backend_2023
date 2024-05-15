import frappe

def update_fetch_from_fields(self):
	data_for_updates = []

	if self.has_value_changed("customer_name_en"):
		data_for_updates.append({"doctype":"Sale","update_field":"customer_name='{}'".format(self.customer_name_en)})
		data_for_updates.append({"doctype":"Sale Payment","update_field":"customer_name='{}'".format(self.customer_name_en)})
	
 
	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			sql="update `tab{}` set {} where customer='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				self.name
			)
			
			frappe.db.sql(sql)