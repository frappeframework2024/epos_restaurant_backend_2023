import frappe
import json

@frappe.whitelist()
def get_group_gl_entries(posting_date):
    sql = """select
                coalesce(account, '') as account,
                coalesce(sum(coalesce(credit_amount,0)),0) as credit_amount,
                coalesce(sum(coalesce(debit_amount,0)),0) as debit_amount
            from `tabGeneral Ledger`
            where is_cancelled = 0 and qb_synced = 0 and posting_date = '{0}'
            group by account""".format(posting_date)
    data = frappe.db.sql(sql, as_dict=1)
    return data

@frappe.whitelist()
def get_reference_gl_entries(posting_date):
    sql = """select
               name
            from `tabGeneral Ledger`
            where is_cancelled = 0 and qb_synced = 0 and posting_date = '{0}'""".format(posting_date)
    data = frappe.db.sql(sql, as_dict=1)
    return data

@frappe.whitelist()
def add_gl_entries_to_sync_queue(name,posting_date):
    config = frappe.get_doc("Quickbooks Desktop Integration")
    gl_entry = get_group_gl_entries(posting_date)
    account_mapping = config.tbl_chart_of_account_mapping
    for a in account_mapping:
        for b in gl_entry:
            if a.reference_name == b["account"]:
                b["account"] = a.qb_name
    sorted_gl_entry = sorted(gl_entry, key=lambda x: x["account"])
    doc = frappe.new_doc("Quickbooks Sync Queues")
    doc.action = "Add"
    doc.status = "Pending"
    doc.action_type = "GL Entry"
    doc.reference_name = name
    doc.payload ="{\"data\": " + json.dumps(sorted_gl_entry) + "}"
    doc.reference_gl_entries = str(json.dumps(get_reference_gl_entries(posting_date)))
    doc.insert()
    frappe.db.commit()