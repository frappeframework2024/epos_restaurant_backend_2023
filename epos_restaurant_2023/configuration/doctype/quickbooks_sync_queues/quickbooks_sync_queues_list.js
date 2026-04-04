// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt
frappe.listview_settings['Quickbooks Sync Queues'] = {
    onload(me) { 
        frappe.realtime.on("get_data_notification", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
        });
    },
    refresh: function(listview) {
        frappe.realtime.on("get_data_notification", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
        });
        listview.page.add_inner_button("Get Chart of Account", function() {
            frappe.call({method: "epos_restaurant_2023.api.qb.request.qbwc_get_data.get_qb_chart_of_account"});
        }, __("Get QB Data")),
        listview.page.add_inner_button("Get Payment Type", function() {
            frappe.call({method: "epos_restaurant_2023.api.qb.request.qbwc_get_data.get_qb_payment_type"});
        }, __("Get QB Data")),
        listview.page.add_inner_button("Get Customer", function() {
            frappe.call({method: "epos_restaurant_2023.api.qb.request.qbwc_get_data.get_qb_customer"});
        }, __("Get QB Data"));
        listview.page.add_inner_button("Get Product", function() {
            frappe.call({method: "epos_restaurant_2023.api.qb.request.qbwc_get_data.get_qb_product"});
        }, __("Get QB Data"));
    },
};