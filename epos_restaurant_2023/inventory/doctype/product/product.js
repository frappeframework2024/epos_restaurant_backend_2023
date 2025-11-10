// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
let dialogGoogleSearch = undefined
let myForm = undefined

frappe.ui.form.on('Product Variants', {
    opening_qty: function(frm, cdt, cdn) {
        let doc = locals[cdt][cdn];
        let a = frm.previous.product_variants.filter(r => r.variant_code == doc.variant_code)
        if(a != null){
            frappe.model.set_value(cdt, cdn, "opening_qty", a[0].opening_qty);
        }
    }
});

frappe.ui.form.on('Product Price', {
    product_price_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "base_unit", frm.doc.base_unit);
        let doc = locals[cdt][cdn];
        frappe.call({
            method: "epos_restaurant_2023.inventory.inventory.get_uom_conversion_zero",
            args:{
                from_uom:doc.unit,
                to_uom:doc.base_unit
            },
            callback: function (r) {
                frappe.model.set_value(cdt, cdn, "conversion_factor", r.message);
            }
        });
    },
    unit: function(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        if(doc.base_unit){
            frappe.call({
                method: "epos_restaurant_2023.inventory.inventory.get_uom_conversion_zero",
                args:{
                    from_uom:doc.unit,
                    to_uom:doc.base_unit
                },
                callback: function (r) {
                    frappe.model.set_value(cdt, cdn, "conversion_factor", r.message);
                }
            });
        }
    }
});

