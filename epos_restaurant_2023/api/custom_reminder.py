import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint
from frappe.utils.data import add_to_date, get_datetime, now_datetime


def send_reminders():
	# Ensure that we send all reminders that might be before next job execution.
	job_freq = cint(frappe.get_conf().scheduler_interval) or 240
	upper_threshold = add_to_date(now_datetime(), seconds=job_freq, as_string=True, as_datetime=True)

	lower_threshold = add_to_date(now_datetime(), hours=-8, as_string=True, as_datetime=True)

	pending_reminders = frappe.get_all(
		"Reminder",
		filters=[
			("remind_at", "<=", upper_threshold),
			("remind_at", ">=", lower_threshold),  # dont send too old reminders if failed to send
			("notified", "=", 0),
		],
		pluck="name",
	)

	for reminder in pending_reminders:
		send_reminder(reminder)
		
def send_reminder(reminder):
    doc = frappe.get_doc("Reminder",reminder)

    if doc.notified:
        return

    doc.db_set("notified", 1, update_modified=False)

    try:
        notification = frappe.new_doc("Notification Log")
        notification.for_user = doc.user
        notification.set("type", "Alert")
        notification.document_type = doc.reminder_doctype
        notification.document_name = doc.reminder_docname
        notification.subject = doc.description
        notification.custom_property = doc.custom_property
        
        notification.insert()
    except Exception:
        doc.log_error("Failed to send reminder")
