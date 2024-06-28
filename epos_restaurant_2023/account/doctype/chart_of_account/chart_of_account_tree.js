frappe.treeview_settings['Chart Of Account'] = {
    breadcrumb: 'Chart Of Account',
    title: 'Chart Of Account',
    fields: [
        {
            fieldtype:'Check', 
            fieldname:'is_group', 
            label:__('Is Group'),
            reqd:true
        },
        {
            fieldtype:'Data', 
            fieldname:'account_code', 
            label:__('Account Code')
        },
        {
            fieldtype:'Data', 
            fieldname:'account_name', 
            label:__('Account Name')
        },
        {
            fieldtype:'Link', 
            fieldname:'business_branch', 
            options:'Business Branch', 
            label:__('Business Branch')
        },
        {
            fieldtype:'Select', 
            fieldname:'root_type', 
            label:__('Root Type'), 
            options:"Asset\nLiabilities\nEquity\nIncome\nExpenses"
        },
        {
            fieldtype:'Select', 
            fieldname:'account_type', 
            label:__('Account Type'),
            options:"\nReceivable\nPayable\nCash\nBank\nIncome\nExpense"
        }
    ],
    extend_toolbar: true
}
