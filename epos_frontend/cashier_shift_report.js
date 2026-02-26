// frappe.pages['cashier-shift-report'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Cashier Shift Report',
// 		single_column: true
// 	});
// }
frappe.pages['cashier-shift-report'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}
frappe.ui.form.on('Cashier Shift Report', {
    onload: function(frm) {
        cur_frm.set_query('cashier_shift', function() {
            return {
                filters: [
                    ['Cashier Shift', 'is_edoor_shift', '=', 1]
                ]
            };
        });
    }
});

MyPage = Class.extend({
	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Cashier Shift Report',
			single_column: true
		});
		this.make();
		this.print = this.page.set_primary_action('Print', () => this.onPrint(), 'octicon octicon-plus')
		this.page.set_secondary_action('View Report', () => this.onViewReport(), 'octicon octicon-plus')
		
		this.property = this.page.add_field({
			label: 'Property',
			fieldtype: 'Link',
			fieldname: 'property',
			options:"Business Branch",
			change: () => {
				const selectedProperty = this.property.get_value()

				this.cashier_shift.df.filters.business_branch = selectedProperty;
			},

		});
		this.date = this.page.add_field({
			label: 'Working Date',
			fieldtype: 'Date',
			fieldname: 'date',
			options:"Date",
			default:frappe.datetime.get_today(),
			change: () => {
				const selectedDate = this.date.get_value()

				this.cashier_shift.df.filters.posting_date = selectedDate;
			},
		});

		this.cashier_shift = this.page.add_field({
    		label: 'Cashier Shift',
			fieldtype: 'Link',
			fieldname: 'cashier_shift',
			options: 'Cashier Shift',
			filters: {
				'is_edoor_shift': 1,
				'business_branch': this.property.get_value(),
				'posting_date': this.date.get_value(),
			},
		});
		
		this.ledger_group = this.page.add_field({
			label: 'Group By Ledger Name',
			fieldtype: 'Check',
			fieldname: 'group_by_ledger_type',
			default:1
		});
		this.show_account = this.page.add_field({
			label: 'Show Account Code',
			fieldtype: 'Check',
			fieldname: 'show_account_code',
			default:1 
		});
		this.cash_float = this.page.add_field({
			label: 'Show Cash Float',
			fieldtype: 'Check',
			fieldname: 'show_cash_float',
			default:1
		});
		this.cash_count = this.page.add_field({
			label: 'Show Cash Count',
			fieldtype: 'Check',
			fieldname: 'show_cash_count',
			default:1
		});
		this.report_name = this.page.add_field({
			label: 'Report Name',
			fieldtype: 'Select',
			fieldname: 'report_name',
			options: [
				'Cashier Shift Transaction Detail',
				'Cashier Shift Transaction Summary',
			],
			default:'Cashier Shift Transaction Detail'
			
		});
		this.iframe = document.querySelector("#iframe_cashier_shift_report")
		
		this.iframe.addEventListener('load', function() { 
			const iframe_report = document.querySelector("#iframe_cashier_shift_report")
			iframe_report.style.height = iframe_report.contentWindow.document.body.scrollHeight + 'px';
		});
	},
	make: function() {
		$(frappe.render_template("cashier_shift_report", this)).appendTo(this.page.main);
	},onViewReport:function(){
		const ledgerGroup = this.ledger_group.get_value();
		const showAccount = this.show_account.get_value();
		const cashFloat = this.cash_float.get_value();
		const cashCount = this.cash_count.get_value();
		let newUrl;
		// this.cashier_shift.filters = [
		// 	['Cashier Shift', 'is_edoor_shift', '=', 1],
		// ];
		if(this.property.get_value() != '' && this.cashier_shift.get_value() != ''){
			if (this.report_name.get_value()=="Cashier Shift Transaction Detail"){
				newUrl = "/printview?doctype=Business%20Branch&name="+ encodeURIComponent((this.property.get_value())) +"&format=Night%20Audit%20Cashier%20Shift%20Transaction%20Detail&&settings=%7B%7D&show_toolbar=0&start_date="+this.date.get_value() +"&cashier_shift="+ encodeURI(this.cashier_shift.get_value()) 
						+"&group_by_ledger_type="+ ledgerGroup +"&show_account_code="+ showAccount +"&show_cash_float="+ cashFloat +"&show_cash_count="+ cashCount +"&_lang=en&refresh=13.978092580913248"
				this.iframe.src = newUrl;
			}else if (this.report_name.get_value()=="Cashier Shift Transaction Summary"){
				newUrl = "/printview?doctype=Business%20Branch&name="+ encodeURIComponent((this.property.get_value())) +"&format=Night%20Audit%20Cashier%20Shift%20Transaction%20Summary&&settings=%7B%7D&show_toolbar=0&start_date="+this.date.get_value() +"&cashier_shift="+ encodeURI(this.cashier_shift.get_value())  
				+"&group_by_ledger_type="+ ledgerGroup +"&show_account_code="+ showAccount +"&show_cash_float="+ cashFloat +"&show_cash_count="+ cashCount +"&_lang=en&refresh=13.978092580913248"
				this.iframe.src = newUrl;
			}else{
				this.iframe.src = this.iframe.src + "&refresh=" + (Math.random() * 16)
			}
		}else{
			frappe.msgprint("Please Select <strong>Property</strong> or <strong>Cashier Shift</strong> to View Report.")
		}
		
		
	},
	onPrint: function(){
		this.iframe.contentWindow.print()
	},
	setLinked: function(){
		const property = this.property.get_value();
		if (property) {
			const cashier_shift = this.cashier_shift.get_value();
			cashier_shift.df.get_query = function () {
				return {
					filters: {
						"business_branch": property
					}
				};
			};

		}
	}
})