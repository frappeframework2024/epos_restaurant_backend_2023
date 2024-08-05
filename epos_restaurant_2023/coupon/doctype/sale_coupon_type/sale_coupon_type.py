# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SaleCouponType(Document):
	pass

def  get_sale_coupon_type_search_link(txt):
	data = frappe.db.get_list('Sale Coupon Type',
		fields=["concate(total_visit,' Time(s), ', price) as description",'name','coupon_type'],
		filters={
			"":['like',f'%{txt}%']
		}
	)
	return data