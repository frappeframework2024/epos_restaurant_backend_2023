frappe.listview_settings['Customer'] = {
    hide_name_column: true, // hide the last column which shows the `name`
    onload: function(listview) {
        if(frappe.session.user == "Administrator"){
            listview.page.add_inner_button(__('Update Customer Transaction'), function() {
            
                frappe.confirm(
                    'Are you sure you want to update all customer information transaction?',
                    function(){
                        frappe.call('epos_restaurant_2023.selling.doctype.customer.customer.update_customer_infomation_to_transaction').then(r => {
                            frappe.show_alert('Update complete')
                        })
                        
                    },
                )
            });
        }
        
    }
};