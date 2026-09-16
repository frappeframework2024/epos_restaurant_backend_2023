// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Customer List"] = {
	"filters": [

	],

	onload: function (report) { 
		const custom_css = `
            <style>
                .datatable .dt-row .dt-cell:first-child .dt-cell__content{
					min-width: 90px !important;
					width: 90px !important;
					align-content: center !important;
				}
            </style>`;
        $(custom_css).appendTo("head");
	},
};
