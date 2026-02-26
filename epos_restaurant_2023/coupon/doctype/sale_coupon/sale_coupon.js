// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sale Coupon", {
	refresh(frm) {
	},

    onload(frm){
        on_member_type_changed(frm)
    },
    duration_base_on:function(frm){
        on_duration_base_on_changed(frm,true)
    },

    duration:function(frm){
        on_duration_changed(frm,true)
    },

    member_type:function(frm){
        on_member_type_changed(frm, true)
    },


    member:function(frm){
        on_member_changed(frm,true)
    },
 
    price:function(frm){
        on_price_changed(frm,true)
    },
    discount_type:function(frm){
        on_discount_type_changed(frm,true)
    },
    discount_value:function(frm){
        on_discount_value_changed(frm,true)
    }
});

function on_duration_base_on_changed(frm, changed){
    on_duration_changed(frm,changed)
}

function on_duration_changed(frm, changed){
    if(changed){
        frm.set_df_property('end_date', 'read_only', 0);
        frm.set_df_property('end_date', 'read_only', 0);
        const _date = new Date(frm.doc.start_date);  
        const _duration =   frm.doc.duration;   
        let _end_date = _date;
        switch(frm.doc.duration_base_on){
            case 'Day(s)':
                _end_date = new Date(_date.setDate(_date.getDate() + _duration));   
                break
            case 'Month(s)':
                const new_month = new Date(_date.setMonth(_date.getMonth() +_duration)); 
                _end_date =  new Date(new_month.setDate(new_month.getDate() -1)); 
                break;
        }  
        frm.doc.end_date = _end_date;  
        frm.doc.expiry_date = _end_date;
        frm.refresh_field("end_date"); 
        frm.refresh_field("expiry_date"); 
        
        frm.set_df_property('end_date', 'read_only', 1);
        frm.set_df_property('expiry_date', 'read_only', 1);
    }
}



function on_member_type_changed(frm, changed){
    frm.set_df_property('member', 'hidden',0);
    if(changed){       
        if(frm.doc.member_type=="Individual"){
            frm.doc.member = ""
            frm.set_df_property('member', 'hidden', 1);
            reset_and_refresh_member_fields(frm,true)
        }    
        frm.refresh_field("member");   
    }else{
        if(frm.doc.member_type=="Individual"){
            frm.set_df_property('member', 'hidden', 1);
        }
    }    
}

function on_member_changed(frm, changed){
    if((frm.doc.member|| "") != ""){
        frappe.db.get_doc("Customer", frm.doc.member).then((r)=>{
            frm.doc.member_name = r.customer_name_en;
            frm.doc.member_name_kh = r.customer_name_kh;
            frm.doc.gender = r.gender;
            frm.doc.phone_number = r.phone_number;
            frm.doc.phone_number_2 = r.phone_number_2;

            reset_and_refresh_member_fields(frm)           
        })
    }else{

    } 
}

function on_coupon_type_changed(frm,changed){
    calculate_grand_total(frm,changed)
}

function on_price_changed(frm, changed){
    calculate_grand_total(frm,changed)
}

function on_discount_type_changed(frm,changed){
    calculate_grand_total(frm,changed)
}


function on_discount_value_changed(frm,changed){
    calculate_grand_total(frm,changed)
}

function calculate_grand_total(frm,changed){ 
    frm.set_df_property('grand_total', 'read_only',0);
    frm.set_df_property('payment_balance', 'read_only',0);
    let discount_amount = frm.doc.discount_value;
    if(frm.doc.discount_type=="Percent"){
        discount_amount =  frm.doc.price * ( frm.doc.discount_value / 100)
    }
    frm.doc.grand_total = frm.doc.price - discount_amount;
    frm.doc.payment_balance =  frm.doc.grand_total - frm.doc.total_payment_amount;
    
    frm.set_df_property('grand_total', 'read_only',1);
    frm.set_df_property('payment_balance', 'read_only',1);
    frm.refresh_field("grand_total");
    frm.refresh_field("payment_balance");
}


function reset_and_refresh_member_fields(frm,reset){
    if(reset==1){
        frm.doc.member_name = ""
        frm.doc.member_name_kh = ""
        frm.doc.phone_number = ""
        frm.doc.phone_number_2 = ""
    }
    frm.refresh_field("member_name");    
    frm.refresh_field("member_name_kh");    
    frm.refresh_field("phone_number");    
    frm.refresh_field("phone_number_2");    
    frm.refresh_field("gender");    
}

function update_summary(frm){
    if(frm.doc.docstatus ==0 ){
        const payments = frm.doc.payments
        let total_payment_amount = payments==undefined?0: payments.reduce((n, d) => n + d.payment_amount, 0)
        frm.set_value('total_payment_amount',total_payment_amount);
        frm.refresh_field("total_payment_amount");

        frm.set_value('payment_balance',  (frm.doc.grand_total||0) - total_payment_amount);
        frm.refresh_field("payment_balance");
        
    }
}

//sale coupon items
frappe.ui.form.on('Sale Coupon Items', { 
	coupon_type(frm,cdt, cdn){ 
        const row = locals[cdt][cdn];
        //get coupon type
        frappe.db.get_doc("Sale Coupon Type",row.coupon_type).then((r)=>{ 
            row.regular_price = r.price;
            row.price = r.price;
            row.total_visit = r.total_visit;
            row.amount = row.price * (row.quantity || 1);

            update_sale_coupon_items(frm,cdt, cdn);
        }) 
	},

    quantity(frm,cdt, cdn){
        update_sale_coupon_items(frm,cdt, cdn);
    },

    price(frm,cdt, cdn){      
        update_sale_coupon_items(frm,cdt, cdn);
    },

    items_remove: function (frm){
		update_sale_coupon_summary(frm);
	},
})

function update_sale_coupon_items(frm,cdt, cdn){
    const row = locals[cdt][cdn];
    row.amount = row.price * (row.quantity || 1);
    frm.refresh_field("items");
    
    update_sale_coupon_summary(frm);
}
function update_sale_coupon_summary(frm){
    const items = frm.doc.items
    let total_price = items==undefined?0: items.reduce((n, d) => n + d.amount, 0);
    let limit_visit = items==undefined?0: items.reduce((n, d) => n + (d.total_visit * d.quantity), 0);
    frm.set_value('regular_price',total_price);
    frm.set_value('price',total_price);
    frm.set_value('limit_visit',limit_visit);
    frm.refresh_field("price");
    
    //
}


// sale coupon payment
frappe.ui.form.on('Sale Coupon Payment', { 
	input_amount(frm,cdt, cdn){ 
        const row = locals[cdt][cdn];
        row.payment_amount = row.input_amount / (row.exchange_rate || 1);
        update_summary(frm);
	},
    payments_remove: function (frm){
		update_summary(frm);
	},
})


