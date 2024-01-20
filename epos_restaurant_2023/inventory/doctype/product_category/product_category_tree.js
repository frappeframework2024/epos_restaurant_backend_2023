frappe.treeview_settings['Product Category'] = {
    breadcrumb: 'Product Category',
    title: 'Product Category',
    fields: [
        {
            fieldtype:'Link', 
            fieldname:'parent_product_category', 
            label:__('Parent Product Category'), 
            options:"Product Category",
            get_query: function () {
				return {
					filters: [["Product Category", "is_group", "=", 1]]
				};
			},
            reqd:true
        },
        {
            fieldtype:'Data', 
            fieldname:'product_category_name_en', 
            label:__('Product Category Name EN'),
            reqd:true
        },
        {
            fieldtype:'Data', 
            fieldname:'product_category_name_kh', 
            label:__('Product Category Name KH')
        },
        {
            fieldtype:'Link', 
            fieldname:'revenue_group', 
            label:__('Revenue Group'), 
            options:"Revenue Group",
            reqd:true
        },
        {
            fieldtype:'Check', 
            fieldname:'is_group', 
            label:__('Is Group')
        },
        {
            fieldtype:'Check', 
            fieldname:'show_in_pos_shortcut_menu', 
            label:__('Show In Menu')
        },
        {
            fieldtype:'Check', 
            fieldname:'allow_sale', 
            label:__('Allow Sale')
        },
    ],
    extend_toolbar: true
}
