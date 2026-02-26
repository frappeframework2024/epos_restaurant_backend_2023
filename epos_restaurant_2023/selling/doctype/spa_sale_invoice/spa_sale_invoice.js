// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("SPA Sale Invoice", {
	refresh(frm) { 

        // Hide the sidebar
        frm.page.sidebar.hide();
        // Hide the comments section
        frm.timeline.wrapper.hide();
         setTimeout(() => {
            $('.comment-box').hide();
            $('.dropdown-menu li:contains("Print")').hide();
            $('.dropdown-menu li:contains("Duplicate")').hide();
            $('.dropdown-menu li:contains("Links")').hide();
            $('.dropdown-menu li:contains("Rename")').hide();
            $('.dropdown-menu li:contains("Jump to field")').hide();
            $('.dropdown-menu li:contains("Email")').hide();
            $('.dropdown-menu li:contains("Redo")').hide();
            $('.dropdown-menu li:contains("Undo")').hide();
            $('.dropdown-menu li:contains("Remind Me")').hide();
        }, 100);


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


        if (frm.is_new()) {
            frm.remove_custom_button('Print');
            frm.page.clear_icons();  // hides print, email, etc. icons in the top-right
        }


         // Show the button only if submitted
        if (frm.doc.docstatus === 1) { 
            if(frappe.perm.has_perm('SPA Sale Invoice', 0, 'amend')){
                frm.add_custom_button('Edit Invoice', function() {
                // Example: Set doc to draft (not recommended unless intentional)

                    frappe.confirm(
                        'Are you sure you want to edit this invoice?',
                        // Confirm callback
                        () => {
                        frappe.call({
                            method: "epos_restaurant_2023.selling.doctype.spa_sale_invoice.spa_sale_invoice.on_edit_to_remove_sale",
                            args: {
                                sale: frm.doc.sale,
                                name: frm.doc.name
                            },
                            callback: function() {
                                frappe.show_alert("Docstatus set to Draft");
                                frm.reload_doc();
                            }
                        }); },
                        // Cancel callback
                        ()=>{},);
                    });
            }
           
        }

	},

    validate: function(frm) {
        //
    },
    after_save: function(frm) { 
        update_child_table_field_visibility(frm) 
        if (frm.doc.docstatus === 1) {            
            // frappe.set_route('Form', 'SPA Sale Invoice','New');
            frappe.new_doc('SPA Sale Invoice');                    
        }
    },

    discount_type(frm){
        update_invoice_summary(frm)
    },
    discount(frm){
        update_invoice_summary(frm)
    },
    tax_rule(frm){
        update_invoice_summary(frm)
    },
    bank_fee(frm){
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


    time_in(frm, cdt, cdn) {
        const row = locals[cdt][cdn];  

        // let parts = row.time_in.split(':');
        // let startDate = new Date();
        // startDate.setHours(parseInt(parts[0]));
        // startDate.setMinutes(parseInt(parts[1]));
        // startDate.setSeconds(parseInt(parts[2] || 0));

        // // Add duration (in minutes)
        // startDate.setMinutes(startDate.getMinutes());

        // // Format back to "HH:mm:ss"
        // let hh = String(startDate.getHours()).padStart(2, '0');
        // let mm = String(startDate.getMinutes()).padStart(2, '0');
        // let ss = String(startDate.getSeconds()).padStart(2, '0'); 
        // setTimeout(() => {
        //     // Find the correct grid row field input
        //     const grid = frm.fields_dict["items"].grid;
        //     const field = grid.grid_rows_by_docname[cdn];
        //     const $input = $(field.wrapper).find('[data-fieldname="time_in"] input');

        //             // Track whether the change is from manual input or slider
        //     let isManualChange = false;                
        //     // Detect manual input change (typing in the input)
        //     $input.on('input', function() {
        //         isManualChange = true;
        //     });
           
        //     // Detect slider change
        //     $input.on('change', function() {
        //         console.log(isManualChange)
        //         if (!isManualChange) {
        //             console.log("Time changed from the slider.");
        //         } else {
        //             if ($input.length && $input.data('datepicker')) {
        //                 const datepicker = $input.data('datepicker');
        //                 const currentDate = datepicker.selectedDates[0] || new Date();
        //                 currentDate.setHours(parseInt(hh));
        //                 currentDate.setMinutes(parseInt(mm));
        //                 currentDate.setSeconds(parseInt(ss));
        //                 datepicker.selectDate(currentDate);  // Sync UI slider
        //             }
        //         } 
        //         isManualChange = false;
        //     });

             
        // }, 100);

        update_time_out(frm,row)   
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
                            base_unit:e.data('base-unit'),
                            unit:e.data('unit'),
                            duration_value:  e.data('duration'),
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


function update_time_out(frm, row){
    if (row.time_in && row.duration_value) {
        // Parse start_time (expected format: "HH:mm:ss")
        let parts = row.time_in.split(':');
        let startDate = new Date();
        startDate.setHours(parseInt(parts[0]));
        startDate.setMinutes(parseInt(parts[1]));
        startDate.setSeconds(parseInt(parts[2] || 0));

        // Add duration (in minutes)
        startDate.setMinutes(startDate.getMinutes() + row.duration_value);

        // Format back to "HH:mm:ss"
        let hh = String(startDate.getHours()).padStart(2, '0');
        let mm = String(startDate.getMinutes()).padStart(2, '0');
        let ss = String(startDate.getSeconds()).padStart(2, '0');
        let newTime = `${hh}:${mm}:${ss}`;

        // Set the result to another Time field (e.g., time_out)
        frappe.model.set_value(row.doctype, row.name, "time_out", newTime).then(() => { 
            setTimeout(() => {
                const $input = $(`[data-fieldname="time_out"] input`);
                if ($input.length && $input.data('datepicker')) {
                    const datepicker = $input.data('datepicker');
                    const currentDate = datepicker.selectedDates[0] || new Date();
                    currentDate.setHours(parseInt(hh));
                    currentDate.setMinutes(parseInt(mm));
                    currentDate.setSeconds(parseInt(ss));
                    datepicker.selectDate(currentDate);  // Update the picker
                } 
            }, 100);

            frm.fields_dict["items"].grid.refresh();
        }); 
    }
}


function update_item_duration_price(frm, row, data){
    update_child_table_field_visibility(frm)
    row.duration = data[0].portion;
    row.duration_value = data[0].duration_value || 0;
    row.price = data[0].price;
    row.regular_price = data[0].price;
    row.base_unit = data[0].base_unit;
    row.unit = data[0].unit;  
    update_item_amount(frm,row);


    update_time_out(frm,row);
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


     // //load function for child table
    $(grid_row.grid_form.fields_dict.therapist.wrapper).on('click', '#unassign-therapist', function(e) {
        e.preventDefault();
        const tr = e.target.closest("tr");
        
        const employeeId = $(this).data("employee-id")

        let therapist_data = JSON.parse(row.therapist_data||'[]');
        therapist_data = therapist_data.filter(t => t.employee_id !== employeeId);
        
        row.therapist_data = JSON.stringify(therapist_data); 
        const result = therapist_data.map(item => `${item.employee_name} (${item.duration_title})`).join(', ');

        frappe.model.set_value(row.doctype, row.name, "therapist_name", result);        
        tr.remove();
        frm.refresh_field("items"); 
    }); 
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

                // Example validation: check if any button has data-selected="1"
                const therapist = $(dlg.fields_dict.therapist_html.wrapper).find('.therapies_button[data-selected="1"]');
                if (therapist.length === 0) { 
                    frappe.show_alert({
                        message: "Please select a therapist before proceeding.",
                        indicator: "yellow"
                    }); 
                    return;
                }

                const duration = $(dlg.fields_dict.therapist_html.wrapper).find('.durations_button[data-selected="1"]');
                if (duration.length === 0) { 
                    frappe.show_alert({
                        message: "Please select a duration before proceeding.",
                        indicator: "yellow"
                    });  
                    return;
                }

                const commssion = $(dlg.fields_dict.therapist_html.wrapper).find('.commissions_button[data-selected="1"]');
                if (commssion.length === 0) { 
                    frappe.show_alert({
                        message: "Please select a commission before proceeding.",
                        indicator: "yellow"
                    });   
                    return;
                }


                // Optional: Get therapist data from selected button (assuming you stored data-* attributes)
                const therapist_selected = {
                    "employee_id": therapist.data("employee-id"), // or use .attr("data-employee-id")
                    "employee_name": therapist.data("employee-name"),
                    "duration_title": duration.data("duration-title"),
                    "duration": duration.data("duration"),
                    "commission_amount": commssion.data("commission-amount"),
                    "is_overtime": duration.data("is-overtime") || 0
                };

               

                // Assign data to row
                let therapist_data = JSON.parse(row.therapist_data||'[]');
                therapist_data.push(therapist_selected);
                row.therapist_data = JSON.stringify(therapist_data); 
                const result = therapist_data.map(item => `${item.employee_name} (${item.duration_title})`).join(', ');

                frappe.model.set_value(row.doctype, row.name, "therapist_name", result);

               
                on_render_therapist(frm, row);
                dlg.hide();
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
        callback: async function(resp) { 
            const data = resp.message; 
            const dataHtml = frappe.render_template("select_therapist_dialog_template", { therapies: data.therapies, durations:data.durations,commissions:data.commissions, isInIframe: (window.self !== window.top) }); 
            $(dialog.fields_dict.therapist_html.wrapper).html(dataHtml); 
            await select_therapist_load_selected_data()
            dialog.fields_dict.therapist_html.refresh();

           await on_button_render_select_changed(dialog)
        },
        error: function(err) { 
            //
        }
    }); 
}

