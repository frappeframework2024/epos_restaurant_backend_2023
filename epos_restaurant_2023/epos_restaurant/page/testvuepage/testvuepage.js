frappe.pages["testvuepage"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("TestVuePage"),
		single_column: true,
	});
};

frappe.pages["testvuepage"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("testvuepage.bundle.js").then(() => {
		frappe.testvuepage = new frappe.ui.Testvuepage({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}