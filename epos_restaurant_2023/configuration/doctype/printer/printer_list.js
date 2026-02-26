frappe.listview_settings['Printer'] = {
    onload: function(listview) {
        frappe.realtime.on("update_printer_to_products", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
        });
        listview.page.add_inner_button(__('Update Printer to Products'), function() {
            frappe.confirm(
                'Are you sure you want process this transaction?',
                function(){
                    frappe.call('epos_restaurant_2023.configuration.doctype.printer.printer.enqueue_update_product')
                },
            )
        });
    }
};