import functools
import re
import json
import frappe
from frappe import _

@frappe.whitelist()
def generate_audit_trail_from_version():
    audit_trail_documents = frappe.db.get_list("Audit Trail Document", pluck='name')
    version_data = frappe.db.get_list('Version',
                        filters={
                            'ref_doctype': ["in",audit_trail_documents],
                            "custom_is_converted_to_audit_trail":0
                        },
                        fields=['name','ref_doctype', 'docname',"creation"],
                        page_length=100
                    )
 
    if len(version_data)> 0:
        for v in version_data:
            
            if frappe.db.exists(v.ref_doctype, v.docname):
                doc = frappe.get_doc("Version", v.name)

                submit_update_audit_trail_from_version(doc)
        
        #update is converted
        frappe.db.sql("update `tabVersion` set custom_is_converted_to_audit_trail=1 where name in %(names)s", {"names":[d.name for d in version_data]})
        frappe.db.commit()
        return version_data

def update_audit_trail_from_version(doc, method=None, *args, **kwargs):    
    if frappe.db.exists("Audit Trail Document",doc.ref_doctype,cache=True):
        submit_update_audit_trail_from_version(doc)
        # frappe.enqueue("edoor.api.utils.submit_update_audit_trail_from_version", queue='short', doc=doc)

def submit_update_audit_trail_from_version(doc):
    if frappe.db.exists("Audit Trail Document",doc.ref_doctype,cache=True):
        doctype = frappe.get_doc("Audit Trail Document", doc.ref_doctype)
        data = json.loads(doc.data)
        data_changed = []
        if doc.ref_doctype == "Reservation Room Rate":
            data_changed.append("<b>Date:</b> " +  frappe.db.get_value("Reservation Room Rate", doc.docname,"date").strftime('%d-%m-%Y'))

        for d in data["changed"]:
            if d[0] in [f.field_name for f in doctype.tracking_field] and ((d[1] or '')!='' or (d[2] or '')!=''):
                field = [f  for f in doctype.tracking_field if f.field_name==d[0]][0]
                if field.field_type=="Check":
                    data_changed.append(f'<b>{field.label}</b>: {"Yes" if d[1]==1 else "No"} <b>to</b> {"Yes" if d[2]==1 else "No"}')
                elif 'tax_' in field.field_name:
                    ref_doc = frappe.get_doc(doc.ref_doctype,doc.docname)
                    if field.field_name == 'tax_1_rate':
                        data_changed.append(f'<b>{ref_doc.tax_1_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    elif field.field_name == 'tax_1_amount':
                        data_changed.append(f'<b>{ref_doc.tax_1_name} Amount </b>: {d[1]} <b>to</b> {d[2]}')
                    elif field.field_name == 'tax_2_rate':
                        data_changed.append(f'<b>{ref_doc.tax_2_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    elif field.field_name == 'tax_2_amount':
                        data_changed.append(f'<b>{ref_doc.tax_2_name} Amount </b>: {d[1]} <b>to</b> {d[2]}')
                    elif field.field_name == 'tax_2_rate':
                        data_changed.append(f'<b>{ref_doc.tax_2_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    
                    elif field.field_name == 'tax_3_rate':
                        data_changed.append(f'<b>{ref_doc.tax_3_name}</b>: {d[1]}% <b>to</b> {d[2]}%')
                    elif field.field_name == 'tax_3_amount':
                        data_changed.append(f'<b>{ref_doc.tax_3_name} Amount </b>: {d[1]} <b>to</b> {d[2]}')
                        
                else:
                    if field.hide_old_value==1:
                        data_changed.append(f'<b>{field.label}</b>: {d[2]}')
                    else:
                        data_changed.append(f'<b>{field.label}</b>: {d[1]} <b>to</b> {d[2]}')


        if doc.ref_doctype == "Reservation Room Rate":
            if len(data_changed)==1:
                #we skip it cause have only 1 record is date
                return

        if len(data_changed)>0:
            comment_doc = []
            comment_doc.append({
            "creation":doc.creation,
            "subject": "Change Value",
            "custom_audit_trail_type":"Updated",
            "custom_icon":"pi pi-file-edit",
            "reference_doctype":doc.ref_doctype,
            "reference_name":doc.docname,
            "content":", ".join(data_changed)  
            })
            # frappe.enqueue("edoor.api.utils.add_audit_trail", queue='long', data=comment_doc)
            add_audit_trail(comment_doc, update_creation_date=True)


    
def add_audit_trail(data,update_creation_date=False):
    for d in data:
        if not hasattr(d,"custom_property"):
            doc = frappe.get_doc(d["reference_doctype"],d["reference_name"])
            if hasattr(doc,"property"):
                working_day = get_working_day(doc.property)
                d["custom_posting_date"]= working_day["date_working_day"]
                
                if working_day["cashier_shift"]:
                    d["custom_cashier_shift"]= working_day["cashier_shift"]["name"]
                d["custom_property"]= doc.property
            elif hasattr(doc,"business_branch"):
                working_day = get_working_day(doc.business_branch)
                
                d["custom_posting_date"]= working_day["date_working_day"]
                d["custom_property"]= doc.business_branch
                if working_day["cashier_shift"]:
                    d["custom_cashier_shift"]= working_day["cashier_shift"]["name"]

        d["doctype"]="Comment"
        if not hasattr(d,"comment_type"):
            d["comment_type"]="Info"
            
        d["custom_is_audit_trail"]=1
        d["comment_by"]:frappe.session.user.full_name

        doc = frappe.get_doc(d).insert(ignore_permissions=True)
        if update_creation_date:
            frappe.db.sql("update `tabComment` set creation=%(creation)s where name=%(name)s",{"name":doc.name, "creation":d["creation"]})

@frappe.whitelist()
def get_working_day(property = ''):
    working_day = frappe.db.sql("select  posting_date as date,name,pos_profile from `tabWorking Day` where business_branch = '{0}' order by creation desc limit 1".format(property),as_dict=1)
    cashier_shift = None
    if len(working_day)>0:
        data = frappe.db.sql("select creation, shift_name,name from `tabCashier Shift` where business_branch = '{}' and working_day='{}' and pos_profile='{}' ORDER BY creation desc limit 1".format(property,working_day[0]["name"],working_day[0]["pos_profile"]),as_dict=1)
        
        if len(data)>0:
            cashier_shift = data[0]
        
    return {
        "date_working_day": working_day[0]["date"] if len(working_day)>0 else '',
        "name":working_day[0]["name"] if len(working_day)>0 else '',
        "cashier_shift":cashier_shift
    }