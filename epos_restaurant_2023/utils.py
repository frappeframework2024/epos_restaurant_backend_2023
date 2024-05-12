import frappe
from py_linq import Enumerable
from datetime import datetime
from frappe.utils import date_diff,today ,add_months, add_days,getdate,add_to_date

@frappe.whitelist()
def get_date_range_by_timespan(timespan):
    # timespan is Today, This Month, Yesterday, Last Month, This Year, Last Year
   
    date_range = {}
    if timespan=="Today":
        date_range["start_date"] = today()
        date_range["end_date"] = today()
    elif timespan=="Yesterday":
        date_range["start_date"] = add_to_date(getdate(today()),days=-1)
        date_range["end_date"] = add_to_date(getdate(today()),days=-1)    
    elif timespan=="This Month":
        date_range["start_date"] = getdate(today()).replace(day=1)
        date_range["end_date"] = add_to_date( date_range["start_date"] ,months=1,days=-1)    
        
    elif timespan=="Next Month":
        date_range["start_date"] = add_to_date( getdate(today()).replace(day=1),months= 1)
        date_range["end_date"] = add_to_date( date_range["start_date"] ,months=1,days=-1)   
    elif timespan=="Last Month":
        date_range["start_date"] = add_to_date( getdate(today()).replace(day=1),months=-1)
        date_range["end_date"] = add_to_date( date_range["start_date"] ,months=1,days=-1)   
    elif timespan=="This Year":
        date_range["start_date"] =getdate(today()).replace(day=1,month=1)
        date_range["end_date"] = add_to_date( date_range["start_date"] ,years=1,days=-1)
    elif timespan=="Last Year":
        date_range["start_date"] =getdate(today()).replace(day=1,month=1,year=getdate(today()).year-1)
        date_range["end_date"] = add_to_date( date_range["start_date"] ,years=1,days=-1)
    return date_range
        
    
def date_diff(end_date, start_date):
	date_format = "%Y-%m-%d"
	date1 = datetime.strptime(start_date, date_format)
	date2 = datetime.strptime(end_date, date_format)

	delta = date2 - date1
	return delta.days

def get_tour_package_price(self):
	data = frappe.db.sql("select coalesce(max(price),0) as price from `tabTour Package Prices` where parent='{}' and number_of_person = {}".format(self.tour_package,self.adult or 1), as_dict=1)
	if data[0]["price"]>0:
		return data[0]["price"]
	price = frappe.db.get_value("Tour Packages",self.tour_package, "price")
	return price  

def get_room_rate(hotel_name, room_type):
	data = frappe.db.sql("select coalesce(max(room_rate),0) as rate from `tabTour Hotel Room Type` where parent='{}' and room_type = '{}'".format(hotel_name, room_type), as_dict=1)
	if data:
		return data[0]["rate"]
	return 0