frappe.ui.form.on("Product", {
     product_code(frm) {
         frappe.call({
            method: "epos_restaurant_2023.inventory.doctype.product.product.check_existing_product",
            args:{
                product_code:frm.doc.product_code
            },
            callback: function (r) {
                if (r.message == 1) {
                    frm.fields_dict["existing_error"].$wrapper.html(`<div style="color: red; text-align: center;width: 100%;margin-bottom:5px">❌ Product code ${frm.doc.product_code} already exist</div>`);
                    const parentDiv = frm.fields_dict.product_code.$wrapper;
                    parentDiv.find('.help-box').hide();
                    parentDiv.css('margin-bottom', '8px');
                }
                else{
                    frm.fields_dict["existing_error"].$wrapper.html('');
                }
            }
        });
    },
    refresh(frm) {
        custom_rename(frm);
        if(!frm.is_new()){
            frm.$wrapper.find('#custom-image-wrapper').remove();
        }
        frm.add_custom_button('Take Photo', () => {
            show_camera_dialog(frm);
          });
        setup_barcode_field("product_code",frm);
        setup_barcode_field("product_code_2",frm);
        setup_barcode_field("product_code_3",frm);
        frm.previous = JSON.parse(JSON.stringify(frm.doc))
        if(!frm.is_new() && frm.doc.is_inventory_product == 1){
            frm.set_df_property("is_inventory_product", "read_only", 1)
        }
        frm.set_query("product", "product_recipe", function () {
            return {
                filters: [
                    ["Product", "is_recipe", "=", 1]
                ]
            }
        });
        frm.set_query("product", "product_combo_menus", function () {
            return {
                filters: [
                    ["Product", "is_combo_menu", "=", 0]
                ]
            }
        });
        const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
        if (!isMobile) {
            // frm.dashboard.render_heatmap()
            // frappe.call({
            //     method: "epos_restaurant_2023.api.api.get_product_activity_log",
            //     args:{
            //         product:frm.doc.name,
            //         doctype:frm.doc.doctype
            //     },
            //     callback: function (r) {
            //         if (r.message) {
                        
            //             new frappe.Chart(".heatmap", {
            //                 type: 'heatmap',
            //                 start: new Date(moment().subtract(1, 'year').toDate()),
            //                 countLabel: "transaction",
            //                 discreteDomains: 1,
            //                 radius: 3, // default 0
            //                 data: {
            //                     'dataPoints': r.message
            //                 },
                            
            //             });
                        
            //         }
            //     }
            // });
        }

        
        print_barcode_button(frm);

        set_product_indicator(frm);

        frm.set_df_property('naming_series', 'reqd', 0)

        add_search_image_from_google_button(frm)
        change_expired_date(frm)


      // frm.fields_dict['qb_product_name'].get_query = function() {           
        //     return {
        //         query: 'epos_restaurant_2023.api.quickbook_intergration.qb_product.get_product_autocomplete',
        //         filters:{
        //             "name": frm.doc.qb_product_name
        //         }
        //     };
        // }; 



         // auto-complete select product from qb 
        let $dropdown;
        frm.fields_dict['qb_product_name'].$input.on('input', debounce(function(){
                 let inputValue = $(this).val();
                if (inputValue.length > 0) {
                    frappe.call({
                        method: 'epos_restaurant_2023.api.quickbook_intergration.qb_product.get_product_autocomplete',
                        freeze: true,
                        args: {
                            name: inputValue,
                        },
                        callback: function(r) {
                            if (r.message) {
                                let suggestions = r.message;                            
                                // Clear existing dropdown
                                if ($dropdown) {
                                    $dropdown.remove();
                                } 

                                // Create dropdown if it doesn't exist
                                $dropdown = $('<ul role="listbox" id="e-custom" style="min-width: 100%;">')
                                    .appendTo(frm.fields_dict['qb_product_name'].$input.parent());

                                $.each(suggestions, function(index, item) { 
                                    $('<li><a><p><strong>'+item+'</strong></p></a></li>')
                                        // .text(item) 
                                        .appendTo( $dropdown)
                                        .on('click', function() {
                                            frm.set_value('qb_product_name',item); // Set the selected item
                                            $dropdown.remove(); // Remove dropdown after selection
                                        });
                                });

                                // Hide dropdown if no suggestions
                                if (suggestions.length === 0) {
                                    $dropdown.remove();
                                } 

                            }
                        }
                    });
                }else{
                if ($dropdown) {
                        $dropdown.remove();
                    }
                }

            }, 400)          
            
        );

        // Handle blur event
        frm.fields_dict['qb_product_name'].$input.on('blur', function() {
            setTimeout(function() {
                if ($dropdown) {
                    $dropdown.remove();
                }
            }, 400);
        });

        // end auto-complete select product from db



    },
    onload(frm){
        if(!frm.is_new()){
            frm.$wrapper.find('#custom-image-wrapper').remove();
        }
        frm.fields_dict['qb_product_name'].get_query = function() {           
            return {
                query: 'epos_restaurant_2023.api.quickbook_intergration.qb_product.get_product_autocomplete',
            };
        }; 
    },
    setup(frm) {
        frappe.realtime.on("product_available_shifts", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
        });
        frappe.realtime.on("product_menus", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
        });
        frappe.realtime.on("product_printers", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
        });
        for (const key in frm.fields_dict) {
            if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
                frm.fields_dict[key].$wrapper.addClass('custom_control');
            }
        }    
        // set form to public to reload when change photo from google search
        myForm = frm
        window.addEventListener('message', savePhoto, false);
    },

    qb_product_name(frm,cdt, cdn){ 
        if((frm.doc.qb_product_name||"" )!="" ){
            frappe.call({
                method:"epos_restaurant_2023.api.quickbook_intergration.qb_product.get_product_by_name",
                freeze: true,
                args:{
                    "name":frm.doc.qb_product_name
                },
                callback:function(resp){
                    frm.doc.qb_product_id = resp.message.Id  ;
                    frm.refresh_field("qb_product_id");
                },
                error:function(err){
                    frm.doc.qb_product_id = undefined;
                    frm.refresh_field("qb_product_id");
                    console.log({"Bug" : err})
                }
            }) ;
        }else{
            row.qb_product_id = undefined;
            frm.refresh_field("qb_product_id");
        }
	},


    generate_variant(frm) {
        frm.call({
            method: 'generate_variants',
            doc: frm.doc,
            callback: function (r) {
                if (r.message) {
                    frm.set_value('product_variants', r.message);
                }
            },
            async: true,
        });
    },
    is_timer_product: function (frm) {
        if (frm.doc.is_timer_product == 1 && (frm.is_new() || frm.doc.roundup_list.length == 0)) {
            frm.call({
                method: 'generate_roundup',
                doc: frm.doc,
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("roundup_list", r.message)
                    }
                },
                async: true,
            });
        }
    },

});

