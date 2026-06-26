# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class GYMTrainingTime(Document):
	def validate(self):
		if self.start_time >= self.end_time:
			frappe.throw("Start Time must be less than End Time")
	def before_save(self):
		self.duration_in_second = int((datetime.strptime(self.end_time, "%H:%M:%S") - datetime.strptime(self.start_time, "%H:%M:%S")).total_seconds())
