import frappe
from frappe import _
from  epos_restaurant_2023.api.cache_function import get_default_account_from_pos_config, get_default_account_from_revenue_group, get_doctype_value_cache
def submit_stock_to_general_ledger_entry_on_submit(self):

      from epos_restaurant_2023.api.account import submit_general_ledger_entry
      entry_type =frappe.db.get_value("Stock Entry Type", self.entry_type, "purpose")
      docs = []
      againt = [x for x in self.items if x.default_account]
      if not againt:
            frappe.throw(_("No items with a default account found."))
      againt = againt[0]  # Assuming all items have the same default account, use the first one

      if entry_type == 'Stock In':
            doc={
                  "doctype":"General Ledger",
                  "posting_date":self.posting_date,
                  "account":self.default_inventory_account,
                  "debit_amount":self.total_amount,
                  "againt":againt.default_account,
                  "voucher_type":"Stock Entry",
                  "voucher_subtype":self.entry_type,
                  "voucher_number":self.name,
                  "business_branch": self.business_branch,
            }
            doc["remark"] = "Accounting Entry for Stock"
            docs.append(doc)
            doc={
                  "doctype":"General Ledger",
                  "posting_date":self.posting_date,
                  "account":againt.default_account,
                  "credit_amount":self.total_amount,
                  "againt":self.default_inventory_account,
                  "voucher_type":"Stock Entry",
                  "voucher_subtype":self.entry_type,
                  "voucher_number":self.name,
                  "business_branch": self.business_branch,
            }
            doc["remark"] = "Accounting Entry for Stock"
            docs.append(doc)
      if entry_type == 'Stock Out':
            doc={
                  "doctype":"General Ledger",
                  "posting_date":self.posting_date,
                  "account":self.default_inventory_account,
                  "credit_amount":self.total_amount,
                  "againt":againt.default_account,
                  "voucher_type":"Stock Entry",
                  "voucher_subtype":self.entry_type,
                  "voucher_number":self.name,
                  "business_branch": self.business_branch,
            }
            doc["remark"] = "Accounting Entry for Stock"
            docs.append(doc)

            doc={
                  "doctype":"General Ledger",
                  "posting_date":self.posting_date,
                  "account":againt.default_account,
                  "debit_amount":self.total_amount,
                  "againt":self.default_inventory_account,
                  "voucher_type":"Stock Entry",
                  "voucher_subtype":self.entry_type,
                  "voucher_number":self.name,
                  "business_branch": self.business_branch,
            }
            doc["remark"] = "Accounting Entry for Stock"
            docs.append(doc)
      submit_general_ledger_entry(docs=docs)