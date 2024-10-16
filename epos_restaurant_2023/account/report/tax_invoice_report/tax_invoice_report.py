# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from epos_restaurant_2023.utils import get_date_range_by_timespan
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
 
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Tax Invoice Report"} )
	if filters.timespan != "Date Range":
		date_range = get_date_range_by_timespan(filters.timespan)
		filters.start_date =date_range["start_date"]
		filters.end_date = date_range["end_date"]
	columns = get_report_columns(filters, report_config.report_fields)
	raw_data = get_data(filters,report_config.report_fields)
	report_data = get_report_data(filters = filters, report_fields= report_config.report_fields,data= raw_data)
	summary = get_report_summary( filters= filters, report_fields =  report_config.report_fields, data = raw_data )
	
	chart = get_report_chart(filters,report_data,report_config.report_fields)
	return  columns, report_data, None, chart, summary


def get_report_columns(filters,  report_fields):
	columns = []
	report_fields = [d for d in report_fields if d.show_in_report==1]
	report_fields = report_fields if not filters.show_columns else [d for d in report_fields if d.fieldname in filters.show_columns]
		
	for g in report_fields:
		if g.fieldtype=='Link' and g.link_field_doctype:
			columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":"Link","options":g.link_field_doctype,"align": g.align })
		else:
			columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })

	if filters.row_group:
		columns = [d for d in columns if d["fieldname"] != filters.row_group]
 
	

	return columns

def get_report_data (filters, report_fields, data):
	
	
	
	report_data = []
	if filters.row_group:
		parent_row = get_parent_row_row_by_data(filters,data)
		for parent in parent_row:
			
			d = parent
			
			report_data.append({
				"indent":0,
				report_fields[0].fieldname: d if not filters.row_group =="tax_invoice_date" else frappe.format(d,{'fieldtype':'Date'}),
				"is_group":1,
				"is_group_total":0,
			})

			report_data = report_data + [g for g in data if get_row_group_filter_key(filters, g, parent)]

			# total group row
			

			total_row = {
				"indent":1,
				report_fields[0].fieldname: "Total",
				"document_name":len([d for d in data if get_row_group_filter_key(filters, d, parent)]),
				"is_group":1,
				"is_group_total":1,
			}
	 
			for f in [d for d in report_fields if d.show_in_report==1 and d.fieldtype!='Date' and d.fieldtype!='Data' and d.fieldtype!='Link' and d.show_in_summary==1]:
				total_row[f.fieldname] = (sum([d[f.fieldname] for d in data if get_row_group_filter_key(filters, d, parent)]))
			report_data.append(total_row)

		report_data.append({"indent":0}) 
		grand_total_row = ({"indent":0,report_fields[0].fieldname: "Grand Total","is_group":1,"document_name":len([d for d in data])}) 
		for f in [d for d in report_fields if d.show_in_report==1 and d.fieldtype!='Date' and d.fieldtype!='Data' and d.fieldtype!='Link' and d.show_in_summary==1]:
			grand_total_row[f.fieldname] = (sum([d[f.fieldname] for d in data]))
		report_data.append(grand_total_row)
	else:
		report_data = data
		total_row = ({
      			"indent":0,
				report_fields[0].fieldname: "Total",
    			"is_group":1,
                "document_name":len([d for d in data])
                }) 
		for f in [d for d in report_fields if d.show_in_report==1 and d.fieldtype!='Date' and d.fieldtype!='Data' and d.fieldtype!='Link' and d.show_in_summary==1]:
			total_row[f.fieldname] = (sum([d[f.fieldname] for d in data]))
		report_data.append(total_row)

	

	return report_data


def get_row_group_filter_key(filters, key_data,value_data):
    return  ((key_data[filters.row_group] if not key_data.row_group=="tax_invoice_date" else getdate(key_data[filters.row_group])) == value_data) 

def get_parent_row_row_by_data(filters, data):
	 
	rows = sorted(set([d[filters.row_group] for d in  data]))
	return rows
	
def get_data (filters,report_fields):
	sql ="select {} as indent, 0 as is_group, ".format(1 if filters.row_group else 0)

	sql ="{} {}".format(sql, ",".join([d.sql_expression for d in report_fields if d.sql_expression]))

	if filters.row_group and len([d for d in report_fields if d.fieldname == filters.row_group]) == 0:
		sql = "{} , {}".format(sql, filters.row_group)

	sql = """{} from `tabTax Invoice`  
 		where 
   			property=%(property)s and 
   			tax_invoice_date between %(start_date)s and %(end_date)s
		order by
			tax_invoice_date
     """.format(sql)

	
	data = frappe.db.sql(sql, filters ,as_dict=1)
	return data


def get_report_summary(filters,report_fields, data):
	summary = []
	summary_fields = [d for d in report_fields if d.show_in_summary==1 ]
 

	if filters.show_in_summary:
		summary_fields = [d for d in summary_fields if d.fieldname in filters.show_in_summary]
	if filters.show_summary:
		summary.append({
			"value":len(data),"indicator":"blue","label":_("Total Inv.")
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
	report_fields = [d for d in report_fields if d.show_in_chart ==1]
	if filters.show_chart_series:
		report_fields = [d for d in report_fields if d.show_in_chart ==1 and d.fieldname in filters.show_chart_series]
	else:
		report_fields = [d for d in report_fields if d.show_in_chart_when_no_fields_selected ==1]
	
	if len(report_fields)==0:
		return None
	
	
	columns =[]
	
	datasets = []
	
	if filters.row_group:
		chart_label_field = "name"
		columns = [d[chart_label_field] for d in  data if 'is_group' in d and  d["is_group"] == 1 and d['name']!="Total" and d['name']!="Grand Total"]
	else:
		chart_label_field = "name"
		columns = [d[chart_label_field] for d in  data if 'is_group' in d and  d["is_group"] == 0 and d['name']!="Total" and d['name']!="Grand Total"]

	for f in report_fields:
		if f.show_in_chart==1:
			if filters.row_group:
				if (f.fieldtype=="Currency"):
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname],int(precision)) for d in  data if 'is_group_total' in d and  d["is_group_total"] ==1]
					})

				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in  data if    'is_group_total' in d and  d["is_group_total"] ==1]
					})
			else:
				if (f.fieldtype=="Currency"):
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname],int(precision)) for d in  data if 'is_group' in d and  d["is_group"] ==0]
					})

				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in  data if    'is_group' in d and  d["is_group"] ==0]
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
