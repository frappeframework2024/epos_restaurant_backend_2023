# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt
from frappe.utils import add_days, add_months, cint, flt, formatdate, get_first_day, getdate
import math
from datetime import datetime


def get_months(start_date, end_date):
	diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
	return diff + 1

def get_label(periodicity, from_date, to_date):
	if periodicity == "Yearly":
		if formatdate(from_date, "YYYY") == formatdate(to_date, "YYYY"):
			label = formatdate(from_date, "YYYY")
		else:
			label = formatdate(from_date, "YYYY") + "-" + formatdate(to_date, "YYYY")
	else:
		label = formatdate(from_date, "MMM YY") + "-" + formatdate(to_date, "MMM YY")
	return label


def validate_fiscal_year(from_fiscal_year, to_fiscal_year):
	if from_fiscal_year > to_fiscal_year:
		frappe.throw(_("End Year cannot be before Start Year"))

def validate_dates(from_date, to_date):
	if from_date > to_date:
		frappe.throw(_("To Date cannot be less than From Date"))

def get_period_list(
	period_start_date,
	period_end_date,
	filter_based_on,
	periodicity,
	filters=None,
	accumulated_values=False,
	reset_period_on_fy_change=True,
	ignore_fiscal_year=False,
):
	"""Get a list of dict {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
	Periodicity can be (Yearly, Quarterly, Monthly)"""
	from datetime import date
	current_fiscal_year = date.today()
	year_start_date = current_fiscal_year
	year_end_date = current_fiscal_year
	if filter_based_on == "Fiscal Year":
		current_fiscal_year = date.today()
		from_fiscal_year =  datetime.strptime((filters.from_fiscal_year+"-01-01"), "%Y-%m-%d").date()
		to_fiscal_year =  datetime.strptime(filters.to_fiscal_year+"-12-31", "%Y-%m-%d").date()
		validate_fiscal_year(from_fiscal_year,to_fiscal_year)
		year_start_date = from_fiscal_year if from_fiscal_year else current_fiscal_year
		year_end_date = to_fiscal_year if to_fiscal_year else current_fiscal_year
	else:
		validate_dates(year_start_date,year_end_date)
		year_start_date = getdate(period_start_date)
		year_end_date = getdate(period_end_date)
	months_to_add = {"Yearly": 12, "Half-Yearly": 6, "Quarterly": 3, "Monthly": 1}[periodicity]
	period_list = []
	start_date = year_start_date
	months = get_months(year_start_date, year_end_date)
	for i in range(cint(math.ceil(months / months_to_add))):
		period = frappe._dict({"from_date": start_date})
		if i == 0 and filter_based_on == "Date Range":
			to_date = add_months(get_first_day(start_date), months_to_add)
		else:
			to_date = add_months(start_date, months_to_add)
		start_date = to_date
		to_date = add_days(to_date, -1)
		if to_date <= year_end_date:
			period.to_date = to_date
		else:
			period.to_date = year_end_date
		if not ignore_fiscal_year:
			period.to_date_fiscal_year = "2025"
			period.from_date_fiscal_year_start_date = "2025"
		period_list.append(period)
		if period.to_date == year_end_date:
			break
	for opts in period_list:
		key = opts["to_date"].strftime("%b_%Y").lower()
		if periodicity == "Monthly" and not accumulated_values:
			label = formatdate(opts["to_date"], "MMM YYYY")
		else:
			if not accumulated_values:
				label = get_label(periodicity, opts["from_date"], opts["to_date"])
			else:
				if reset_period_on_fy_change:
					label = get_label(periodicity, opts.from_date_fiscal_year_start_date, opts["to_date"])
				else:
					label = get_label(periodicity, period_list[0].from_date, opts["to_date"])
		opts.update(
			{
				"key": key.replace(" ", "_").replace("-", "_"),
				"label": label,
				"year_start_date": year_start_date,
				"year_end_date": year_end_date,
			}
		)
	return period_list

