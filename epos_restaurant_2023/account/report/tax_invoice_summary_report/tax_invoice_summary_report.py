# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from epos_restaurant_2023.utils import get_date_range_by_timespan

def execute(filters=None):
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Tax Invoice Summary Report"} )
	if filters.timespan != "Date Range":
		date_range = get_date_range_by_timespan(filters.timespan)
		filters.start_date =date_range["start_date"]
		filters.end_date = date_range["end_date"]

	report_data = get_report_data(filters, report_config.report_fields)
	summary = get_report_summary(filters, report_config.report_fields, report_data)
	columns = get_report_columns(filters, report_config.report_fields)
	# chart = get_report_chart(filters,report_data,report_config.report_fields)
	return  columns, report_data, None, None, summary


def get_report_columns(filters,  report_fields):
	if filters.row_group == "Date":
		columns = [
        {'key': "Date","fieldname":"row_group","label":"Date","width":125},
    ]
	elif filters.row_group == "Month":
		columns = [
        {'key': "Month","fieldname":"row_group","label":"Month","width":125},
    ]
	elif filters.row_group == "Year":
		columns = [
        {'key': "Year","fieldname":"row_group","label":"Year","width":125},
    ]
	elif filters.row_group == "Tax Invoice Type":
		columns = [
        {'key': "Tax Invoice Type","fieldname":"row_group","label":"Tax Invoice Type","width":125},
    ]
	elif filters.row_group == "Document Type":
		columns = [
        {'key': "Document Type","fieldname":"row_group","label":"Document Type","width":125},
    ]
	report_fields = [d for d in report_fields if d.show_in_report==1]
	
	report_fields = report_fields if not filters.show_columns else [d for d in report_fields if d.fieldname in filters.show_columns]
	for g in report_fields:
		columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })

	return columns

def get_report_data (filters, report_fields):
	sql ="""
		select 
			{0},
			{1}
		from `tabTax Invoice` 
		where 
			property=%(property)s and 
			tax_invoice_date between %(start_date)s and %(end_date)s 
		group by
			{2}
		""".format(
			get_group_field(filters),
			get_report_fields(report_fields),
			get_group_field(filters).split(" as ")[0]
		)
 
	report_data = frappe.db.sql(sql, filters, as_dict=1)
	# total row
	# TODO
	total_row = {
		"row_group":_("Total"),
		"is_total_row": 1,
	
	}
	for f in [d for d in report_fields if d.show_in_report==1]:
		total_row[f.fieldname] = (sum([d[f.fieldname] for d in report_data])) 

	report_data.append(total_row)

	return report_data
			
def get_report_fields(report_fields):
	return  ",".join([d.sql_expression for d in report_fields if d.show_in_report == 1])
 
 

def get_report_summary(filters,report_fields, data):
	summary = []
	summary_fields = [d for d in report_fields if d.show_in_summary==1 ]

	if filters.show_in_summary:
		summary_fields = [d for d in summary_fields if d.fieldname in filters.show_in_summary]

	for x in summary_fields:
		summary.append({
        "value": sum([d[x.fieldname] for d in data if x.fieldname in d]),
        "indicator": x.summary_indicator,
        "label": x.label,
        "datatype": x.fieldtype
})
	return summary


def get_report_chart(filters,data,report_fields):
	precision = frappe.db.get_single_value("System Settings","currency_precision")
	if filters.show_chart_series:
		report_fields = [d for d in report_fields if d.show_in_chart ==1 and d.fieldname in filters.show_chart_series]
	else:
		report_fields = [d for d in report_fields if d.show_in_chart_when_no_fields_selected ==1]
	
	if len(report_fields)==0:
		return None
	
	
	columns =[]
	
	datasets = []
	chart_label_field = "name"
	columns = [d[chart_label_field] for d in  data if 'is_group' in d and  d["is_group"] == 1 and d['name']!="Total"]
	
	for f in report_fields:
		if f.show_in_chart==1:
			if (f.fieldtype=="Currency"):
				datasets.append({
					"name": f.label,
					"values": [round(d[f.fieldname],int(precision)) for d in  data if 'is_group_total' in d and  d["is_group_total"] ==1]
				})

			else:
				datasets.append({
					"name": f.label,
					"values": [d[f.fieldname] for d in  data if 'is_group_total' in d and  d["is_group_total"] ==1]
				})
				
	chart = {
		'data':{
			'labels':columns,
			'datasets':datasets
		},
		"type": filters.chart_type,
		"lineOptions": {
			"regionFill": 1,
		},
		'valuesOverPoints':1,
		"axisOptions": {"xIsSeries": 1}
	}
	return chart

def get_group_field(filters):
	return [d["sql_expression"] for d in group_fields() if d["key"] == filters.row_group][0]

def group_fields():
	return [
		{"key":"Date", "sql_expression":"date_format(tax_invoice_date,'%%d-%%m-%%Y') as row_group"},
		{"key":"Month", "sql_expression":"date_format(tax_invoice_date,'%%b-%%Y') as row_group"},
		{"key":"Year", "sql_expression":"date_format(tax_invoice_date,'%%Y') as row_group"},
		{"key":"Tax Invoice Type", "sql_expression":"tax_invoice_type as row_group"},
		{"key":"Document Type", "sql_expression":"document_type as row_group"},
	]