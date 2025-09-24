# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
import functools
import re
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt
from pypika.terms import ExistsCriterion
value_fields = (
	"opening_debit",
	"opening_credit",
	"debit",
	"credit",
	"closing_debit",
	"closing_credit",
)

def get_report_summary(data):
	opening_debit, opening_credit, debit,credit,closing_debit,closing_credit = [],[],[],[],[],[]
	opening_debit.append(sum([d.get("opening_debit",0) for d in data if d.get("account","") == "Total"]))
	opening_credit.append(sum([d.get("opening_credit",0) for d in data if d.get("account","") == "Total"]))
	debit.append(sum([d.get("debit",0) for d in data  if d.get("account","") == "Total"]))
	credit.append(sum([d.get("credit",0) for d in data  if d.get("account","") == "Total"]))
	closing_debit.append(sum([d.get("closing_debit",0) for d in data if d.get("account","") == "Total"]))
	closing_credit.append(sum([d.get("closing_credit",0) for d in data if d.get("account","") == "Total"]))
	return [
		{"value": opening_debit, "label": _("Opening Debit"), "datatype": "Currency"},
		{"value": opening_credit, "label": _("Opening Credit"), "datatype": "Currency"},
		{"value": debit, "label": _("Debit"), "datatype": "Currency"},
		{"value": credit, "label": _("Credit"), "datatype": "Currency"},
		{"value": closing_debit, "label": _("Closing Debit"), "datatype": "Currency"},
		{"value": closing_credit, "label": _("Opening Credit"), "datatype": "Currency"},
	]

def get_report_chart(data):
	opening_debit, opening_credit, debit,credit,closing_debit,closing_credit = [],[],[],[],[],[]

	opening_debit.append(sum([d.get("opening_debit",0) for d in data if d.get("account","") == "Total"]))
	opening_credit.append(sum([d.get("opening_credit",0) for d in data if d.get("account","") == "Total"]))
	debit.append(sum([d.get("debit",0) for d in data  if d.get("account","") == "Total"]))
	credit.append(sum([d.get("credit",0) for d in data  if d.get("account","") == "Total"]))
	closing_debit.append(sum([d.get("closing_debit",0) for d in data if d.get("account","") == "Total"]))
	closing_credit.append(sum([d.get("closing_credit",0) for d in data if d.get("account","") == "Total"]))
	
	datasets = []
	datasets.append({"name": _("Opening Debit"), "values": opening_debit})
	datasets.append({"name": _("Opening Credit"), "values": opening_credit})
	datasets.append({"name": _("Debit"), "values": debit})
	datasets.append({"name": _("Credit"), "values": credit})
	datasets.append({"name": _("Closing Debit"), "values": closing_debit})
	datasets.append({"name": _("Closing Credit"), "values": closing_credit})

	chart = {"data": {"labels": ["Balances"], "datasets": datasets}}
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
			gl_entry.debit_amount if not group_by_account else Sum(gl_entry.debit_amount).as_("debit"),
			gl_entry.credit_amount if not group_by_account else Sum(gl_entry.credit_amount).as_("credit")
		)
	)
	query = query.select(gl_entry.posting_date)
	query = query.where(gl_entry.is_cancelled == 0)
	query = query.where(gl_entry.posting_date >= from_date)
	query = query.where(gl_entry.posting_date <= to_date)
	if filters.business_branch:
		query = query.where(gl_entry.business_branch == filters.business_branch)
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
		if show_zero_values or d.get("has_value"):
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
			if a.root_type != b.root_type and a.root_type == "Asset":
				return -1
			if a.root_type == "Liability" and b.root_type == "Equity":
				return -1
			if a.root_type == "Income" and b.root_type == "Expense":
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
		accounts_by_name[d.name] = d
		parent_children_map.setdefault(d.parent_chart_of_account or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			sort_accounts(children, is_root=True if parent is None else False)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	report_chart = get_report_chart(data)
	report_summary = get_report_summary(data)
	return columns, data,None,report_chart,report_summary

def validate_dates(from_date, to_date):
	if not from_date or not to_date:
		frappe.throw("From Date and To Date are mandatory")
	if from_date > to_date:
		frappe.throw(_("To Date cannot be less than From Date"))

def get_data(filters):
	validate_dates(filters.from_date,filters.to_date)
	accounts = frappe.db.sql("""select name, account_code, parent_chart_of_account, account_name, root_type, is_group, lft, rgt from `tabChart Of Account` order by lft""",as_dict=True)
	if not accounts:
		return None
	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
	gl_entries_by_account = {}
	opening_balances = get_opening_balances(filters)
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
		gl_entries_by_account,
		opening_balances,
		filters.get("show_net_values")
	)
	accumulate_values_into_parents(accounts, accounts_by_name)
	data = prepare_data(accounts, filters, parent_children_map)
	data = filter_out_zero_value_rows(
		data, parent_children_map, show_zero_values=filters.get("show_zero_values")
	)
	return data


def get_opening_balances(filters):
	balance_sheet_opening = get_rootwise_opening_balances(filters)
	pl_opening = get_rootwise_opening_balances(filters)

	balance_sheet_opening.update(pl_opening)
	return balance_sheet_opening


