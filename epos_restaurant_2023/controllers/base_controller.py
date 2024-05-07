
import frappe
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import json
class BaseController(Document):
    def get_print_settings(self):
        # check addition print setting from doctype 
        if frappe.db.exists("Additional Print Setting",self.doctype):
            setting_doc = frappe.get_doc("Additional Print Setting",self.doctype)
            self.check_print_setting()
            return [s["fieldname"] for s in json.loads(setting_doc.additional_print_setting)]
            
        return []

    def check_print_setting(self):
        
        setting_doc = frappe.get_doc("Additional Print Setting",self.doctype)
        if json.loads(setting_doc.additional_print_setting):
            new_settings=[]
            for s in json.loads(setting_doc.additional_print_setting):
                if not frappe.db.exists("Custom Field",{"dt":self.doctype,"fieldname":s["fieldname"]}):
                    new_settings.append(s)
            if len(new_settings):
                create_custom_fields(
                        {
                            "Print Settings": new_settings
                        }
                    )
                frappe.db.commit()