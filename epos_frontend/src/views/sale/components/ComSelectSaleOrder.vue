<template>
    <ComModal :fullscreen="mobile" @onClose="onClose" width="1200px" :hideOkButton="true" :hideCloseButton="true">
        <template #title>
            {{ $t('Table') }}#: {{ params.table.tbl_no }}  
        </template>
        <template #content>
            <ComLoadingDialog v-if="isLoading" />
            <ComPlaceholder :is-not-empty="params.data.length > 0 || reservations.length >0">
                <v-row class="!-m-1">
                    <!-- Booking Information -->    
                    <v-col cols="12" md="6" v-if="reservations.length>0"  v-for="(booking, index) in reservations" :key="index">
                        <v-card class="pa-4" elevation="3" rounded="lg">
                            <div class="d-flex justify-space-between align-center mb-3">
                                <div>
                                    <div class="text-h6 font-weight-bold">
                                        {{ booking.customer_name }}
                                    </div>
                                    <div class="text-caption text-grey">
                                        {{ booking.name }}
                                    </div>
                                </div>

                                <v-chip :color="booking.sale_status_color" text-color="white" >
                                    {{ booking.sale_type_status }} - {{ booking.rs_sale_status }}
                                </v-chip>
                            </div>

                            <v-divider class="mb-3" />
                            <v-row dense>
                                <v-col cols="6">
                                    <div class="text-caption text-grey">{{ $t("Arrival Time") }}</div>
                                    <div class="font-weight-medium">
                                        <v-icon size="16">mdi-clock-outline</v-icon>
                                        {{ moment(booking.creation).format("hh:mm A") }}
                                    </div>
                                </v-col>

                                <v-col cols="6">
                                    <div class="text-caption text-grey">{{ $t("Guests") }}</div>
                                    <div class="font-weight-medium">
                                        <v-icon size="16">mdi-account-group</v-icon>
                                        {{ booking.guest_cover }}
                                    </div>
                                </v-col>

                                <v-col cols="12">
                                    <div class="text-caption text-grey">{{ $t("Phone") }}</div>
                                    <div class="font-weight-medium">
                                        <v-icon size="16">mdi-phone</v-icon>
                                        {{ booking.phone_number }}
                                    </div>
                                </v-col>
                            </v-row>

                            <v-btn
                                color="success"
                                size="large"
                                block
                                class="mt-4"
                                prepend-icon="mdi-door-open"
                                @click="checkedIn(booking)"
                            >
                                {{ $t('Checked-In') }}
                            </v-btn>
                        </v-card>
                        </v-col>

                    <v-col class="!p-0" cols="12" md="6" v-for="(s, index) in params.data" :key="index">
                        <ComSaleListItem :sale="s" @click="openOrder(s)" />
                    </v-col>
                </v-row>
            </ComPlaceholder>
        </template>
        <template #action>
            <ComSelectSaleOrderAction :isDesktop="isDesktop"
                :is-bill-requested="params.data.filter(r => r.sale_status == 'Bill Requested').length == params.data.length"
                @onClose="onClose" @onNewOrder="onNewOrder" @onQuickPay="onQuickPay" @onQuickPayOtherPaymentType="onQuickPayOtherPaymentType" @onPrintAllBill="onPrintAllBill"
                @onCancelPrintBill="onCancelPrintBill" />
        </template>
    </ComModal>

</template>
<script setup>
import { computed, inject, ref, useRouter, confirmDialog,  smallViewSaleProductListModal, i18n,ComSelectPaymentTypeQuickPaymentDialog } from '@/plugin'
import { confirm } from '@/utils/dialog';
import { useDisplay } from 'vuetify'
import ComSaleListItem from './ComSaleListItem.vue';
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';
import { createToaster } from "@meforma/vue-toaster";
import ComSelectSaleOrderAction from './ComSelectSaleOrderAction.vue';
const moment = inject("$moment");

const socket = inject("$socket")
const { t: $t } = i18n.global;

const isLoading = ref(false);
const { mobile } = useDisplay()
const sale = inject("$sale")
const frappe = inject("$frappe")
const gv = inject("$gv")
const tableLayout = inject("$tableLayout")
const router = useRouter()
const toaster = createToaster({ position: "top-right" });
const isDesktop = localStorage.getItem('is_window');
const emit = defineEmits(["resolve"]);

const db = frappe.db();
const call = frappe.call();
const payment_promises = ref([])

const props = defineProps({
    params: {
        type: Object,
        require: true
    }
});

const reservations = computed(() => { return props.params.reservation;    });





