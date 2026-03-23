import frappe
import json
from collections import defaultdict
from frappe.model.naming import make_autoname

@frappe.whitelist()
def get_gl_entries(is_grouped,transaction_type,doctype,voucher_number,business_branch=""):
    fields = "name"
    filters = ""
    operator = ""
    group_by = ""
    final_filters = ""
    
    filters = get_voucher_number(doctype,voucher_number)
    if business_branch != "":
        filters += " and business_branch = %(business_branch)s"
    if transaction_type == "GL Entry":
        operator = "not in"
    else:
        operator = "in"
    static_filters = "voucher_type in ('Sale','Sale Payment','Cash Transaction') and is_cancelled = 0 and qb_synced = 0"
    order_by = "order by name"
    
    if is_grouped == 1:
        group_by = "GROUP BY account,coalesce(account_type,'Not Set'),case when coalesce(account_type,'Not Set') = 'Receivable' then party else party end,business_branch"
        fields = "account,"
        if transaction_type == "Sale":
            fields += "voucher_number sale_id,"
            group_by = "GROUP BY account,voucher_number,coalesce(account_type,'Not Set'), case when coalesce(account_type,'Not Set') = 'Receivable' then party else party end,business_branch"
            final_filters = " where account_type not in ('Receivable') "
            
        fields += """case when coalesce(account_type,'Not Set') = 'Receivable' then party else party end name,
                    coalesce(account_type,'Not Set') account_type,
                    business_branch,
                    sum(coalesce(debit_amount,0)) debit,
                    sum(coalesce(credit_amount,0)) credit"""
        order_by = "order by account"
        
        
    sql = """with gl_entries as(SELECT 
                {0}
            FROM `tabGeneral Ledger`
            WHERE voucher_number {1} (
            select
                voucher_number
            from `tabGeneral Ledger`
                WHERE account_type = 'Receivable' AND
                {2} and {3}) and
            {2} and {3}
            {4})""".format(fields,operator,static_filters,filters,group_by)
    sql += " select * from gl_entries {0} {1} ".format(final_filters,order_by)
    data = frappe.db.sql(sql,{"business_branch":business_branch}, as_dict=1)
    return data

def get_branches(doctype,voucher_number):
    filters = get_voucher_number(doctype,voucher_number)
    data = frappe.db.sql("""select 
                        business_branch as name
                    from `tabGeneral Ledger`
                    WHERE voucher_type in ('Sale','Sale Payment') and is_cancelled = 0 and qb_synced = 0 and {0}
                    group by business_branch""".format(filters),as_dict=1)
    return data

def get_voucher_number(doctype,voucher_number):
    filters = ""
    if doctype == "Cashier Shift":
        filters = "cashier_shift = '{}'".format(voucher_number)
    else:
        filters = "working_day = '{}'".format(voucher_number)
    return filters

@frappe.whitelist()
def add_gl_entries_to_sync_queue(name,doctype,posting_date):
    config = frappe.get_doc("Quickbooks Desktop Integration")
    branches = get_branches(doctype,name)
    if len(branches or []) > 0:
        transaction_types = ["GL Entry","Sale"]
        grouped_gl_entries = None
        gl_entries = None
        for branch in branches:
            for transaction_type in transaction_types:
                grouped_gl_entries = get_gl_entries(1,transaction_type,doctype,name,branch["name"])
                gl_entries = get_gl_entries(0,transaction_type,doctype,name,branch["name"])
                account_mapping = config.tbl_chart_of_account_mapping
                for a in account_mapping:
                    for b in grouped_gl_entries:
                        if a.reference_name == b["account"]:
                            b["qb_account"] = a.qb_name
                
                customer_mapping = config.tbl_customers_mapping
                for a in customer_mapping:
                    for b in grouped_gl_entries:
                        if a.reference_name == b["name"]:
                            b["qb_cust_name"] = a.qb_name
                            b["qb_cust_list_id"] = a.qb_list_id
                 
                 
                if transaction_type == "Sale": 
                    def add_groupby_sale(posting_date, data):
                        # Group by sale_id
                        grouped = defaultdict(list)
                        for row in data:
                            grouped[row["sale_id"]].append(row)

                        # Build full grouped structure with totals
                        full_grouped = {}
                        for sale_id, lines in grouped.items():
                            full_grouped[sale_id] = lines                           
                        
                        for inv in full_grouped.values():                            
                            doc = frappe.new_doc("Quickbooks Sync Queues")
                            doc.action = "Add"
                            doc.status = "Pending"
                            doc.action_type = transaction_type
                            doc.reference_name = name
                            doc.reference_doctype = doctype
                            doc.payload ="{\"posting_date\": \"" + str(posting_date) + "\",\"data\": " + json.dumps(inv) + "}"
                            doc.reference_gl_entries = str(json.dumps([{"name": d["name"]} for d in gl_entries]))
                            doc.code = make_autoname("QBINV.-.####")
                            doc.business_branch = branch["name"]
                            doc.insert()   
                            
                    add_groupby_sale(posting_date, grouped_gl_entries)
                    
                else:                     
                    doc = frappe.new_doc("Quickbooks Sync Queues")
                    doc.action = "Add"
                    doc.status = "Pending"
                    doc.action_type = transaction_type
                    doc.reference_name = name
                    doc.reference_doctype = doctype
                    doc.payload ="{\"posting_date\": \"" + str(posting_date) + "\",\"data\": " + json.dumps(grouped_gl_entries) + "}"
                    doc.reference_gl_entries = str(json.dumps([{"name": d["name"]} for d in gl_entries]))
                    doc.code = make_autoname("JE.-.######")
                    doc.business_branch = branch["name"]
                    doc.insert()
                frappe.db.commit()