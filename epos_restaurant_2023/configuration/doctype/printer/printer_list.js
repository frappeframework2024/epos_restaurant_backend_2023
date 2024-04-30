frappe.listview_settings['Printer'] = {
    onload: function(listview) {
        

        
        listview.page.add_inner_button(__('Update Printer to Products'), function() {
            
            frappe.confirm(
                'Are you sure you want process this transaction?',
                function(){
                    frappe.call('epos_restaurant_2023.configuration.doctype.printer.printer.update_printer_to_product').then(r => {
                        frappe.show_alert('Update complete')
                    })
                    
                },
                
            )
        });

       

    }
};