# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Task(Document):
	def on_update(self):
		project = frappe.get_doc("Project", self.project)
		project.complete_percentage = calculate_completion_percentage(self.project)
		project.status =  get_status(self.project)
		project.save()
			
def calculate_completion_percentage(project):
		total_tasks = frappe.db.count("Task", filters={"project": project})
		completed_tasks = frappe.db.count("Task", filters={"project": project, "status": "Completed"})
		return (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

def get_working_tasks(project):
		return frappe.db.count("Task", filters={"project": project, "status": "Working"})

def get_status(project):
		working_task = get_working_tasks(project)
		percent = calculate_completion_percentage(project)
		if (percent < 100 and percent > 0) or working_task > 0:
			return "In Progress"
		elif percent == 0:
			return "Open"
		else:
			return "Completed"
		