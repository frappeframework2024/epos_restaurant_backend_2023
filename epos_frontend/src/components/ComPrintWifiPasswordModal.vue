<template>
    <ComModal :mobileFullscreen="true" @onClose="onClose()" width="500px" :hideOkButton="false" titleOKButton="Print" @onOk="onPrint()">
      <template #title>
        {{$t('Print WiFi Password')}}
      </template>
      <template #content>
        <ComInput :placeholder="$t('Enter WiFi Password')" v-model="wifi_password" keyboard autofocus/>
      </template>
    </ComModal>
  </template>
<script setup>
import { defineEmits, i18n,ref,inject} from "@/plugin";
import ComModal from "./ComModal.vue";
import ComInput from "./form/ComInput.vue";
import { createToaster } from "@meforma/vue-toaster";
const gv = inject('$gv')
const frappe = inject('$frappe')
const call = frappe.call();
const { t: $t } = i18n.global;
const toaster = createToaster({position:"top"});

const wifi_password = ref("")
  const emit = defineEmits(["resolve"])
 
  function onClose() { 
    emit('resolve', false);
  }
  if (localStorage.key('wifi')){
    wifi_password.value = localStorage.getItem('wifi')
  }
  function onPrint(){
    if(!wifi_password.value){
      toaster.warning($t('msg.Please enter WiFi password'))
    }else {
      if (localStorage.key('wifi')){
        localStorage.setItem('wifi',wifi_password.value)
      }

      if((gv.setting?.device_setting?.use_server_network_printing||0)==1){
          var printer = (gv.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
          if (printer.length <= 0) {
              toaster.warning($t("Printer not yet configt for this device"))
              return // not printer
          } 
          if(printer[0].usb_printing == 0){
              const body ={
                  "data":{
                      "password":wifi_password.value,
                      "printer" : {
                            "printer_name": printer[0].printer_name,
                            "ip_address": printer[0].ip_address,
                            "port": printer[0].port,
                            "cashier_printer": printer[0].cashier_printer,
                            "is_label_printer": printer[0].is_label_printer,
                            "usb_printing": printer[0].usb_printing,
                        }
                  }
              } 
              console.log(body)
              call.post("epos_restaurant_2023.api.network_printing_api.print_wifi_to_network_printer",body)
              toaster.success($t("Print processing"))
              return // print network
          }      
      }
      
      window.chrome.webview.postMessage(JSON.stringify({action:"print_wifi_password",setting:{wifi_password:wifi_password.value}}));
      emit('resolve', false);
    }
  }
  </script>