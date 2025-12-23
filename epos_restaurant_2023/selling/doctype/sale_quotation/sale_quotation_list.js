frappe.listview_settings['Sale Quotation'] = {
    add_fields: [''],
    hide_name_column: true,
    has_indicator_for_draft: false,
    get_indicator(doc) {
       if(doc.status=="Open"){ 
			return [__(doc.status), "green"];
		}else if(doc.status=="Draft"){
			return [__(doc.status), "red"];
		}else if(doc.status=="Cancelled"){
			return [__(doc.status), "red"];
		}else if(doc.status=="Ordered"){
			return [__(doc.status), "red"];
		}	
    },
}