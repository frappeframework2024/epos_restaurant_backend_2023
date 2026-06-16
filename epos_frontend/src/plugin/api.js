
import {handleServerMessage} from './handle-server-message'
import { FrappeApp } from 'frappe-js-sdk';
  const frappe = new FrappeApp()
    const db = frappe.db()
    const call = frappe.call()

export function getDoc(doctype, name){
  

    return  new Promise((resolve, reject)=>{
        db.getDoc(doctype, name)
        .then((doc) => { 
            resolve(doc)
        })
        .catch((error) => {
            const message = handleServerMessage(error)
            reject(message)
        });
    })
}
export function getDocList(doctype, option){
 
    return new Promise((resolve, reject)=>{
        db.getDocList(doctype, option)
        .then((doc) => {
            resolve(doc)
        })
        .catch((error) => {
            const message = handleServerMessage(error)
            reject(error)
           
        });
    })
}
 
export function getCount(doctype, filters){
 
    return new Promise((resolve, reject)=>{
        db.getCount(doctype, filters,false,false)
        .then((doc) => {
            resolve(doc)
        })
        .catch((error) => {
            reject(error)
            window.postMessage('show_error|' + 'Server Error', '*')
        });
    })
}
export function updateDoc(doctype, name, data, message){
 
    return new Promise((resolve, reject)=>{
        db.updateDoc(doctype, name, data)
        .then((doc) => {
            resolve(doc)
            window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
        })
        .catch((error) => {
            
            const message = handleServerMessage(error)
            reject(error) 
        });
    })
}
export function createUpdateDoc(doctype, data, message, rename=null,show_error_message=true){ 
 
 
 
    return new Promise((resolve, reject)=>{
        if(data.name){
      
            db.updateDoc(doctype, data.name, data)
            .then((doc) => {
               
                // rename
                if(rename && (rename.old_name != rename.new_name)){
                    var update_name = {
                        doctype: doctype,
                        old_name: rename.old_name,
                        new_name: rename.new_name
                    }
                    postApi('utils.rename_doc', { data: update_name },'', false).then((r)=>{
                        doc.name = rename.new_name
                        resolve(doc)
                        window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
                    }).catch((err)=>{
                        reject(err)
                    })
                }
                else{
                    resolve(doc) 
                    window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
                }
            })
            .catch((error) => {
              
                if(show_error_message){
                    handleServerMessage(error)
                } 
                reject(error) 
            });
        }
        else{ 
            db.createDoc(doctype, data)
            .then((doc) => {
                resolve(doc)
                window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
                
            })
            .catch((error) => {
                const message = handleServerMessage(error)
                reject(error) 
            });
        }
    })
}
export function deleteDoc(doctype, name, message){
 
 
    return new Promise((resolve, reject)=>{
        db.deleteDoc(doctype, name)
        .then((doc) => {
           
            resolve(doc.message)
            window.postMessage('show_success|' + `${message ? message : 'Deleted successful'}`, '*')
        })
        .catch((error) => {
     
            const message = handleServerMessage(error)
            reject(message) 
        });
    })
}
export function getApi(api, params = Object,base_url="epos_restaurant_2023.api."){
 
    return new Promise((resolve, reject)=>{
        call.get(`${base_url}${api}`, params).then((result) => {
            resolve(result)
        }).catch((error) =>{
          
            handleServerMessage(error)
            reject(error)
        })
    })
}
export function postApi(api, params = Object, message,show_message=true,base_url="epos_restaurant_2023.api."){
 
    const frappe = new FrappeApp()
    const call = frappe.call()
    return new Promise((resolve, reject)=>{
        call.post(`${base_url}${api}`, params).then((result) => {
            if(show_message == true){
                if(show_message && !result.hasOwnProperty("_server_messages")){
                    window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
                }else{
                    if(result.hasOwnProperty("_server_messages")){
                        const _server_messages = JSON.parse(result._server_messages)
                        _server_messages.forEach(r => {
                            window.postMessage('show_success|' + JSON.parse(r).message, '*')
                        });
                    }
                   
                }
            }
            resolve(result)
        }).catch((error) =>{
            handleServerMessage(error)
            reject(error)
        })
    })
}


export async function postData(api, params = Object, message="",show_message=true,base_url="epos_restaurant_2023.api."){
      let api_url = ""
        if (api.startsWith("epos_restaurant_2023.")){
            
            api_url = api
        }else {
            api_url = `${base_url}${api}`
        }

      return call.post( api_url, params)
      .then((result) => {
        if(show_message == true){
            if(show_message && !result.hasOwnProperty("_server_messages")){
                window.postMessage('show_success|' + `${message ? message : 'Update successful'}`, '*')
            }else{
                if(result.hasOwnProperty("_server_messages")){
                    const _server_messages = JSON.parse(result._server_messages)
                    _server_messages.forEach(r => {
                            // window.postMessage('show_success|' + JSON.parse(r).message, '*')
                            let _message = JSON.parse(r)
                            
                            if (!_message.indicator){
                                
                            //  window.postMessage('show_success|' + _message.message, '*')
                             showSuccess(_message.title || _message.message,_message.title?_message.message:"")
                            }
                            else {
                                if (_message.indicator=="info"){
                                    showInfo(_message.title || _message.message,_message.title?_message.message:"",10000,"tr")
                                }
                            }
                            
                        });
                }
               
            }
        }
       return  { data: result.message, error: null }
    
      })
      .catch((error) => {
        handleServerMessage(error)
        return { data: null, error }
    });
}

export function postReservationStay(docname,data,update_docs){
    let doc = {
        docname: docname,
        data: [],
        update_doc: update_docs // ['update_reservation']
    }
    for (var key in data) {
        doc.data.push({fieldname: key, value: data[key]})
    }
    return new Promise((resolve, reject)=>{
        postApi('reservation.auto_update_reservation_stay', doc).then((r)=>{
            resolve(r.message)
        }).catch((err)=>{
            reject(err)
        }) 
    })
    
}
export function deleteApi(api, params = Object, message){
 
    return new Promise((resolve, reject)=>{
        call.delete(`epos_restaurant_2023.api.${api}`, params).then((result) => {
            window.postMessage('show_success|' + `${message ? message : 'Deleted successful'}`, '*')
            resolve(result)
        }).catch((error) =>{
            handleServerMessage(error)
            reject(error)
        })
    })
}
export function renameDoc(doctype, old_name,new_name){
    let doc = {
        doctype: doctype,
        old_name: old_name,
        new_name: new_name
    }

    return new Promise((resolve, reject)=>{
        if(doc.old_name != doc.new_name){
            postApi('utils.rename_doc', { data: doc }).then((r)=>{
                resolve(r.message)
            }).catch((err)=>{
                reject(err)
            }) 
        }
    })
}
export function uploadFiles(files, fileArgs = Object){

 
    const file = frappe.file();
    return new Promise((resolve, reject)=>{
        let countFile = 0
        files.forEach((r)=>{
            fileArgs.otherData={custom_title: r.custom_title || "",custom_description:r.custom_description || ""}
            file.uploadFile(
                r,
                fileArgs,
                undefined,
                "epos_restaurant_2023.api.upload.upload_file"
            )
            .then((r) => {
                if(r.data && r.data.message){
                    countFile++
                    if(countFile == files.length){
                        window.postMessage('show_success|' + 'Upload files successfull.', '*')
                        resolve(true)
                    }
                }
                
            })
            .catch((error) =>{
                handleServerMessage(error)
                reject(error)
            })
        })
    })
    
}

