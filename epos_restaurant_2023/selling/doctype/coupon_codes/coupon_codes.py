# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import datetime
from frappe.utils import get_datetime
import os, shutil
import shlex, subprocess
from frappe.utils import cstr
class CouponCodes(Document):
	def validate(self):
		# validate coupon exist with status Unused
		if self.coupon:
		 
			if self.is_new():

				if frappe.db.exists("Coupon Codes",{"coupon":self.coupon,"coupon_status":["in",["Unused","Used"]]}):
					frappe.throw(_("Coupon {} code already exist").format(self.coupon))
			else:
				if frappe.db.exists("Coupon Codes",{"coupon":self.coupon,"coupon_status":["in",["Unused","Used"]],"name":["!=",self.name]}):
					frappe.throw(_("Coupon {} code already exist").format(self.coupon))

	def on_trash(self):
		if frappe.db.exists("Coupon Transaction",{"coupon_code":self.name}):
			frappe.throw(_("Cannot delete coupon code as it has transactions"))

		frappe.msgprint(_("Delete coupon code successfully"))

@frappe.whitelist()
def check_coupon_code(coupon):
	if not coupon:
		frappe.throw(_("Please scan the QR code of the coupon"))
	data = frappe.db.sql("select name, coupon,coupon_status,expired_date from `tabCoupon Codes` where coupon = %(coupon)s order by creation desc limit 1",{"coupon":coupon},as_dict=1)
	if not data:
		frappe.throw(_("This coupon is not exist in the system"))
	 
	if data[0].get("coupon_status") == "Redeemed":
		frappe.throw(_("Coupon code is already redeem"))

	if data[0].get("coupon_status") == "Expired":
		frappe.throw(_("This coupon code is already expired"))
	if data[0].get("coupon_status") == "Used":
		if datetime.datetime.now() > get_datetime(data[0].expired_date):
			frappe.throw(_("This coupon code is expired"))   

		frappe.throw(_("Coupon code is already used"))
	
	if data[0].get("coupon_status") == "Redeemed":
		frappe.throw(_("Coupon code is already redeem"))


	if data[0].get("coupon_register"):
		if frappe.get_cached_value("Coupon Register",data[0].get("coupon_register"),"docstatus") == 0:
			frappe.throw(_("This coupon status is <strong>Pending</strong>. Please submit your coupont register number {}".format(data[0].get("coupon_register"))))
	

	
	
	

	return data[0]

@frappe.whitelist()
def get_coupon_info(coupon):
	coupon_codes = frappe.db.sql("select name,coupon,creation,owner,coupon_status,sale_date from `tabCoupon Codes` where coupon = %(coupon)s",{"coupon":coupon},as_dict=1)

	if not coupon_codes:
		frappe.throw(_("Coupon code not found"))
		
	sql="""
		select 
			coupon_code,
			ct.coupon_number,
			ct.posting_date,
			ct.sale,
			ct.transaction_type,
			ct.customer,
			ct.customer_name,
			ct.actual_amount,
			ct.coupon_amount,
			ct.input_actual_amount,
			ct.currency,
			ct.exchange_rate


		from `tabCoupon Transaction` ct
		where
			ct.coupon_code in %(coupon_codes)s and 
			coalesce(ct.status,'') <> 'Deleted'
		order by
			ct.posting_date,
			ct.creation
	"""
	coupon_transactions = frappe.db.sql(sql,{"coupon_codes":[d.get("name") for d in coupon_codes]},as_dict=1)


	return {
		"coupon_number":coupon,
		"coupon_info":coupon_codes,
		"coupon_transactions":coupon_transactions
	}

@frappe.whitelist()
def move_to_history():
	from frappe.model.document import bulk_insert
	from datetime import datetime, timedelta
	run_backup_command()
	setting = frappe.get_doc("ePOS Settings")
	cutoff_date = datetime.now() - timedelta(days=(setting.clear_coupon_clear_days or 14))
	codes = frappe.db.get_list('Coupon Codes',filters={'moved_to_history':0,'coupon_status':['!=','Unused']},fields=['*'],as_list=False)
	clear_codes = frappe.db.get_list('Coupon Codes',filters={ 'creation': ['<', cutoff_date],'coupon_status':['!=','Unused']},fields=['name'],as_list=False)
	try:
		if codes:
			bulk_insert("Coupon Codes History", convert_to_history(codes) , chunk_size=10000)
			frappe.db.sql("update `tabCoupon Codes` set moved_to_history = 1 where name in %(names)s",{'names':[a.name for a in codes]})
		if clear_codes:
			frappe.db.delete("Coupon Codes",filters={"name": ["in", [a.name for a in clear_codes]]})
		frappe.db.commit()
		msg = "Moved {0} rows to history".format(len(codes)) if len(codes)>0 else "All rows have already been moved to history"
		return msg
	except Exception as e:
		frappe.db.rollback()

def convert_to_history(transactions):
	for a in transactions:
		a.doctype = "Coupon Codes History"
		doc = frappe.get_doc(a)
		yield doc
	
@frappe.whitelist()
def run_backup_command():
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
    command = f"bench --site {site_name} backup --include 'Coupon Codes'"
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