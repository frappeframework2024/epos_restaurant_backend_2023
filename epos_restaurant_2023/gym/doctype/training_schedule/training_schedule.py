# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt
from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document


class TrainingSchedule(Document):
	def validate(self):
		self.total_members = len(self.members)



@frappe.whitelist(allow_guest= True)
def get_event(start,end,filters):
	data = frappe.db.get_all("Training Schedule",
						  fields = [
							  "name",
							  "day",
							  "time_training",
							  "start_date",
							  "start_time",
							  "end_date",
							  "end_time",
							  "class_type",
							  "color",
							  "trainer",
							  "trainer_name_en",
							  "total_members",
							  "monday",
							  "tuesday",
							  "wednesday",
							  "thursday",
							  "friday",
							  "saturday",
							  "sunday"
						], 
						filters=filters)
	result =[]
	current_date = datetime.now() 

	for d in data: 
		generate_days = get_days(data=d)	

		

		start_date_obj =  (d.start_date or current_date.date())
		end_date_obj = (d.end_date or current_date.date())

		stime = (str(d.start_time) or current_date.strftime("%H:%M:%S")).split(":")
		etime =  (str(d.end_time) or (current_date + timedelta(hours=1)).strftime("%H:%M:%S")) .split(":") 

		start_date = start_date_obj
		while start_date <= end_date_obj:
			if len(generate_days) <=0:
				start_date += timedelta(days=1)
			else:
				day_name = start_date.strftime("%A") 				
				if len([ x for x in generate_days if x == day_name]) > 0 :
					start_on = datetime(start_date.year, start_date.month, start_date.day, int(stime[0]), int(stime[1]), int(stime[2]))
					end_on = datetime(start_date.year, start_date.month, start_date.day, int(etime[0]), int(etime[1]), int(etime[2]))
					trainer = ""
					if d.get("trainer"):
						trainer = "({}) - {}".format(d.get("trainer"), d.get("trainer_name_en"))

					title =  """{}\nTrainer: {}\nMembers: {}""".format( d.get("class_type"), trainer,d.get("total_members"))
					result.append({
						"start": start_on,
						"end": end_on,
						"name": d.get("name"),
						"all_day": 0,
						"title":title , 
						"color": d.get("color"),
						
					})
				start_date += timedelta(days=1)
		

	return	result

@frappe.whitelist(allow_guest= True)
def get_days(data):
	d = data
	days = []
	if d.monday:
		days.append("Monday")
	if d.tuesday:
		days.append("Tuesday")
	if d.wednesday:
		days.append("Wednesday")
	if d.thursday:
		days.append("Thursday")
	if d.friday:
		days.append("Friday")
	if d.saturday:
		days.append("Saturday")
	if d.sunday:
		days.append("Sunday")

	return days