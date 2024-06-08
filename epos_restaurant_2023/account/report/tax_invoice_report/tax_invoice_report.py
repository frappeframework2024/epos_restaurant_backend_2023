# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from epos_restaurant_2023.utils import get_date_range_by_timespan

def execute(filters=None):
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Tax Invoice Report"} )
	if filters.timespan != "Date Range":
		date_range = get_date_range_by_timespan(filters.timespan)
		filters.start_date =date_range["start_date"]
		filters.end_date = date_range["end_date"]

	report_data = get_report_data(filters, report_config.report_fields)
	summary = get_report_summary(filters, report_config.report_fields, report_data)
	columns = get_report_columns(filters, report_config.report_fields)
	chart = get_report_chart(filters,report_data,report_config.report_fields)
	return  columns, report_data, None, chart, summary


def get_report_columns(filters,  report_fields):
	columns = []
	report_fields = [d for d in report_fields if d.show_in_report==1]
	
	for g in report_fields:
		columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })

	if filters.row_group:
		columns = [d for d in columns if d["fieldname"] != filters.row_group]

	return columns

def get_report_data (filters, report_fields):
	data = get_data(filters,report_fields)
	
	report_data = []
	if filters.row_group:
		parent_row = get_parent_row_row_by_data(filters,data)
		for parent in parent_row:
			d = parent
			report_data.append({
				"indent":0,
				report_fields[0].fieldname: d,
				"is_group":1,
				"is_group_total":0,
			})

			report_data = report_data + [d for d in data if d[filters.row_group] == parent]
		report_data.append({
			"indent":0,
			report_fields[0].fieldname: "Total",
			"is_group":1,
			"sub_total":sum([d['sub_total'] for d in data if d[filters.row_group] == parent]),
			"service_charge":sum([d['service_charge'] for d in data if d[filters.row_group] == parent]),
			"accommodation_tax":sum([d['accommodation_tax'] for d in data if d[filters.row_group] == parent]),
			"specific_tax":sum([d['specific_tax'] for d in data if d[filters.row_group] == parent]),
			"vat":sum([d['vat'] for d in data if d[filters.row_group] == parent]),
			"grand_total":sum([d['grand_total'] for d in data if d[filters.row_group] == parent]),
			"is_group_total":1,
		})
	else:
		report_data = data
	
	return report_data

def get_parent_row_row_by_data(filters, data):
	
	rows = set([d[filters.row_group] for d in  data])

	return rows
	
def get_data (filters,report_fields):
	sql ="select {} as indent, 0 as is_group, ".format(1 if filters.row_group else 0)

	sql ="{} {}".format(sql, ",".join([d.sql_expression for d in report_fields if d.sql_expression]))

	if filters.row_group and len([d for d in report_fields if d.fieldname == filters.row_group]) == 0:
		sql = "{} , {}".format(sql, filters.row_group)

	sql = "{} from `tabTax Invoice`  ".format(sql)
	sql = "{} {}".format(sql, get_filters(filters))
	
	data = frappe.db.sql(sql, filters ,as_dict=1)
	return data

def get_filters(filters):
	sql = """where property=%(property)s
	and tax_invoice_date between %(start_date)s and %(end_date)s """
	

	return sql


def get_report_summary(filters,report_fields, data):
	summary = []
	summary_fields = [d for d in report_fields if d.show_in_summary==1 ]

	if filters.show_in_summary:
		summary_fields = [d for d in summary_fields if d.fieldname in filters.show_in_summary]
	summary.append({
		"value":len([d for d in data if d['indent']==1]),"indicator":"blue","label":"Total Inv."
	})
	for x in summary_fields:
		summary.append({
        "value": sum([d[x.fieldname] for d in data if d["is_group"] == 0 and x.fieldname in d]),
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
