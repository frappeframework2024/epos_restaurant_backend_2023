frappe.listview_settings['Sales Order'] = {
    add_fields: [],
    hide_name_column: false, // hide the last column which shows the `name`
    // set this to true to apply indicator function on draft documents too
    has_indicator_for_draft: false,

    get_indicator(doc) {
        if(doc.status=="Draft"){ 
            return [__("Draft"), "red"];
        }else if(doc.status=="To Bill"){
            return [__("To Bill"), "orange"];
        }else if(doc.status=="Cancelled"){
            return [__("Cancelled"), "red"];
        }
        else{
            return [__("Completed"), "green"];
        }
    },
}
