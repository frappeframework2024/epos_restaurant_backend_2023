frappe.pages['table-booking-availa'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage = Class.extend({
	setting_storage_key: "table_booking_availa_time_setting",

	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Table Booking Availability',
			single_column: true
		});
		this.page.set_secondary_action('Refresh', () => this.onReload(), 'octicon octicon-sync')
			this.page.add_inner_button('Active Reservation', () => this.show_active_reservation_dialog());
		this.page.add_menu_item('Setting', () => this.show_setting_dialog());

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
					if (this.get_time_setting().show_unassigned_reservations) {
						this.load_unassigned_reservations(date, data);
					} else {
						data.unassigned_bookings = [];
						this.render_map(this.prepare_timeline_data(data, date));
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
                    this.render_map(this.prepare_timeline_data(data, date));
                },
                error: () => {
                    data.unassigned_bookings = [];
                    this.render_map(this.prepare_timeline_data(data, date));
                }
            });
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
            frappe.call({
                method: "epos_restaurant_2023.selling.page.table_booking_availa.table_booking_availa.get_active_reservation",
                freeze: true,
                freeze_message: "Loading active reservations...",
                callback: (r) => {
                    let data = this.prepare_active_reservation_data(r.message || []);
                    let dialog = new frappe.ui.Dialog({
                        title: "Active Reservation",
                        fields: [
                            { fieldname: "active_reservation_html", fieldtype: "HTML" }
                        ],
                        size: "large"
                    });

                    dialog.fields_dict.active_reservation_html.$wrapper.html(frappe.render_template("active_booking_list", data));
                    dialog.show();
                    this.bind_active_reservation_events(dialog);
                },
                error: () => {
                    frappe.msgprint("Unable to load active reservations.");
                }
            });
        },

        bind_active_reservation_events: function(dialog) {
            dialog.$wrapper.find(".active-booking-view").off("click").on("click", (e) => {
                let booking_number = $(e.currentTarget).attr("data-booking-number");
                if (booking_number) {
                    this.open_booking_detail(booking_number);
                }
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
                fields: [
                    {
                        label: "Table Group",
                        fieldtype: "Link",
                        fieldname: "table_group",
                        options: "Table Group",
                        default: doc.table_group || doc.tbl_group || "",
                        change: () => {
                            change_dialog.set_value("table_id", "");
                        }
                    },
                    {
                        label: "Table",
                        fieldtype: "Link",
                        fieldname: "table_id",
                        options: "Tables Number",
                        reqd: 1,
                        default: doc.table_id || "",
                        get_query: () => {
                            let table_group = change_dialog.get_value("table_group");
                            if (!table_group) {
                                return {};
                            }
                            return {
                                filters: {
                                    tbl_group: table_group
                                }
                            };
                        }
                    }
                ],
                primary_action_label: "Save",
                primary_action: (values) => {
                    this.change_booking_table(doc, values, detail_dialog, change_dialog);
                }
            });

            change_dialog.show();
        },

        change_booking_table: function(doc, values, detail_dialog, change_dialog) {
            if (!values.table_id) {
                frappe.msgprint("Table is required.");
                return;
            }

            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "POS Reservation",
                    name: doc.name,
                    fieldname: {
                        table_id: values.table_id
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
                fields: [
                    {
                        fieldname: "confirm_message",
                        fieldtype: "HTML",
                        options: "<div class='alert alert-info' style='margin-bottom: 12px;'>Please select a table to assign to this reservation before confirming. Table is optional.</div>"
                    },
					{
                        label: "Dine In Duration (Hour)",
                        fieldtype: "Select",
                        fieldname: "dine_in_duration",
                        options: "1\n2\n3\n4\n5",
                        default: "1",
                        change: () => {
                            this.update_checkout_time_from_duration(confirm_dialog, doc);
                        }
                    },
					 {
                        label: "Check Out Time",
                        fieldtype: "Time",
                        fieldname: "check_out_time",
                        reqd: 1,
                        default: doc.check_out_time || ""
                    },
                    
                    {
                        label: "Table Group",
                        fieldtype: "Link",
                        fieldname: "table_group",
                        options: "Table Group",
                        default: doc.table_group || doc.tbl_group || "",
                        change: () => {
                            confirm_dialog.set_value("table_id", "");
                        }
                    },
                   
                    {
                        label: "Table",
                        fieldtype: "Link",
                        fieldname: "table_id",
                        options: "Tables Number",
                        default: doc.table_id || "",
                        get_query: () => {
                            let table_group = confirm_dialog.get_value("table_group");
                            if (!table_group) {
                                return {};
                            }
                            return {
                                filters: {
                                    tbl_group: table_group
                                }
                            };
                        }
                    }
                ],
                primary_action_label: "Confirm",
                primary_action: (values) => {
                    this.confirm_booking(doc, values, detail_dialog, confirm_dialog);
                }
            });

            confirm_dialog.show();
            this.update_checkout_time_from_duration(confirm_dialog, doc);
        },

        update_checkout_time_from_duration: function(dialog, doc) {
            let arrival_minutes = this.time_to_minutes(doc.arrival_time);
            let duration_hour = this.to_int(dialog.get_value("dine_in_duration"));

            if (arrival_minutes === null || !duration_hour) {
                return;
            }

            let checkout_minutes = (arrival_minutes + (duration_hour * 60)) % (24 * 60);
            dialog.set_value("check_out_time", this.minutes_to_time(checkout_minutes));
        },
        confirm_booking: function(doc, values, detail_dialog, confirm_dialog) {
            if (!values.check_out_time) {
                frappe.msgprint("Check Out Time is required.");
                return;
            }


			 
            let field_values = {
                table_id: values.table_id || doc.table_id || "",
                check_out_time: values.check_out_time || doc.check_out_time || ""
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
                    frappe.msgprint("Unable to save table and check out time before confirming.");
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

		return {
			booking_number: doc.name || "-",
			reservation_date: this.format_date(doc.reservation_date) || "-",
			arrival_date: this.format_date(doc.arrival_date) || "-",
			arrival_time: this.format_time(doc.arrival_time) || "-",
			check_out_time: this.format_time(doc.check_out_time) || "-",
			adult: doc.adult || doc.total_adult || 0,
			child: doc.child || doc.total_child || 0,
			elderly: doc.elderly || doc.total_elderly || 0,
			total_guest: doc.total_guest || 0,
			guest_name: doc.guest_name || "-",
			phone_number: doc.phone_number || "-",
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
			card.stack_top = is_virtual ? (index * 36) : ((index % 2) * 8);
			if (is_virtual) {
				card.card_class += " is-unassigned";
			}
			return card;
		});
		let row_height = is_virtual ? Math.max(66, (cards.length * 36) + 18) : 66;
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
