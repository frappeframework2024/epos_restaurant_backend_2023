# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CashCouponItems(Document):
    pass
	# def validate(self):
	# 	sql = "select count(name) from `tabCash Coupon Items` where code == %(code)s and name != %(name)s"
	# 	docs = frappe.db.sql(sql,{"code":self.code, "name":self.name})
	# 	if len( docs) > 0:
	# 		frappe.throw(_(""))
