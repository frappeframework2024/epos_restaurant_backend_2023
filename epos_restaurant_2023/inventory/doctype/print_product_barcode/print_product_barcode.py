# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PrintProductBarcode(Document):
	@frappe.whitelist(allow_guest=True)
	def get_product_price(self):
		cat = frappe.db.get_value('Product Category', self.category, ['lft', 'rgt'], as_dict=1)
		products = frappe.db.sql("""WITH categories AS(
									SELECT 
										name 
									FROM `tabProduct Category` 
									where lft >= {0} and rgt <= {1})

									SELECT
										coalesce(a.barcode,'Not Set') product_code,
										a.price_rule,
										a.unit,
										a.price,
						   				a.photo,
										b.product_name_en,
										b.product_name_kh
									FROM `tabProduct Price` a
									INNER JOIN `tabProduct` b ON b.name = a.parent
									WHERE b.product_category IN(SELECT name FROM categories)""".format(cat.lft,cat.rgt),as_dict=1)
		return products
