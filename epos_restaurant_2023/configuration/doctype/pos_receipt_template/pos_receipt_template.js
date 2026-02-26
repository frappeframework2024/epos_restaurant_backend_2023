frappe.ui.form.on("POS Receipt Template", {
    refresh(frm) {

        if (!frm.is_new()) {
            frm.add_custom_button(__('Preview'), function () {

                let dialog = new frappe.ui.Dialog({
                    title: 'Preview',
                    fields: [
                        {
                            label: 'Preview',
                            fieldname: 'preview',
                            fieldtype: 'HTML'
                        },
                    ],
                    size: 'extra-large',
                });

                dialog.show();

                setTimeout(function () {
                    frappe.call({
                        method: "epos_restaurant_2023.configuration.doctype.pos_receipt_template.pos_receipt_template.get_print_preview_data",
                        args: { name: frm.doc.name }
                    }).then(result => {

                        // Your template + style from DocFields
                        const html = frappe.render_template("preview", {
                            content: frm.doc.template,     // your html template field
                            style: frm.doc.style           // your css field
                        });

                        // IMPORTANT: Use $wrapper.html(...)
                        dialog.fields_dict.preview.$wrapper.html(html);

                    });
                }, 300);

            });

        }

    },
});
