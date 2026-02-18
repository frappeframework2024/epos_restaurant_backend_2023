#~app/epos_restaurant_2023/epos_restaurant_2023/helpers/payway_helper.py

from frappe import _
import frappe
from datetime import datetime, timezone

@frappe.whitelist()
def create_error_log_enqueue(params, error):
    frappe.enqueue(
            "epos_restaurant_2023.helpers.payway_helper.create_error_log", # python function or a module path as string
            queue="short", # one of short, default, long
            job_name="create_payway_integration_log", # specify a job name
            # enqueue_after_commit=True,
            params = params,
            error = error
        )

@frappe.whitelist()   
def create_error_log(params, error):
    try: 
        #remove key
        error.pop("http_status_code",None)
        #create logs
        doc = frappe.new_doc("PayWay Error Logs")
        doc.request_params =frappe.as_json(params)
        doc.error_message = frappe.as_json(error)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error(
            title="PayWay Error Logs",
            message=frappe.get_traceback()
        )

@frappe.whitelist(allow_guest=True) 
def update_payway_tranaction_id_on_callback_success_enqueue(tran):
    frappe.enqueue(
            "epos_restaurant_2023.helpers.payway_helper.update_payway_tranaction_id_on_callback_success", # python function or a module path as string
            queue="short", # one of short, default, long
            job_name="update_payway_tranaction_id_on_callback_success", # specify a job name
            enqueue_after_commit=True,
            tran = tran
        )
    # return update_payway_tranaction_id_on_callback_success_enqueue(tran)

@frappe.whitelist() 
def update_payway_tranaction_id_on_callback_success(tran):
    (tran.get("response") or {}).pop("temp_tran_id",None)
    update_sql = """
        UPDATE `tabSale`
        SET payment_transaction = CONCAT(
            IFNULL(payment_transaction, ''),
            %(tran)s
        )
        WHERE name = %(invoice_id)s
    """
    filters = {"tran":frappe.as_json(tran), "invoice_id":  (tran.get("response") or {}).get("invoice_id") }
    frappe.db.sql(update_sql,filters)
    frappe.db.commit()

    return "update success"

