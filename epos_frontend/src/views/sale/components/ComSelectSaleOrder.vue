<template>
    <ComModal :fullscreen="mobile" @onClose="onClose" width="1200px" :hideOkButton="true" :hideCloseButton="true">
        <template #title>
            {{ $t('Table') }}#: {{ params.table.tbl_no }}
        </template>
        <template #content>
            <ComLoadingDialog v-if="isLoading" />
            <ComPlaceholder :is-not-empty="params.data.length > 0">
                <v-row class="!-m-1">
                    <v-col class="!p-0" cols="12" md="6" v-for="(s, index) in params.data" :key="index">
                        <ComSaleListItem :sale="s" @click="openOrder(s)" />
                    </v-col>
                </v-row>
            </ComPlaceholder>
        </template>
        <template #action>
            <ComSelectSaleOrderAction :isDesktop="isDesktop"
                :is-bill-requested="params.data.filter(r => r.sale_status == 'Bill Requested').length == params.data.length"
                @onClose="onClose" @onNewOrder="onNewOrder" @onQuickPay="onQuickPay" @onPrintAllBill="onPrintAllBill"
                @onCancelPrintBill="onCancelPrintBill" />
        </template>
    </ComModal>

</template>
<script setup>
import { inject, ref, useRouter, confirmDialog, createDocumentResource, createResource, smallViewSaleProductListModal, i18n, onMounted } from '@/plugin'
import { useDisplay } from 'vuetify'
import ComSaleListItem from './ComSaleListItem.vue';
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';
import { createToaster } from "@meforma/vue-toaster";
import ComSelectSaleOrderAction from './ComSelectSaleOrderAction.vue';

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

async function onQuickPay(isPrint = true) {
    if (props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").length == 0) {
        toaster.warning($t("msg.There are no bills to settle"));
        return;
    }

    if (await confirmDialog({ title: $t("Quick Pay"), text: $t('msg.are you sure to process quick pay and close order') })) {
        isLoading.value = true;

        props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => {

            payment_promises.value.push({
                sale: d.name,
                payment_type: sale.setting?.default_payment_type
            })
        });
        Promise.all(payment_promises.value).then(async () => {
            await call.get('epos_restaurant_2023.api.api.on_sale_quick_pay', {
                data: JSON.stringify(payment_promises.value)
            }).then((res) => {
                props.params.data.filter(r => r.sale_status == "Submitted" || r.sale_status == "Bill Requested").forEach(async (d) => {
                    const _sale = res.message.filter((r) => r.name == d.name)
                    if (_sale.length > 0) {
                        d.sale_status = "Closed";
                        d.sale_status_color = sale.setting.sale_status.find(r => r.name == 'Closed').background_color; 
                        onPrintProcess("print_receipt",sale.setting?.default_pos_receipt,_sale[0])                        
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

        })
    }
}

async function PrintReceipt(d, receipt) { 
    await call.get("epos_restaurant_2023.api.api.update_print_bill_requested", {name: d.name}).then((resp)=>{
        let doc = resp.message;
        if((doc.sale_products.length||0)>0){
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
    if((sale.setting?.device_setting?.use_server_network_printing||0)==1){
        var printer = (sale.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
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
            call.post("epos_restaurant_2023.api.network_printing_api.print_bill_to_network_printer",body)
            other_printing = false;
        }      
    } 

    if(other_printing==true){
        if (receipt.pos_receipt_file_name && localStorage.getItem("is_window")) {
            window.chrome.webview.postMessage(JSON.stringify(data)); 
        } else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
            var printer = (sale.setting?.device_setting?.Sstation_printers).filter((e) => e.cashier_printer == 1);
            if (printer.length <= 0) {
                
            } else {
                data.printer = {
                    "printer_name": printer[0].printer_name,
                    "ip_address": printer[0].ip_address,
                    "port": printer[0].port,
                    "cashier_printer": printer[0].cashier_printer,
                    "is_label_printer": printer[0].is_label_printer,
                    "usb_printing": printer[0].usb_printing,
                }
                flutterChannel.postMessage(JSON.stringify(data));
            }
        } else { 
            if (receipt.pos_receipt_file_name) {
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
            const promises = [];
            props.params.data.filter(r => r.sale_status == "Bill Requested").forEach(async (d) => {
                promises.push(submitCancelPrintBill(d));
            });

            Promise.all(promises).then(() => {
                toaster.success($t('msg.Cancel print successfully'));
                tableLayout.getSaleList();
                isLoading.value = false;
            });
        }
    })

}


async function submitCancelPrintBill(d) {
    const resource = createDocumentResource({
        doctype: "Sale",
        name: d.name,
    });
    await resource.get.fetch().then(async (v) => {
        await resource.setValue.submit({
            sale_status: 'Submitted'
        }).then((data) => {
            d.sale_status = "Submitted";
            d.sale_status_color = sale.setting.sale_status.find(r => r.name == 'Submitted').background_color;
        });
    })
}

async function openOrder(s) {
    if (mobile.value) {
        await sale.LoadSaleData(s.name).then(async (v) => {
            localStorage.setItem('make_order_auth', JSON.stringify(props.params.make_order_auth));
            const result = await smallViewSaleProductListModal({ title: s.name ? s.name : 'New Sale', data: { from_table: true } });
        })
    } else {
        localStorage.setItem('make_order_auth', JSON.stringify(props.params.make_order_auth));
        router.push({ name: "AddSale", params: { name: s.name } });
    }
    emit('resolve', false);
}

async function onNewOrder() {
    emit('resolve', { action: "new_sale" });
}
function onClose() {
    emit("resolve", false);
}
</script>