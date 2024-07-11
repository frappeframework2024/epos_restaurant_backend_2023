 
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
			$(frappe.render_template("pending_order", result.message)).appendTo(this.content_container);
			
			// $('.table-number').on('click', function (e) {
			// 	e.preventDefault();
			// 	frappe.msgprint(frappe.render_template("pending_order_detail",{data:["data1","data 2","Item 3","Item 4","Item 5"]}))
			//   });

		})	

	},

	onReload:function(){ 
		this.make();
	}
})
 