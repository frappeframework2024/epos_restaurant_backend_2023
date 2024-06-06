// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("eMenu", {
	refresh(frm) {

	},
});


frappe.ui.form.on('eMenu Selection', {
	async sort_product(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
        console.log(doc)
        const products = await  getMenuProduct(doc.menu)
        
        
		let dlg = new frappe.ui.Dialog({
            title: 'Product Sort Order',
            size: 'extra-large', 
            fields: [
                {fieldname:"menu", default:doc.menu,fieldtype:"Data",hidden:1},
                {
                    fieldname: 'products',
                    fieldtype: 'Table',
                    cannot_add_rows: true,
                    in_place_edit: false,
                    data:products,
                    fields: [
                        { fieldname: 'product_code', fieldtype: 'Data', in_list_view: 1, label: 'Product Code',read_only:1 },
                        { fieldname: 'product_name_en', fieldtype: 'Data', in_list_view: 1, label: 'Product Name',read_only:1 },
                        {
                            fieldtype: 'Button',
                            fieldname: 'move_up',
                            label: 'Move Up',
                            in_list_view: 1,
                            click: function(x) {
                                let row = $(this).closest('.grid-row');
                                let index = row.index();
                                reorder_records(dlg, index, Math.max(index - 1, 0));
                            }
                        },
                        {
                            fieldtype: 'Button',
                            fieldname: 'move_down',
                            label: 'Move Down',
                            in_list_view: 1,
                            click: function() {
                                let row = $(this).closest('.grid-row');
                                let index = 1;
                       
                                reorder_records(dlg, index, Math.min(index + 1, dlg.fields_dict.products.df.data.length - 1));
                            
                            }
                        }

                    ]
                }
            ],
            primary_action_label: 'Save',
            primary_action(values) {
                
                frappe.call({ 
                    method: "epos_restaurant_2023.api.emenu.save_emenu_sort_order_products", 
                    args:{data:values} ,
                	freeze: true
                }).then(result => {
                    dlg.hide();
                })
                
            }

        });

        
        dlg.show()
	}
})

function reorder_records(dialog, fromIndex, toIndex) {
    let tableField = dialog.fields_dict.products;
    let data = tableField.df.data;

    if (fromIndex >= 0 && fromIndex < data.length && toIndex >= 0 && toIndex < data.length) {
        let recordToMove = data.splice(fromIndex, 1)[0];
        data.splice(toIndex, 0, recordToMove);
        tableField.grid.refresh();
    } else {
        frappe.msgprint(__('Invalid indices.'));
    }
}

function getMenuProduct(pos_menu) {
  return new Promise(function(resolve, reject) {
        frappe.db.get_list("Temp Product Menu",{fields:["product_code","product_name_en","sort_order"],filters:{pos_menu:pos_menu},order_by:"sort_order",limit:1000}).then(result=>{
            resolve(result);
        })
   
      
     
  });
}