async function onPrintAllBill(receipt) {
    if (receipt.pos_receipt_file_name == null) {
        toaster.warning($t('msg.This receipt have not POS receipt file'));
        return;
    }
    if (props.params.data.filter(r => r.sale_status == "Submitted").length == 0) {
        toaster.warning($t('msg.All receipts were printed'));
        return;
    }

    if (await confirmDialog({ title: $t('Print all Receipts'), text: $t('msg.are you sure to print all receipts') })) {
        let promises = [];
        isLoading.value = true; 
        // check if print server printing
        let printer = (sale.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);

        let other_printing = true
         if((sale.setting?.device_setting?.use_server_network_printing||0)==1){           
             if (printer.length <= 0) {
                 other_printing = false;
                 toaster.warning($t("Printer not yet config for this device"))
             } 
             if(printer[0].usb_printing == 0){ 
                other_printing = await _onNetworkPrintAll("print_invoice", receipt,printer) 
             }      
         } 

        
        if(other_printing==true){
            //end check if server printing             
            props.params.data.filter(r => r.sale_status == "Submitted").forEach(async (d) => { 
                promises.push(PrintReceipt(d,receipt));         
            });

            Promise.all(promises).then(() => {
                toaster.success($t('msg.All receipts has been sent to printer successfully'));
                tableLayout.getSaleList();
                isLoading.value = false;
                emit('resolve', true);
            })
        }
    }

}

async function _onNetworkPrintAll(action, receipt,printer){     
    let data_print ={
        "name":null,
        "reprint":0,
        "action":action,
        "print_setting":receipt,
        "payment_type":sale.setting?.default_payment_type,
        "template_name":receipt["pos_receipt_template"],
        "printer" : {
            "printer_name": printer[0].printer_name,
            "actual_printer_name": printer[0].actual_printer_name || printer[0].printer_name,
            "ip_address": printer[0].ip_address,
            "port": printer[0].port,
            "cashier_printer": printer[0].cashier_printer,
            "is_label_printer": printer[0].is_label_printer,
            "usb_printing": printer[0].usb_printing,
        }
    }

    let data_prints = []
   

    if (action=="print_invoice"){
        props.params.data.filter(r => r.sale_status == "Submitted").forEach(async (d) => {  
            let _d = JSON.parse( JSON.stringify(data_print))
            _d["name"] =  d["name"]
            data_prints.push(_d)       
        }); 

        call.post("epos_restaurant_2023.api.network_printing_api.print_all_bill_to_network_printer",
        {
            "data":data_prints
        }).then((r)=>{ 
            props.params.data.filter(r => r.sale_status == "Submitted").forEach(async (d) => { 
                d.sale_status = "Bill Requested";         
            });
            tableLayout.getSaleList();
            isLoading.value = false;
            emit('resolve', true);
        });

    }else if (action =="print_receipt"){
        props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => {  
            let _d = JSON.parse( JSON.stringify(data_print))
            _d["name"] =  d["name"]
            data_prints.push(_d)       
        }); 

        call.post("epos_restaurant_2023.api.network_printing_api.print_all_bill_quick_pay_to_network_printer",
        {
            "data":data_prints
        }).then((resp)=>{ 
            props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => { 
                d.sale_status = "Closed";      
                d.sale_status_color = sale.setting.sale_status.find(r => r.name == 'Closed').background_color;    
            });
            tableLayout.getSaleList();
            isLoading.value = false;
            emit('resolve', true);
        });
    }   

    return false;
}

async function onQuickPay(isPrint = true) {
    
    if (props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").length == 0) {
        toaster.warning($t("msg.There are no bills to settle"));
        return;
    }

    if (await confirmDialog({ title: $t("Quick Pay"), text: $t('msg.are you sure to process quick pay and close order') })) {
        isLoading.value = true;
        let other_printing = true
         if((sale.setting?.device_setting?.use_server_network_printing||0)==1 && isPrint == true ){
             var printer = (sale.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
             if (printer.length <= 0) {
                 other_printing = false;
                 toaster.warning($t("Printer not yet config for this device"))
             } 
             if(printer[0].usb_printing == 0){ 
                other_printing = await _onNetworkPrintAll("print_receipt", sale.setting?.default_pos_receipt, printer) 
             }      
         } 

         if(other_printing){
            props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => {
                payment_promises.value.push({
                    sale: d.name,
                    payment_type: sale.setting?.default_payment_type
                })
            });


            Promise.all(payment_promises.value).then(async () => {
                const print_setting = {
                    copies:sale.setting?.default_pos_receipt.pos_receipt_template?.print_receipt_copies ?? 1
                }
                await call.get('epos_restaurant_2023.api.api.on_sale_quick_pay', {
                    data: JSON.stringify(payment_promises.value),
                    print_server_url:sale.getPrintServerUrl(),
                    print_setting:print_setting
                }).then((res) => {
                    props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => {
                        const _sale = res.message.filter((r) => r.name == d.name)
                        if (_sale.length > 0) {
                            d.sale_status = "Closed";
                            d.sale_status_color = sale.setting.sale_status.find(r => r.name == 'Closed').background_color; 
                          
                            if(isPrint && !sale.getPrintServerUrl()){
                                onPrintProcess("print_receipt",sale.setting?.default_pos_receipt,_sale[0])      
                            }                  
                        }
                    });

                    toaster.success($t('msg.Payment successfully'));
                    tableLayout.getSaleList();
                    isLoading.value = false;
                    emit('resolve', true);
                }).catch((r) => {
                    toaster.error(r.message);
                    isLoading.value = false;
                });
            });
         }
    }
}

