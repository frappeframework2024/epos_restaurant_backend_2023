frappe.listview_settings['Coupon Codes'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Move To History'), function() {
            frappe.confirm(
                'Are you sure you want to move transactions to history?',
                function(){
                    frappe.call('epos_restaurant_2023.selling.doctype.coupon_codes.coupon_codes.move_to_history').then(r => {
                        frappe.show_alert(r.message)
                    })  
                },
            )
        });
    }
};