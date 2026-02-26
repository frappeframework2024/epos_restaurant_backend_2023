# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from epos_restaurant_2023.inventory.inventory import check_uom_conversion
from frappe.model.document import Document

class ModifierCode(Document):
	def validate(self):
		if self.flags.ignore_validate==True:
			return 
		#validate product recipe
		for d in self.product_recipe:
			if d.unit != d.base_unit:
				if not check_uom_conversion(d.base_unit, d.unit):
						frappe.throw(_("There is no UoM conversion for product {}-{} from {} to {}".format(d.product, d.product_name, d.base_unit, d.unit)))

	def  on_update(self):
		frappe.clear_document_cache("Modifier Code",self.name)

	def after_rename(self, old_name,new_name,merge):
		frappe.enqueue("epos_restaurant_2023.inventory.doctype.modifier_code.modifier_code.update_temp_menu_after_rename", queue='short', old_name=old_name, new_name=new_name)

@frappe.whitelist()
def update_temp_menu_after_rename(old_name, new_name):
	from epos_restaurant_2023.inventory.doctype.product.product import add_product_to_temp_menu

	frappe.db.sql("""UPDATE `tabModifiers` SET modifier_code = '{0}' WHERE modifier_code = '{1}'""".format(new_name, old_name))
	frappe.db.commit()

	product_ids = frappe.db.sql("""SELECT parent FROM `tabModifiers` WHERE modifier_code = '{0}'""".format(new_name),as_dict=1)
	product_names = [d.get("parent") for d in product_ids]
	if product_names:
		products = frappe.db.sql("""SELECT name FROM `tabProduct` WHERE name IN %(product_names)s""", {"product_names": product_names}, as_dict=1)
		for p in products:
			product_doc = frappe.get_doc("Product", p.get("name"))
			add_product_to_temp_menu(product_doc)
		frappe.db.commit()
