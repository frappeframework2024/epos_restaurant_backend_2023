import frappe
from py_linq import Enumerable
from datetime import datetime
from frappe.utils import date_diff,today ,add_months, add_days,getdate,add_to_date
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import base64

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


@frappe.whitelist(methods="POST")
def change_language(user,lang):
    frappe.db.set_value("User",user,"language",lang)
    return "Done"


def math_round(value, precision = None):
	import math
	if not precision:
		precision = int( frappe.get_cached_value("System Settings", None, "currency_precision") or 0)
	result = math.floor(((value or 0) * math.pow(10, (precision or 0) )) + 0.5) / math.pow(10, (precision or 0))
	return result



def encrypt_aes_base64(plain_text: str, key: str = None, iv: str = None) -> str:
    site_config = frappe.get_site_config()
    
    if not key:
        key = site_config.get("encrypt_key")
    if not iv:
        iv = site_config.get("encrypt_iv")

    # convert key and iv from str -> bytes
    key_bytes = key.encode("utf-8")
    iv_bytes = iv.encode("utf-8")
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    ct_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(ct_bytes).decode("utf-8")

def decrypt_aes_base64(cipher_text: str, key: str = None, iv: str = None) -> str:

 
    site_config = frappe.get_site_config()
    if not key:
        key = site_config.get("encrypt_key")
    if not iv:
        iv = site_config.get("encrypt_iv")
    
    key_bytes = key.encode("utf-8")
    iv_bytes = iv.encode("utf-8")

 
    
    # Clean ciphertext
    cipher_text = cipher_text.strip().replace("\n", "")
    # Base64 decode
    ct_bytes = base64.b64decode(cipher_text)

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    decrypted_padded = cipher.decrypt(ct_bytes) 
    # Unpad
    decrypted = unpad(decrypted_padded, AES.block_size)
    return decrypted.decode("utf-8")


def run_me():
     print("u run me")
     


def get_lastweek_to_currentweek():
    from datetime import datetime, timedelta
    start_date = datetime.strptime( frappe.utils.today(), "%Y-%m-%d")
 
    weekday = start_date.weekday()   
    last_week_start = start_date - timedelta(days=weekday + 7)
 
    current_week_end = start_date + timedelta(days=(6 - weekday))

    return frappe.utils.getdate(last_week_start.date()), frappe.utils.getdate(current_week_end.date())



@frappe.whitelist()
def run_backup_command():
    import os, shutil
    import shlex, subprocess
    from frappe.utils import cstr
    """Run site backup and clean old backups (blocking)"""
    site_name = cstr(frappe.local.site)
    folder = frappe.utils.get_site_path(frappe.conf.get("backup_path", "private/backups"))

    # Clean old backup files
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            frappe.log_error(f"Failed to delete {file_path}: {e}")

    # Build and run the bench backup command (synchronously)
    command = f"bench --site {site_name} backup --include 'Coupon Transaction'"
    command = shlex.split(command)

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        frappe.log_error(
            title="Backup Failed",
            message=f"Command: {command}\n\nSTDERR:\n{result.stderr}"
        )
        raise Exception("Backup failed! Check logs.")

    frappe.logger().info(result.stdout)
    return "Backup completed successfully."