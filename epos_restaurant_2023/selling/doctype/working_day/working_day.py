# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.naming import NamingSeries
from frappe.utils.print_format import download_pdf
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class WorkingDay(Document):
    
	def validate(self):
		if self.flags.ignore_validate == True:
			return
		
		pos_profile = frappe.get_doc("POS Profile", self.pos_profile)	 

		if self.is_new():
			if pos_profile.business_branch != self.business_branch:
				frappe.throw("Invalid POS Profile configuration")

			
			if frappe.db.exists('Working Day', {'business_branch': self.business_branch, 'is_closed': 0}):
				frappe.throw("Working day is already opened")
		
		# validate close working day only from edoor night audit process only
		# check if have edoor app install 
  
		if 'edoor' in frappe.get_installed_apps():
			if self.pos_profile !="eDoor Profile"  :
				frappe.throw("Your are not allow to close working from POS Station. Please ask your night auditor to run night audit.")
      
		if not self.created_by:
			user = frappe.get_doc("User", self.owner)
			self.created_by = user.full_name

	

		
		#if close shift check current bill open 
		if self.is_closed==1:
			if not self.close_pos_profile:
				self.close_pos_profile = self.pos_profile
			if 'edoor' in frappe.get_installed_apps():
				if self.close_pos_profile !="eDoor Profile"  :
					frappe.throw("Your are not allow to close working from POS Station. Please ask your night auditor to run night audit.")
			user = frappe.get_doc("User", self.modified_by)
			self.closed_by = user.full_name
			if not self.closed_date:
				self.closed_date =  frappe.utils.now()
			# validate cashier shift open 
			pending_cashier_shift = frappe.db.sql("select name from `tabCashier Shift` where is_closed  = 0 and working_day = '{}'".format(self.name), as_dict=1)
			if pending_cashier_shift:
				frappe.throw("Please close cashier shift first.")
			#Validate Allow Closed Working Day when when has bill
			pos_config = frappe.db.get_value('POS Profile', self.pos_profile, 'pos_config')
			allow_closed_working_day_when_has_pending_order = frappe.db.get_value('POS Config', pos_config, 'allow_closed_working_day_when_has_pending_order')
			if allow_closed_working_day_when_has_pending_order == 0:
				pending_orders = frappe.db.sql("select name from `tabSale` where docstatus = 0 and working_day = '{}'".format(self.name), as_dict=1)
				if pending_orders:
					frappe.throw("Please close all pending order before closing working day.")

			#check reset waiting number
			
			if pos_profile.reset_waiting_number_after=="Close Working Day":
				prefix = pos_profile.waiting_number_prefix.replace('.','').replace("#",'')
				naming_series = NamingSeries(prefix)
				naming_series.update_counter(0)
			# self.send_mail_closed_day()


		# validte coupon shift opened then foce to close coupon shift first
		# for business sell coupon
		if self.is_closed == 1:
			if frappe.db.exists("Coupon Shift", {"is_closed":0}):
				frappe.throw(_("Please close all pending coupon shift before closing working day."))


	def on_update(self):
		if 'edoor' in frappe.get_installed_apps():
			if self.pos_profile !="eDoor Profile":
				frappe.throw("Your are not allow to close working from POS Station. Please ask your night auditor to run night audit.")
		frappe.clear_document_cache("Working Day",self.name)

		# this validatation is use for ecoupon when we close working day all coupon must be mark as expired imediatly
		if self.has_value_changed("is_closed"):
			if self.is_closed == 1:
				from epos_restaurant_2023.api.qb.controller import add_quickbooks_sync_queue
				add_quickbooks_sync_queue(self.name,"Working Day",self.posting_date)
				sql = "update `tabCoupon Codes` set coupon_status ='Expired' where coupon_status ='Used' and working_day = %(working_day)s"
				frappe.db.sql(sql,{"working_day":self.name})

				# submit coupon use balance to gl entry
				submit_Gl_Entry(self)

				site_config = frappe.get_site_config()
				if site_config.get("supabase_api_url"):
					frappe.enqueue("epos_restaurant_2023.api.supabase.delete_coupon_code_data", queue='short')

			
  


def get_unuse_coupon_balance(self):
	sql = "select sum(coupon_amount) as balance, sum(actual_amount) as actual_balance from `tabCoupon Transaction` where working_day = %(working_day)s and coalesce(status,'') <> 'Deleted' and reference_doctype <> 'Coupon Issue'"
	data = frappe.db.sql(sql, {"working_day":self.name},as_dict = 1)
	
	
	if data:
		return data[0]["balance"] or 0
	return 0

def submit_Gl_Entry(self):
	from epos_restaurant_2023.utils import math_round
	balance = math_round(abs(get_unuse_coupon_balance(self)))
	if balance> 0:
		from_account,to_account = frappe.get_cached_value("Business Branch",self.business_branch,["default_unearned_revenue_account","default_unused_coupon_account"])
		docs = []
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":from_account,
			"debit_amount": balance,
			"againt":to_account,
			"voucher_type":"Working Day",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark" : "Transfer unused amount from unearned to " + to_account,

		}
		docs.append(doc)
	
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":to_account,
			"credit_amount": balance,
			"againt": from_account,
			"voucher_type":"Working Day",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark" : "Revenue from use use coupon balance"
			}
		docs.append(doc)
		submit_general_ledger_entry(docs=docs)
  
 