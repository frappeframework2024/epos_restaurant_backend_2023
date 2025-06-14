# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe.model.document import Document


class ScheduleJobConfig(Document):
	pass

@frappe.whitelist(allow_guest=True)
def check_custom_schedule():
	now = frappe.utils.now_datetime()
	jobs = frappe.get_all("Scheduled Job Config", filters={"enabled": 1})
	for job in jobs:
		config = frappe.get_doc("Scheduled Job Config", job.name)
		if (config.execute_time or "") != "":
			scheduled_time = datetime.datetime.strptime(config.execute_time, "%H:%M:%S").time()
			if now.hour == scheduled_time.hour and now.minute == scheduled_time.minute:
				frappe.enqueue(config.api_method,queue="long", job_name=config.name)