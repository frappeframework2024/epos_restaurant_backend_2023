frappe.listview_settings['Coupon Transaction'] = {
    onload: function(listview) {
        // listview.page.add_inner_button(__('Move To History'), function() {
        //     frappe.confirm(
        //         'Are you sure you want to move transactions to history?',
        //         function(){
        //             frappe.call('epos_restaurant_2023.selling.doctype.coupon_transaction.coupon_transaction.move_to_history').then(r => {
        //                 frappe.show_alert(r.message)
        //             })  
        //         },
        //     )
        // });
    }
};