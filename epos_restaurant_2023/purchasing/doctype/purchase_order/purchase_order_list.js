frappe.listview_settings['Purchase Order'] = {
    add_fields: ['balance', 'total_amount','total_paid'],
    hide_name_column: false, // hide the last column which shows the `name`
    // set this to true to apply indicator function on draft documents too
    has_indicator_for_draft: false,

    get_indicator(doc) {
        if(doc.status=="Paid"){ 
            return [__("Paid"), "green"];
        }else if(doc.status=="Partially Paid"){
            return [__("Partially Paid"), "orange"];
        }else{
            return [__("Unpaid"), "red"];
        }
    },
}
