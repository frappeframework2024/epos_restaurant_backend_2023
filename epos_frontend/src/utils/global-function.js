

import {postData } from "@/plugin/api.js";
 
  
 
globalThis.app.postApi =  async function (api_url,param,message="",show_message=true,base_url="epos_restaurant_2023.api.") {
  return await postData(api_url,param,message,show_message,base_url)
}
 