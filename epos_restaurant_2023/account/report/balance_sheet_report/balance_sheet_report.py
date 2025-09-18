# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
import functools
import re
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt
from pypika.terms import ExistsCriterion
value_fields = [
	"amount"
]

def get_report_summary(data):
	total_profits,total_assets,total_liabilities= [],[],[]
	profits = (sum([d.get("amount",0) for d in data if d.get("account_name","") == "profit"]))
	assets = (sum([d.get("amount",0) for d in data if d.get("account_name","") == "total_assets"]))
	liabilities = (sum([d.get("amount",0) for d in data if d.get("account_name","") == "total_liabilities"]))
	total_profits.append(profits)
	total_assets.append(assets)
	total_liabilities.append(liabilities)
	return [
		{"value": total_profits, "label": _("Provisional Profit / Loss"), "datatype": "Currency"},
		{"value": total_assets, "label": _("Total Asset"), "datatype": "Currency"},
		{"value": total_liabilities, "label": _("Total Liabilities"), "datatype": "Currency"},
	]

def get_report_chart(data):
	total_profits,total_assets,total_liabilities= [],[],[]
	profits = (sum([d.get("amount",0) for d in data if d.get("account_name","") == "profit"]))
	assets = (sum([d.get("amount",0) for d in data if d.get("account_name","") == "total_assets"]))
	liabilities = (sum([d.get("amount",0) for d in data if d.get("account_name","") == "total_liabilities"]))
	total_profits.append(profits)
	total_assets.append(assets)
	total_liabilities.append(liabilities)
	
	datasets = []
	datasets.append({"name": _("Provisional Profit / Loss"), "values": total_profits})
	datasets.append({"name": _("Assets"), "values": total_assets})
	datasets.append({"name": _("Liabilities"), "values": total_liabilities})

	chart = {"data": {"labels": ["Amount"], "datasets": datasets}}
	chart["type"] = "bar"
	chart["fieldtype"] = "Currency"
	return chart

def get_account_filter_query(root_lft, root_rgt, root_type, gl_entry):
	acc = frappe.qb.DocType("Chart Of Account")
	exists_query = (
		frappe.qb.from_(acc).select(acc.name).where(acc.name == gl_entry.account).where(acc.is_group == 0)
	)
	if root_lft and root_rgt:
		exists_query = exists_query.where(acc.lft >= root_lft).where(acc.rgt <= root_rgt)

	if root_type:
		exists_query = exists_query.where(acc.root_type == root_type)

	return exists_query

def get_accounting_entries(
	doctype,
	from_date,
	to_date,
	filters,
	root_lft=None,
	root_rgt=None,
	root_type=None,
	group_by_account=False,
):
	gl_entry = frappe.qb.DocType(doctype)
	query = (
		frappe.qb.from_(gl_entry)
		.select(
			gl_entry.account,
			(gl_entry.debit_amount - gl_entry.credit_amount) if not group_by_account else Sum(gl_entry.debit_amount - gl_entry.credit_amount).as_("amount"),
		)
	)
	query = query.select(gl_entry.posting_date)
	query = query.where(gl_entry.is_cancelled == 0)
	query = query.where(gl_entry.posting_date >= from_date)
	query = query.where(gl_entry.posting_date <= to_date)
	if filters.outlet:
		query = query.where(gl_entry.outlet == filters.outlet)
	if (root_lft and root_rgt) or root_type:
		account_filter_query = get_account_filter_query(root_lft, root_rgt, root_type, gl_entry)
		query = query.where(ExistsCriterion(account_filter_query))

	from frappe.desk.reportview import build_match_conditions

	query, params = query.walk()
	match_conditions = build_match_conditions(doctype)

	if match_conditions:
		query += "and" + match_conditions

	if group_by_account:
		query += " GROUP BY `account`"
	return frappe.db.sql(query, params, as_dict=True)


def set_gl_entries_by_account(
	from_date,
	to_date,
	filters,
	gl_entries_by_account,
	root_lft=None,
	root_rgt=None,
	root_type=None,
	group_by_account=False,
):
	"""Returns a dict like { "account": [gl entries], ... }"""
	gl_entries = []
	gl_entries += get_accounting_entries(
		"General Ledger",
		from_date,
		to_date,
		filters,
		root_lft,
		root_rgt,
		root_type,
		group_by_account=group_by_account,
	)
	for entry in gl_entries:
		gl_entries_by_account.setdefault(entry.account, []).append(entry)
	return gl_entries_by_account

def filter_out_zero_value_rows(data, parent_children_map, show_zero_values=False):
	data_with_value = []
	for d in data:
		if show_zero_values or d.get("has_value") or d.get("account") in ["Total Asset","Total Liabilities",""]:
			data_with_value.append(d)
		else:
			# show group with zero balance, if there are balances against child
			children = [child.name for child in parent_children_map.get(d.get("account")) or []]
			if children:
				for row in data:
					if row.get("account") in children and row.get("has_value"):
						data_with_value.append(d)
						break

	return data_with_value

def sort_accounts(accounts, is_root=False, key="name"):
	"""Sort root types as Asset, Liability, Equity, Income, Expense"""

	def compare_accounts(a, b):
		if re.split(r"\W+", a[key])[0].isdigit():
			# if Chart Of Account is numbered, then sort by number
			return int(a[key] > b[key]) - int(a[key] < b[key])
		elif is_root:
			if a.get("root_type") != b.get("root_type") and a.get("root_type") == "Asset":
				return -1
			if a.get("root_type") == "Liability" and b.root_type == "Equity":
				return -1
			if a.get("oot_type") == "Income" and b.root_type == "Expense":
				return -1
		else:
			# sort by key (number) or name
			return int(a[key] > b[key]) - int(a[key] < b[key])
		return 1

	accounts.sort(key=functools.cmp_to_key(compare_accounts))

