# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt
import shutil
import frappe
from frappe import utils
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import getdate

class Expense(Document):
	def validate(self):
		frappe_path = frappe.utils.get_bench_path()
    	shutil.copy2(frappe_path + '/' + 'apps/epos_restaurant_2023/epos_restaurant_2023/print_template/print_grid.html', frappe_path + '/' + 'apps/frappe/frappe/public/js/frappe/views/reports/print_grid.html')
		#validate expense dsate
		if getdate(self.posting_date)>getdate(utils.today()):
			frappe.throw(_("Expense date cannot greater than current date"))

		#validate amount
		total_amount = 0
		total_quantity = 0
		for d in self.expense_items:
			d.amount = d.price * d.quantity
			total_quantity = total_quantity + d.quantity
			total_amount = total_amount + d.amount

		self.total_quantity = total_quantity
		self.total_amount = total_amount

		self.balance = self.total_amount
  


	


		
