 
frappe.listview_settings['Translation'] = {
    onload(me) { 
        me.page.add_inner_button(__('Update Translation to Client'), function() {
            
            frappe.confirm(
                'Are you sure you want to update translation to client?',
                function(){
                    frappe.call('epos_restaurant_2023.api.api.update_language').then(r => {
                        frappe.show_alert('Update translation complete')
                    })
                    
                },
                
            )
        });
    }
};