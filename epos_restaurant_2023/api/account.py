import frappe
from frappe.utils import getdate
import uuid  
from frappe.model.document import bulk_insert

def submit_general_ledger_entry(docs):
    # bulk insert
    bulk_insert("General Ledger", get_general_ledger_entry_record(docs=docs) , chunk_size=10000)
    frappe.db.commit()


def get_general_ledger_entry_record(docs):
 
    for d in docs:
        doc = frappe.get_doc(d)
        doc.name =  str(uuid.uuid4())
        yield doc