async function select_therapist_load_selected_data(){
    setTimeout(function() { 

        //durations
        const durations = $('.durations_button'); 
        durations.each(function(i, e) { 
            render_selected_button(e)
        });
        //commission
        const commissions = $('.commissions_button'); 
        commissions.each(function(i, e) { 
            render_selected_button(e)
        });
         
    }, 250);
}

async function on_button_render_select_changed(dialog){
   await on_button_click(dialog, '.therapies_button')
   await on_button_click(dialog, '.durations_button')
   await on_button_click(dialog, '.commissions_button')
}

async function on_button_click(dialog, class_name){
    $(dialog.fields_dict.therapist_html.wrapper).on('click', class_name, function() {      
        const selected = $(this).attr("data-selected");
        $(class_name).each(function() { 
            $(this)[0].style.removeProperty('border-color');
            $(this)[0].style.removeProperty('color');
            $(this).attr('data-selected', 0);
        }); 
        if(selected==0){ 
            $(this).attr('data-selected', 1);
        }
        render_selected_button(this) 
    }); 
}

function render_selected_button(e){   
    const selected = $(e).attr("data-selected") == 1;
    if(selected){
        $(e).each(function() {
            $(e)[0].style.setProperty('border-color', '#ff0000', 'important'); // Custom border color
            $(e)[0].style.setProperty('color', '#ff0000', 'important'); // Custom text color
        });
    }else{
        $(e).each(function() {
            $(e)[0].style.removeProperty('border-color');
            $(e)[0].style.removeProperty('color');
        }); 
    }
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