def get_accounts(root_type):
	return frappe.db.sql(
		"""
		select  
			name, 
			account_code, 
			parent_chart_of_account, 
			account_name, 
			root_type, 
			is_group, 
			lft, 
			rgt 
		from `tabChart Of Account`
		where root_type=%s order by lft""",
		(root_type),
		as_dict=True,
	)

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
			sort_accounts(children, is_root=True if parent == None else False)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)
	add_to_list(None, 0)
	return filtered_accounts, accounts_by_name, parent_children_map

def sort_accounts(accounts, is_root=False, key="name"):
	import re
	import functools
	def compare_accounts(a, b):
		if re.split(r"\W+", a[key])[0].isdigit():
			return int(a[key] > b[key]) - int(a[key] < b[key])
		elif is_root:
			if a.report_type != b.report_type and a.report_type == "Balance Sheet":
				return -1
			if a.root_type != b.root_type and a.root_type == "Asset":
				return -1
			if a.root_type == "Liabilities" and b.root_type == "Equity":
				return -1
		else:
			return int(a[key] > b[key]) - int(a[key] < b[key])
		return 1
	accounts.sort(key=functools.cmp_to_key(compare_accounts))

def set_gl_entries_by_account(
	from_date,
	to_date,
	root_lft,
	root_rgt,
	filters,
	gl_entries_by_account
):
	"""Returns a dict like { "account": [gl entries], ... }"""
	additional_conditions = ""
	if filters.get("business_branch"):
		additional_conditions += "business_branch = '{0}' and ".format(filters.get("business_branch"))
	accounts = frappe.db.sql_list(
		"""select name from `tabChart Of Account`
		where lft >= %s and rgt <= %s""",
		(root_lft, root_rgt),
	)
	if accounts:
		additional_conditions += "account in ({})".format(
			", ".join(frappe.db.escape(d) for d in accounts)
		)
		gl_filters = {
			"from_date": from_date,
			"to_date": to_date
		}
		sql = """
			select posting_date, account, debit_amount, credit_amount,year(posting_date) fiscal_year from `tabGeneral Ledger`
			where {additional_conditions}
			and posting_date <= %(to_date)s
			and is_cancelled = 0""".format(
				additional_conditions=additional_conditions
			)
		gl_entries = frappe.db.sql(sql
			,
			gl_filters,
			as_dict=True,
		)
		for entry in gl_entries:
			gl_entries_by_account.setdefault(entry.account, []).append(entry)

		return gl_entries_by_account

def calculate_values(
	accounts_by_name,
	gl_entries_by_account,
	period_list,
	accumulated_values,
):
	for entries in gl_entries_by_account.values():
		for entry in entries:
			d = accounts_by_name.get(entry.account)
			try:
				for period in period_list:
					if entry.posting_date <= period.to_date:
						if (accumulated_values or (entry.posting_date >= period.from_date)) and (int(entry.fiscal_year) == int(period.to_date_fiscal_year)):
							d[period.key] = d.get(period.key, 0.0) + flt(entry.debit_amount) - flt(entry.credit_amount)
			except:
				frappe.throw(str(entry.account))

def get_data(
	root_type="",
	balance_must_be="",
	period_list=[],
	only_current_fiscal_year=True,
	filters= None,
	accumulated_values=1
):

	accounts = get_accounts(root_type)
	if not accounts:
		return None
	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
	outlet_currency = frappe.get_doc("ePOS Settings").currency
	gl_entries_by_account = {}
	for root in frappe.db.sql(
		"""select lft, rgt from `tabChart Of Account`
			where root_type=%s and ifnull(parent_chart_of_account, '') = ''""",
		root_type,
		as_dict=1,
	):
		set_gl_entries_by_account(
			period_list[0]["year_start_date"] if only_current_fiscal_year else None,
			period_list[-1]["to_date"],
			root.lft,
			root.rgt,
			filters,
			gl_entries_by_account
		)
	calculate_values(
		accounts_by_name,
		gl_entries_by_account,
		period_list,
		accumulated_values
	)
	accumulate_values_into_parents(accounts, accounts_by_name, period_list)
	out = prepare_data(accounts, balance_must_be, period_list, outlet_currency)
	out = filter_out_zero_value_rows(out, parent_children_map,filters.show_zero_values)
	add_total_row(out, root_type, balance_must_be, period_list, outlet_currency)
	return out