function show_camera_dialog(frm) {
    let streamRef;
    let d = new frappe.ui.Dialog({
        title: 'Take a Photo',
        fields: [
          {
            fieldname: 'camera_html',
            fieldtype: 'HTML'
          },
          {
            label: 'Take Photo',
            fieldname: 'take_photo',
            fieldtype: 'Button',
            click: () => {
              const canvas = document.getElementById('canvas');
              const video = document.getElementById('video');
              const context = canvas.getContext('2d');
              context.drawImage(video, 0, 0, canvas.width, canvas.height);
              const imageData = canvas.toDataURL('image/png');
              // Call backend to save
              frappe.call({
                method: "epos_restaurant_2023.inventory.doctype.product.product.upload_photo",
                args: {
                    base64_image: imageData
                },
                callback: function(r) {
                  if (!r.exc) {
                    if(frm.is_new()){
                        frm.set_value("photo", r.message);
                        show_taken_photo(frm)
                    }
                    else{
                        frm.set_value("photo", r.message);
                        show_taken_photo(frm)
                        frm.save();
                    }
                  }
                }
              });
              d.hide();
            }
          }
        ]
      });
    $(d.$wrapper).on('hide.bs.modal', function () {
        d.$wrapper.remove();
        d = null;
        const video = document.getElementById('video');
        if (video) {
            video.pause();
            video.srcObject = null;
        }
        if (streamRef) {
            streamRef.getTracks().forEach(track => track.stop());
        }
    });
    d.show();
    setTimeout(() => {
        const button_wrapper = d.fields_dict.take_photo.$wrapper;
        button_wrapper.css({
            'text-align': 'right',
            'margin-top': '20px'
        });
        let btn = d.fields_dict.take_photo.$wrapper.find('button');
        btn.css({
            'color': '#fff',            // text color
            'background-color': '#007bff', // custom background
            'border-color': '#007bff',
            'height': '50px',
            'font-size': '15px',
            'border-radius': '5px',
        });
    }, 100);
    d.$wrapper.find('.modal-dialog').addClass('modal-lg');
  
    // Inject HTML for camera feed
    const wrapper = d.fields_dict.camera_html.$wrapper;
    wrapper.html(`
      <div style="text-align: center;">
        <video id="video" autoplay playsinline style="width: 100%; max-width: 100%; height: auto; border-radius: 8px;"></video>
        <canvas id="canvas" width="960" height="1280" style="display: none;"></canvas>
      </div>
    `);
    
    // Delay to ensure DOM is ready
    setTimeout(() => {
      const video = document.getElementById('video');
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" }
        }).then(function(stream) {
          streamRef = stream;
          video.srcObject = stream;
          video.play().catch(err => {
            console.error('Error playing video:', err);
        });
        }).catch(function(err) {
          frappe.msgprint("Camera error: " + err.message);
        });
      } else {
        frappe.msgprint("Camera not supported.");
      }
    }, 200);
  }

function show_taken_photo(frm) {
    const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
    if (isMobile && frm.is_new()) {
        frm.$wrapper.find('#custom-image-wrapper').remove();
        const imageUrl = frm.doc.photo;
        if (imageUrl) {
            const imageHtml = `<div id="custom-image-wrapper" style="text-align:center"><img src="${imageUrl}"  style="width: 80%; height: auto; border-radius:4px; border:1px solid #ccc;"/></div>`;
            console.log(imageHtml);
            $('.layout-main-section').first().before(imageHtml);
        }
    }
}

function custom_rename(frm) {
    frm.page.add_menu_item(__('Rename Product'), () => {
    const dialog = new frappe.ui.Dialog({
        title: 'Rename',
        fields: [
            {
                label: 'New Code',
                fieldname: 'new_name',
                fieldtype: 'Data',
                reqd: 1
            },
                {
                fieldtype: 'HTML',
                fieldname: 'error_msg'
            }
        ],
        primary_action_label: 'Rename',
        primary_action(values) {
            frappe.call({
                method: 'epos_restaurant_2023.inventory.doctype.product.product.custom_rename_doc',
                args: {
                    doctype: frm.doc.doctype,
                    old: frm.doc.name,
                    new: values.new_name,
                    merge: 0
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.set_route('Form', frm.doc.doctype, values.new_name);
                    }
                }
            });
            dialog.hide();
        }
    });
    dialog.show();
    const $rename_btn = dialog.get_primary_btn();
    setTimeout(() => {
        const $input_wrapper = dialog.fields_dict.new_name.$wrapper;
        dialog.fields_dict.new_name.$input.on('input', async function() {
        const val = $(this).val().trim();
        dialog.fields_dict.error_msg.$wrapper.html('');
        $rename_btn.prop('disabled', false);
        if (!val) {
            $rename_btn.prop('disabled', true);
            return;
        }
        try {
            check_existing_product(dialog,frm.doc.doctype, val,$rename_btn);
        } catch (e) {
            console.error(e);
        }
        });
        const $input = $input_wrapper.find('input');
        const $icon = $(`
            <span style="position: absolute; right: 10px; top: 72%; transform: translateY(-50%); cursor: pointer;">
                <a class="btn-open no-decoration" title="${__("Scan")}">
                    ${frappe.utils.icon("scan", "sm")}
                </a>
            </span>`);
        $input_wrapper.css('position', 'relative');
        $input.css('padding-right', '30px');
        $input_wrapper.append($icon);
        $icon.on('click', () => {
            const scanner = new frappe.ui.Scanner({
                dialog: true,
                on_scan: (data) => {
                    dialog.set_value('new_name', data.result.text);
                    check_existing_product(dialog,frm.doc.doctype, data.result.text,$rename_btn);
                }
            });
            scanner.show();
        });
    }, 100);
});
}

