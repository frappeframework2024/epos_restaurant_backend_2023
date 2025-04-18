import frappe
import base64 


@frappe.whitelist(allow_guest=True)
def approve_click(form_dict, action): 
    from frappe.model.workflow import get_transitions, apply_workflow

    frappe.set_user('Administrator')  # danger zone 🚨
    frappe.flags.ignore_permissions = True
    frappe.flags.in_workflow = True

    doc = frappe.get_doc("Purchase Request", form_dict["name"])
    doc.flags.ignore_permissions = True

    apply_workflow(doc, action=action)

    frappe.flags.in_workflow = False
    frappe.set_user(frappe.session.user)  # restore original user
    return {"status": "ok"}

@frappe.whitelist(allow_guest=True)
def testing(name,workflow_state):
    str_params = "doctype=Purchase Request&name={}&format=Purchase Request Invoice&workflow_state={}".format(name, workflow_state)
    str_params = base64.b64encode(str_params.encode()).decode('utf-8')
    str_params = base64.b64encode(str_params.encode()).decode('utf-8')
    return "data=key{}estc&doctype=NONE&name=NONE&preview=1".format(str_params)
    