def add_total_row(out, root_type, balance_must_be, period_list, outlet_currency):
	total_row = {
		"account_name": _("Total {0} ({1})").format(_(root_type), _(balance_must_be)),
		"account": _("Total {0} ({1})").format(_(root_type), _(balance_must_be)),
		"currency": outlet_currency,
		"opening_balance": 0.0,
	}

	for row in out:
		if not row.get("parent_chart_of_account"):
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)
				row[period.key] = row.get(period.key, 0.0)

			total_row.setdefault("total", 0.0)
			total_row["total"] += flt(row["total"])
			total_row["opening_balance"] += row["opening_balance"]
			row["total"] = ""
	if "total" in total_row:
		out.append(total_row)
		out.append({})

def filter_out_zero_value_rows(data, parent_children_map, show_zero_values=False):
	data_with_value = []
	for d in data:
		if show_zero_values or d.get("has_value"):
			data_with_value.append(d)
		else:
			children = [child.name for child in parent_children_map.get(d.get("account")) or []]
			if children:
				for row in data:
					if row.get("account") in children and row.get("has_value"):
						data_with_value.append(d)
						break
	return data_with_value

def prepare_data(accounts, balance_must_be, period_list, outlet_currency):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")
	for d in accounts:
		has_value = False
		total = 0
		row = frappe._dict(
			{
				"account": _(d.name),
				"parent_chart_of_account": _(d.parent_chart_of_account) if d.parent_chart_of_account else "",
				"indent": flt(d.indent),
				"year_start_date": year_start_date,
				"year_end_date": year_end_date,
				"currency": outlet_currency,
				"include_in_gross": d.include_in_gross,
				"account_type": d.account_type,
				"is_group": d.is_group,
				"opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be == "Debit" else -1),
				"account_name": (
					"%s - %s" % (_(d.account_number), _(d.account_name))
					if d.account_number
					else _(d.account_name)
				),
			})
		for period in period_list:
			if d.get(period.key) and balance_must_be == "Credit":
				d[period.key] *= -1
			row[period.key] = flt(d.get(period.key, 0.0), 3)
			if abs(row[period.key]) >= 0.005:
				has_value = True
				total += flt(row[period.key])
		row["has_value"] = has_value
		row["total"] = total
		data.append(row)
	return data

def accumulate_values_into_parents(accounts, accounts_by_name, period_list):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		if d.parent_chart_of_account:
			for period in period_list:
				accounts_by_name[d.parent_chart_of_account][period.key] = accounts_by_name[d.parent_chart_of_account].get(
					period.key, 0.0
				) + d.get(period.key, 0.0)

			accounts_by_name[d.parent_chart_of_account]["opening_balance"] = accounts_by_name[d.parent_chart_of_account].get(
				"opening_balance", 0.0
			) + d.get("opening_balance", 0.0)

def get_columns(periodicity, period_list, accumulated_values=1, outlet=None):
	columns = [
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Chart Of Account",
			"width": 300,
		}
	]
	for period in period_list:
		columns.append(
			{
				"fieldname": period.key,
				"label": period.label,
				"fieldtype": "Currency",
				"options": "currency",
				"width": 150,
			}
		)
	if periodicity != "Yearly":
		if not accumulated_values:
			columns.append(
				{"fieldname": "total", "label": _("Total"), "fieldtype": "Currency", "width": 150}
			)
	return columns

def execute(filters=None):
	period_list = get_period_list(
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		filters
	)
	currency = frappe.get_doc("ePOS Settings").currency
	asset = get_data(
		"Asset",
		"Debit",
		period_list,
		False,
		filters,
		filters.accumulated_values,
	)
	liability = get_data(
		"Liabilities",
		"Credit",
		period_list,
		False,
		filters,
		filters.accumulated_values,
	)
	equity = get_data(
		"Equity",
		"Credit",
		period_list,
		False,
		filters,
		filters.accumulated_values,
	)
	provisional_profit_loss, total_credit = get_provisional_profit_loss(
		asset, liability, equity, period_list, filters.outlet, currency
	)
	data = []
	data.extend(asset or [])
	data.extend(liability or [])
	data.extend(equity or [])
	if provisional_profit_loss:
		data.append(provisional_profit_loss)
	if total_credit:
		data.append(total_credit)

	columns = get_columns(
		filters.periodicity, period_list, filters.accumulated_values, outlet=filters.outlet
	)
	chart = get_chart_data(filters, columns, asset, liability, equity)
	report_summary = get_report_summary(
		period_list, asset, liability, equity, provisional_profit_loss, currency, filters
	)
	return columns, data, None, chart, report_summary


