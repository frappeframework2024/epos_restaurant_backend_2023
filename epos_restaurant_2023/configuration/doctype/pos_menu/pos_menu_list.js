frappe.listview_settings['POS Menu'] = {
    onload(me) { 
         me.page.add_action_item('Assign Shift Availability', function() {
            let d = new frappe.ui.Dialog({
                title: 'Assign Shift Availability',
                fields: [
                    {'fieldname': 'shift_type', 'fieldtype': 'Link', 'options': 'Shift Type'},
                ],
                primary_action_label: 'Save',
                primary_action(values) {
                    const selected =  me.get_checked_items() ;
                    const result = selected.map(item => item.name).join(',');
                    d.freeze= true;
                    frappe.call({
                        method: "epos_restaurant_2023.configuration.doctype.pos_menu.pos_menu.assign_available_shift",
                        args: {
                            "menus": result,
                            "shift_type": values.shift_type
                        },
                        callback: function(r) {
                            frappe.msgprint("Available Shift Updated")                            
                        }
                    });
                    d.freeze= false;
                    d.hide();
                },              
            })
            d.show();           
        });

        me.page.add_action_item('Remove Shift Availability', function() {
            let d = new frappe.ui.Dialog({
                title: 'Remove Shift Availability',
                fields: [
                    {'fieldname': 'shift_type', 'fieldtype': 'Link', 'options': 'Shift Type'},
                ],
                primary_action_label: 'Save',
                primary_action(values) {
                    const selected =  me.get_checked_items() ;
                    const result = selected.map(item => item.name).join(',');
                    d.freeze= true;
                    frappe.call({
                        method: "epos_restaurant_2023.configuration.doctype.pos_menu.pos_menu.remove_available_shift",
                        args: {
                            "menus": result,
                            "shift_type": values.shift_type
                        },
                        callback: function(r) {
                            frappe.msgprint("Available Shift Removed")                            
                        }
                    });
                    d.freeze= false;
                    d.hide();
                },              
            })
            d.show();           
        });
    },
   
}