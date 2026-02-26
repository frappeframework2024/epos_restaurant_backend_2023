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
	jobs = frappe.db.get_list('Schedule Job Config',filters={"enabled": 1},fields=['execute_time', 'api_method','enqueue'],as_list=0)
	for job in jobs:
		if (job.execute_time or "") != "":
			time = datetime.datetime.strptime(str(job.execute_time), "%H:%M:%S").time()
			scheduled_datetime = datetime.datetime.combine(now.date(), time)
			if now.hour == scheduled_datetime.hour and now.minute == scheduled_datetime.minute:
				if job.enqueue == 1:
					frappe.enqueue(job.api_method,queue="long", job_name=job.name)
					return "Enqueued"
				else:
					frappe.call(job.api_method)
					return "Executed"
			else:
				return "Not Scheduled"
		else:
			return "No Scheduled"