def get_rootwise_opening_balances(filters):
	gle = get_opening_balance("General Ledger", filters)
	opening = frappe._dict()
	for d in gle:
		opening.setdefault(
			d.account,
			{
				"account": d.account,
				"opening_debit": 0.0,
				"opening_credit": 0.0,
			},
		)
		opening[d.account]["opening_debit"] += flt(d.debit_amount)
		opening[d.account]["opening_credit"] += flt(d.credit_amount)

	return opening


def get_opening_balance(
	doctype,
	filters,
	start_date=None
):
	closing_balance = frappe.qb.DocType(doctype)
	opening_balance = (
		frappe.qb.from_(closing_balance)
		.select(
			closing_balance.account,
			Sum(closing_balance.debit_amount).as_("debit_amount"),
			Sum(closing_balance.credit_amount).as_("credit_amount"),
		).groupby(closing_balance.account)
	)
	if start_date:
		opening_balance = opening_balance.where(
			(closing_balance.posting_date >= start_date)
			& (closing_balance.posting_date < filters.from_date)
		)
	else:
		opening_balance = opening_balance.where(closing_balance.posting_date < filters.from_date)
	if filters.business_branch:
		opening_balance = opening_balance.where(closing_balance.business_branch == filters.business_branch)
	if doctype == "General Ledger":
		opening_balance = opening_balance.where(closing_balance.is_cancelled == 0)
	gle = opening_balance.run(as_dict=1)
	return gle


def calculate_values(accounts,gl_entries_by_account, opening_balances, show_net_values):
	init = {
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"debit": 0.0,
		"credit": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0,
	}

	for d in accounts:
		d.update(init.copy())
		d["opening_debit"] = opening_balances.get(d.name, {}).get("opening_debit", 0)
		d["opening_credit"] = opening_balances.get(d.name, {}).get("opening_credit", 0)

		for entry in gl_entries_by_account.get(d.name, []):
			d["debit"] += flt(entry.debit)
			d["credit"] += flt(entry.credit)

		d["closing_debit"] = d["opening_debit"] + d["debit"]
		d["closing_credit"] = d["opening_credit"] + d["credit"]

		if show_net_values:
			prepare_opening_closing(d)


def calculate_total_row(accounts):
	total_row = {
		"account":"Total",
		"account_name":"Total",
		"warn_if_negative": True,
		"opening_debit": 0.0,
		"opening_credit": 0.0,
		"debit": 0.0,
		"credit": 0.0,
		"closing_debit": 0.0,
		"closing_credit": 0.0,
		"parent_chart_of_account": None,
		"indent": 0,
		"has_value": True
	}

	for d in accounts:
		if not d.parent_chart_of_account:
			for field in value_fields:
				total_row[field] += d[field]

	return total_row


def accumulate_values_into_parents(accounts, accounts_by_name):
	for d in reversed(accounts):
		if d.parent_chart_of_account:
			for key in value_fields:
				accounts_by_name[d.parent_chart_of_account][key] += d[key]


def prepare_data(accounts, filters, parent_children_map):
	data = []

	for d in accounts:
		# Prepare opening closing for group account
		if parent_children_map.get(d.account) and filters.get("show_net_values"):
			prepare_opening_closing(d)

		has_value = False
		row = {
			"account": d.name,
			"parent_chart_of_account": d.parent_chart_of_account,
			"indent": d.indent,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"is_group_account": d.is_group,
			"acc_name": d.account_name,
			"acc_number": d.account_code,
			"account_name": (
				f"{d.account_code} - {d.account_name}" if d.account_code else d.account_name
			),
		}

		for key in value_fields:
			row[key] = flt(d.get(key, 0.0), 3)

			if abs(row[key]) >= 0.005:
				# ignore zero values
				has_value = True

		row["has_value"] = has_value
		data.append(row)

	total_row = calculate_total_row(accounts)

	if not filters.get("show_group_accounts"):
		data = hide_group_accounts(data)

	data.extend([{}, total_row])

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
			"fieldname": "opening_debit",
			"label": _("Opening (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"fieldname": "opening_credit",
			"label": _("Opening (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"fieldname": "closing_debit",
			"label": _("Closing (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"fieldname": "closing_credit",
			"label": _("Closing (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
	]


def prepare_opening_closing(row):
	dr_or_cr = "debit" if row["root_type"] in ["Asset", "Equity", "Expense"] else "credit"
	reverse_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"

	for col_type in ["opening", "closing"]:
		valid_col = col_type + "_" + dr_or_cr
		reverse_col = col_type + "_" + reverse_dr_or_cr
		row[valid_col] -= row[reverse_col]
		if row[valid_col] < 0:
			row[reverse_col] = abs(row[valid_col])
			row[valid_col] = 0.0
		else:
			row[reverse_col] = 0.0


def hide_group_accounts(data):
	non_group_accounts_data = []
	for d in data:
		if not d.get("is_group_account"):
			d.update(indent=0)
			non_group_accounts_data.append(d)
	return non_group_accounts_data
