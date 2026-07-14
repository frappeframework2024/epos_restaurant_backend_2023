

import {postData } from "@/plugin/api.js";
  
import { showLoading } from '@/utils/loading.js'
  
 
globalThis.app.postApi =  async function (api_url,param,message="",show_message=true,base_url="epos_restaurant_2023.api.") {
  return await postData(api_url,param,message,show_message,base_url)
}
  
 
globalThis.app.apiPost =  async function (api_url,param,message="",show_message=true,base_url="epos_restaurant_2023.api.") {
  return await postData(api_url,param,message,show_message,base_url)
}
globalThis.app.postData =  async function (api_url,param,message="",show_message=true,base_url="epos_restaurant_2023.api.") {
  return await postData(api_url,param,message,show_message,base_url)
}


globalThis.app.print_to_print_server = async function (print_server_url, html) {
  const payload = {
    html: html,
    printer_name: 'Cashier Printer'
  };

  // Execute the POST request
  fetch(print_server_url + "/print", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
}


globalThis.app.showLoading =  showLoading
 