frappe.views.calendar['Training Schedule'] = {

    get_events_method: 'epos_restaurant_2023.gym.doctype.training_schedule.training_schedule.get_event',

    options: {
        eventClick: function(info) {
            frappe.db.get_doc("Training Schedule", info.id).then(doc => {
                const dlg = new frappe.ui.Dialog({
                    title: 'Class Training Attendance',
                    fields: [
                        {
                            label: 'Schedule ID',
                            fieldname: 'schedule_id',
                            fieldtype: 'Link',
                            options: "Training Schedule",
                            default: doc.name,
                            read_only: 1
                        },
                        {
                            label: 'Scan Card ID',
                            fieldname: 'card_id',
                            fieldtype: 'Data',
                            default: "",
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            label: 'Day',
                            fieldname: 'day',
                            fieldtype: 'Data',
                            default: new Date(info.start).toLocaleDateString('en-US', { weekday: 'long' }),
                            read_only: 1
                        },
                        {
                            label: 'Class',
                            fieldname: 'class_type',
                            fieldtype: 'Data',
                            default: doc.class_type,
                            read_only: 1
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            fieldtype: 'Section Break',
                        },
                        {
                            label: "Training Time",
                            fieldtype: "Data",
                            default: doc.time_training,
                            read_only: 1
                        },
                        {
                            fieldtype: 'Section Break',
                            label: "Members"
                        },
                        {
                            fieldtype: 'Section Break',
                        },
                        {
                            label: "Note",
                            fieldtype: "Small Text",
                            default: doc.note,
                            read_only: 1
                        }
                    ],
                    size: 'extra-large',
                    primary_action_label: 'Check IN',
                    primary_action(data) {
                        // console.log(data);
                        // dlg.hide();
                    }
                });

                // Use Frappe's event system to capture the Enter key press after the dialog is shown
                dlg.show();

                // Bind the keyup event to the `card_id` field after the dialog is displayed
                const cardIdField = dlg.fields_dict.card_id.input;
                cardIdField.addEventListener('keyup', async function(e) {
                    if (e.key === 'Enter') {
                        let cardId = dlg.fields_dict.card_id.get_value();
                        let resp = await scan_card_attendance(cardId, dlg)
                        if(resp.data){

                            frappe.show_alert({
                                message: `
                                    <strong>Attendance tracked successfully!</strong><br>
                                    <span>${cardId} - was Check IN</span>
                                `,  // The message you want to display
                                indicator: 'success',  // The color indicator for success ('green' for success)
                            }, 5);
                             
                        }else{
                            frappe.show_alert({
                                message: "Success",  // The message you want to display
                                indicator: 'green',  // The color indicator for success ('green' for success)
                            }, 5);
                            //
                        }
                        cardIdField.select();
                        console.log(resp)
                    }
                });
            });

            return false;
        },
        select: function(info) {
            return false;
        },
        eventDrop: function(event, delta, revertFunc) {
            revertFunc();
            return;
        }
    }
};


async function scan_card_attendance(card, dialog) {
    // Return a Promise to ensure we handle async results properly
    return new Promise((resolve, reject) => {
        // Initialize result object
        let result = { "data": undefined, "error": undefined };

        frappe.call({
            method: 'epos_restaurant_2023.api.gym.training_attendance_track',
            type: 'POST',
            args: {
                param: {
                    "card": card,
                }
            },
            callback: function(resp) {
                // If the response is successful, set the data and resolve the promise
                result.data = resp.message;
                resolve(result); // Return the result when the call is complete
            },
            error: function(err) {
                // If there is an error, set the error field and reject the promise
                result.error = err;
                reject(result); // Reject the promise with the error
            }
        });
    });
}
