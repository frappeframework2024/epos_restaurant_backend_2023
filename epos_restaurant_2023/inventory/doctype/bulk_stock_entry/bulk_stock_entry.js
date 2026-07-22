// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

const BULK_STOCK_PRODUCT_OPTION_FIELDS = [
	{ fieldname: "option_1_html", value_field: "option_1", label: "Option 1" },
	{ fieldname: "option_2_html", value_field: "option_2", label: "Option 2" },
	{ fieldname: "option_3_html", value_field: "option_3", label: "Option 3" },
];

frappe.ui.form.on("Bulk Stock Entry", {
	setup(frm) {
		frm.fields_dict.search_product_code.get_query = () => ({
			query:
				"epos_restaurant_2023.inventory.doctype.bulk_stock_entry.bulk_stock_entry.search_product",
		});
	},

	refresh(frm) {
		frm.toggle_display("search_product_code_section", frm.doc.docstatus === 0);

		if (frm.doc.docstatus !== 0) return;

		frm.selected_product_options = frm.selected_product_options || {
			option_1: [],
			option_2: [],
			option_3: [],
		};

		BULK_STOCK_PRODUCT_OPTION_FIELDS.forEach((field) => {
			make_product_option_tag_input(
				frm,
				field.fieldname,
				field.label,
				frm.selected_product_options[field.value_field]
			);
		});
	},

	async get_product(frm) {
		const product_code = (frm.doc.search_product_code || "").trim();
		if (!product_code) {
			frappe.msgprint(__("Please enter a product code."));
			return;
		}
		frappe.dom.freeze("Loading product...")
		await frm.call("get_product", {
			product_code,
			options: frm.selected_product_options,
		})
		frappe.dom.unfreeze()
	},
});

frappe.ui.form.on("Bulk Stock Entry Product", {
	product_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (!row.product_code) {
			frappe.model.set_value(cdt, cdn, "current_quantity", 0);
			return;
		}

		frm.call("get_current_product_qty", {
			row_name: cdn,
		});
	},

	quantity(frm, cdt, cdn) {
		update_product(frm, cdt, cdn);
	},

	cost(frm, cdt, cdn) {
		update_product(frm, cdt, cdn);
	},

	products_remove(frm) {
		clearTimeout(frm.update_summary_timeout);
		frm.update_summary_timeout = setTimeout(() => {
			frm.call("update_summary");
		}, 300);
	},
});

function update_product(frm, cdt, cdn) {
	const row = locals[cdt][cdn];

	frm.call("update_product", {
		row,
	});
}

function make_product_option_tag_input(frm, fieldname, label, tags) {
	const field = frm.fields_dict[fieldname];
	if (!field || !field.$wrapper) return;

	field.$wrapper.empty();

	$("<label>", {
		class: "control-label",
		text: __(label),
	}).appendTo(field.$wrapper);

	const $editor = $("<div>", {
		class: "bulk-stock-product-tag-editor",
		"data-fieldname": fieldname,
	}).css({
		display: "flex",
		"flex-wrap": "wrap",
		gap: "4px",
		"min-height": "38px",
		padding: "5px 6px",
		border: "1px solid var(--border-color)",
		"border-radius": "var(--border-radius)",
		background: "var(--control-bg)",
		cursor: "text",
	});

	const $input = $("<input>", {
		type: "text",
		placeholder: __("Type a value and press Enter"),
	}).css({
		flex: "1 0 90px",
		"min-width": "90px",
		border: 0,
		outline: 0,
		background: "transparent",
	});

	field.$wrapper.append($editor);

	function focus_input() {
		setTimeout(() => {
			$input.trigger("focus");
		}, 0);
	}

	function add_values(value, keep_focus = false) {
		const existing = new Set(tags.map((tag) => tag.toLocaleLowerCase()));
		let changed = false;

		String(value || "")
			.split(/[,\n\r]+/)
			.map((tag) => tag.trim())
			.filter(Boolean)
			.forEach((tag) => {
				const key = tag.toLocaleLowerCase();
				if (!existing.has(key)) {
					tags.push(tag);
					existing.add(key);
					changed = true;
				}
			});

		$input.val("");
		if (changed) render();
		if (keep_focus) focus_input();
	}

	function render() {
		$input.detach();
		$editor.empty();

		tags.forEach((tag, index) => {
			const $tag = $("<span>").css({
				display: "inline-flex",
				"align-items": "center",
				gap: "4px",
				padding: "3px 7px",
				border: "1px solid #cfd4da",
				"border-radius": "6px",
				background: "#e2e6ea",
				color: "#343a40",
			});

			$("<span>", { text: tag }).appendTo($tag);
			$("<button>", {
				type: "button",
				text: "\u00d7",
				title: __("Remove {0}", [tag]),
				"aria-label": __("Remove {0}", [tag]),
			})
				.css({
					border: 0,
					padding: 0,
					background: "transparent",
					color: "inherit",
					"font-size": "14px",
				})
				.on("click", (event) => {
					event.stopPropagation();
					tags.splice(index, 1);
					render();
					focus_input();
				})
				.appendTo($tag);

			$editor.append($tag);
		});

		$input.attr("placeholder", tags.length ? "" : __("Type a value and press Enter"));
		$editor.append($input);
	}

	$editor.on("click", focus_input);
	$input.on("keydown", (event) => {
		if (["Enter", ",", "Tab"].includes(event.key) && $input.val().trim()) {
			event.preventDefault();
			add_values($input.val(), true);
		} else if (event.key === "Backspace" && !$input.val() && tags.length) {
			tags.pop();
			render();
			focus_input();
		}
	});
	$input.on("blur", () => add_values($input.val(), false));
	$input.on("paste", () => {
		setTimeout(() => {
			if (/[,\n\r]/.test($input.val())) add_values($input.val(), true);
		}, 0);
	});

	render();
}
