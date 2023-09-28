// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Membership", {
	refresh(frm) {
        on_membership_value_changed(frm)       
	},
    membership:function(frm){
        on_membership_value_changed(frm)
    },
    duration_type:function(frm){        
        on_duration_type_value_changed(frm)
    }  ,
    start_date:function(frm){
        on_start_date_changed(frm)
    }
});

function on_membership_value_changed(frm){ 
    on_duration_type_value_changed(frm)
    frm.set_df_property('duration_type', 'hidden', 0);
    if(frm.doc.membership=="" || frm.doc.membership == undefined){
        frm.set_df_property('duration_type', 'hidden', 1); 
    } 
    frm.refresh_field("duration_type");   
}

function on_duration_type_value_changed(frm){ 
    frm.set_df_property('start_date', 'hidden', 0);
    frm.set_df_property('end_date', 'hidden', 0);
    if(frm.doc.duration_type =="Ongoing" || frm.doc.membership=="" || frm.doc.membership == undefined){
        frm.set_df_property('start_date', 'hidden', 1);
        frm.set_df_property('end_date', 'hidden',1);
    }else{
        if(frm.doc.duration_type=="Limited Duration"){
            on_start_date_changed(frm)
            
        }
    }
    frm.refresh_field("start_date");
    frm.refresh_field("end_date");    
}

function on_start_date_changed(frm){
    frm.set_df_property('end_date', 'read_only', 0);   
    const _date = new Date(frm.doc.start_date);  
    const _duration =   frm.doc.membership_duration;   
    switch(frm.doc.duration_base_on){
        case 'Day(s)':
            frm.doc.end_date = new Date(_date.setDate(_date.getDate() + _duration));   
            break
        case 'Week(s)':
            frm.doc.end_date = new Date(_date.setDate(_date.getDate() + (_duration * 7) - 1));   
            break;
        case 'Month(s)':
            const new_month = new Date(_date.setMonth(_date.getMonth() +_duration)); 
            frm.doc.end_date =  new Date(new_month.setDate(new_month.getDate() -1)); 
            break;
        case 'Year(s)':
            const new_year = new Date(_date.setFullYear(_date.getFullYear() +_duration)); 
            frm.doc.end_date =  new Date(new_year.setDate(new_year.getDate() -1)); 
            break;
        default:
            frm.doc.end_date  = frm.doc.start_date;
            break;
    }
    frm.refresh_field("end_date");  
    frm.set_df_property('end_date', 'read_only', 1);   
}