# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours
import frappe
from datetime import datetime

class Timesheet(Document):
	def validate(self):
		for a in self.time_sheets:
			if (a.from_time or "") == "" and self.status != "Completed":
				a.from_time = ""
			else:
				a.from_time = a.from_time if (a.from_time or "") != "" else datetime.now().strftime('%H:%M:%S')

			if (a.to_time or "") == "" and self.status != "Completed":
				a.to_time = ""
			else:
				a.to_time = a.to_time if (a.to_time or "") != "" else datetime.now().strftime('%H:%M:%S')

			if (a.from_time or "") != "" and (a.to_time or "") != "":
				a.actual_time = time_diff_in_hours(a.to_time, a.from_time)
			else:
				a.actual_time = 0

			task = frappe.get_doc("Task", a.task)
			task.status = self.status
			task.save()
		self.total_working_hours = sum([(a.actual_time or 0) for a in self.time_sheets])