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
    onPrintVoucher('rpt_voucher','print_voucher_slip',voucherTopUp.value)
}

async function onPrintVoucher(receipt, action, doc) {
        const data = {
            action: action,
            setting: gv.setting?.pos_setting,
            voucher: doc,
            station_device_printing:(gv.setting?.device_setting?.station_device_printing)||"",
        }
        if (localStorage.getItem("is_window")) {
            window.chrome.webview.postMessage(JSON.stringify(data));
        } else {           
            if (receipt.pos_receipt_file_name) {
                socket.emit('PrintReceipt', JSON.stringify(data));
            }
            else {
                onOpenBrowserPrint("Voucher", action.name,  action.name)
            }
        }
    }

    function onOpenBrowserPrint(doctype, docname, filename) {
        const url = getPrintReportPath(doctype, docname, filename, 1)        
        window.open(url).print();
        window.close();
    }
    function getPrintReportPath(doctype, name, reportName, isPrint = 0) {
        let url = "";
         
        const serverUrl = window.location.protocol + "//" + window.location.hostname +  (window.location.protocol =="https:"? "": (":"+ gv.setting?.pos_setting?.backend_port)) ;
        url = serverUrl + "/printview?doctype=" + doctype + "&name=" + name + "&format=" + reportName + "&no_letterhead=0&letterhead=Defualt%20Letter%20Head&settings=%7B%7D&_lang=en&d=" + new Date()
        if (isPrint) {
            url = url + "&trigger_print=" + isPrint
        }        
        return url;
    }


function onClose() {
    emit('resolve', false);
}

</script>