async function onQuickPayOtherPaymentType(isPrint = true) {
 if (props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").length == 0) {
     toaster.warning($t("msg.There are no bills to settle"));
     return;
 }
 const dialog_response = await ComSelectPaymentTypeQuickPaymentDialog({data:props.params.data})
 
 if (dialog_response != false) {
     isLoading.value = true;
     let other_printing = true
      if((sale.setting?.device_setting?.use_server_network_printing||0)==1 && isPrint == true ){
          var printer = (sale.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
          if (printer.length <= 0) {
              other_printing = false;
              toaster.warning($t("Printer not yet config for this device"))
          } 
          if(printer[0].usb_printing == 0){ 
             other_printing = await _onNetworkPrintAll("print_receipt", sale.setting?.default_pos_receipt, printer) 
          }
      }
      payment_promises.value=[]
      if(other_printing){
         props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => {
             payment_promises.value.push({
                 sale: d.name,
                 payment_type: dialog_response.paymentType.payment_method,
                 additional_info: dialog_response.paymentType,
                 'room_number':dialog_response['room']||'',
                'folio_number':dialog_response['folio_number']||'',
                'folio_transaction_type':dialog_response['folio_transaction_type']||'',
                'reservation_stay':dialog_response['reservation_stay']||'',
                'fee_amount':d.grand_total * dialog_response['fee_percentage']
             })
         });
         Promise.all(payment_promises.value).then(async () => {
            const print_setting = {
                    copies:sale.setting?.default_pos_receipt.pos_receipt_template?.print_receipt_copies ?? 1
                }

             await call.get('epos_restaurant_2023.api.api.on_sale_quick_pay_payment_type', {
                 data: JSON.stringify(payment_promises.value),
                 print_server_url: sale.getPrintServerUrl(),
                 print_setting:print_setting
             }).then((res) => {
                 props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => {
                     const _sale = res.message.filter((r) => r.name == d.name)
                     if (_sale.length > 0) {
                         d.sale_status = "Closed";
                         d.sale_status_color = sale.setting.sale_status.find(r => r.name == 'Closed').background_color; 
                         if(isPrint && !sale.getPrintServerUrl()){
                             onPrintProcess("print_receipt",sale.setting?.default_pos_receipt,_sale[0])      
                         }                  
                     }
                 });

                 toaster.success($t('msg.Payment successfully'));
                 tableLayout.getSaleList();
                 isLoading.value = false;
                 emit('resolve', true);
             }).catch((r) => {
                 toaster.error(r.message);
                 isLoading.value = false;
             });
         });
      }
 }
}

async function PrintReceipt(d, receipt) { 
   await call.get("epos_restaurant_2023.api.api.update_print_bill_requested", {name: d.name,print_server_url:sale.getPrintServerUrl()}).then((resp)=>{
        let doc = resp.message;
        if((doc.sale_products.length||0)>0 && !sale.getPrintServerUrl()){
            onPrintProcess("print_invoice",receipt,doc);
        }
        d.sale_status = doc.sale_status;
    }) 
}


