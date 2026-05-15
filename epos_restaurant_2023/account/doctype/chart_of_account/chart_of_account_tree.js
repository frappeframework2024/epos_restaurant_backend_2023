frappe.treeview_settings['Chart Of Account'] = {
    breadcrumb: 'Chart Of Account',
    title: 'Chart Of Account',
    onload(treeview) {
        treeview.from_add_child = false;
        treeview.parent_name = null;
        $(document).on('mousedown','.tree-node .btn-default',
            function () {
                treeview.parent_name = $('.tree-link.selected').find('.tree-label').text().trim();
                treeview.from_add_child = true;
            }
        );
        treeview.page.btn_primary.on('mousedown', () => {
            treeview.from_add_child = false;
            treeview.parent_name = null;
        });
        const original_dialog = frappe.ui.Dialog.prototype.show;
        frappe.ui.Dialog.prototype.show = function () {
            let dialog = this;
            setTimeout(() => {
                if (treeview.from_add_child && treeview.parent_name)
                {
                    dialog.set_value('parent_chart_of_account',treeview.parent_name);
                }},100);
            return original_dialog.apply(this, arguments);
        };
    },
    fields: [
        {
            fieldtype:'Link', 
            fieldname:'parent_chart_of_account', 
            options:'Chart Of Account', 
            label:__('Parent Chart Of Account'),
             get_query: function () {
                return {
                    filters: {
                        is_group: 1
                    }
                };
            }
        },
        {
            fieldtype:'Link', 
            fieldname:'business_branch', 
            options:'Business Branch', 
            label:__('Business Branch'),
            reqd:true
        },
        {
            fieldtype:'Check', 
            fieldname:'is_group', 
            label:__('Is Group')
        },
        {
            fieldtype: 'Column Break'
        },
        {
            fieldtype:'Data', 
            fieldname:'account_name', 
            label:__('Account Name'),
            reqd: true
        },
        {
            fieldtype:'Data', 
            fieldname:'account_code', 
            label:__('Account Code')
        },
        {
            fieldtype: 'Section Break'
        },
        {
            fieldtype:'Select', 
            fieldname:'root_type', 
            label:__('Root Type'), 
            options:"Asset\nLiabilities\nEquity\nIncome\nExpenses",
            reqd: true
        },
        {
            fieldtype: 'Column Break'
        },
        {
            fieldtype:'Select', 
            fieldname:'account_type', 
            label:__('Account Type'),
            options:"\nReceivable\nPayable\nCash\nBank\nIncome\nExpense\nTemporary"
        },
        {
            fieldtype: 'Section Break'
        },
        {
            fieldtype:'Small Text', 
            fieldname:'description', 
            label:__('Description')
        }
    ],
    extend_toolbar: true
}
