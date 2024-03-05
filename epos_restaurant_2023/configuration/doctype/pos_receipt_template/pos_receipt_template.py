# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.jinja import validate_template
from frappe.modules.utils import export_module_json, get_doc_module
import json, os
from frappe.model.document import Document

from frappe.utils import (
    validate_email_address,
    nowdate,
    parse_val,
    is_html,
    add_to_date,
)

class POSReceiptTemplate(Document):
	def validate(self):
		validate_template(self.template)



