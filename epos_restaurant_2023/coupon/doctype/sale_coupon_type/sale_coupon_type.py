# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SaleCouponType(Document):
	pass

@frappe.whitelist()
def  get_sale_coupon_type_search_link(txt):
	data = frappe.db.get_list('Sale Coupon Type',
		fields=['total_visit','price','name','coupon_type'],
		filters={
			"name":['like','%' + txt+'%']
		}
	)
	return data