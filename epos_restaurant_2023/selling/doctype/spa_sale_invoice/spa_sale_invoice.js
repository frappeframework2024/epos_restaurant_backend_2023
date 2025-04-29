// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("SPA Sale Invoice", {
	refresh(frm) { 
        if(frm.doc.__islocal==1 && frm.doc.tax_rule == undefined){
            frm.doc.tax_rule = ""
        }
        if(frm.doc.__islocal==undefined){
            frm.doc._temp_tax_rule = JSON.parse(frm.doc.tax_rule_data||"[]") 

            const html = frappe.render_template("invoice_summary_template", frm.doc )		
            $(frm.fields_dict['invoice_summary'].wrapper).html(html);
        }else{
            $(frm.fields_dict['invoice_summary'].wrapper).html('');
        }

       

        // //load function for child table
        frm.fields_dict['items'].grid.wrapper.on('click', '#assign-therapist', function(e) {
            e.preventDefault();
            let row_name = $(this).data('row-name'); 
            let row = frm.doc.items.find(d => d.name === row_name); 
            on_assign_therapist(frm, row);
        }); 

        update_child_table_field_visibility(frm)
	},

    validate: function(frm) {
        //
    },
    after_save: function(frm) { 
        update_child_table_field_visibility(frm)
    },

    discount_type(frm){
        update_invoice_summary(frm)
    },
    discount(frm){
        update_invoice_summary(frm)
    },
    tax_rule(frm){
        update_invoice_summary(frm)
    }
});

frappe.ui.form.on('SPA Sale Invoice Payment', {
	form_render:function(frm, cdt,cdn){
        
        
		// const doc = locals[cdt][cdn];
		// const element = document.querySelector('[data-name="' + doc.name + '"]');			 
	},   

	payments_remove: function (frm) {
        update_invoice_summary(frm)
	},

    payment_type(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if(row.input_amount){
            row.amount = row.input_amount / (row.exchange_rate || 1);
            frm.refresh_field("payments"); 
            update_invoice_summary(frm) 
            
        }
    },
    input_amount(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if(row.payment_type){
            row.amount = row.input_amount / (row.exchange_rate || 1);
            frm.refresh_field("payments");  
            update_invoice_summary(frm)
        }
    }
});





frappe.ui.form.on('SPA Sale Invoice Product', {
	form_render:function(frm, cdt,cdn){
		const doc = locals[cdt][cdn]; 
		const element = document.querySelector('[data-name="' + doc.name + '"]');		
        doc.__is_open = 1;      
         
 
        update_child_table_field_visibility(frm)
      
        on_render_therapist(frm,doc);  


	}, 
  

	items_remove: function (frm) {
        update_invoice_summary(frm)
	},  
    article(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        frappe.call({
            method: 'epos_restaurant_2023.selling.doctype.spa_sale_invoice.spa_sale_invoice.get_product_by_id',
            type: 'GET',            
            freeze: true,
            args: {
                name:row.article
            },
            callback: function(resp) {
                const val = resp.message;
                if(val.length > 1){
                    const dlg = select_portion_dialog(frm,row, val);
                     
                }else{ 
                    if(val[0].is_require_employee == 1){
                        update_child_table_field_visibility(frm)
                    }
                    update_item_duration_price(frm,row,val);
                }               
            },
            error: function(err) { 
                
                on_reset_value_article(frm,row) 
            }
        });        
    },
	
	price(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
        update_item_amount(frm,row)

	},
	quantity(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		update_item_amount(frm,row)
	},
	discount(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		update_item_amount(frm,row)
	},
	discount_type(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		update_item_amount(frm,row)
	},
	
})



 

function on_reset_value_article(frm, row){
    row.article = "";
    update_child_table_field_visibility(frm)
    frm.refresh_field("items");  
}


