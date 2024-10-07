# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import datetime
import json
import os
from datetime import timedelta

import frappe
import frappe.desk.reportview
from frappe import _
from frappe.core.utils import ljust_list
from frappe.desk.reportview import clean_params, parse_json
from frappe.model.utils import render_include
from frappe.modules import get_module_path, scrub
from frappe.monitor import add_data_to_monitor
from frappe.permissions import get_role_permissions
from frappe.utils import cint, cstr, flt, format_duration, get_html_format, sbool
from frappe.desk import query_report

from epos_restaurant_2023.api.data_export import data_export
@frappe.whitelist()
def export_to_excel():
    """export from query reports"""
    from frappe.desk.utils import get_csv_bytes, pop_csv_params, provide_binary_file

    form_params = frappe._dict(frappe.local.form_dict)
    csv_params = pop_csv_params(form_params)
    clean_params(form_params)
    parse_json(form_params)

    report_name = form_params.report_name
    frappe.permissions.can_export(
        frappe.get_cached_value("Report", report_name, "ref_doctype"),
        raise_exception=True,
    )

    file_format_type = form_params.file_format_type
    custom_columns = frappe.parse_json(form_params.custom_columns or "[]")
    include_indentation = form_params.include_indentation
    visible_idx = form_params.visible_idx

    if isinstance(visible_idx, str):
        visible_idx = json.loads(visible_idx)

    data = query_report.run(
        report_name, form_params.filters, custom_columns=custom_columns, are_default_filters=False
    )
    data = frappe._dict(data)
    if not data.columns:
        frappe.respond_as_web_page(
            _("No data to export"),
            _("You can try changing the filters of your report."),
        )
        return
 
    data_export.export_excel(report_name,data,chart_image=form_params.chart_image,
                             filters_html=form_params.filters_html,
                             filters=form_params.filters)
    
    
    
    
    
	
    