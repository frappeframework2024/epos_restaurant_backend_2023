 
frappe.pages['pending-sale-order-b'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}


MyPage = Class.extend({
	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Pending Sale Order',
			single_column: true
		});
		this.page.set_secondary_action('Reload', () => this.onReload(), 'octicon octicon-plus')
		
		// Create a container for the filters
		this.filter_container = $('<div class="filter-container"></div>').appendTo(this.page.main);
	
		// Create a container for the rendered content
		this.content_container = $('<div class="content-container"></div>').appendTo(this.page.main);
		// this.make();
		let root = this;
		this.property = this.page.add_field({
			label: 'Property',
			fieldtype: 'Link',
			fieldname: 'property',
			options:"Business Branch",
			"reqd": 1,
			change() {
				root.pos_profile.df.filters= {
					business_branch: this.get_value()
				}
				root.pos_profile.set_value('')
				this.refresh();
				
			}
		})
		this.pos_profile = this.page.add_field({
			label: 'POS Profile',
			fieldtype: 'Link',
			fieldname: 'pos_profile',
			options:"POS Profile",
			"reqd": 1,
			change(){
				if (root.pos_profile.get_value()){
					root.make()
				}
				
			}
		})

		async function get_dynamic_default() {
			
			const result = (await frappe.db.get_list("Business Branch"));
			return result[0].name;
		}
		
		// Set the default value after rendering the field
		(async () => {
			const default_value = await get_dynamic_default();
			if (default_value) {
				// Set the value of the field
				
				this.property.set_value(default_value);
				this.pos_profile.df.filters= {
					business_branch: default_value
				}
			}
		})();

		
 
		
	},
	make: function() {
		$(this.content_container).empty(); 
		if (this.property.get_value()=="") frappe.throw("Please Select Property.")
		if (this.pos_profile.get_value()=="") frappe.throw("Please Select POS Profile.")
		let param = {
			"param":{
				"business_branch": this.property.get_value(),
				"pos_profile": this.pos_profile.get_value(),
			}
		}

		frappe.call("epos_restaurant_2023.selling.page.pending_sale_order_b.pending_order.get_pending_order",param).then(result=>{		
			result.message.table_groups.forEach(group => {
				group.tables.forEach(item => {
					item.sales.forEach(s => {
						s.sale = btoa(JSON.stringify(s));
					});
					item.sales_json = btoa(JSON.stringify(item.sales));
				}); 
			});
			$(frappe.render_template("pending_order", result.message)).appendTo(this.content_container);
			const self = this;

			$('.table-number').on('click', function (e) {	
				
				const sales = JSON.parse(atob($(this).data("sales")));
				if(sales.length > 1){
					const saleDialog = new frappe.ui.Dialog({
						title: 'Choose Invoices',
						size: 'small',
						fields: [
							{
								fieldtype: 'HTML',
								fieldname: 'iframe_area',
								options: `${frappe.render_template("pending_order_detail",{sales: sales, iframe:undefined})}`								
							}
						]
					});				
					saleDialog.show();

					// 🔽 Add event listener for sale-item
					saleDialog.$wrapper.find('.sale-item').on('click', function (e) {
						e.preventDefault();
						const saleData = JSON.parse(atob($(this).data('sale')));
						self.on_view_receipt(saleData);
					});

					
					
				}
				else if(sales.length == 1){
					self.on_view_receipt(sales[0])
				}else{
					// frappe.throw("No Invoice")

				}
			});		
			

		})	.catch(err => {
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Failed to load pending orders: ') + err.message
			});
		});

	},

	 on_view_receipt: function(e) {
		
		const iframe_url = `/printview?doctype=Sale&name=`+encodeURI(e.name)+`&format=`+encodeURI(e.print_format)+`&no_letterhead=0&show_toolbar=0&letterhead=Default%20Letterhead&settings=%7B%7D&_lang=en`;
		const dialog = new frappe.ui.Dialog({
			title: `Bill ID: ${e.name}` ,
			size: 'extra-large',
			fields: [
				{
					fieldtype: 'HTML',
					fieldname: 'iframe_area',
				}
			]
		});			
		dialog.show();
 
		dialog.fields_dict.iframe_area.$wrapper.html(`
			 <div style="height:80vh;">
			<iframe src="${iframe_url}" style="width:100%; height:100%; border:none;"></iframe>
			</div>
		`);
	},
	

	onReload:function(){ 
		this.make();
	}
})
 