function select_portion_dialog(frm,row,data){
    if(!row.__is_busy ){
        row.__is_busy = true;
        row.__reset_value = true;
        const fields = [
            { fieldtype: 'HTML', fieldname: 'portions' },
        ];


        const dlg = new frappe.ui.Dialog({
            title: "Duration/Portion",
            fields: fields,
            size: 'small',
            primary_action_label: "Accept",
            primary_action: function() {
                const active_button = $('.duration_portion_option.active'); 
                if(active_button){
                    var e = $(active_button[0]);                   
                    const result =[
                        {
                            is_require_employee: data[0].is_require_employee || 0,
                            portion:e.data('portion'),
                            price:e.data('price'),
                            base_unit:e.data('base_unit'),
                            unit:e.data('unit')
                        }
                    ]
                    update_item_duration_price(frm, row,result);
                    row.__reset_value = false;
                    row.__is_busy = false;
                    dlg.hide();
                }  
            }
        });
        render_duration_or_portion(data,dlg)

        dlg.show();

        // Handle cancel/close event
        dlg.$wrapper.on('hide.bs.modal', () => {
            const grid_row = frm.fields_dict['items'].grid.grid_rows_by_docname[row.name];    
            if(row.__is_open && row.__is_open==1){
                grid_row.show_form();             
            } 

            $(dlg.fields_dict.portions.wrapper).empty();
            
            if(row.__reset_value == true){
                on_reset_value_article(frm,row)
            }
            row.__is_busy = false;
        });
        return dlg; 
    }
}


function update_item_duration_price(frm, row, data){
    update_child_table_field_visibility(frm)


    row.duration = data[0].portion;
    row.price = data[0].price;
    row.regular_price = data[0].price;
    row.base_unit = data[0].base_unit;
    row.unit = data[0].unit; 
    update_item_amount(frm,row)
}


function render_duration_or_portion(data, dialog) {   
    
    const dataHtml = frappe.render_template("select_portion_template", { data: data, isInIframe: (window.self !== window.top) }); 
    $(dialog.fields_dict.portions.wrapper).html(dataHtml); 
    // Use a small timeout to ensure content is rendered and then add the active class
    setTimeout(function() { 
        const buttons = $('.duration_portion_option'); 
        buttons.each(function(i, e) { 
            if(i==0){
                $(e).addClass('active').each(function() {
                    $(e)[0].style.setProperty('border-color', '#007bff', 'important'); // Custom border color
                    $(e)[0].style.setProperty('color', '#007bff', 'important'); // Custom text color
                });
            }else{
                $(e).removeClass('active').each(function() {
                    // Reset border and text color with !important using setProperty()
                    $(e)[0].style.setProperty('border-color', '#dfdfdf', 'important');
                    $(e)[0].style.setProperty('color', '#4338ca', 'important');
                }); 
            }
        });
         
    }, 250);
    dialog.fields_dict.portions.refresh();

    $(dialog.fields_dict.portions.wrapper).on('click', '.duration_portion_option', function() {
            // Remove 'active' class from all buttons
            $('.duration_portion_option').removeClass('active').each(function() { 
                $(this)[0].style.setProperty('border-color', '#dfdfdf', 'important');
                $(this)[0].style.setProperty('color', '#4338ca', 'important');
            });
        
            // Add 'active' class to the clicked button and apply custom styles with !important
            $(this).addClass('active').each(function() {
                $(this)[0].style.setProperty('border-color', '#007bff', 'important');  
                $(this)[0].style.setProperty('color', '#007bff', 'important');  
            });
    }); 
}


function update_item_amount(frm,row){
    let sub_total = (row.price || 0) * (row.quantity || 1);
    let discount = 0;

    discount = row.discount_type =="Amount"? row.discount : sub_total * ((row.discount || 0) / 100)
    row.discount_amount = discount;
    row.amount =  sub_total - discount;
    frm.refresh_field("items");  

    update_invoice_summary(frm)

}

