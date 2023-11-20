frappe.listview_settings['Account Code'] = {
    onload: function(listview) {
        
        listview.page.add_inner_button(__('Sort Order Account Code'), function() {
            new frappe.ui.form.MultiSelectDialog({
                doctype: "Account Code",
                target: this.cur_frm,
                sortable: true,
                setters: {

                    is_group: 0
                },
                get_query() {
                    return {
                        filters: { is_group: ['==', 0] }
                    }
                },
                action(selections) {
                    console.log(selections);
                }
            });

            // new frappe.ui.form.MultiSelectDialog({
            //     doctype: "Account",
            //     target: cur_frm,
                
            //     action(selections) {
            //         console.log(selections);
            //     }
            // });
        });
    }
};