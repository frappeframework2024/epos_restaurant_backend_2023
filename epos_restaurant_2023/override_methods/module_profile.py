import frappe

def on_update(doc, method=None, *args, **kwargs):
    # Fetch all users who have the updated module profile
    users = frappe.get_all("User", filters={"module_profile": doc.name})
    for user in users:
        user_doc = frappe.get_doc("User", user.name)
        # Update module selection field (assuming a field called `modules` in User doctype)
        user_doc.set("block_modules", [])
        for m in doc.block_modules:
            user_doc.append("block_modules", {
                "module":m.module
            })
            
        user_doc.save()

    frappe.db.commit()