function update_invoice_summary(frm){ 
    if(frm.doc.items == undefined){
        frm.set_value('items', []);
    }
    if(frm.doc.payments == undefined){
        frm.set_value('payments', []);
    } 

    frappe.call({
        method: 'epos_restaurant_2023.selling.doctype.spa_sale_invoice.spa_sale_invoice.client_script_update_summary',
        type: 'GET',            
        freeze: true,
        args: {
            param:frm.doc
        },
        callback: function(resp) { 
            update_summary_value(frm,resp.message);            
        },
        error: function(err) { 
            update_summary_value(frm, undefined)
        }
    });
}
 
async function update_summary_value(frm, data){
    const t = data;

    //set value to field
    frm.set_value('total_quantity', t.total_quantity || 0);
    frm.set_value('sub_total', t.sub_total||0);
    frm.set_value('item_discount', t.item_discount||0);
    frm.set_value('discount_amount', t.discount_amount || 0);
    frm.set_value('total_discount', t.total_discount || 0);

    frm.set_value('tax_1_rate', t.tax_1_rate || 0);
    frm.set_value('tax_1_amount', t.tax_1_amount || 0);
    frm.set_value('tax_1_taxable_amount', t.tax_1_taxable_amount || 0);
    frm.set_value('tax_2_rate', t.tax_2_rate || 0);
    frm.set_value('tax_2_amount', t.tax_2_amount || 0);
    frm.set_value('tax_2_taxable_amount', t.tax_2_taxable_amount || 0); 
    frm.set_value('tax_3_rate', t.tax_3_rate || 0);
    frm.set_value('tax_3_amount', t.tax_3_amount || 0);
    frm.set_value('tax_3_taxable_amount', t.tax_3_taxable_amount || 0); 

    frm.set_value('total_amount', t.total_amount || 0); 
    frm.set_value('total_paid', t.total_paid || 0); 
    frm.set_value('balance', t.balance || 0); 
    frm.set_value('changed_amount', t.changed_amount || 0); 



    //refresh fields
    frm.refresh_field('total_quantity');
    frm.refresh_field('sub_total');
    frm.refresh_field('item_discount');
    frm.refresh_field('total_discount');

    frm.refresh_field('tax_1_rate');
    frm.refresh_field('tax_1_amount');
    frm.refresh_field('tax_1_taxable_amount');
    frm.refresh_field('tax_2_rate');
    frm.refresh_field('tax_2_amount');
    frm.refresh_field('tax_2_taxable_amount');
    frm.refresh_field('tax_3_rate');
    frm.refresh_field('tax_3_amount');
    frm.refresh_field('tax_3_taxable_amount');

    frm.refresh_field('total_amount');
    frm.refresh_field('total_paid');
    frm.refresh_field('balance');
    frm.refresh_field('changed_amount');

    if(t.tax_rule_data){ 
        frm.doc._temp_tax_rule = t.tax_rule_data
    }else{
        frm.doc._temp_tax_rule = []
    }

    const html = frappe.render_template("invoice_summary_template", frm.doc )		
	$(frm.fields_dict['invoice_summary'].wrapper).html(html);
}



//therapist blog
function on_render_therapist(frm, row){   
    let grid_row = frm.fields_dict['items'].grid.grid_rows_by_docname[row.name]; 
    $(grid_row.grid_form.fields_dict.therapist.wrapper).empty(); 
    row.__therapist_data_json = JSON.parse(row.therapist_data ||'[]') 
    const html = frappe.render_template("selected_therapist_template", {doc:row, enabled: frm.doc.docstatus == 0} )	 
    $(grid_row.grid_form.fields_dict.therapist.wrapper).html(html);
}

