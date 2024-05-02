<template>
    <ComModal @onClose="onClose" :mobileFullscreen="true" hideOkButton>
        <template #title>
            {{ voucherTopUp.customer }} - {{ voucherTopUp.customer_name }}
        </template>
        <template #bar_custom>
      <v-btn append-icon="mdi-printer" @click="onPrinterVoucherClick">{{ $t('Print') }}</v-btn>
    </template>
        <template #content>
            <div  v-if="voucherTopUp">
                <div>
                <v-table>
                    <tr>
                        <th class="text-left">ID</th>
                        <td>{{ voucherTopUp.name }}</td>
                        <th class="text-left">{{ $t("Actual Amount") }}</th>
                        <td>
                            <CurrencyFormat :value="voucherTopUp.actual_amount" />
                        </td>
                    </tr>
                    <tr>
                        <th class="text-left">{{ $t("Posting Date") }}</th>
                        <td>{{ moment(voucherTopUp.posting_date).format("DD-MM-YYYY") }}</td>
                        <th class="text-left">{{ $t("Credit Amount") }}</th>
                        <td>
                            <CurrencyFormat :value="voucherTopUp.credit_amount" />
                        </td>
                    </tr>
                    <tr>
                        <th class="text-left">{{ $t("Customer") }}</th>
                        <td>{{ voucherTopUp.customer }} - {{ voucherTopUp.customer_name }}</td>
                       
                    </tr>
                    <tr>
                        <th class="text-left">{{ $t("Phone") }}</th>
                        <td>{{ voucherTopUp.phone }}</td>
                        <th class="text-left">{{ $t("Status") }}</th>
                        <td>
                            <v-chip v-if="voucherTopUp.docstatus == 1" color="success" density="comfortable" size="small">
                                {{ $t("Submitted") }}
                            </v-chip>
                            <v-chip v-if="voucherTopUp.docstatus == 0" color="warning" density="comfortable" size="small">
                                {{ $t("Draft") }}
                            </v-chip>
                        </td>
                    </tr>
                </v-table>
            </div>
            <div v-if="voucherTopUp?.payments?.length > 0">
                <p class="font-weight-bold pt-6 pb-2">
                    {{ $t('Payments') }}
                </p>
                <div>
                    <v-table>
                        <thead>
                            <tr>
                                <th class="text-center">{{ $t("Posting Date") }}</th>
                                <th>{{ $t("Reference Number") }}</th>
                                <th>{{ $t("Payment Type") }}</th>
                                <th class="text-right">{{ $t("Payment Amount") }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="payment in voucherTopUp.payments">
                                <td class="text-center">{{ moment(payment.posting_date).format("DD-MM-YYYY") }}</td>
                                <td>{{ payment.reference_no }}</td>
                                <td>{{ payment.payment_type }}</td>
                                <td class="text-right"><CurrencyFormat :value="payment.payment_amount" /></td>
                            </tr>
                        </tbody>
                    </v-table>
                </div>
            </div>
            </div>
           
        </template>
    </ComModal>
</template>

<script setup>
import { ref, inject, onMounted, i18n } from '@/plugin'
import ComModal from '../../components/ComModal.vue';
const moment = inject('$moment')

const { t: $t } = i18n.global;
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const gv = inject('$gv')
const props = defineProps({
    params: {
        type: Object,
        required: true,
    },
})


const emit = defineEmits(["resolve"])

const voucherTopUp = ref({})
let loading = ref(false)

onMounted(async () => {
    
    db.getDoc('Voucher', props.params.name).then((result) => {
            voucherTopUp.value = result
            loading.value = false;
    });
})

function onPrinterVoucherClick(){
    onPrintVoucher('print_voucher_slip',voucherTopUp.value)
}

async function onPrintVoucher( action, doc) {
    const data = {
            action: action,
            setting: gv.setting?.pos_setting,
            voucher: doc,
            station_device_printing:(gv.setting?.device_setting?.station_device_printing)||"",
            station: (gv.setting?.device_setting?.name) || "",
        }

        if((gv.setting?.device_setting?.use_server_network_printing||0)==1){
            var printer = (gv.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
            if (printer.length <= 0) {
                return // not printer
            } 
            if(printer[0].usb_printing == 0){
                const body ={
                    "data":{
                        "name":data["voucher"]["name"],
                        "station": data["station"],
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
                call.post("epos_restaurant_2023.api.network_printing_api.print_voucher_to_network_printer",body)
                return // print network
            }      
        }



        if (localStorage.getItem("is_window")) {
            window.chrome.webview.postMessage(JSON.stringify(data));
        }else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
            var printer = (gv.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
            if (printer.length <= 0) {
                toaster.warning($t("Printer not yet config for this device"))
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
        }else {            
                socket.emit('PrintReceipt', JSON.stringify(data));
             
        }        
}



function onClose() {
    emit('resolve', false);
}

</script>