async function onPrintProcess(action, receipt,doc){
    let data = {
        action: action,
        print_setting: receipt,
        setting: sale.setting?.pos_setting,
        sale: doc,
        station_device_printing: (sale.setting?.device_setting?.station_device_printing) || "",
        station: (sale.setting?.device_setting?.name) || "",
    }

    let other_printing = true;
    let printer = (sale.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
    let _printer = undefined;
    if(printer.length>0){
        _printer = {
            "printer_name": printer[0].printer_name,
            "actual_printer_name": printer[0].actual_printer_name || printer[0].printer_name,
            "ip_address": printer[0].ip_address,
            "port": printer[0].port,
            "cashier_printer": printer[0].cashier_printer,
            "is_label_printer": printer[0].is_label_printer,
            "usb_printing": printer[0].usb_printing,
        }
    }

    if((sale.setting?.device_setting?.use_server_network_printing||0)==1){
        if (printer.length <= 0) {
            other_printing = false;
            toaster.warning($t("Printer not yet config for this device"))
        } 
        if(printer[0].usb_printing == 0){ 
            const body ={
                "data":{
                    "name":data["sale"]["name"],
                    "reprint":0,
                    "action":data["action"],
                    "print_setting":data["print_setting"],
                    "template_name":data["print_setting"]["pos_receipt_template"],
                    "printer" : _printer
                }
            }  
            call.post("epos_restaurant_2023.api.network_printing_api.print_bill_to_network_printer",body)
            other_printing = false;
        }  else if((localStorage.getItem("flutterWrapper") || 0) == 1)    {
            data.printer = _printer;
            socket.emit('PrintReceipt', JSON.stringify(data));
            other_printing = false;
        }
    } 

    if(other_printing==true){
        let isWindows = localStorage.getItem("is_window")=="1";
	    let isElectron= localStorage.getItem("electronWrapper") == "1";

        if (receipt.pos_receipt_file_name && (isWindows || isElectron)) {
            let _message_data = JSON.stringify(data);
            if(isWindows){
                window.chrome.webview.postMessage(_message_data); 
            }
            else if(isElectron){
                console.info("electron message action => ",data.action)
                window.electronAPI.send('vue-message', _message_data);
            }            
        } else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
            if (printer.length <= 0) {
                //
            } else {
                data.printer = _printer;
                flutterChannel.postMessage(JSON.stringify(data));
            }
        } else { 
            if (receipt.pos_receipt_file_name) {
                data.printer = _printer;
                socket.emit('PrintReceipt', JSON.stringify(data));
            }
        } 
    }
}



async function onCancelPrintBill() {
    if (props.params.data.filter(r => r.sale_status == "Bill Requested").length == 0) {
        toaster.warning($t('msg.There are no bills to cancel print'));
        return;
    }

    gv.authorize("cancel_print_bill_required_password", "cancel_print_bill", "cancel_print_bill_required_note", "Cancel Print Bill Note").then((v) => {
        if (v) {
            isLoading.value = true; 
            let data_canncel_print =[]
            props.params.data.filter(r => r.sale_status == "Bill Requested").forEach(async (d) => {
                data_canncel_print.push(d)
            });
            let body ={
                data : data_canncel_print
            } 
            call.post("epos_restaurant_2023.api.api.update_cancel_print_request",body).then((resp)=>{
                if(resp.message){
                    props.params.data.filter(r => r.sale_status == "Bill Requested").forEach((d)=>{
                        d.sale_status = "Submitted";
                        d.sale_status_color = sale.setting.sale_status.find(r => r.name == 'Submitted').background_color;
                    }) 
                    toaster.success($t('msg.Cancel print successfully'));
                    tableLayout.getSaleList();                
                    isLoading.value = false;
                }  
            }).catch((err)=>{

                isLoading.value = false;
                toaster.warning($t('There are problem on bill canncel'));
            }) 
        }
    })

}
 

async function openOrder(s) {
    if (await tableLayout.validateNewtowkSaleLock(props.params.table,s.name)){
        return
    }


    if (mobile.value) {
        await sale.LoadSaleData(s.name).then(async (v) => {
            localStorage.setItem('make_order_auth', JSON.stringify(props.params.make_order_auth));
            const result = await smallViewSaleProductListModal({ title: s.name ? s.name : 'New Sale', data: { from_table: true } });
        })
    } else {
        localStorage.setItem('make_order_auth', JSON.stringify(props.params.make_order_auth));

        let template = (gv.device_setting?.main_sale_screen??"Default");
        if(template == "Default"){
            router.push({  name: "AddSale", params: { name: s.name}});
        }else {
            const result = template.toLowerCase().replace(/\s+/g, '-');
                let _template = result;
            router.push({ 
                name: "SaleOrder",
                params: { name: s.name },
                query: { menu: _template }
            });
        }
        
    }
    emit('resolve', false);
}

async function onNewOrder() {
    emit('resolve', { action: "new_sale" });
}

const checkedIn = async (booking) => {  
   if(await confirm({ title: $t("Checked In"), text: $t("msg.are you sure to checked in this reservation") })){
        const doc = await db.getDoc("POS Reservation", booking.name)
        emit('resolve',{"action":"checked_in","doc":doc});
    }
}

function onClose() {
    emit("resolve", false);
}
</script>