function on_assign_therapist(frm,row){
    if(!row.__is_busy ){
        row.__is_busy = true;
        const fields = [
            { fieldtype: 'HTML', fieldname: 'therapist_html' },
        ];

        const dlg = new frappe.ui.Dialog({
            title: "Therapist",
            fields: fields,
            size: 'large',
            primary_action_label: "Accept",
            primary_action: function() {

                const therapist_selected = [
                    {
                        "employee_id":"02",
                        "employee_name":"Mey GBgg",
                        "duration_title":"1H",
                        "duration":60,
                        "commission_amount":1.5,
                        "is_overtime":0
                     }
                ]


                row.therapist_data = JSON.stringify(therapist_selected)
            
                on_render_therapist(frm, row) 
                dlg.hide()

                frm.refresh_field("items");   
            }
        });
    
        render_select_therapist_dialog(frm,row,dlg)


        // Handle cancel/close event
        dlg.$wrapper.on('hide.bs.modal', () => { 
            row.__is_busy = false;

            frm.fields_dict['items'].grid.grid_rows_by_docname[row.name].show_form();
        });
        dlg.show(); 
    }
}
function render_select_therapist_dialog(frm,row,dialog){
    $(dialog.fields_dict.therapist_html.wrapper).empty()
    frappe.call({
        method: 'epos_restaurant_2023.selling.doctype.spa_sale_invoice.spa_sale_invoice.get_therapist_data',
        type: 'GET',            
        freeze: true,
        args: {
            duration:row.duration
        },
        callback: function(resp) { 
            const data = resp.message; 
            const dataHtml = frappe.render_template("select_therapist_dialog_template", { therapies: data.therapies, durations:data.durations,commissions:data.commissions, isInIframe: (window.self !== window.top) }); 
            $(dialog.fields_dict.therapist_html.wrapper).html(dataHtml); 

            dialog.fields_dict.therapist_html.refresh();
        },
        error: function(err) { 
            //
        }
    });



   
    // Use a small timeout to ensure content is rendered and then add the active class
    // setTimeout(function() { 
    //     const buttons = $('.duration_portion_option'); 
    //     buttons.each(function(i, e) { 
    //         if(i==0){
    //             $(e).addClass('active').each(function() {
    //                 $(e)[0].style.setProperty('border-color', '#007bff', 'important'); // Custom border color
    //                 $(e)[0].style.setProperty('color', '#007bff', 'important'); // Custom text color
    //             });
    //         }else{
    //             $(e).removeClass('active').each(function() {
    //                 // Reset border and text color with !important using setProperty()
    //                 $(e)[0].style.setProperty('border-color', '#dfdfdf', 'important');
    //                 $(e)[0].style.setProperty('color', '#4338ca', 'important');
    //             }); 
    //         }
    //     });
         
    // }, 250);
   

    // $(dialog.fields_dict.portions.wrapper).on('click', '.duration_portion_option', function() {
    //         // Remove 'active' class from all buttons
    //         $('.duration_portion_option').removeClass('active').each(function() { 
    //             $(this)[0].style.setProperty('border-color', '#dfdfdf', 'important');
    //             $(this)[0].style.setProperty('color', '#4338ca', 'important');
    //         });
        
    //         // Add 'active' class to the clicked button and apply custom styles with !important
    //         $(this).addClass('active').each(function() {
    //             $(this)[0].style.setProperty('border-color', '#007bff', 'important');  
    //             $(this)[0].style.setProperty('color', '#007bff', 'important');  
    //         });
    // }); 
}



// Function to update field visibility in child table rows
function update_child_table_field_visibility(frm) {
    // Get the child table grid
    let grid = frm.fields_dict['items'].grid;

    // Iterate over each row in the child table
    grid.grid_rows.forEach(function(row) {
        let row_data = row.doc; 
        if (row_data.is_required_therapist === 0) {
            let field_cell = row.wrapper.find(`[data-fieldname="assign_unassigned_therapist"]`); 
            if (field_cell.length) {
                field_cell.hide();
            }
        } else { 
            // Show the field in this row
            let field_cell = row.wrapper.find(`[data-fieldname="assign_unassigned_therapist"]`); 
            if (field_cell.length) {
                field_cell.show();
            }
        }
    });

    // Ensure the grid is refreshed to reflect changes
    frm.refresh_field('items');
}