async function check_existing_product(dialog,doctype,result,$rename_btn) {
    const exists = await frappe.db.exists(doctype, result);
    if (exists) {
        dialog.fields_dict.error_msg.$wrapper.html(
        `<div style="color: red; text-align: center;width: 100%;">❌ Product code ${result} already exist</div>`
        );
        $rename_btn.prop('disabled', true);
    } else {
        dialog.fields_dict.error_msg.$wrapper.html('');
        $rename_btn.prop('disabled', false);
    }
}

function setup_barcode_field(field_name,frm) {
    field = frm.fields_dict[field_name];
    field.$wrapper.append(
        `<span class="link-btn">
            <a class="btn-open no-decoration" title="${__("Scan")}">
                ${frappe.utils.icon("scan", "sm")}
            </a>
        </span>`
    );
    this.$scan_btn = field.$wrapper.find(".link-btn");
    this.$scan_btn.toggle(true);
    this.$scan_btn.on("click", "a", () => {
        setTimeout(() => {
            new frappe.ui.Scanner({
                dialog: true,
                multiple: false,
                on_scan(data) {
                    if (data && data.result && data.result.text) {
                        frm.doc[field_name] = "";
                        frm.doc[field_name] = data.result.text;
                        frm.refresh_field(field_name);
                        if(field_name == "product_code"){
                            frappe.call({
                                method: "epos_restaurant_2023.inventory.doctype.product.product.check_existing_product",
                                args:{
                                    product_code:frm.doc.product_code
                                },
                                callback: function (r) {
                                    if (r.message == 1) {
                                        frm.fields_dict["existing_error"].$wrapper.html(`<div style="color: red; text-align: center;width: 100%;margin-bottom:5px">❌ Product code ${frm.doc.product_code} already exist</div>`);
                                        const parentDiv = frm.fields_dict.product_code.$wrapper;
                                        parentDiv.find('.help-box').hide();
                                        parentDiv.css('margin-bottom', '8px');
                                    }
                                    else{
                                        frm.fields_dict["existing_error"].$wrapper.html('');
                                    }
                                }
                            });
                        }
                    }
                },
            });
        }, 200);
    });
}

// deboounce text  auto-complete
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}


function add_search_image_from_google_button(frm) {
    if (!frm.is_new()) {
        frm.add_custom_button(__('Search Image From Google'), function () {

            dialogGoogleSearch = new frappe.ui.Dialog({
                title: 'Search Image from Google',
                fields: [
                    {
                        label: 'Keyword',
                        fieldname: 'keyword',
                        fieldtype: 'Data',
                        default: frm.doc.product_name_en,
                        onchange: function (e) {

                            frappe.call({ method: "epos_restaurant_2023.api.api.search_image_from_google", args: { keyword: this.value } }).then(result => {
                                const html = frappe.render_template("search_image", { images: result.message })
                                dialogGoogleSearch.set_value("result", html);

                            })
                        }
                    },
                    {
                        label: 'Search Result',
                        fieldname: 'result',
                        fieldtype: 'HTML',
                        options: "<p>Please enter keyword </p>"
                    },


                    // Add other fields as needed
                ],
                size: 'extra-large', // Choose from 'small', 'large', or 'extra-large'

            });

            dialogGoogleSearch.show()

            setTimeout(function () {
                frappe.call({ method: "epos_restaurant_2023.api.api.search_image_from_google", args: { keyword: frm.doc.product_name_en } }).then(result => {
                    const html = frappe.render_template("search_image", { images: result.message })
                    dialogGoogleSearch.set_value("result", html);

                })
            }, 1000)


        });

    }
}

