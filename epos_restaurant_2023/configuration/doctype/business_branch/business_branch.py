# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt


from epos_restaurant_2023.api.cache_function import get_doctype_value_cache
import frappe
from frappe.model.document import Document


class BusinessBranch(Document):
    def on_update(self):
        frappe.clear_document_cache("Business Branch", self.name)
        get_doctype_value_cache.cache_clear()
        frappe.clear_document_cache("Business Branch", self.name)

    @frappe.whitelist()
    def update_to_transaction(self):
        data = {"property": self.name}
        sql = "select distinct parent from `tabDocField`  where fieldtype='Link' and options = 'Business Branch'"
        doc_names = frappe.db.sql(sql, as_dict=1)
        for dt in doc_names:
            frappe.db.sql(
                "update `tab{}` set property=%(property)s".format(dt["parent"]), data
            )

        frappe.db.commit()

        frappe.msgprint("Update complete")