def filter_accounts(accounts, depth=20):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.get("name")] = d
		parent_children_map.setdefault(d.get("parent_chart_of_account") or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			sort_accounts(children, is_root=True if parent is None else False)

			for child in children:
				child["indent"] = level
				filtered_accounts.append(child)
				add_to_list(child.get("name"), level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	report_summary = get_report_summary(data)
	report_chart = get_report_chart(data)
	return columns, data,None,report_chart,report_summary

def get_data(filters):
	accounts = frappe.db.sql("""select 
						  name, 
						  account_code, 
						  parent_chart_of_account, 
						  account_name, 
						  root_type, 
						  is_group, 
						  lft, 
						  rgt 
						  from `tabChart Of Account` 
						  where root_type in ('Asset','Liabilities','Equity') order by lft""",as_dict=True)
	accounts.append({"name":"Total Asset","account_code":"","parent_chart_of_account":None,"account_name":"total_asset","root_type":"Asset","is_group":1,"lft":0,"rgt":0})
	accounts.append({"name":"","account_code":"","parent_chart_of_account":None,"account_name":"","root_type":"Asset","is_group":1,"lft":0,"rgt":0})
	accounts.append({"name":"Total Liabilities","account_code":"","parent_chart_of_account":None,"account_name":"total_liabilities","root_type":"Liabilities","is_group":1,"lft":0,"rgt":0})
	accounts.append({"name":"","account_code":"","parent_chart_of_account":None,"account_name":"","root_type":"Liabilities","is_group":1,"lft":0,"rgt":0})
	if not accounts:
		return None
	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
	gl_entries_by_account = {}
	set_gl_entries_by_account(
		filters.from_date,
		filters.to_date,
		filters,
		gl_entries_by_account,
		root_lft=None,
		root_rgt=None,
		group_by_account=True,
	)
	calculate_values(
		accounts,
		gl_entries_by_account
	)
	accumulate_values_into_parents(accounts, accounts_by_name)
	data = prepare_data(accounts, filters, parent_children_map)
	data = filter_out_zero_value_rows(
		data, parent_children_map, show_zero_values=filters.get("show_zero_values")
	)
	return data

def calculate_values(accounts,gl_entries_by_account):
	init = {
		"amount": 0.0,
	}
	for d in accounts:
		d.update(init.copy())
		for entry in gl_entries_by_account.get(d.get("name"), []):
			d["amount"] += flt(entry.amount)
	for d in accounts:
		d["amount"] = d["amount"]*-1 if (d.get("root_type") == "Liabilities") else d["amount"]

def calculate_total_row(accounts):
	total_row = []
	row1 = {
		"account":"Provisional Profit / Loss (Credit)",
		"account_name": "profit",
		"warn_if_negative": True,
		"amount": 0.0,
		"parent_chart_of_account": None,
		"indent": 0,
		"has_value": True
	}
	assets = (sum([d.get("amount",0) for d in accounts if d.get("account_name","") != "Total" and not d.get("parent_chart_of_account") and d.get("root_type") == "Asset"]))
	liabilities = (sum([d.get("amount",0) for d in accounts if d.get("account_name","") != "Total" and not d.get("parent_chart_of_account") and d.get("root_type") == "Liabilities"]))
	for field in value_fields:
		row1[field] = (assets-liabilities)
	total_row.append(row1)
	return total_row,assets,liabilities

def accumulate_values_into_parents(accounts, accounts_by_name):
	for d in reversed(accounts):
		if d.get("parent_chart_of_account"):
			for key in value_fields:
				accounts_by_name[d.get("parent_chart_of_account")][key] += d[key]


def prepare_data(accounts, filters, parent_children_map):
	data = []
	for d in accounts:
		has_value = False
		row = {
			"account": d.get("name"),
			"parent_chart_of_account": d.get("parent_chart_of_account"),
			"indent": d.get("indent"),
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"is_group_account": d.get("is_group"),
			"acc_name": d.get("account_name"),
			"acc_number": d.get("account_code"),
			"account_name": (
				d.get("account_code")+"-"+d.get("account_name") if d.get("account_code") else d.get("account_name")
			),
			"root_type":d.get("root_type")
		}

		for key in value_fields:
			row[key] = flt(d.get(key, 0.0), 3)

			if abs(row[key]) >= 0.005:
				# ignore zero values
				has_value = True

		row["has_value"] = has_value
		data.append(row)

	total_row,assets,liabilities = calculate_total_row(accounts)
	if not filters.get("show_group_accounts"):
		data = hide_group_accounts(data)
	data.extend(total_row)
	for a in data:
		if a.get("account") == "Total Asset":
			a["amount"] = assets
		if a.get("account") == "Total Liabilities":
			a["amount"] = liabilities
	return data


def get_columns():
	return [
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Chart Of Account",
			"width": 300,
		},
		{
			"fieldname": "acc_name",
			"label": _("Account Name"),
			"fieldtype": "Data",
			"hidden": 1,
			"width": 250,
		},
		{
			"fieldname": "root_type",
			"label": _("Root Type"),
			"fieldtype": "Data",
			"hidden": 1,
			"width": 250,
		},
		{
			"fieldname": "acc_number",
			"label": _("Account Number"),
			"fieldtype": "Data",
			"hidden": 1,
			"width": 120,
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1,
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
	]

def hide_group_accounts(data):
	non_group_accounts_data = []
	for d in data:
		if not d.get("is_group_account"):
			d.update(indent=0)
			non_group_accounts_data.append(d)
	return non_group_accounts_data
