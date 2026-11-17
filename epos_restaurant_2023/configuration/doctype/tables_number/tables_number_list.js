frappe.listview_settings['Tables Number'] = {
    hide_name_column: true,
    onload(me) {
        me.page.add_menu_item(__('Sync Tables to Emenu'), () => {
            frappe.confirm(
                __('Are you sure you want to sync all tables to Emenu?'),
                () => {
                    frappe.call({
                        method: 'epos_restaurant_2023.api.emenu_integration.sync.sync_tables_to_emenu',
                        type: 'POST',
                        freeze: true,
                        freeze_message: __('Syncing tables to Emenu, please wait...'),
                        callback(r) {
                            if (!r.exc) {
                                me.refresh();
                                frappe.show_alert({
                                    message: r.message || __('Tables successfully synced to Emenu!'),
                                    indicator: 'green'
                                });
                            }
                        }
                    });
                }
            );
        });
    }
};