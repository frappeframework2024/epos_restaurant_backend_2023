// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

const GENERATE_PRODUCT_OPTION_FIELDS = ["option_1_html", "option_2_html", "option_3_html","option_4_html","option_5_html"];
frappe.ui.form.on("Generate Products", {
	refresh(frm) {
		GENERATE_PRODUCT_OPTION_FIELDS.forEach((fieldname) => {
			make_generate_product_tag_input(frm, fieldname);
		});
	},
	setup(frm){
        frappe.realtime.on("generate_product", (data) => {
			if (data.message === "Products Generated") {
				frm.set_df_property("duplicated_products", "hidden", 0);
				frm.refresh_field("duplicated_products");
				frm.reload_doc();
			}
			frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
		});
    },
});

function make_generate_product_tag_input(frm, fieldname) {
	const field = frm.fields_dict[fieldname];
	if (!field || !field.$wrapper) return;
	
	field.$wrapper.find(".generate-product-tag-editor").remove();
	if (field.$input_area) field.$input_area.hide();
	if (field.$disp_area) field.$disp_area.hide();
	field.$wrapper.find(".control-value").hide();

	let tags = parse_generate_product_tags(frm.doc[fieldname.toString().replace("_html","")]);
	let dragged_index = null;
	const can_write = frm.perm && frm.perm[0] && frm.perm[0].write;
	const read_only = Boolean(field.df.read_only || frm.read_only || !can_write);
	const $editor = $("<div>", {
		class: "generate-product-tag-editor",
		"data-fieldname": fieldname,
	}).css({
		display: "flex",
		"flex-wrap": "wrap",
		gap: "4px",
		"min-height": "38px",
		padding: "5px 6px",
		border: "1px solid var(--border-color)",
		"border-radius": "var(--border-radius)",
		background: read_only ? "var(--disabled-control-bg)" : "var(--control-bg)",
		cursor: read_only ? "default" : "text",
	});
	const $input = $("<input>", {
		type: "text",
		placeholder: __("Type a value and press Enter"),
		disabled: read_only,
	}).css({
		flex: "1 0 90px",
		"min-width": "90px",
		border: 0,
		outline: 0,
		background: "transparent",
	});

	field.$wrapper.append($editor);
	
	function save_and_render() {
		const value_update = frm.set_value(
			fieldname.toString().replace("_html",""),
			tags.length ? JSON.stringify(tags) : ""
		);
		render();
		focus_input();
		Promise.resolve(value_update).then(focus_input);
	}

	function focus_input() {
		if (read_only) return;
		$input.trigger("focus");
		const input = $input.get(0);
		const cursor_position = input.value.length;
		input.setSelectionRange(cursor_position, cursor_position);
	}

	function add_values(value) {
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
		if (changed) save_and_render();
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
				"font-weight": "400",
				cursor: read_only ? "default" : "grab",
				"user-select": "none",
			});
			$tag.attr("data-tag-index", index);
			$("<span>", { text: tag }).appendTo($tag);
			if (!read_only) {
				$tag.attr("draggable", "true");
				$tag.on("dragstart", (event) => {
					dragged_index = index;
					event.originalEvent.dataTransfer.effectAllowed = "move";
					event.originalEvent.dataTransfer.setData("text/plain", String(index));
					$tag.css("opacity", "0.55");
				});
				$tag.on("dragover", (event) => {
					if (dragged_index === null) return;

					event.preventDefault();
					event.stopPropagation();
					event.originalEvent.dataTransfer.dropEffect = "move";
					const rectangle = $tag.get(0).getBoundingClientRect();
					const drop_after = event.originalEvent.clientX > rectangle.left + rectangle.width / 2;

					$editor.find("[data-tag-index]").css("box-shadow", "");
					$tag
						.data("drop-after", drop_after)
						.css(
							"box-shadow",
							drop_after
								? "3px 0 0 var(--primary)"
								: "-3px 0 0 var(--primary)"
						);
				});
				$tag.on("drop", (event) => {
					if (dragged_index === null) return;
					event.preventDefault();
					event.stopPropagation();

					let insert_at = index + ($tag.data("drop-after") ? 1 : 0);
					const source_index = dragged_index;
					if (source_index < insert_at) insert_at -= 1;

					$editor.find("[data-tag-index]").css({ opacity: "", "box-shadow": "" });
					dragged_index = null;
					if (source_index === insert_at) {
						focus_input();
						return;
					}

					const [moved_tag] = tags.splice(source_index, 1);
					tags.splice(insert_at, 0, moved_tag);
					save_and_render();
				});
				$tag.on("dragend", () => {
					$editor.find("[data-tag-index]").css({ opacity: "", "box-shadow": "" });
					dragged_index = null;
					focus_input();
				});
				$("<button>", {
					type: "button",
					text: "\u00d7",
					title: __("Remove {0}", [tag]),
					"aria-label": __("Remove {0}", [tag]),
					draggable: false,
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
						save_and_render();
					})
					.appendTo($tag);
			}
			$editor.append($tag);
		});
		if (!read_only) {
			$input.attr("placeholder", tags.length ? "" : __("Type a value and press Enter"));
			$editor.append($input);
		}
	}
	$editor.on("click", () => $input.trigger("focus"));
	$input.on("keydown", (event) => {
		if (["Enter", ",", "Tab"].includes(event.key) && $input.val().trim()) {
			event.preventDefault();
			add_values($input.val());
		} else if (event.key === "Backspace" && !$input.val() && tags.length) {
			tags.pop();
			save_and_render();
		}
	});
	$input.on("blur", () => add_values($input.val()));
	$input.on("paste", () => {
		setTimeout(() => {
			if (/[,\n\r]/.test($input.val())) add_values($input.val());
		}, 0);
	});
	
	render();
}

function parse_generate_product_tags(value) {
	if (!value) return [];
	try {
		const parsed = JSON.parse(value);
		if (Array.isArray(parsed)) return parsed.map(String);
	} catch (error) {
		// Legacy comma/newline text is converted when the user edits or saves.
	}
	return String(value).split(/[,\n\r]+/).map((tag) => tag.trim()).filter(Boolean);
}
