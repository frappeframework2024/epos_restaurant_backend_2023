

frappe.views.calendar['Training Schedule'] =   {

    get_events_method: 'epos_restaurant_2023.gym.doctype.training_schedule.training_schedule.get_event',

    options: {
        eventClick: function(info) {
            
            frappe.db.get_doc("Training Schedule",info.id).then(doc=>{

                let trainer = ""
                if(doc.trainer){
                    trainer = `${doc.trainer}`
                    if(doc.trainer_name_en){
                        trainer = `(${doc.trainer}) - ${doc.trainer_name_en}`
                    }
                }
                 
                const dlg  = new frappe.ui.Dialog({
                    title: 'Class Training Attendance',
                    fields: [
                        {
                            label: 'ID',
                            fieldname: 'name',
                            fieldtype: 'Link',
                            default: doc.name,
                            read_only:1
                             
                        },
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            label: 'Class',
                            fieldname: 'class_type',
                            fieldtype: 'Data',
                            default: doc.class_type,
                            read_only:1
                             
                        },
                        
                        {
                            fieldtype: 'Column Break',
                        },
                        {
                            label: 'Trainer',
                            fieldname: 'trainer',
                            fieldtype: 'Data',
                            options:"Trainer",
                            default:  trainer,
                            read_only:1
                             
                        }, {
                            fieldtype: 'Section Break',
                        },
                        
                        {label:"Training Time",fieldtype:"Data",default:doc.time_training,read_only:1},
                        {fieldtype: 'Section Break',label:"Members"},
                        {
                            fieldname: 'members',
                            fieldtype: 'Table',
                            cannot_add_rows: true,
                            cannot_edit_rows: true,
                            cannot_delete_rows: true,
                            in_place_edit: false,
                            data:doc.members,
                            read_only: 1,
                            fields: [
                                { fieldname: 'member_name',  fieldtype: 'Data',  in_list_view: 1, label: 'Member' },
                                
                            ]
                        },
                        {fieldtype: 'Section Break'},
                        {label:"Note",fieldtype:"Small Text",default:doc.note,read_only:1},
                          
                    ],
                    size: 'extra-large', // Choose from 'small', 'large', or 'extra-large'
                    primary_action_label: 'Check IN',
                    primary_action(data) {
                        
                     
                        console.log(info);
                        dlg.hide();
                    }
                });
                dlg.show()
            })
            
            
            return false;
        },
        select: function(info) {
         
            return false;
        },
        
        eventDrop: function (event, delta, revertFunc) {    
            revertFunc();
            return
        }

    },
   
}

   

