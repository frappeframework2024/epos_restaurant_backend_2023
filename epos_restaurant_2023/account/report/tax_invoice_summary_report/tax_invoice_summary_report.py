# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
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
	
	for g in report_fields:
		columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })

	return columns

def get_report_data (filters, report_fields):
	data = get_data(filters,report_fields)
	row_group = get_row_group_report_data(filters)
	
	report_data = []
	for g in row_group:
		report_data.append({
			"indent":0,
			"row_group": g['row_group'],
			"sub_total":sum([d['sub_total'] for d in data if d['tax_invoice_date'] == g['row_group'] or d['tax_invoice_type']==g['row_group'] or d['document_type']==g['row_group']]),
			"service_charge":sum([d['service_charge'] for d in data if d['tax_invoice_date'] == g['row_group'] or d['tax_invoice_type']==g['row_group'] or d['document_type']==g['row_group']]),
			"accommodation_tax":sum([d['accommodation_tax'] for d in data if d['tax_invoice_date'] == g['row_group'] or d['tax_invoice_type']==g['row_group'] or d['document_type']==g['row_group']]),
			"specific_tax":sum([d['specific_tax'] for d in data if d['tax_invoice_date'] == g['row_group'] or d['tax_invoice_type']==g['row_group'] or d['document_type']==g['row_group']]),
			"vat":sum([d['vat'] for d in data if d['tax_invoice_date'] == g['row_group'] or d['tax_invoice_type']==g['row_group'] or d['document_type']==g['row_group']]),
			"grand_total":sum([d['grand_total'] for d in data if d['tax_invoice_date'] == g['row_group'] or d['tax_invoice_type']==g['row_group'] or d['document_type']==g['row_group']]),
		})

	
	return report_data


	
def get_data (filters,report_fields):

	sql ="select date_format(tax_invoice_date,'%%d-%%m-%%Y') as tax_invoice_date,tax_invoice_type,document_type,{}".format(",".join([d.sql_expression for d in report_fields if d.sql_expression]))

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

def get_row_group_report_data(filters):
	sql = ""
	if filters.row_group =='Date':
		sql ="select date_format(date,'%%d-%%m-%%Y') as row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date" 
	elif filters.row_group =='Month':
		sql ="select date_format(date,'%%b-%%Y') as row_group from `tabDates` where date between %(start_date)s and %(end_date)s group by  date_format(date,'%%b-%%Y') order by year(date),month(date)"      
	elif filters.row_group =='Year':
		sql ="select date_format(date,'%%Y') as row_group from `tabDates` where date between %(start_date)s and %(end_date)s group by  date_format(date,'%%Y') order by year(date),month(date)" 
	elif filters.row_group == 'Tax Invoice Type':
		sql = "select tax_invoice_type as row_group from `tabTax Invoice` group by tax_invoice_type"
	elif filters.row_group == 'Document Type':
		sql = "select document_type as row_group from `tabTax Invoice` group by document_type"
	data = frappe.db.sql(sql,filters,as_dict=1)

	return data