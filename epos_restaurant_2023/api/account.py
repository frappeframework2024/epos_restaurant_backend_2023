import frappe
from frappe.utils import getdate
import uuid  
from frappe.model.document import bulk_insert
from frappe.model.naming import make_autoname
import json
from functools import lru_cache
def submit_general_ledger_entry(docs):
    # bulk insert
    bulk_insert("General Ledger", get_general_ledger_entry_record(docs=docs) , chunk_size=10000)
    frappe.db.commit()


def get_general_ledger_entry_record(docs):
    for d in docs:
        doc = frappe.get_doc(d)
        if doc.amount and not (doc.credit_amount or doc.debit_amount ):
            root_type = frappe.get_cached_value("Chart Of Account",doc.account,"root_type")
            if root_type in ["Asset","Expenses"]:
                if doc.amount>0:
                    doc.debit_amount = abs(doc.amount)
                else:
                    doc.credit_amount = abs(doc.amount)
            else:
                if doc.amount>0:
                    doc.credit_amount = abs(doc.amount)
                else:
                    doc.debit_amount =abs(doc.amount)
      
        doc.name  = make_autoname("GLE.YYYY.-.#####")
        yield doc
        
        
def cancel_general_ledger_entery(doctype,docname):
    sql = "select * from `tabGeneral Ledger` where voucher_type='{}' and voucher_number= '{}'".format( doctype,docname)
    data = frappe.db.sql(sql,as_dict=1)
    docs = []
    for r in data:
        doc = {
                "doctype":"General Ledger",
                "posting_date":r["posting_date"],
                "account":r["account"],
                "credit_amount":r["debit_amount"],
                "debit_amount":r["credit_amount"],
                "againt":r["againt"],
                "againt_voucher_type":"Sale",
                "againt_voucher_number": r["againt_voucher_number"],
                "voucher_type":doctype,
                "voucher_number":docname,
                "business_branch": r["business_branch"],
                "remark": r["remark"],
                "party_type": r["party_type"],
                "party": r["party"],
                "is_cancelled":1,
            }
        docs.append(doc)
        
    submit_general_ledger_entry(docs)
    # update submited record is cancelled = 1
    frappe.db.sql("update `tabGeneral Ledger` set is_cancelled=1 where voucher_type='{}' and voucher_number='{}'".format(doctype,docname))
    frappe.db.commit()
     

@lru_cache(maxsize=128)
def  get_hierarchy_account_for_report_by_parent(parent,business_branch):
    sql="""
        WITH RECURSIVE hierarchy AS (
            SELECT
                name as account,
                parent_chart_of_account,
                0 AS indent,
                CAST(account_code AS CHAR(255)) AS path 
            FROM
                `tabChart Of Account`
            WHERE
                name = %(parent)s  and 
                business_branch = %(business_branch)s
            
            UNION ALL
            SELECT
                t.name as account,
                t.parent_chart_of_account,
                h.indent + 1 AS indent,
                CONCAT(h.path, '-', t.account_code) AS path 
            FROM
                `tabChart Of Account` t
            JOIN
                hierarchy h ON t.parent_chart_of_account = h.account
        )
        SELECT
            account,
            parent_chart_of_account,
            indent
        FROM
            hierarchy
        ORDER BY
            path;

    """
    return frappe.db.sql(sql,{"parent":parent,"business_branch":business_branch},as_dict=1)

    
    
@lru_cache(maxsize=128)
def  get_accounts_by_root_types(filters):
    filters = json.loads(filters)
  
    data = frappe.db.sql("select name from `tabChart Of Account` where business_branch=%(business_branch)s and root_type in %(root_types)s and is_group=0",filters,as_dict=1)
    return [d["name"] for d in data]