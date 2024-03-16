# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet

class ProductCategory(NestedSet):
	def validate(self):
		if self.flags.ignore_validate==True:
			return 
		if not self.product_category_name_kh:
			 self.product_category_name_kh=  self.product_category_name_en