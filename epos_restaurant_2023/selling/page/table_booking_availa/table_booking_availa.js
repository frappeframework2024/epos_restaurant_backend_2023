frappe.pages['table-booking-availa'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage = Class.extend({
	setting_storage_key: "table_booking_availa_time_setting",
	view_storage_key: "table_booking_availa_view_mode",

	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Table Booking Availability',
			single_column: true
		});
		this.page.set_secondary_action('Refresh', () => this.onReload(), 'octicon octicon-sync')
			this.page.add_inner_button('Active Reservation', () => this.show_active_reservation_dialog());
		this.page.add_menu_item('View Booking Calendar', () => this.set_view_mode('booking_calendar'));
		this.page.add_menu_item('View Table Plan', () => this.set_view_mode('table_plan'));
		this.page.add_menu_item('Setting', () => this.show_setting_dialog());

		this.view_mode = this.get_saved_view_mode();
		this.time_setting = this.get_time_setting();
		this.filter_container = $('<div class="filter-container"></div>').appendTo(this.page.main);
		this.content_container = $('<div class="content-container"></div>').appendTo(this.page.main);

		let root = this;
		this.property = this.page.add_field({
			label: 'Date',
			fieldtype: 'Date',
			fieldname: 'Date',
			default: frappe.datetime.get_today(),
			"reqd": 1,
			change() {
				root.make();
			}
		})
		this.pos_profile = this.page.add_field({
			label: 'Table Group',
			fieldtype: 'Link',
			fieldname: 'table_group',
			options: "Table Group",
			change() {
				root.make();
			}
		})
		this.table_status = this.page.add_field({
			label: 'Table Status',
			fieldtype: 'Select',
			fieldname: 'table_status',
			options: "\nAvailable\nOccupy\nHas Booking",
			change() {
				root.make();
			}
		})

		this.make();
	},

	set_view_mode: function(view_mode) {
		if (["table_plan", "booking_calendar"].indexOf(view_mode) === -1 || this.view_mode === view_mode) {
			return;
		}
		this.view_mode = view_mode;
		try {
			localStorage.setItem(this.view_storage_key, view_mode);
		} catch (e) {
			// Continue switching views when browser storage is unavailable.
		}
		this.make();
	},

	get_saved_view_mode: function() {
		try {
			let view_mode = localStorage.getItem(this.view_storage_key);
			if (["table_plan", "booking_calendar"].indexOf(view_mode) !== -1) {
				return view_mode;
			}
		} catch (e) {
			// Use the default view when browser storage is unavailable.
		}
		return "booking_calendar";
	},

	get_time_setting: function() {
		let default_setting = {
			min_hour: 9,
			max_hour: 18,
			show_occupy_card: 1,
			show_unassigned_reservations: 1
		};

		try {
			let saved = JSON.parse(localStorage.getItem(this.setting_storage_key) || "{}");
			let min_hour = this.to_int(saved.min_hour);
			let max_hour = this.to_int(saved.max_hour);

			if (this.is_valid_hour_range(min_hour, max_hour)) {
				return {
					min_hour: min_hour,
					max_hour: max_hour,
					show_occupy_card: saved.show_occupy_card === undefined ? 1 : this.to_int(saved.show_occupy_card),
					show_unassigned_reservations: saved.show_unassigned_reservations === undefined ? 1 : this.to_int(saved.show_unassigned_reservations)
				};
			}
		} catch (e) {
			// Ignore invalid local storage data and use defaults.
		}

		return default_setting;
	},

	show_setting_dialog: function() {
		let setting = this.get_time_setting();
		let dialog = new frappe.ui.Dialog({
			title: 'Setting',
			fields: [
				{
					label: 'Min Hour',
					fieldname: 'min_hour',
					fieldtype: 'Int',
					reqd: 1,
					default: setting.min_hour,
					description: '0 to 23'
				},
				{
					label: 'Max Hour',
					fieldname: 'max_hour',
					fieldtype: 'Int',
					reqd: 1,
					default: setting.max_hour,
					description: '1 to 24'
				},
				{
					label: 'Show Occupy Card',
					fieldname: 'show_occupy_card',
					fieldtype: 'Check',
					default: setting.show_occupy_card === undefined ? 1 : setting.show_occupy_card
                    },
                    {
                        label: 'Show Unassigned Table Reservation',
                        fieldname: 'show_unassigned_reservations',
                        fieldtype: 'Check',
                        default: setting.show_unassigned_reservations === undefined ? 1 : setting.show_unassigned_reservations
				}
			],
			primary_action_label: 'Save',
			primary_action: (values) => {
				let min_hour = this.to_int(values.min_hour);
				let max_hour = this.to_int(values.max_hour);

				if (!this.is_valid_hour_range(min_hour, max_hour)) {
					frappe.msgprint('Please enter valid hours. Min Hour must be 0-23 and Max Hour must be greater than Min Hour, up to 24.');
					return;
				}

				this.time_setting = {
					min_hour: min_hour,
					max_hour: max_hour,
					show_occupy_card: values.show_occupy_card ? 1 : 0,
					show_unassigned_reservations: values.show_unassigned_reservations ? 1 : 0
				};
				localStorage.setItem(this.setting_storage_key, JSON.stringify(this.time_setting));
				dialog.hide();
				this.make();
			}
		});

		dialog.show();
	},

	is_valid_hour_range: function(min_hour, max_hour) {
		return min_hour >= 0 && min_hour < 24 && max_hour > 0 && max_hour <= 24 && min_hour < max_hour;
	},

		make: function() {
			let date = this.property.get_value();
			let table_group = this.pos_profile.get_value() || "";

			if (!date) {
				frappe.throw("Please select date.");
			}

			this.render_loading();

			frappe.call({
				method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_data",
				args: {
					date: date,
					table_group: table_group
				},
					callback: (r) => {
						let data = r.message || {};
						if (this.view_mode === "table_plan") {
							this.load_table_plan_unassigned_reservations(data, date);
							return;
						}
						if (this.get_time_setting().show_unassigned_reservations) {
						this.load_unassigned_reservations(date, data);
					} else {
						data.unassigned_bookings = [];
						this.load_legend_info(data, date);
					}
				},
				error: () => {
					this.render_error();
				}
			});
		},

        load_unassigned_reservations: function(date, data) {
            frappe.call({
                method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_unasign_table_reservations",
                args: {
                    date: date
                },
                callback: (r) => {
                    data.unassigned_bookings = this.normalize_unassigned_bookings(r.message);
                    this.load_legend_info(data, date);
                },
                error: () => {
                    data.unassigned_bookings = [];
                    this.load_legend_info(data, date);
                }
            });
        },

	load_legend_info: function(data, date) {
		frappe.call({
			method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_legend_color",
			callback: (r) => {
				data.legend = this.prepare_legend_data(r.message || {});
				this.render_map(this.prepare_timeline_data(data, date));
			},
			error: () => {
				data.legend = this.prepare_legend_data({});
				this.render_map(this.prepare_timeline_data(data, date));
			}
		});
	},

	prepare_legend_data: function(value) {
		let reservation_status = Array.isArray(value.reservation_status) ? value.reservation_status : [];
		let sale_status = Array.isArray(value.sale_status) ? value.sale_status : [];
		let normalize = (items) => items.map((item) => ({
			name: item.name || "-",
			background_color: this.get_valid_color(item.background_color, "#d8e1ee"),
			color: this.get_valid_color(item.color, "#25324b")
		}));

		return {
			reservation_status: normalize(reservation_status),
			sale_status: this.get_time_setting().show_occupy_card ? normalize(sale_status) : [],
			has_items: reservation_status.length > 0 ||
				(this.get_time_setting().show_occupy_card && sale_status.length > 0)
		};
	},

        normalize_unassigned_bookings: function(value) {
            if (!value) {
                return [];
            }
            if (Array.isArray(value)) {
                return value;
            }
            if (Array.isArray(value.reservations)) {
                return value.reservations;
            }
            if (Array.isArray(value.data)) {
                return value.data;
            }
            if (Array.isArray(value.message)) {
                return value.message;
            }
            return [];
        },


	render_loading: function() {
		$(this.content_container).html(
			'<div class="table-booking-state">Loading table availability...</div>'
		);
	},

	render_error: function() {
		$(this.content_container).html(
			'<div class="table-booking-state table-booking-state-error">Unable to load table availability.</div>'
		);
	},

	render_map: function(data) {
		$(this.content_container).empty();
		$(frappe.render_template("table_booking_availa", data)).appendTo(this.content_container);
		this.bind_booking_card_events();
	},

	load_table_plan_unassigned_reservations: function(data, date) {
		frappe.call({
			method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_unasign_table_reservations",
			args: { date: date },
			callback: (r) => {
				if (this.view_mode !== "table_plan") return;
				data.unassigned_bookings = this.normalize_unassigned_bookings(r.message);
				this.load_table_plan_legend(data, date);
			},
			error: () => {
				if (this.view_mode !== "table_plan") return;
				data.unassigned_bookings = [];
				this.load_table_plan_legend(data, date);
			}
		});
	},

	load_table_plan_legend: function(data, date) {
		frappe.call({
			method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_legend_color",
			callback: (r) => {
				if (this.view_mode !== "table_plan") return;
				this.render_table_plan(data, date, this.prepare_legend_data(r.message || {}));
			},
			error: () => {
				if (this.view_mode !== "table_plan") return;
				this.render_table_plan(data, date, this.prepare_legend_data({}));
			}
		});
	},

	render_table_plan: function(data, date, legend) {
		let tables = Array.isArray(data.tables) ? data.tables : [];
		tables = this.filter_tables_by_status(tables, this.table_status ? this.table_status.get_value() : "");
		let plan_data = this.prepare_confirm_table_selector({
			table_groups: data.table_groups || [],
			tables: tables
		});
		plan_data.date_label = this.format_date(date) || date;
		plan_data.legend = legend || this.prepare_legend_data({});
		plan_data.unassigned_reservations = this.prepare_unassigned_reservation_data(data.unassigned_bookings);

		$(this.content_container).empty();
		$(frappe.render_template("table_plan", plan_data)).appendTo(this.content_container);
		this.bind_table_plan_events();
	},

	bind_table_plan_events: function() {
		let wrapper = $(this.content_container);
		wrapper.find(".table-plan-group-chip").off("click").on("click", (e) => {
			let group_index = $(e.currentTarget).attr("data-group-index");
			wrapper.find(".table-plan-group-chip").removeClass("is-active");
			wrapper.find(".table-plan-group-panel").removeClass("is-active");
			$(e.currentTarget).addClass("is-active");
			wrapper.find('.table-plan-group-panel[data-group-index="' + group_index + '"]').addClass("is-active");
		});
		wrapper.find(".reservation-unassign-card").off("click").on("click", (e) => {
			let booking_number = $(e.currentTarget).attr("data-booking-number");
			if (booking_number) this.open_booking_detail(booking_number);
		});
		wrapper.find(".table-plan-card.has-single-reservation").off("click").on("click", (e) => {
			let booking_number = $(e.currentTarget).attr("data-booking-number");
			if (booking_number) this.open_booking_detail(booking_number);
		});
		wrapper.find(".table-plan-reservation-row[data-booking-number]").off("click").on("click", (e) => {
			e.stopPropagation();
			let booking_number = $(e.currentTarget).attr("data-booking-number");
			if (booking_number) this.open_booking_detail(booking_number);
		});
	},

	prepare_unassigned_reservation_data: function(rows) {
		rows = this.normalize_unassigned_bookings(rows).slice();
		rows.sort((a, b) => String(a.arrival_time || "").localeCompare(String(b.arrival_time || "")));

		let reservations = rows.map((row) => ({
			booking_number: row.booking_number || row.name || "",
			booking_number_display: row.booking_number || row.name || "-",
			guest_name: row.guest_name || "Guest",
			phone_number: row.phone_number || "-",
			total_guest: row.total_guest || 0,
			adult: row.adult || 0,
			child: row.child || 0,
			elderly: row.elderly || 0,
			arrival_time: this.format_time(row.arrival_time) || "-",
			check_out_time: row.check_out_time ? this.format_time(row.check_out_time) : "Open",
			reservation_status: row.reservation_status || "-",
			background_color: this.get_valid_color(row.background_color, "#fff7ed"),
			text_color: this.get_valid_color(row.text_color, "#9a3412")
		}));

		return {
			reservations: reservations,
			reservation_count: reservations.length,
			has_reservations: reservations.length > 0
		};
	},

	bind_booking_card_events: function() {
		$(this.content_container).find(".table-booking-reservation.is-booking").off("click").on("click", (e) => {
			e.stopPropagation();
			let booking_number = $(e.currentTarget).attr("data-booking-number");
			if (booking_number) {
				this.open_booking_detail(booking_number);
			}
		});
	},

	open_booking_detail: function(booking_number) {
		frappe.db.get_doc("POS Reservation", booking_number).then((doc) => {
			this.show_booking_detail_dialog(doc);
		}).catch(() => {
			frappe.msgprint("Unable to load booking detail.");
		});
	},

	        show_active_reservation_dialog: function() {
	            let dialog = new frappe.ui.Dialog({
	                title: "Active Reservation",
	                fields: [
	                    { fieldname: "active_reservation_html", fieldtype: "HTML" }
	                ],
	                size: "large"
	            });

	            dialog.active_reservation_request_id = 0;
	            dialog.show();
	            dialog.fields_dict.active_reservation_html.$wrapper.html(
	                "<div class='active-booking-empty'>Loading active reservations...</div>"
	            );
	            this.load_active_reservations(dialog, "", false);
	        },

	        load_active_reservations: function(dialog, keyword, restore_focus) {
	            let request_id = ++dialog.active_reservation_request_id;
	            frappe.call({
	                method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_active_reservation",
	                args: {
	                    keyword: keyword || ""
	                },
	                callback: (r) => {
	                    if (request_id !== dialog.active_reservation_request_id) return;
	                    let data = this.prepare_active_reservation_data(r.message || []);
	                    dialog.fields_dict.active_reservation_html.$wrapper.html(
	                        frappe.render_template("active_booking_list", data)
	                    );
	                    this.bind_active_reservation_events(dialog, keyword || "");

	                    if (restore_focus) {
	                        setTimeout(() => {
	                            let input = dialog.$wrapper.find(".active-booking-search-input");
	                            input.trigger("focus");
	                            let input_element = input.get(0);
	                            if (input_element && input_element.setSelectionRange) {
	                                input_element.setSelectionRange(input.val().length, input.val().length);
	                            }
	                        }, 0);
	                    }
	                },
	                error: () => {
	                    if (request_id !== dialog.active_reservation_request_id) return;
	                    frappe.msgprint("Unable to load active reservations.");
	                }
	            });
	        },

	        bind_active_reservation_events: function(dialog, keyword) {
	            dialog.$wrapper.find(".active-booking-view").off("click").on("click", (e) => {
	                let booking_number = $(e.currentTarget).attr("data-booking-number");
	                if (booking_number) {
	                    this.open_booking_detail(booking_number);
	                }
	            });

	            let input = dialog.$wrapper.find(".active-booking-search-input");
	            let help = dialog.$wrapper.find(".active-booking-search-help");
	            let search_timer = null;
	            input.val(keyword || "");
	            if (keyword) {
	                help.text("Showing results for “" + keyword + "”.");
	            }

	            input.off("input").on("input", (e) => {
	                let value = String($(e.currentTarget).val() || "").trim();
	                clearTimeout(search_timer);
	                dialog.active_reservation_request_id += 1;

	                if (value.length > 0 && value.length < 3) {
	                    help.text("Type at least 3 characters to search.");
	                    return;
	                }

	                help.text(value ? "Searching..." : "Loading all active reservations...");
	                search_timer = setTimeout(() => {
	                    this.load_active_reservations(dialog, value, true);
	                }, 350);
	            });
	        },
        prepare_active_reservation_data: function(rows) {
            rows = Array.isArray(rows) ? rows.slice() : [];
            rows.sort((a, b) => String(a.arrival_date || "").localeCompare(String(b.arrival_date || "")));

            let groups = [];
            let group_map = {};

            rows.forEach((row) => {
                let arrival_date = row.arrival_date || "No Date";
                if (!group_map[arrival_date]) {
                    group_map[arrival_date] = {
                        date: arrival_date,
                        date_label: this.format_date(row.arrival_date) || "No Date",
                        reservations: []
                    };
                    groups.push(group_map[arrival_date]);
                }

                group_map[arrival_date].reservations.push({
                    booking_number: row.booking_number || "-",
                    table_id: row.table_id || "Unassigned",
                    table_number: row.table_number || "Unassigned",
                    guest_name: row.guest_name || "Guest",
                    phone_number: row.phone_number || "-",
                    total_guest: row.total_guest || 0,
                    adult: row.adult || 0,
                    child: row.child || 0,
                    elderly: row.elderly || 0,
                    note: row.note || "-",
                    arrival_time: this.format_time(row.arrival_time) || "-",
                    check_out_time: this.format_time(row.check_out_time) || "Open",
                    reservation_status: row.reservation_status || "-",
                    background_color: this.get_valid_color(row.background_color, "#eef3ff"),
                    text_color: this.get_valid_color(row.text_color, "#3654a4")
                });
            });

            return {
                groups: groups,
                has_reservations: rows.length > 0
            };
        },

        show_booking_detail_dialog: function(doc) {
            let data = this.prepare_booking_detail_data(doc || {});
            let dialog = new frappe.ui.Dialog({
                title: "Booking Detail",
                fields: [
                    { fieldname: "booking_detail_html", fieldtype: "HTML" }
                ],
                size: "large"
            });

            dialog.fields_dict.booking_detail_html.$wrapper.html(frappe.render_template("booking_detail", data));
            dialog.show();
            this.add_booking_detail_actions(dialog, doc || {});
        },

	        add_booking_detail_actions: function(dialog, doc) {
	            this.bind_booking_detail_time_actions(dialog, doc);
	            let reservation_status = doc.reservation_status || doc.status || "";
            let can_confirm = ["Reserved", "Pending"].indexOf(reservation_status) !== -1;
            let footer = dialog.$wrapper.find(".modal-footer");

            if (can_confirm) {
                dialog.set_primary_action("Confirm", () => {
                    this.open_confirm_booking_dialog(doc, dialog);
                });
            }

            if (reservation_status === "Confirmed") {
                dialog.set_primary_action("Change Table", () => {
                    this.open_change_table_dialog(doc, dialog);
                });
            }

            if (reservation_status === "Pending" || reservation_status === "Confirmed" || reservation_status === "Reserved"  ) {
                $("<button class='btn btn-danger btn-sm'>Cancel Reservation</button>")
                    .prependTo(footer)
                    .on("click", () => {
                        this.open_cancellation_note_dialog(doc, dialog);
                    });
	            }
	        },

	        bind_booking_detail_time_actions: function(dialog, doc) {
	            dialog.$wrapper.find(".booking-detail-time-edit").off("click").on("click", (e) => {
	                let fieldname = $(e.currentTarget).attr("data-time-field");
	                this.open_booking_time_dialog(dialog, doc, fieldname);
	            });
	        },

	        open_booking_time_dialog: function(detail_dialog, doc, fieldname) {
	            let field_labels = {
	                arrival_time: "Arrival Time",
	                check_out_time: "Check Out Time"
	            };
	            let field_label = field_labels[fieldname];

	            if (!field_label || !doc || !doc.name) {
	                frappe.msgprint("Unable to edit this booking time.");
	                return;
	            }

	            let current_minutes = this.time_to_minutes(doc[fieldname]);
	            if (current_minutes === null) {
	                current_minutes = 0;
	            }

	            let hour_options = Array.from({ length: 24 }, (value, index) => this.pad_time(index)).join("\n");
	            let minute_options = Array.from({ length: 60 }, (value, index) => this.pad_time(index)).join("\n");
	            let dialog_fields = [];
	            let time_dialog;

	            if (fieldname === "check_out_time") {
	                let arrival_minutes = this.time_to_minutes(doc.arrival_time);
	                let duration_minutes = arrival_minutes === null ? 0 : current_minutes - arrival_minutes;
	                let duration_hour = duration_minutes > 0 && duration_minutes % 60 === 0 ? duration_minutes / 60 : 0;
	                let duration_default = duration_hour >= 1 && duration_hour <= 5 ? String(duration_hour) : "";

	                dialog_fields.push({
	                    label: "Dine In Duration (Hour)",
	                    fieldtype: "Select",
	                    fieldname: "dine_in_duration",
	                    options: "\n1\n2\n3\n4\n5",
	                    default: duration_default,
	                    change: () => {
	                        this.update_edit_checkout_from_duration(time_dialog, doc);
	                    }
	                });
	            }

	            dialog_fields.push(
	                {
	                    fieldtype: "Section Break"
	                },
	                {
	                    label: "Hour",
	                    fieldtype: "Select",
	                    fieldname: "hour",
	                    options: hour_options,
	                    default: this.pad_time(Math.floor(current_minutes / 60)),
	                    reqd: 1
	                },
	                {
	                    fieldtype: "Column Break"
	                },
	                {
	                    label: "Minute",
	                    fieldtype: "Select",
	                    fieldname: "minute",
	                    options: minute_options,
	                    default: this.pad_time(current_minutes % 60),
	                    reqd: 1
	                }
	            );

	            time_dialog = new frappe.ui.Dialog({
	                title: "Edit " + field_label,
	                fields: dialog_fields,
	                primary_action_label: "Save",
	                primary_action: (values) => {
	                    this.save_booking_time(detail_dialog, time_dialog, doc, fieldname, values);
	                }
	            });

	            time_dialog.show();
	        },

	        update_edit_checkout_from_duration: function(time_dialog, doc) {
	            if (!time_dialog) return;

	            let arrival_minutes = this.time_to_minutes(doc.arrival_time);
	            let duration_hour = this.to_int(time_dialog.get_value("dine_in_duration"));
	            if (arrival_minutes === null || duration_hour < 1 || duration_hour > 5) {
	                return;
	            }

	            let checkout_minutes = (arrival_minutes + (duration_hour * 60)) % (24 * 60);
	            time_dialog.set_value("hour", this.pad_time(Math.floor(checkout_minutes / 60)));
	            time_dialog.set_value("minute", this.pad_time(checkout_minutes % 60));
	        },

	        save_booking_time: function(detail_dialog, time_dialog, doc, fieldname, values) {
	            if (!values || values.hour === undefined || values.minute === undefined) {
	                frappe.msgprint("Hour and minute are required.");
	                return;
	            }

	            let time_value = values.hour + ":" + values.minute + ":00";
	            let validation_error = this.get_booking_time_validation_error(doc, fieldname, time_value);
	            if (validation_error) {
	                frappe.msgprint(validation_error);
	                return;
	            }

	            let field_values = {};
	            field_values[fieldname] = time_value;

	            frappe.call({
	                method: "frappe.client.set_value",
	                args: {
	                    doctype: "POS Reservation",
	                    name: doc.name,
	                    fieldname: field_values
	                },
	                freeze: true,
	                freeze_message: "Saving " + fieldname.replace(/_/g, " ") + "...",
	                callback: (r) => {
	                    Object.assign(doc, r.message || {});
	                    doc[fieldname] = time_value;
	                    let data = this.prepare_booking_detail_data(doc);
	                    detail_dialog.fields_dict.booking_detail_html.$wrapper.html(frappe.render_template("booking_detail", data));
	                    this.bind_booking_detail_time_actions(detail_dialog, doc);
	                    time_dialog.hide();
	                    frappe.show_alert({ message: "Booking time updated.", indicator: "green" });
	                    this.make();
	                },
	                error: () => {
	                    frappe.msgprint("Unable to update booking time.");
	                }
	            });
	        },

	        get_booking_time_validation_error: function(doc, fieldname, time_value) {
	            if (["arrival_time", "check_out_time"].indexOf(fieldname) === -1) {
	                return "Invalid booking time field.";
	            }

	            let booking_date = String(doc.arrival_date || doc.reservation_date || "").slice(0, 10);
	            let selected_minutes = this.time_to_minutes(time_value);
	            let now = new Date();
	            let today = now.getFullYear() + "-" + this.pad_time(now.getMonth() + 1) + "-" + this.pad_time(now.getDate());

	            if (!booking_date) {
	                return "Arrival Date is required before editing booking time.";
	            }

	            if (booking_date < today || (booking_date === today && selected_minutes < ((now.getHours() * 60) + now.getMinutes()))) {
	                return (fieldname === "arrival_time" ? "Arrival Time" : "Check Out Time") + " cannot be earlier than the current date and time.";
	            }

	            let arrival_time = fieldname === "arrival_time" ? time_value : doc.arrival_time;
	            let check_out_time = fieldname === "check_out_time" ? time_value : doc.check_out_time;
	            let arrival_minutes = this.time_to_minutes(arrival_time);
	            let check_out_minutes = this.time_to_minutes(check_out_time);

	            if (arrival_minutes !== null && check_out_minutes !== null && check_out_minutes <= arrival_minutes) {
	                return "Check Out Time must be later than Arrival Time.";
	            }

	            return "";
	        },

	        open_cancellation_note_dialog: function(doc, detail_dialog) {
            let cancel_dialog = new frappe.ui.Dialog({
                title: "Cancellation Note",
                fields: [
                    {
                        label: "Note",
                        fieldtype: "Small Text",
                        fieldname: "cancelled_note",
                        reqd: 1,
                        default: doc.cancelled_note || ""
                    }
                ],
                primary_action_label: "Cancel Now",
                primary_action: (values) => {
                    this.cancel_booking_with_note(doc, values, detail_dialog, cancel_dialog);
                }
            });

            cancel_dialog.show();
        },

        cancel_booking_with_note: function(doc, values, detail_dialog, cancel_dialog) {
            if (!values.cancelled_note) {
                frappe.msgprint("Cancellation note is required.");
                return;
            }

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "POS Reservation",
                    name: doc.name,
                    fieldname: {
                        cancelled_note: values.cancelled_note
                    }
                },
                freeze: true,
                freeze_message: "Saving cancellation note...",
                callback: (r) => {
                    let updated_doc = r.message || doc;
                    this.apply_booking_workflow(updated_doc, "Cancelled", detail_dialog, cancel_dialog);
                },
                error: () => {
                    frappe.msgprint("Unable to save cancellation note.");
                }
            });
        },

	        open_change_table_dialog: function(doc, detail_dialog) {
	            let change_dialog = new frappe.ui.Dialog({
	                title: "Change Table",
	                size: "large",
	                fields: [
	                    {
	                        fieldname: "table_selector_html",
	                        fieldtype: "HTML"
	                    }
	                ],
	                primary_action_label: "Save",
	                primary_action: () => {
	                    this.change_booking_table(doc, change_dialog.selected_table_id, detail_dialog, change_dialog);
	                }
	            });

	            change_dialog.selected_table_id = "";
	            change_dialog.selected_table_group = "";
	            change_dialog.table_selector_map = {};
	            change_dialog.show();
	            change_dialog.get_primary_btn().prop("disabled", true);
	            change_dialog.fields_dict.table_selector_html.$wrapper.html("<div class='booking-table-selector-empty'>Loading tables...</div>");
	            this.load_confirm_table_selector(change_dialog, doc);
	        },

	        change_booking_table: function(doc, table_id, detail_dialog, change_dialog) {
	            if (!table_id) {
	                frappe.msgprint("Table is required.");
	                return;
            }

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "POS Reservation",
	                    name: doc.name,
	                    fieldname: {
	                        table_id: table_id
                    }
                },
                freeze: true,
                freeze_message: "Saving table...",
                callback: () => {
                    change_dialog.hide();
                    detail_dialog.hide();
                    frappe.show_alert({ message: "Table updated.", indicator: "green" });
                    this.make();
                },
                error: () => {
                    frappe.msgprint("Unable to update table.");
                }
            });
        },

	        open_confirm_booking_dialog: function(doc, detail_dialog) {
	            let confirm_dialog = new frappe.ui.Dialog({
	                title: "Confirm Booking",
	                size: "large",
	                fields: [
	                    {
	                        fieldname: "table_selector_html",
	                        fieldtype: "HTML"
	                    }
	                ],
	                primary_action_label: "Confirm",
	                primary_action: () => {
	                    this.confirm_booking(doc, detail_dialog, confirm_dialog);
	                }
	            });

	            confirm_dialog.selected_table_id = "";
	            confirm_dialog.selected_table_group = "";
	            confirm_dialog.table_selector_map = {};
	            confirm_dialog.show();
	            confirm_dialog.get_primary_btn().prop("disabled", true);
	            confirm_dialog.fields_dict.table_selector_html.$wrapper.html("<div class='booking-table-selector-empty'>Loading tables...</div>");
	            this.load_confirm_table_selector(confirm_dialog, doc);
	        },

	        load_confirm_table_selector: function(confirm_dialog, doc) {
	            frappe.call({
	                method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_data",
	                args: {
	                    date: doc.arrival_date || this.property.get_value(),
	                    table_group: ""
	                },
	                callback: (r) => {
	                    let selector_data = this.prepare_confirm_table_selector(r.message || {});
	                    confirm_dialog.table_selector_map = selector_data.table_map;
	                    confirm_dialog.fields_dict.table_selector_html.$wrapper.html(
	                        frappe.render_template("render_select_table", selector_data)
	                    );
	                    this.bind_confirm_table_selector(confirm_dialog);
	                    confirm_dialog.get_primary_btn().prop("disabled", false);
	                },
	                error: () => {
	                    confirm_dialog.fields_dict.table_selector_html.$wrapper.html(
	                        "<div class='alert alert-danger'>Unable to load tables.</div>"
	                    );
	                    confirm_dialog.get_primary_btn().prop("disabled", false);
	                }
	            });
	        },

	        prepare_confirm_table_selector: function(data) {
	            let tables = Array.isArray(data.tables) ? data.tables : [];
	            let table_groups = Array.isArray(data.table_groups) ? data.table_groups : [];
	            let group_names = [];
	            let table_map = {};
	            let selector_key = 0;

	            table_groups.forEach((group) => {
	                let group_name = group.table_group || group.name || "";
	                if (group_name && group_names.indexOf(group_name) === -1) {
	                    group_names.push(group_name);
	                }
	            });
	            tables.forEach((table) => {
	                let group_name = table.table_group || "Ungrouped";
	                if (group_names.indexOf(group_name) === -1) {
	                    group_names.push(group_name);
	                }
	            });

	            let groups = group_names.map((group_name) => {
	                let group_tables = tables
	                    .filter((table) => (table.table_group || "Ungrouped") === group_name)
	                    .map((table) => {
	                        let reservations = Array.isArray(table.reservations) ? table.reservations : [];
	                        let occupy = Array.isArray(table.occupy) ? table.occupy : [];
	                        let has_booking = reservations.length > 0;
	                        let has_occupy = occupy.length > 0 || this.is_table_occupied(table);
	                        let is_available = !has_booking && !has_occupy;
	                        let is_selectable = true;
	                        let reservation_list = reservations.map((reservation) => ({
	                            booking_number: reservation.booking_number || reservation.booking_no || reservation.name || "",
	                            guest_name: reservation.guest_name || "Guest",
	                            phone_number: reservation.phone_number || "-",
	                            adult: reservation.adult || reservation.total_adult || 0,
	                            child: reservation.child || reservation.total_child || 0,
	                            elderly: reservation.elderly || reservation.total_elderly || 0,
	                            arrival_time: this.format_time(reservation.arrival_time) || "-",
	                            check_out_time: reservation.check_out_time ? this.format_time(reservation.check_out_time) : "Open"
	                        }));
	                        let occupy_duration = occupy.length ? this.format_time_ago(occupy[0].creation) : "";
	                        let occupy_label = "Occupied" + (occupy_duration ? " / " + occupy_duration : "");
	                        let status_label = reservations.length === 1
	                            ? reservation_list[0].arrival_time + " - " + reservation_list[0].check_out_time
	                            : (reservations.length > 1 ? reservations.length + " Bookings" : (has_occupy ? occupy_label : "Available"));
	                        let status_class = has_booking ? "is-booked" : (has_occupy ? "is-occupied" : "is-available");
	                        let color_source = has_booking ? reservations[0] : (occupy.length ? occupy[0] : null);
	                        let key = String(selector_key++);
	                        let table_data = {
	                            selector_key: key,
	                            name: table.name,
	                            table_number: table.table_number || table.name,
	                            table_group: group_name,
	                            is_available: is_available,
	                            is_selectable: is_selectable,
	                            is_occupied: has_occupy,
	                            occupy_label: occupy_label,
	                            has_reservations: reservation_list.length > 0,
	                            reservation_count: reservation_list.length,
	                            reservations: reservation_list,
	                            status_label: status_label,
	                            status_class: status_class,
	                            has_status_background: !!color_source,
	                            background_color: color_source ? this.get_valid_color(color_source.background_color, "#f8fafc") : "",
	                            text_color: color_source ? "#000000" : ""
	                        };

	                        table_map[key] = table_data;
	                        return table_data;
	                    });

	                return {
	                    name: group_name,
	                    tables: group_tables,
	                    table_count: group_tables.length,
	                    selectable_count: group_tables.filter((table) => table.is_selectable).length,
	                    is_active: false
	                };
	            });

	            if (groups.length) {
	                let active_index = groups.findIndex((group) => group.tables.length > 0);
	                groups[active_index === -1 ? 0 : active_index].is_active = true;
	            }

	            return {
	                groups: groups,
	                has_groups: groups.length > 0,
	                table_map: table_map
	            };
	        },

	        bind_confirm_table_selector: function(confirm_dialog) {
	            let wrapper = confirm_dialog.fields_dict.table_selector_html.$wrapper;

	            wrapper.find(".booking-table-group-chip").off("click").on("click", (e) => {
	                let group_index = $(e.currentTarget).attr("data-group-index");
	                wrapper.find(".booking-table-group-chip").removeClass("is-active");
	                wrapper.find(".booking-table-group-panel").removeClass("is-active");
	                $(e.currentTarget).addClass("is-active");
	                wrapper.find('.booking-table-group-panel[data-group-index="' + group_index + '"]').addClass("is-active");
	            });

	            wrapper.find(".booking-table-card:not(:disabled)").off("click").on("click", (e) => {
	                let card = $(e.currentTarget);
	                let table_key = card.attr("data-table-key");
	                let table = confirm_dialog.table_selector_map[table_key];
	                if (!table || !table.is_selectable) return;

	                if (card.hasClass("is-selected")) {
	                    card.removeClass("is-selected");
	                    confirm_dialog.selected_table_id = "";
	                    confirm_dialog.selected_table_group = "";
	                    wrapper.find(".booking-table-selected-label").text("None");
	                    return;
	                }

	                wrapper.find(".booking-table-card").removeClass("is-selected");
	                card.addClass("is-selected");
	                confirm_dialog.selected_table_id = table.name;
	                confirm_dialog.selected_table_group = table.table_group;
	                wrapper.find(".booking-table-selected-label").text(table.table_group + " / " + table.table_number);
	            });
	        },

	        confirm_booking: function(doc, detail_dialog, confirm_dialog) {
	            let selected_table_id = confirm_dialog.selected_table_id || doc.table_id || "";

	            let field_values = {
	                table_id: selected_table_id
	            };

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "POS Reservation",
                    name: doc.name,
                    fieldname: field_values
                },
                freeze: true,
                freeze_message: "Saving booking...",
                callback: (r) => {
                    let updated_doc = r.message || doc;
                    this.apply_booking_workflow(updated_doc, "Confirmed", detail_dialog, confirm_dialog);
                },
	                error: () => {
	                    frappe.msgprint("Unable to save the selected table before confirming.");
	                }
	            });
        },
        apply_booking_workflow: function(doc, action, detail_dialog, action_dialog) {
            if (!doc || !doc.name) {
                frappe.msgprint("Unable to update booking. Missing booking document.");
                return;
            }

            frappe.call({
                method: "frappe.model.workflow.apply_workflow",
                args: {
                    doc: doc,
                    action: action
                },
                freeze: true,
                freeze_message: action === "Confirmed" ? "Confirming booking..." : "Cancelling booking...",
                callback: () => {
                    if (action_dialog) {
                        action_dialog.hide();
                    }
                    if (detail_dialog) {
                        detail_dialog.hide();
                    }
                    frappe.show_alert({ message: action === "Confirmed" ? "Booking confirmed." : "Booking cancelled.", indicator: "green" });
                    this.make();
                },
                error: () => {
                    frappe.msgprint(action === "Confirmed" ? "Unable to confirm booking." : "Unable to cancel booking.");
                }
            });
        },

	prepare_booking_detail_data: function(doc) {
		let status = doc.status || doc.reservation_status || "";
		let cancelled_note = doc.cancelled_note || doc.cancel_note || "";
		let phone_number = String(doc.phone_number || "").trim();
		let callable_phone_number = phone_number.replace(/[^\d+*#,;]/g, "");

		return {
			booking_number: doc.name || "-",
			reservation_date: this.format_date(doc.reservation_date) || "-",
			arrival_date: this.format_date(doc.arrival_date) || "-",
			table_number: doc.table_number || doc.table_id || "",
			has_table: !!(doc.table_number || doc.table_id),
			arrival_time: this.format_time(doc.arrival_time) || "-",
			check_out_time: this.format_time(doc.check_out_time) || "-",
			adult: doc.adult || doc.total_adult || 0,
			child: doc.child || doc.total_child || 0,
			elderly: doc.elderly || doc.total_elderly || 0,
			total_guest: doc.total_guest || 0,
			guest_name: doc.guest_name || "-",
			phone_number: phone_number || "-",
			phone_href: callable_phone_number ? "tel:" + callable_phone_number : "",
			has_phone_number: !!callable_phone_number,
			email_address: doc.email_address || "-",
			note: doc.note || "-",
			status: status || "-",
				reservation_status_color: this.get_valid_color(doc.reservation_status_color || doc.text_color, '#3654a4'),
				reservation_status_background_color: this.get_valid_color(doc.reservation_status_background_color || doc.background_color, '#eef3ff'),
			cancelled_note: cancelled_note || "-",
			show_cancelled_note: status === "Cancelled" && !!cancelled_note
		};
	},

	prepare_timeline_data: function(data, date) {
		this.time_setting = this.get_time_setting();
		let start_minute = this.time_setting.min_hour * 60;
		let end_minute = this.time_setting.max_hour * 60;
		let total_minutes = end_minute - start_minute;
		let tables = data.tables || [];
			let unassigned_bookings = this.normalize_unassigned_bookings(data.unassigned_bookings);
			if (this.time_setting.show_unassigned_reservations && unassigned_bookings.length) {
				tables = [{
					table_group: "Unassigned Bookings",
					name: "__unassigned__",
					table_number: "Unassigned",
					is_virtual: 1,
					reservations: unassigned_bookings,
					occupy: []
				}].concat(tables);
			}
		tables = this.filter_tables_by_status(tables, this.table_status ? this.table_status.get_value() : "");
		let group_names = [];

		tables.forEach((table) => {
			if (table.table_group && group_names.indexOf(table.table_group) === -1) {
				group_names.push(table.table_group);
			}
		});

		let groups = group_names.map((group_name) => {
			let group_tables = tables
				.filter((table) => table.table_group === group_name)
				.map((table) => this.prepare_table(table, start_minute, end_minute, total_minutes));

			let active_bookings = group_tables.reduce((total, table) => {
				return total + table.reservations.length;
			}, 0);

			return {
				name: group_name,
					hide_header: group_name === "Unassigned Bookings",
				table_count: group_tables.length,
				active_bookings: active_bookings,
				tables: group_tables
			};
		});

		let hour_count = this.time_setting.max_hour - this.time_setting.min_hour;

		return {
			date: date,
			legend: data.legend || this.prepare_legend_data({}),
			hours: this.get_hours(start_minute, end_minute),
			hour_count: hour_count,
			quarter_count: hour_count * 4,
			timeline_width: hour_count * 132,
			groups: groups,
			has_tables: tables.length > 0
		};
	},

	prepare_table: function(table, start_minute, end_minute, total_minutes) {
		let cards = [];

		(table.reservations || []).forEach((reservation) => {
			let card = this.prepare_timeline_card(reservation, start_minute, end_minute, total_minutes, "Booking", "#f3f7fd", "#17345c");
			if (card) {
				cards.push(card);
			}
		});

		if (this.time_setting.show_occupy_card) {
			(table.occupy || []).forEach((occupy) => {
				let card = this.prepare_timeline_card(occupy, start_minute, end_minute, total_minutes, "Occupy", "#ffa069", "#ffffff");
				if (card) {
					cards.push(card);
				}
			});
		}

		cards.sort((a, b) => a.start_minute - b.start_minute);
		let is_virtual = !!table.is_virtual;
		cards = cards.map((card, index) => {
			card.stack_top = is_virtual ? (index * 54) : ((index % 2) * 8);
			if (is_virtual) {
				card.card_class += " is-unassigned";
			}
			return card;
		});
		let row_height = is_virtual ? Math.max(66, 66 + ((cards.length - 1) * 54)) : 66;
		let guest_total = cards.reduce((total, card) => {
			return total + this.to_int(card.total_guest);
		}, 0);

		return {
			name: table.name,
			
				is_virtual: table.is_virtual || 0,
				row_height: row_height,
			table_number: table.table_number || table.name,
			has_occupy: this.is_table_occupied(table),
			reservation_count: cards.length,
			guest_total: guest_total,
			reservations: cards
		};
	},

	prepare_timeline_card: function(source, start_minute, end_minute, total_minutes, card_label, fallback_background, fallback_text) {
		let arrival = this.time_to_minutes(source.arrival_time);
		let checkout = this.time_to_minutes(source.check_out_time);

		if (arrival === null) {
			arrival = start_minute;
		}
		if (checkout === null || checkout <= arrival) {
			checkout = arrival + 90;
		}

		let clipped_start = Math.max(arrival, start_minute);
		let clipped_end = Math.min(checkout, end_minute);

		if (clipped_end <= clipped_start) {
			return null;
		}

		let left = ((clipped_start - start_minute) / total_minutes) * 100;
		let width = ((clipped_end - clipped_start) / total_minutes) * 100;

		return {
			card_label: card_label,
			booking_number: source.booking_number || source.booking_no || source.name || "",
			booking_number_display: source.booking_number || source.booking_no || source.name || "-",
			guest_name: source.guest_name || "Guest",
			phone_number: source.phone_number || "",
			phone_number_display: source.phone_number || "-",
			adult: source.adult || source.total_adult || 0,
			child: source.child || source.total_child || 0,
			elderly: source.elderly || source.total_elderly || 0,
			total_guest: source.total_guest || 0,
			special_request: source.note || source.special_request || source.request || "",
			special_request_display: source.note   || "-",
			arrival_time: this.format_time(source.arrival_time),
			check_out_time: source.check_out_time ? this.format_time(source.check_out_time) : "Open",
			duration_ago: card_label === "Occupy" ? this.format_time_ago(source.creation) : "",
			reservation_status: source.reservation_status || "",
			background_color: this.get_valid_color(source.background_color, fallback_background),
			text_color: this.get_valid_color(source.text_color, fallback_text),
			left: Math.max(0, Math.min(100, left)).toFixed(3),
			width: Math.max(8, Math.min(100, width)).toFixed(3),
			card_class: card_label === "Occupy" ? "is-occupy" : "is-booking",
			can_open_detail: card_label === "Booking" && !!(source.booking_number || source.booking_no || source.name),
			start_minute: arrival,
			stack_top: 0
		};
	},
	filter_tables_by_status: function(tables, table_status) {
		if (!table_status) {
			return tables;
		}

		return tables.filter((table) => {
			let has_booking = (table.reservations || []).length > 0;
			let is_occupied = this.is_table_occupied(table);

			if (table_status === "Available") {
				return !has_booking && !is_occupied;
			}
			if (table_status === "Occupy") {
				return is_occupied;
			}
			if (table_status === "Has Booking") {
				return has_booking;
			}

			return true;
		});
	},

	is_table_occupied: function(table) {
		let value = table.occupy;
		if (Array.isArray(value)) {
			return value.length > 0;
		}
		if (value === undefined) value = table.occupied;
		if (value === undefined) value = table.is_occupied;

		if (typeof value === "string") {
			value = value.toLowerCase();
			return value === "1" || value === "true" || value === "yes" || value === "occupy" || value === "occupied";
		}

		return value === true || value === 1;
	},
	get_hours: function(start_minute, end_minute) {
		let hours = [];
		for (let minute = start_minute; minute < end_minute; minute += 60) {
			hours.push({
				label: this.format_hour_label(Math.floor(minute / 60))
			});
		}
		return hours;
	},

	time_to_minutes: function(value) {
		if (!value) return null;
		let parts = String(value).split(":");
		if (parts.length < 2) return null;
		return this.to_int(parts[0]) * 60 + this.to_int(parts[1]);
	},

        minutes_to_time: function(minutes) {
            minutes = ((this.to_int(minutes) % (24 * 60)) + (24 * 60)) % (24 * 60);
            let hour = Math.floor(minutes / 60);
            let minute = minutes % 60;
            return this.pad_time(hour) + ":" + this.pad_time(minute) + ":00";
        },

	        format_date: function(value) {
	            if (!value) return "";
	            return frappe.format(value, { fieldtype: "Date" });
	        },

	format_time_ago: function(value) {
		if (!value) return "";
		if (frappe.datetime && typeof frappe.datetime.prettyDate === "function") {
			return frappe.datetime.prettyDate(value);
		}
		if (frappe.utils && typeof frappe.utils.pretty_date === "function") {
			return frappe.utils.pretty_date(value);
		}
		return "";
	},

	format_time: function(value) {
		if (!value) return "";
		let parts = String(value).split(":");
		return this.pad_time(this.to_int(parts[0])) + ":" + this.pad_time(this.to_int(parts[1]));
	},

	format_hour_label: function(hour) {
		let period = hour >= 12 ? "PM" : "AM";
		let hour_12 = hour % 12;
		if (hour_12 === 0) {
			hour_12 = 12;
		}
		return hour_12 + ":00 " + period;
	},

	get_valid_color: function(value, fallback) {
		if (!value) return fallback;
		let color = String(value).trim();
		return /^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$/.test(color) ? color : fallback;
	},

	to_int: function(value) {
		return parseInt(value || 0, 10) || 0;
	},

	pad_time: function(value) {
		return String(value).padStart(2, "0");
	},

	on_view_receipt: function(e) {

	},

	onReload: function() {
		this.make();
	}
})
