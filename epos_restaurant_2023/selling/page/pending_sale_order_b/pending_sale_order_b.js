 
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
		this.property = this.page.add_field({
			label: 'Property',
			fieldtype: 'Link',
			fieldname: 'property',
			options:"Business Branch",
			"reqd": 1,
		});

		this.pos_profile = this.page.add_field({
			label: 'POS Profile',
			fieldtype: 'Link',
			fieldname: 'pos_profle',
			options:"POS Profile",
			"reqd": 1
		});
 
		
	},
	make: function() {
		$(this.content_container).empty(); 
		let param = {
			"param":{
				"business_branch": this.property.get_value(),
				"pos_profile": this.pos_profile.get_value(),
			}
		}

		frappe.call("epos_restaurant_2023.selling.page.pending_sale_order_b.pending_order.get_pending_order",param).then(result=>{		 
			$(frappe.render_template("pending_order", result.message)).appendTo(this.content_container);
			$('.table-number').on('click', function (e) {
				e.preventDefault();
				frappe.msgprint($(this).html())
			  });

		})	

	},

	onReload:function(){ 
		this.make();
	}
})
 