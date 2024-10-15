# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from collections import OrderedDict
from frappe.utils import cstr, getdate
TRANSLATIONS = frappe._dict()

def execute(filters=None):
	update_translations()
	return get_columns(filters), get_data(filters)


def update_translations():
	TRANSLATIONS.update(
		dict(OPENING=_("Opening"), TOTAL=_("Total"), CLOSING_TOTAL=_("Closing (Opening + Total)"))
	)

def get_account_type_map(company):
	account_type_map = frappe._dict(
		frappe.get_all(
			"Account", fields=["name", "account_type"], filters={"company": company}, as_list=1
		)
	)

	return account_type_map

def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []
	consolidated_gle = OrderedDict()
	group_by = filters.group_by

	def update_value_in_dict(data, key, gle):
		data[key].debit_amount += gle.debit_amount
		data[key].credit_amount += gle.credit_amount
		if data[key].against_voucher and gle.against_voucher:
			data[key].against_voucher += ", " + gle.against_voucher

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	show_opening_entries = 1

	for gle in gl_entries:
		group_by_value = gle.get(group_by)

		if gle.posting_date < from_date or (cstr(gle.is_opening) == "Yes" and not show_opening_entries):
			update_value_in_dict(gle_map[group_by_value].totals, "opening", gle)
			update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)
			update_value_in_dict(totals, "opening", gle)
			update_value_in_dict(totals, "closing", gle)

		elif gle.posting_date <= to_date or (cstr(gle.is_opening) == "Yes" and show_opening_entries):
			update_value_in_dict(gle_map[group_by_value].totals, "total", gle)
			update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)
			update_value_in_dict(totals, "total", gle)
			update_value_in_dict(totals, "closing", gle)
			gle_map[group_by_value].entries.append(gle)

	for key, value in consolidated_gle.items():
		update_value_in_dict(totals, "total", value)
		update_value_in_dict(totals, "closing", value)
		entries.append(value)

	return totals, entries

def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			account="'{0}'".format(label),
			debit_amount=0.0,
			credit_amount=0.0
		)

	return _dict(
		opening=_get_debit_credit_dict(TRANSLATIONS.OPENING),
		total=_get_debit_credit_dict(TRANSLATIONS.TOTAL),
		closing=_get_debit_credit_dict(TRANSLATIONS.CLOSING_TOTAL),
	)

def initialize_gle_map(gl_entries, filters):
	gle_map = OrderedDict()
	group_by = filters.group_by
	
	for gle in gl_entries:
		gle_map.setdefault(gle.get(group_by), _dict(totals=get_totals_dict(), entries=[]))
	return gle_map

def get_data_with_opening_closing(filters, gl_entries):
	data = []
	gle_map = initialize_gle_map(gl_entries, filters)
	totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)
	if filters.group_by:
		for acc, acc_dict in gle_map.items():
			if acc_dict.entries:
				# if filters.group_by != "voucher_number":
				# 	data.append(acc_dict.totals.opening)
				data += acc_dict.entries
				data.append(acc_dict.totals.total)
				# if filters.group_by != "voucher_number":
				# 	data.append(acc_dict.totals.closing)
			data.append({})
		data.append(totals.total)
	else:
		for acc, acc_dict in gle_map.items():
			if acc_dict.entries:
				data += acc_dict.entries
		data.append(totals.total)
	# data.append(totals.closing)
	return data


def get_result_as_list(data):
	balance = 0
	for d in data:
		if not d.get("posting_date"):
			balance = 0
		balance = get_balance(d, balance)
		d["balance"] = balance
	return data

def get_balance(row, balance):
	balance += row.get("debit_amount", 0) - row.get("credit_amount", 0)
	return balance

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data

def get_data(filters):
	order_by_statement = "order by posting_date, creation, account"
	if filters.get("group_by") == "Group by Voucher":
		order_by_statement = "order by posting_date, debit_amount desc, voucher_type, voucher_no"
	if filters.get("group_by") == "Group by Account":
		order_by_statement = "order by account, posting_date, creation"
	filter  = ""
	if filters.group_by == "party":
		filter += "and coalesce(party,'') <> ''"
	if filters.account:
		filter += " and account in ({0})".format(get_list(filters,"account"))
	if filters.party:
		filter += " and party in ({0})".format(get_list(filters,"party"))
	if filters.voucher_no:
		filter += " and voucher_number like '%{0}%'".format(filters.voucher_no)
	sql = """
			select
			posting_date,
			voucher_number,
			voucher_type,
			account,
			party_type,
			party,
			debit_amount,
			credit_amount,
			(debit_amount-credit_amount) balance,
			remark
			from `tabGeneral Ledger`
			where is_cancelled = 0 and posting_date between '{0}' and '{1}' {2}
			{3}
			""".format(filters.from_date,filters.to_date,filter,order_by_statement)
	sql_data = frappe.db.sql(sql,as_dict=1)
	with_opening_closing_data = get_data_with_opening_closing(filters,sql_data)
	data = get_result_as_list(with_opening_closing_data)
	return data

def get_columns(filters):
	settings = frappe.get_doc("ePOS Settings")
	currency = settings.currency
	columns = [
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Chart Of Account",
			"width": 180,
		},
		{
			"label": _("Debit ({0})").format(currency),
			"fieldname": "debit_amount",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Credit ({0})").format(currency),
			"fieldname": "credit_amount",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Balance ({0})").format(currency),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 140,
		},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 120},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_number",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 200,
		},
		{"label": _("Party Type"), "fieldname": "party_type", "width": 100},
		{"label": _("Party"), "fieldname": "party", "width": 150},
		{"label": _("Remark"), "fieldname": "remark", "align":"left","width": 400}
	]
	return columns
