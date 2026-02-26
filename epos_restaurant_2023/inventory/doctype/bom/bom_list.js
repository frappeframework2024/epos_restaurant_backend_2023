frappe.listview_settings['BOM'] = {
    hide_name_column: false,
    has_indicator_for_draft: false,
    get_indicator(doc) {
       if(doc.is_active == 1){
        return [__("Active"), "green"];
       }
       else{
        return [__("Not Active"), "gray"];
       }
    },
}
