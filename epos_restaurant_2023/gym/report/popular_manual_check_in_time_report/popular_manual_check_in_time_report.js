// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Popular Manual Check In Time Report"] = {
	"filters": [

	],
	onload: function (report) {
		const custom_css = `
            <style>
                .datatable .dt-row .dt-cell:first-child .dt-cell__content{
					min-width: 100px !important;
					width: 100px !important;
					align-content: center !important;
				}
            </style>`;
        $(custom_css).appendTo("head");
	}
};
