<template>
    <PageLayout :title="$t('Receipt List')" icon="mdi-file-chart" full>
      <ComReceiptListCard :headers="headers" doctype="Sale" extra-fields="customer_name,sale_status_color" @callback="onCallback" v-if="mobile"/>
      
      <ComTable :headers="headers" :isPrint="true" @onPrint="onPrint" show-check-box show-index doctype="Sale" :default-filter="defaltFilter" extra-fields="customer_name,sale_status_color" @onFetch="onFetch" business-branch-field="business_branch" pos-profile-field="pos_profile" @callback="onCallback" @onRefresh="onFetch"  v-else>
          <template v-slot:kpi>
            <v-row no-gutters>
          <v-col cols="6" sm="2">
            <v-card class="pa-1 ma-2" elevation="2" color="primary">
              <div class="text-h6 text-center"><CurrencyFormat :value="summary.sub_total" /></div>
              <div class="text-body-2 text-center text-sm">{{ $t('Sub Total') }}</div>
            </v-card>
          </v-col>
          <v-col cols="6" sm="2">
            <v-card class="pa-1 ma-2" elevation="2" color="totaldiscount">
              <div class="text-h6 text-center">
                <CurrencyFormat :value="summary.total_discount" />
              </div>
              <div class="text-body-2 text-center text-sm">{{ $t('Total Discount') }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="2">
            <v-card class="pa-1 ma-2" elevation="2" color="grandtotalbtn">
              <div class="text-h6 text-center">
                <CurrencyFormat :value="summary.grand_total" />
              </div>
              <div class="text-body-2 text-center text-sm">{{ $t('Grand Total') }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="2">
            <v-card class="pa-1 ma-2" elevation="2" color="teal-darken-3">
              <div class="text-h6 text-center">
                <CurrencyFormat :value="summary.total_paid" />
              </div>
              <div class="text-body-2 text-center text-sm">{{ $t('Total Paid') }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="2">
            <v-card class="pa-1 ma-2" elevation="2" color="blue darken-4">
              <div class="text-h6 text-center">
                {{summary.total_receipts || 0}}
              </div>
              <div class="text-body-2 text-center text-sm">{{ $t('Total Reciepts') }}</div>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="2">
            <v-card class="pa-1 ma-2" elevation="2" color="teal darken-4">
              <div class="text-h6 text-center">
                {{summary.total_receipt_deleted || 0}}
              </div>
              <div class="text-body-2 text-center text-sm">{{ $t('Total Deleted Reciepts') }}</div>
            </v-card>
          </v-col>
          
        </v-row>
          </template>
      </ComTable>
    </PageLayout>
</template>
<script setup>
import { ref, saleDetailDialog, customerDetailDialog,i18n,inject,confirm} from '@/plugin'
import PageLayout from '@/components/layout/PageLayout.vue';
import ComTable from '@/components/table/ComTable.vue';
import {useDisplay} from 'vuetify' 
import ComReceiptListCard from './components/ComReceiptListCard.vue';
import { createToaster } from '@meforma/vue-toaster';
const toaster = createToaster({ position: "top-right" });
const socket = inject("$socket");

let summary = ref({})
const frappe = inject('$frappe');
const gv = inject('$gv');
const call = frappe.call();
const db = frappe.db();
const { t: $t } = i18n.global; 
const {mobile} = useDisplay() 
async function onCallback(data) {
 
 if(data.fieldname=="name"){
  const name =  data.data.name;
  const result = await  saleDetailDialog({
      name:name
    });
    if (result=="delete_order"){
      window.parent.postMessage('refresh', '*');
    }
   
  }
  else if(data.fieldname == "customer"){
     customerDetailDialog({
        name: data.data.customer
    })
  }
}

function onFetch(_filters){ 
 
  let filters =[]
  Object.keys(_filters).forEach(key => {
    filters.push({[key]:_filters[key]})
  });
  call.get("epos_restaurant_2023.api.api.receipt_list_summary",{
    filter:JSON.stringify(filters)
  }
   
  ).then((res)=>{
    if (res.message.length > 0){ 
      summary.value = res.message[0]
    }  
  })
}

async function onPrint(val){ 
  
  if(!val){
    toaster.warning($t("Please select bill closed to print"));
    return
  }
  if (await confirm({ title: $t("Print Receipt"), text: $t("msg.Are you sure to print receipt") })) {
    val.forEach(async (v)=>{
      await db.getDoc("Sale", v.name).then(async (doc)=>{
      
        await _onPrintProcess(doc)
      });
      
    }) 
    toaster.success($t("Print processing"));
  }

  
}

async function _onPrintProcess(sale){   //
  let data = {
        action: "print_receipt",
        print_setting: gv.setting.default_pos_receipt,
        setting: gv.setting?.pos_setting,
        sale: sale,
        station: (gv.setting?.device_setting?.name) || "",
        station_device_printing: (gv.setting?.device_setting?.station_device_printing) || "",
        reprint: 1
  } 
  let printer = (gv.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
  let _printer = undefined
  if (printer.length > 0) {
      _printer = {
          "printer_name": printer[0].printer_name,
          "ip_address": printer[0].ip_address,
          "port": printer[0].port,
          "cashier_printer": printer[0].cashier_printer,
          "is_label_printer": printer[0].is_label_printer,
          "usb_printing": printer[0].usb_printing,
      }
  } 

  if((gv.setting?.device_setting?.use_server_network_printing||0)==1){       
      if (printer.length <= 0) {
          // toaster.warning($t("Printer not yet config for this device"));
          console.log("Printer not yet config for this device")
          return // not printer
      }  

      if(printer[0].usb_printing == 0){
          const body ={
              "data":{
                  "name":sale.name,
                  "reprint":1,
                  "action":data["action"],
                  "print_setting":data["print_setting"],
                  "template_name":data["print_setting"]["pos_receipt_template"],
                  "printer" : _printer
              }
          }  
          call.post("epos_restaurant_2023.api.network_printing_api.print_bill_to_network_printer",body)
          // toaster.success($t("Print processing"));
          return // print network
      }  else if((localStorage.getItem("flutterWrapper") || 0) == 1)   {
          data.printer = _printer;
          socket.emit('PrintReceipt', JSON.stringify(data));  
          return;
      }
  }

  //
  if (localStorage.getItem("is_window") == "1") {  
    window.chrome.webview.postMessage(JSON.stringify(data));
    return;
  }
  else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
    if (printer.length <= 0) {
        // toaster.warning($t("Printer not yet config for this device"))
        console.log("Printer not yet config for this device")
    } else {
        data.printer = _printer;
        flutterChannel.postMessage(JSON.stringify(data));
    } 
  }
  else { 
    data.printer = _printer;
    socket.emit('PrintReceipt', JSON.stringify(data));
    return;              
  }
}



const headers = ref([
  { title: $t('ID'), align: 'start',key: 'name',callback: true},
  { title: $t('Invoice No'), align: 'start',key: 'custom_bill_number',callback: true},
  { title: $t('Customer Name'), align: 'start', key: 'customer', template: '{customer}-{customer_name}', callback: true },
  { title: $t('Table'), align: 'start', key: 'tbl_number' },
  { title: $t('Date'), align: 'center', key: 'posting_date', fieldtype: "Date" },
  { title: $t('Qty'), align: 'center', key: 'total_quantity', },
  { title: $t('Grand Total'), align: 'end', key: 'grand_total', fieldtype: "Currency" },
  { title: $t('Total Discount'), align: 'end', key: 'total_discount', fieldtype: "Currency" },
  { title: $t('Total Paid'), align: 'end', key: 'total_paid_with_fee', fieldtype: "Currency" },
  { title: $t('Balance'), align: 'end', key: 'balance', fieldtype: "Currency" },
  { title: $t('Status'), align: 'center', key: 'sale_status', fieldtype: "Status",color_field:"sale_status_color" }
])
if (gv.setting.pos_setting.is_client_side_sync_setting==1){
    headers.value.push({ title: $t('Is Synced'), align: 'center', key: 'is_synced', fieldtype: "Status"})
}
 
</script>