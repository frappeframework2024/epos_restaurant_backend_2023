// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("POS Reservation", {
	refresh(frm) { 
        if(frm.doc.__islocal){
            frm.doc.reservation_status = "Reserved";
            frm.doc.status = "Reserved";
            frm.refresh_field("reservation_status");
            frm.refresh_field("status");

            set_query(frm,"reservation_status",[
                ["POS Reservation Status","reservation_status","=","Reserved"]
            ]); 
        }else{
            if(frm.doc.reservation_status == undefined || frm.doc.reservation_status == ""){
                frm.doc.reservation_status = frm.doc.status;
                frm.refresh_field("status");
            }

            if(frm.doc.reservation_status == "Reserved"){
                set_query(frm,"reservation_status",[
                    ["POS Reservation Status","reservation_status","in","Confirmed,Reserved"]
                ]); 
            }
            else if(frm.doc.reservation_status == "Confirmed"){
                set_query(frm,"reservation_status",[
                    ["POS Reservation Status","reservation_status","in","No Show,Void,Confirmed"]
                ]); 
            }
            else if(frm.doc.reservation_status == "No Show"){
                set_query(frm,"reservation_status",[
                    ["POS Reservation Status","reservation_status","in","No Show,Void"]
                ]); 
            }
            else{
                set_query(frm,"reservation_status",[
                    ["POS Reservation Status","reservation_status","in",`${frm.doc.reservation_status}`]
                ]);  
            }   
            
            //set readonly
            if(frm.doc.reservation_status == "Dine-in" || frm.doc.reservation_status == "Checked Out" || frm.doc.reservation_status == "Void"){
                set_df_propert(frm,"table_id","read_only",1);
                set_df_propert(frm,"total_guest","read_only",1);
                set_df_propert(frm,"reservation_date","read_only",1);
                set_df_propert(frm,"arrival_date","read_only",1);
                set_df_propert(frm,"arrival_time","read_only",1); 
                set_df_propert(frm,"guest","read_only",1);
                set_df_propert(frm,"reservation_product","read_only",1);
                set_df_propert(frm,"reservation_status","read_only",1);
            }
        }
	},
 
    setup(frm) {  
              
    },
    
});

function set_query(frm,field_name, filters){	 
    frm.set_query(field_name, function() {
        return {
            filters: filters
        }
    }); 
}

function set_df_propert(frm,field_name,property,property_value){
    frm.set_df_property(field_name,property, property_value);	
    frm.refresh_field(field_name);
}
