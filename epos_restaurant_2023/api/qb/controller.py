from epos_restaurant_2023.api.qb.qb_post_journal_entry import add_gl_entries_to_sync_queue
import frappe

def add_quickbooks_sync_queue(name,doctype,posting_date):
    config = frappe.get_doc("Quickbooks Desktop Integration")
    if config.enabled :
        if config.sync_mode == "By Invoice":
            if doctype == config.sync_based_on.replace("Close ", ""):
                pass
        elif config.sync_mode == "1 Invoice all sale product":
            if doctype == config.sync_based_on.replace("Close ", ""):
                pass
        elif config.sync_mode == "1 Invoice by revenue group":
            if doctype == config.sync_based_on.replace("Close ", ""):
                pass
        elif config.sync_mode == "Journal entry by revenue group":
            if doctype == config.sync_based_on.replace("Close ", ""):
                add_gl_entries_to_sync_queue(name,doctype,posting_date)
        else:
            pass