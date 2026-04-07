import frappe
import json
from collections import defaultdict
from frappe.model.naming import make_autoname

@frappe.whitelist()
def get_sales(name,doctype):
    filters = get_filters(doctype)
    sql = """select
                a.name,
                a.business_branch
            from `tabSale` a
            {0}""".format(filters)
    data = frappe.db.sql(sql, values={"name": name}, as_dict=1)
    return data

@frappe.whitelist()
def get_sale_products(name,doctype):
    config = frappe.get_doc("Quickbooks Desktop Integration")
    filters = get_filters(doctype)
    sql = """select
                a.business_branch,
                b.product_code,
                b.product_name,
                b.quantity,
                b.price,
                b.amount,
                b.total_discount,
                b.parent
            from `tabSale` a
            inner join `tabSale Product` b on b.parent = a.name
            {0}""".format(filters)
    data = frappe.db.sql(sql, values={"name": name}, as_dict=1)
    for a in data:
        a["qb_company"] = ([b.qb_company for b in config.available_branch if b.business_branch == a.get("business_branch")][0] or "")
        for c in config.tbl_products_mapping:
            if a.get("product_code") == c.get("reference_name") and a.get("qb_company") == c.get("qb_company"):
                a["qb_product_code"] = c.get("qb_name")
    return data

def get_sale_payments(name,doctype):
    config = frappe.get_doc("Quickbooks Desktop Integration")
    filters = get_filters(doctype)
    sql = """select
                b.sale,
                b.name,
                b.payment_type,
                b.payment_amount,
                a.business_branch
            from `tabSale` a
            inner join `tabSale Payment` b on b.sale = a.name
            {0}""".format(filters)
    data = frappe.db.sql(sql, values={"name": name}, as_dict=1)
    for a in data:
        a["qb_company"] = ([b.qb_company for b in config.available_branch if b.business_branch == a.get("business_branch")][0] or "")
        for c in config.tbl_payment_types_mapping:
            if a.get("payment_type") == c.get("reference_name") and a.get("qb_company") == c.get("qb_company"):
                a["qb_payment_type"] = c.get("qb_name")
    return data

def get_available_branches():
    config = frappe.get_doc("Quickbooks Desktop Integration")
    available_branchs  = [x.business_branch for x in config.available_branch]
    return available_branchs

@frappe.whitelist()
def get_filters(doctype):
    filters = "where a.docstatus = 1 and a.business_branch in ({0})".format(",".join(["'{}'".format(d) for d in get_available_branches()]))
    if doctype == "Cashier Shift":
        filters += " and a.cashier_shift = %(name)s"
    else:
        filters += " and a.working_day = %(name)s"
    return filters

@frappe.whitelist()
def add_sales_to_sync_queue(name,doctype,posting_date):
    sales = get_sales(name,doctype)
    sale_products = get_sale_products(name,doctype)
    sale_payments = get_sale_payments(name,doctype)
    for sale in sales:
        neted_sale = {"sale": sale}
        neted_sale["sale"]["products"] = [{"qb_product_code": a.get("qb_product_code"), "product_code": a.get("product_code"), "product_name": a.get("product_name"), "quantity": a.get("quantity"), "price": a.get("price"), "amount": a.get("amount"), "total_discount": a.get("total_discount")} for a in sale_products if a.get("parent") == sale.get("name")]
        doc = frappe.new_doc("Quickbooks Sync Queues")
        doc.action = "Add"
        doc.status = "Pending"
        doc.action_type = "Sale"
        doc.reference_name = sale.get("name")
        doc.reference_doctype = "Sale"
        doc.payload ="{\"posting_date\": \"" + str(posting_date) + "\",\"data\": " + str(json.dumps(neted_sale)) + "}"
        doc.code = make_autoname("SINV.-.####")
        doc.business_branch = sale.get("business_branch")
        doc.insert()
    for payment in sale_payments:
        doc = frappe.new_doc("Quickbooks Sync Queues")
        doc.action = "Add"
        doc.status = "Pending"
        doc.action_type = "Payment"
        doc.reference_name = payment.get("name")
        doc.reference_doctype = "Sale Payment"
        doc.payload ="{\"posting_date\": \"" + str(posting_date) + "\",\"data\": " + str(json.dumps({"sale": payment.get("sale"),"qb_payment_type": payment.get("qb_payment_type"), "payment_type": payment.get("payment_type"), "payment_amount": payment.get("payment_amount")})) + "}"
        doc.code = make_autoname("SPAY.-.####")
        doc.business_branch = payment.get("business_branch")
        doc.insert()
    frappe.db.commit()