def get_provisional_profit_loss(
	asset, liability, equity, period_list, outlet, currency=None, consolidated=False
):
	provisional_profit_loss = {}
	total_row = {}
	if asset and (liability or equity):
		total = total_row_total = 0
		currency = frappe.get_doc("ePOS Settings").currency
		total_row = {
			"account_name": "'" + _("Total (Credit)") + "'",
			"account": "'" + _("Total (Credit)") + "'",
			"warn_if_negative": True,
			"currency": currency,
		}
		has_value = False
		for period in period_list:
			key = period if consolidated else period.key
			effective_liability = 0.0
			if liability:
				effective_liability += flt(liability[-2].get(key))
			if equity:
				effective_liability += flt(equity[-2].get(key))
			provisional_profit_loss[key] = flt(asset[-2].get(key)) - effective_liability
			total_row[key] = effective_liability + provisional_profit_loss[key]
			if provisional_profit_loss[key]:
				has_value = True
			total += flt(provisional_profit_loss[key])
			provisional_profit_loss["total"] = total
			total_row_total += flt(total_row[key])
			total_row["total"] = total_row_total
		if has_value:
			provisional_profit_loss.update(
				{
					"account_name": "'" + _("Provisional Profit / Loss (Credit)") + "'",
					"account": "'" + _("Provisional Profit / Loss (Credit)") + "'",
					"warn_if_negative": True,
					"currency": currency,
				}
			)
	return provisional_profit_loss, total_row

def get_report_summary(
	period_list,
	asset,
	liability,
	equity,
	provisional_profit_loss,
	currency,
	filters,
	consolidated=False,
):
	net_asset, net_liability, net_equity, net_provisional_profit_loss = 0.0, 0.0, 0.0, 0.0
	if filters.get("accumulated_values"):
		period_list = [period_list[-1]]
	for period in period_list:
		key = period if consolidated else period.key
		if asset:
			net_asset += asset[-2].get(key)
		if liability:
			net_liability += liability[-2].get(key)
		if equity:
			net_equity += equity[-2].get(key)
		if provisional_profit_loss:
			net_provisional_profit_loss += provisional_profit_loss.get(key)
	report = []
	if net_asset!=0:
		report.append({"value": net_asset, "label": _("Total Asset"), "datatype": "Currency", "currency": currency})
	if net_liability!=0:
		report.append({"value": net_liability,"label": _("Total Liability"),"datatype": "Currency","currency": currency})
	if net_equity!=0:
		report.append({"value": net_equity, "label": _("Total Equity"), "datatype": "Currency", "currency": currency})
	report.append({"value": net_provisional_profit_loss,"label": _("Provisional Profit / Loss (Credit)"),"indicator": "Green" if net_provisional_profit_loss > 0 else "Red","datatype": "Currency","currency": currency})
	return report


def get_chart_data(filters, columns, asset, liability, equity):
	labels = [d.get("label") for d in columns[2:]]
	asset_data, liability_data, equity_data = [], [], []
	for p in columns[2:]:
		if asset:
			asset_data.append(asset[-2].get(p.get("fieldname")))
		if liability:
			liability_data.append(liability[-2].get(p.get("fieldname")))
		if equity:
			equity_data.append(equity[-2].get(p.get("fieldname")))
	datasets = []
	if asset_data:
		datasets.append({"name": _("Assets"), "values": asset_data})
	if liability_data:
		datasets.append({"name": _("Liabilities"), "values": liability_data})
	if equity_data:
		datasets.append({"name": _("Equity"), "values": equity_data})
	chart = {"data": {"labels": labels, "datasets": datasets}}
	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"
	return chart
