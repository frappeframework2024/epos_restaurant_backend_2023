frappe.listview_settings['Account Category'] = {
    onload: function(listview) {
        
        listview.page.add_inner_button(__('Sort Order Account Category'), function() {
            let msg = frappe.msgprint(
                '<iframe src="/frontdesk/account-category-sort-order" frameBorder="0" width="100%" height="650" title="Sort Order Account Code"></iframe>',
                
                'Sort Order Account Category'
            );
            msg.$wrapper.find('.modal-dialog').css("max-width", "90%");
        });
        
        listview.page.add_inner_button(__('Update Information to Fransaction'), function() {
            frappe.confirm(
                'Are you sure you want to update account category information to folio transaction?',
                function(){
                    frappe.call('edoor.api.utils.update_account_category_information_to_folio_transaction').then(r => {
                        frappe.show_alert('Update complete')
                    })
                    
                },
                
            )
        });
    }
};