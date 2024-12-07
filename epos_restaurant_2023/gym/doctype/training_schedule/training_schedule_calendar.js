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
                            label: "Date",
                            fieldtype: "Date",
                            default: info.start,
                            read_only: 1
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            label: 'Class',
                            fieldname: 'class_type',
                            fieldtype: 'Data',
                            default: doc.class_type,
                            read_only: 1
                        },
                        {
                            label: "Training Time",
                            fieldtype: "Data",
                            default: doc.time_training,
                            read_only: 1
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
                            label: "Attendance Type",
                            fieldname: 'attendance_type',
                            fieldtype: "Select",
                            default: "CHECK IN",
                            options: "CHECK IN\nCHECK OUT",
                        },
                        
                        {
                            fieldtype: 'Section Break',
                        },
                        
                        {
                            label: 'Card ID',
                            fieldname: 'card_id',
                            fieldtype: 'Data',
                            default: "",
                            description:"Please scan or enter Card ID for check-in / out attendance."
                        },
                        {
                            fieldtype: 'Section Break',
                        },
                        
                        {
                            fieldtype: 'Section Break',
                            label: "Members"
                        },
                        {
                            fieldtype: 'Section Break',
                        },
                        {
                            label: 'Reload',
                            fieldname: 'btn_reload_attendance',
                            fieldtype: 'Button',
                            click:async function(){
                              await  get_attendace_list({
                                    "training_date":get_date(info.start),
                                    "training_schedule":info.id
                                }).then((val)=>{ 
            
                                    let html = frappe.render_template("training_attendance", {data:val["data"],isInIframe:(window.self !== window.top)});
                                    $(dlg.fields_dict.attendace_list.wrapper).html(html);
                                    const attendaceList = dlg.fields_dict.attendace_list;
                                    if (attendaceList) {
                                        attendaceList.refresh();                                      
                                    }                                
            
                                })
                            }
                        },

                        {
                            "fieldname": "attendace_list",
                            "fieldtype": "HTML"
                        },
                    ],
                    size: 'extra-large',
                    // primary_action_label: 'Check IN',
                    // primary_action(data) {
                    //     // console.log(data);
                    //     // dlg.hide();
                    // },
                });
     
                dlg.show();

                const cardIdField = dlg.fields_dict.card_id.input;
                // Use a delay to ensure dialog is rendered and the card_id field is available
                setTimeout(() => {
                    const cardIdField = dlg.fields_dict.card_id.input;
                    if (cardIdField) {
                        cardIdField.focus();  
                    }  

                    get_attendace_list({
                        "training_date":get_date(info.start),
                        "training_schedule":info.id
                    }).then((val)=>{ 

                        let html = frappe.render_template("training_attendance", {data:val["data"],isInIframe:(window.self !== window.top)});
                        $(dlg.fields_dict.attendace_list.wrapper).html(html);
                        const attendaceList = dlg.fields_dict.attendace_list;
                        if (attendaceList) {
                            attendaceList.refresh();                                      
                        }                                

                    })

                }, 500);

                cardIdField.addEventListener('keyup', async function(e) {
                    if (e.key === 'Enter') {
                        let cardId = dlg.fields_dict.card_id.get_value();
                        const attendanceType = dlg.fields_dict.attendance_type.get_value();
                        let data = {"card_id":cardId,"info":{
                            "id":info.id,
                            "start": get_date(info.start),
                            "end":get_date(info.end), 
                            "attendance_type":attendanceType
                        }}
                        let resp = await scan_card_attendance(data, dlg)                      

                        if(resp.data){ 

                            //
                          await get_attendace_list({
                                "training_date":get_date(info.start),
                                "training_schedule":info.id
                            }).then((val)=>{ 
                                let html = frappe.render_template("training_attendance", {data:val["data"],isInIframe:(window.self !== window.top)});
                                $(dlg.fields_dict.attendace_list.wrapper).html(html);
                                const attendaceList = dlg.fields_dict.attendace_list;
                                if (attendaceList) {
                                    attendaceList.refresh();                                      
                                }                                

                            }).catch((err)=>{
                                console.log({"_a":"Request attendace","_err": err})
                            })
                            //
                           

                            frappe.show_alert({
                                message: `
                                    <strong>${resp.data.title}</strong><br>
                                    <span>${cardId} - ${resp.data.description}</span>s
                                `, 
                                indicator: 'success', 
                            }, 5);


                             
                        }else{
                            frappe.show_alert({
                                message:` <strong>${resp.error.title}</strong><br>
                                    <span>${cardId} - ${resp.error.description}</span>`,  // The message you want to display
                                indicator: 'yellow',  // The color indicator for success ('green' for success)
                            }, 5);
                        }
                        cardIdField.select();  
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


async function scan_card_attendance(data, dialog) {
    // Return a Promise to ensure we handle async results properly
    return new Promise((resolve, reject) => {
        // Initialize result object
        let result = { "data": undefined, "error": undefined };
        frappe.call({
            method: 'epos_restaurant_2023.api.gym.training_attendance_track',
            type: 'POST',
            freeze: true,
            args: {
                param: data
            },
            callback: function(resp) {
                // If the response is successful, set the data and resolve the promise
                if(resp.message["data"]){
                    result.data = resp.message["data"];
                }else{
                    result.error = resp.message["error"];
                }
                
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

async function get_attendace_list(param){
    return new Promise((resolve, reject) => {
        let result = { "data": undefined, "error": undefined };
        frappe.call({
            method: 'epos_restaurant_2023.api.gym.get_training_attendance',
            type: 'POST',
            freeze: true,
            args: {
                param: param
            },
            callback: function(resp) {
                result.data = resp.message;
                resolve(result); 
            },
            error: function(err) {
                result.error = err;
                reject(result);
            }
        });
    });
}

function get_date(param){
    const date = new Date(param)
    // const date = new Date(Date.UTC(2024, 10, 28, 17, 30, 0));
    console.log(param)
    console.log(date)
    return`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}` ; 
}


