// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tax Invoice", {
  refresh(frm) {
    if (!frm.doc.__islocal) {
      frm.set_intro(
        "This invoice is a " + frm.doc.tax_invoice_type,
        "blue"
      );

      // set default print format
      frm.meta.default_print_format = frm.doc.default_print_format;
      

      if (frm.doc.document_type == "Sale") {
        getItemListFromSale(frm);
      } else  {
        getItemListFromGuestFolio(frm);
      }
    }
  },
  setup(frm) {
    for (const key in frm.fields_dict) {
      if (
        [
          "Currency",
          "Data",
          "Int",
          "Link",
          "Date",
          "Datetime",
          "Float",
          "Select",
        ].includes(frm.fields_dict[key].df.fieldtype)
      ) {
        frm.fields_dict[key].$wrapper.addClass("custom_control");
      }
    }
  },
});

function getItemListFromSale(frm) {
  $(frm.fields_dict["item_list"].wrapper).html("Loading sale product list...");
  frm.refresh_field("item_list");
  frappe.db
    .get_doc("Sale", frm.doc.document_name)
    .then((result) => {
      let html = frappe.render_template("sale_item_list", { doc: result });
      $(frm.fields_dict["item_list"].wrapper).html(html);
      frm.refresh_field("item_list");

      // summary
      html = frappe.render_template("sale_summary", { doc: result });
      $(frm.fields_dict["invoice_summary"].wrapper).html(html);
      frm.refresh_field("invoice_summary");
    })
    .catch((err) => {
      console.log(err)
      $(frm.fields_dict["item_list"].wrapper).html(
        "Get sale data fail. Please refresh your form"
      );
      frm.refresh_field("item_list");
    });
}

function getItemListFromGuestFolio(frm) {
  $(frm.fields_dict["item_list"].wrapper).html(
    "Loading folio transaction list..."
  );
  frm.refresh_field("item_list");
  frappe.db
    .get_list("Folio Transaction", {
      fields: [
        "name",
        "transaction_number",
        "posting_date",
        "reservation",
        "room_number",
        "parent_reference",
        "type",
        "account_code",
        "account_name",
        "quantity",
        "input_amount",
        "price",
        "amount",
        "discount_amount",
        "total_tax",
        "total_amount",
        "bank_fee_amount",
        "note",
        "creation",
        "owner",
        "modified",
        "modified_by",
        "show_print_preview",
        "print_format",
        "is_auto_post",
        "allow_enter_quantity",
        "target_transaction_number",
        "city_ledger_name",
        "source_transaction_number",
        "report_description",
      ],
      filters: [
        ["transaction_number", "=", frm.doc.document_name],
        ["transaction_type", "=", frm.doc.document_type],
      ],
      order_by: "modified asc",
      limit: 1000,
    })
    .then((result) => {
      const folio_transaction = result;
      folio_transaction.forEach((r) => {
        r.quantity = r.allow_enter_quantity == 1 ? r.quantity : 0;
        r.total_amount =
          r.type == "Credit"
            ? (r.total_amount - r.bank_fee_amount) * -1
            : r.total_amount;
        r.amount = r.type == "Credit" ? r.amount * -1 : r.amount;
        r.price =
          r.type == "Credit" ? (r.price + r.bank_fee_amount) * -1 : r.price;
      });

      let html = frappe.render_template("folio_transaction_list", {
        data: folio_transaction?.filter(
          (r) => (r.parent_reference || "") == ""
        ),
      });
      $(frm.fields_dict["item_list"].wrapper).html(html);
      frm.refresh_field("item_list");
    });

  //folio transaction summary
  frappe
    .call("edoor.api.reservation.get_folio_summary_by_transaction_type", {
      transaction_type: frm.doc.document_type,
      transaction_number: frm.doc.document_name,
    })
    .then((result) => {
      html = frappe.render_template("folio_transaction_summary", {
        data: result.message,
      });
      $(frm.fields_dict["invoice_summary"].wrapper).html(html);
      frm.refresh_field("invoice_summary");
 
    })
    .catch((error) => {
      throw new Error(error.exception || error.message);
    });
}
