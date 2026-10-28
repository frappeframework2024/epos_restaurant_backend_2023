// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Currency Exchange", {
	get_current_exchange_rate(frm) {
        if(!frm.doc.posting_date){
            frappe.throw("Please select date")
        }
        if(frm.doc.from_currency == frm.doc.to_currency){
            frappe.throw("Currency cannot be the same")
        }
        frappe.call({
            method: 'epos_restaurant_2023.configuration.doctype.currency_exchange.currency_exchange.get_current_exchange_rate',
            args: {
                posting_date: frm.doc.posting_date,
                base: frm.doc.from_currency,
                quotes: frm.doc.to_currency
            },
            freeze: true,
            freeze_message: __('Getting Exchange Rate...'),
            callback(r) {
                if (r.message) {
                    frm.set_value("exchange_rate_input",r.message.rate)
                    frm.set_value("change_exchange_rate_input",r.message.rate)
                }
            }
        });
	},
});
