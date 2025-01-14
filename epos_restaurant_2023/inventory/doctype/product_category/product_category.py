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

		if self.product_code_prefix is None or self.product_code_prefix == "":
			self.product_code_prefix =  str(self.product_category_name_en[0:4]).upper() + ".####"