function change_expired_date(frm) {
    if (!frm.is_new() && frm.doc.has_expired_date) {
        frm.add_custom_button(__('Edit Expire Date'), function () {
            frm.call({
                method: 'get_product_summary_information',
                doc: frm.doc,
                callback: function (r) {
                    
                    let dlg = new frappe.ui.Dialog({
                        title: 'Edit Expire Date',
                        size: 'extra-large', 
                        fields: [
                            {
                                fieldname: 'stock_location_product',
                                fieldtype: 'Table',
                                cannot_add_rows: true,
                                in_place_edit: false,
                                data:r.message.stock_information,
                                fields: [
                                    { fieldname: 'stock_location', read_only: 1, fieldtype: 'Data', in_list_view: 1, label: 'Stock Location' },
                                    { fieldname: 'quantity', read_only: 1, fieldtype: 'Float', in_list_view: 1, label: 'QTY' },
                                    { fieldname: 'expired_date', read_only: 1, fieldtype: 'Data', in_list_view: 1, label: 'Expired Date' },
                                    { fieldname: 'new_expired_date', fieldtype: 'Date', in_list_view: 1, label: 'New Exp. Date' },
                                ]
                            }
                        ],
                        primary_action_label: 'Save',
                        primary_action(values) {
                            dlg.freeze = true
                            frappe.call({ method: "epos_restaurant_2023.inventory.doctype.product.product.update_expire_date", args:{data:values} }).then(result => {
                                dlg.hide();
                            })
                            
                        }

                    });

                    dlg.show()
                }
            })




        }, __("Actions"));
    }
}


function savePhoto(e) {
    if((e.data.action || "")=="update_product_photo"){
        if (e.isTrusted) {
            frappe.db.set_value("Product", myForm.doc.name, "photo", e.data.url).then(r => {
                myForm.reload_doc()
            })
            dialogGoogleSearch.hide()
        };
    }
}


function print_barcode_button(frm) {
    frappe.db.get_list('Print Barcode', {
        fields: ['title', 'barcode_url'],
    }).then(res => {
        $.each(res, function (i, d) {
            frm.add_custom_button(__(d.title), function () {
                let msg = frappe.msgprint('<iframe src="' + d.barcode_url + '&rs:Command=Render&rc:Zoom=Page%20Width&barcode=' + frm.doc.name + '&price=' + frm.doc.price + '&product_name_kh=' + encodeURIComponent(frm.doc.product_name_kh) + '&product_name=' + encodeURIComponent(frm.doc.product_name_en) + '&cost=' + frm.doc.cost + '" frameBorder="0" width="100%" height="650" title="Print Barcode"></iframe>', 'Print Barcode')
                msg.$wrapper.find('.modal-dialog').css("max-width", "80%");

            }, __("Print Barcode"));
        });
    });

    frm.add_custom_button("Print Barcode", function () {
                let msg = frappe.msgprint('<iframe src="/embed/barcode-builder?product_code=' + frm.doc.name + '&doctype=Product" frameBorder="0" width="100%" height="650" title="Print Barcode"></iframe>', 'Print Barcode')
                msg.$wrapper.find('.modal-dialog').css("max-width", "80%");

            }, __("Actions"));
}

function set_product_indicator(frm) {
    if (frm.doc.__islocal)
        return;

    frm.call({
        method: 'get_product_summary_information',
        doc: frm.doc,
        callback: function (r) {
            if (r.message) {
                let total_total_quantity = 0;
                $.each(r.message.stock_information, function (i, d) {
                    let indicator = "blue";
                    if (d.quantity < 0) {
                        indicator = "red";
                    }
                    total_total_quantity = total_total_quantity + d.quantity;
                    if (d.expired_date) {
                        frm.dashboard.add_indicator(d.stock_location + ": " + d.quantity.toFixed(r.message.precision) + " " + d.unit + ' (Exp. On ' + d.expired_date + ')', indicator);

                    } else {
                        frm.dashboard.add_indicator(d.stock_location + ": " + d.quantity.toFixed(r.message.precision) + " " + d.unit, indicator);
                    }

                });
                if (r.message.stock_information.length > 1) {
                    frm.dashboard.add_indicator(__("Total Quantity: {0}", [total_total_quantity.toFixed(r.message.precision)]), total_total_quantity > 0 ? "blue" : "red");
                }

                if (r.message.total_annual_sale > 0) {
                    frm.dashboard.add_indicator(__("Annual Sale: {0}", [format_currency(r.message.total_annual_sale)]), "green");
                }

            }

        },
        async: true,
    });
}
