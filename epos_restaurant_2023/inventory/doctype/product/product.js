// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
let dialogGoogleSearch = undefined
let myForm = undefined
frappe.ui.form.on("Product", {

    refresh(frm) {
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

        print_barcode_button(frm);

        set_product_indicator(frm);

        frm.set_df_property('naming_series', 'reqd', 0)

        add_search_image_from_google_button(frm)
        change_expired_date(frm)



    },
    setup(frm) {
        for (const key in frm.fields_dict) {
            if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
                frm.fields_dict[key].$wrapper.addClass('custom_control');
            }
        }

        frm.set_query('product_category', () => {
            return {
                filters: {
                    is_group: 0
                }
            }
        });
        // set form to public to reload when change photo from google search
        myForm = frm
        window.addEventListener('message', savePhoto, false);
    },
    generate_variant(frm) {
        frm.call({
            method: 'generate_variant',
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
                    console.log(r.message)
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




        }, __("Action"));
    }
}


function savePhoto(e) {
    if (e.isTrusted) {
        frappe.db.set_value("Product", myForm.doc.name, "photo", e.data.url).then(r => {
            myForm.reload_doc()
        })
        dialogGoogleSearch.hide()
    };
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

}

function set_product_indicator(frm) {
    if (frm.doc.__islocal)
        return;

    frm.call({
        method: 'get_product_summary_information',
        doc: frm.doc,
        callback: function (r) {
            console.log(r)

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