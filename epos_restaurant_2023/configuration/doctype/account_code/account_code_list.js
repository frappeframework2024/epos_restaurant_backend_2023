frappe.listview_settings['Account Code'] = {
    onload: function(listview) {
        
        listview.page.add_inner_button(__('Sort Order Account Code'), function() {
            let msg = frappe.msgprint(
                '<iframe src="/frontdesk/account-code-sort-order" frameBorder="0" width="100%" height="650" title="Sort Order Account Code"></iframe>',
                
                'Sort Order Account Code'
            );
            msg.$wrapper.find('.modal-dialog').css("max-width", "90%");
        });
    }
};