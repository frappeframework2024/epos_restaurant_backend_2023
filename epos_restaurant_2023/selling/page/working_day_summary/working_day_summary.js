frappe.pages['working-day-summary'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage = Class.extend({
	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Working Day Summary',
			single_column: true
		});
		this.make();
		this.print = this.page.set_primary_action('Print', () => this.onPrint(), 'octicon octicon-printer')
		this.page.add_menu_item('PDF', () =>{this.onPDF()},true )
		this.page.set_secondary_action('View Report', () => this.onViewReport(), 'octicon octicon-plus')
		
		this.property = this.page.add_field({
			label: 'Property',
			fieldtype: 'Link',
			fieldname: 'property',
			options:"Business Branch",
			"reqd": 1

		});
		this.working_day = this.page.add_field({
			label: 'Working Day',
			fieldtype: 'Link',
			fieldname: 'working_day',
			options:"Working Day",
			"reqd": 1
		});

		this.pos_profile = this.page.add_field({
			label: 'POS Profile',
			fieldtype: 'Link',
			fieldname: 'pos_profile',
			options:"POS Profile",
			"reqd": 1
		});

		this.lang = this.page.add_field({
			label: 'Language',
			fieldtype: 'Link',
			fieldname: 'lang',
			options:"Language",
			default:"en"
		});
		this.report_name = this.page.add_field({
			label: 'Report',
			fieldtype: 'Link',
			fieldname: 'report',
			options:"POS Print Format Setting",
			filters: {
				'print_format_doc_type': "Working Day"
			},

		});
		this.letter_head = this.page.add_field({
			label: 'Letter Head',
			fieldtype: 'Link',
			fieldname: 'letter_head',
			options:"Letter Head"

		});
		this.iframe = document.querySelector("#iframe_working_day_summary")
		
		this.iframe.addEventListener('load', function() { 
			const iframe_report = document.querySelector("#iframe_working_day_summary")
			iframe_report.style.height = iframe_report.contentWindow.document.body.scrollHeight + 'px';
		});
	},
	make: function() {
		$(frappe.render_template("working_day_summary", this)).appendTo(this.page.main);
	},
	onViewReport:function(){
		let newUrl;
		if(this.property.get_value() != ''){
			newUrl = "/printview?doctype=Working%20Day&name="+ encodeURI(this.working_day.get_value()) +"&format="+ encodeURI(this.report_name.get_value()) +"&settings=%7B%7D&show_toolbar=0&working_day="+ encodeURI(this.working_day.get_value()) +"&pos_profile="+  encodeURI(this.pos_profile.get_value()) +"&_lang="+ encodeURI(this.working_day.get_value()) + "&no_letterhead=0&show_toolbar=0&letterhead="+ encodeURI(this.letter_head.get_value()) + "&refresh=2.886933436472656"
			this.iframe.src = newUrl;
			
		}else{
			frappe.msgprint("Please Select <strong>Property</strong> to View Report.")
		}
	},
	onPrint: function(){
		this.iframe.contentWindow.print()
	},
	onPDF: function(){
		const pdfUrl = `/api/method/frappe.utils.print_format.download_pdf?doctype=Working%20Day&name=${encodeURI(this.working_day.get_value())}&no_letterhead=0&show_toolbar=0&letterhead=${this.letter_head.get_value()}&format=${encodeURI(this.report_name.get_value())}&pos_profile=${encodeURI(this.pos_profile.get_value())}&no_letterhead=0&show_toolbar=0&letterhead=${encodeURI(this.letter_head.get_value())}&settings=%7B%7D&_lang=${this.lang.get_value()}`
		window.open(pdfUrl, '_blank');
	}
})


// frappe.pages['end-of-day-report'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'End of Day Report',
// 		single_column: true
// 	});
// 	let filters={}
// 	let $btnViewReport = page.set_secondary_action('View Report', () => onViewReport(), 'octicon octicon-plus')
// 	let $btnPrintReport = page.set_primary_action('Print', () => onPrintReport(), 'octicon octicon-printer')




// 	function onViewReport(){
// 		alert(filters.property)
// 	}
	

// 	function onPrintReport(){
// 		alert(123)
// 	}


// }