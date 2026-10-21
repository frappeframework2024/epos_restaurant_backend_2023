<template>
    <PageLayout class="pb-4" :title="$t('Close Shift')" icon="mdi-calendar-clock">
        <template #title>
            #{{ cashierShiftResource?.doc?.name }}
        </template>
        <template #action>
             <v-btn prepend-icon="mdi-file-edit" @click="onOpenCashCount">{{ $t('Cash Count') }}</v-btn>
            <v-btn prepend-icon="mdi-file-edit" @click="onChangeShiftName">{{ $t('Change Shift Name') }}</v-btn>
            <v-btn  v-if="setting?.pos_setting?.show_preview_report" prepend-icon="mdi-printer" @click="onOpenReport">{{ $t('Preview Report') }}</v-btn>
        </template>
        <template #default>
            <ComAlertPendingOrder v-if="cashierShiftResource.doc" type="info" :working_day="cashierShiftResource.doc.working_day" :cashier_shift="cashierShiftResource.doc.name"/>
     
            <v-row v-if="cashierShiftResource.doc" class="mt-2 mx-2">
                <v-col cols="12" md="6">
                    <ComInput :label="$t('Working Day')" v-model="cashierShiftResource.doc.working_day" readonly></ComInput>
                </v-col>
                <v-col cols="12" md="6">
                    <ComInput :label="$t('Cashier Shift')" v-model="cashierShiftResource.doc.name" readonly></ComInput>
                </v-col>
                <v-col  cols="12" md="6">
                    <ComInput :label="$t('Close Date')" v-model="current_date" readonly></ComInput>
                </v-col>
                <v-col cols="12" md="6"> 
                    <ComInput :label="$t('Shift Name')" v-model="cashierShiftResource.doc.shift_name" readonly/>
                </v-col>
                <v-col cols="12" md="6"> 
                    <ComInput :label="$t('POS Profile')" v-model="cashierShiftResource.doc.pos_profile" readonly/>
                </v-col>
            </v-row>
            <v-row class="mx-4"> 
                <v-table v-if="cashierShiftSummary.data">
                    <thead>
                        <tr>
                            <th class="text-left">
                                {{ $t('Payment Type') }}
                            </th>
                            <th class="text-center">
                                {{ $t('Opening Amount') }}
                            </th>

                            <th class="text-center">
                                {{ $t('System Close Amount') }}
                            </th>

                            <th class="text-center">
                                {{ $t('Close Amount') }}
                            </th>

                            <th class="text-center">
                                {{ $t('Difference Amount') }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(d, index) in cashierShiftSummary.data" :key="index">
                            <td>{{ d.payment_method }}</td>
                            <td>
                                <CurrencyFormat :value="d.input_amount" :currency="d.currency" />
                            </td>
                            <td>

                                <CurrencyFormat v-if="setting?.pos_setting?.show_system_closed_amount" :value="d.input_system_close_amount" :currency="d.currency" />
                                <span v-else >***</span>
                            </td>
                            <td>
                                <ComInput type="number" v-model="d.input_close_amount" keyboard> </ComInput>
                            </td>
                            <td>
                                <CurrencyFormat v-if="setting?.pos_setting?.show_system_closed_amount" :value="d.input_different_amount" :currency="d.currency" />
                                <span v-else >***</span>
                            </td>
                        </tr>
                    </tbody>
                    <tfoot>
                        <tr>
                            <td>
                                {{ $t('Total') }}
                            </td>
                            <td>
                                <CurrencyFormat :value="cashierShiftSummary.data.reduce((n, r) => n + r.opening_amount, 0)" />
                            </td>
                            <td>
                                <CurrencyFormat v-if="setting?.pos_setting?.show_system_closed_amount" :value="cashierShiftSummary.data.reduce((n, r) => n + r.system_close_amount, 0)" />
                                    <span v-else >***</span>

                            </td>
                            <td>
                                <CurrencyFormat :value="totalCloseAmount" />
                            </td>
                            <td>
                                <CurrencyFormat v-if="setting?.pos_setting?.show_system_closed_amount" :value="totalDifferentAmount" />
                                <span v-else >***</span>
                            </td>
                        </tr>
                    </tfoot>
                </v-table>

            </v-row>
            <ComInput class="my-8 mx-4" :title="$t('Enter Note')" :label="$t('Closed Note')" v-model="doc.closed_note"
                type="textarea" keyboard>
            </ComInput>
            <div class="flex justify-between items-center mx-4">
                <v-btn @click="onCloseShift" color="primary" :loading="(cashierShiftResource.setValue && cashierShiftResource.setValue.loading) ? cashierShiftResource.setValue.loading : false" style="font-family: Khmer OS Siemreap;">{{ $t('Close Shift') }}</v-btn>
                <v-btn  @click="router.push({ name: 'Home' })" color="error" class="ml-4" style="font-family: Khmer OS Siemreap;">{{ $t("Cancel") }}</v-btn>
            </div>
        </template>
    </PageLayout>
</template>

<script setup>
import moment from '@/utils/moment.js';
import { watch, onMounted, createDocumentResource, ref, createResource, useRouter, createToaster, computed, inject ,ChangeShiftNameModal,i18n,getApi} from "@/plugin";
import PageLayout from '../../components/layout/PageLayout.vue';

import ComInput from '../../components/form/ComInput.vue';
import { printPreviewDialog, confirm } from '@/utils/dialog';
import ComAlertPendingOrder from '../../components/layout/components/ComAlertPendingOrder.vue';
import ComCashCount from './ComCashCount.vue';
import { useDisplay } from 'vuetify';
import { useDialog } from 'primevue/usedialog'
const { t: $t } = i18n.global; 
const dialog = useDialog()
const router = useRouter();
const toaster = createToaster({position:"top-right"});
const gv = inject('$gv');
const setting = gv.setting;  
const cashCountSetting = ref()
const current_date = moment(new Date).format('DD-MM-YYYY');
const exchangeRates = ref()
const mainCurrency = ref()
const secondCurrency = ref()
let doc = ref({
    closed_note: "",
    is_closed: 1,
    pos_station_closed:localStorage.getItem("device_name"),
    closed_date: moment(new Date()).format('YYYY-MM-DD HH:mm:ss'),
    cash_float: []
})
const cashierShiftResource = ref({});
let cashierShiftSummary = ref({});
let totalDifferentAmount = ref(0);
const totalCloseAmount = computed(() => {
    if (cashierShiftSummary.value.data) {
        return cashierShiftSummary.value.data.reduce((n, r) => n + (r.input_close_amount / (r.exchange_rate == 0? 1 : r.exchange_rate)), 0);
    }
    return 0;
})

let cashierShiftInfo = createResource({
    url: "epos_restaurant_2023.api.api.get_current_cashier_shift",
    params: {
        pos_profile: localStorage.getItem("pos_profile")
    }
});
 

onMounted(async () => {
    getCashCountSetting()
    await cashierShiftInfo.fetch();
    if (!cashierShiftInfo.data) {
        toaster.warning( $t('msg.There is no cashier shift opened'), {
            position: "top",
        });
        router.push({ name: "Home" });

    }
    cashierShiftResource.value = createDocumentResource({
        url: 'frappe.client.get',
        doctype: 'Cashier Shift',
        name: cashierShiftInfo.data.name,
        setValue: {
            async onSuccess(doc) {

                toaster.success($t("msg.Close Shift successfully"), {
                    position: "top",
                });
                //check from setting if system will need to print after close shift
                if (localStorage.getItem("is_window") == 1) {
                    if (setting.print_cashier_shift_summary_after_close_shift == 1) {
                        window.chrome.webview.postMessage("hello");
                    }

                    if (setting.print_cashier_shift_sale_product_summary_after_close_shift == 1) {
                        window.chrome.webview.postMessage("hello");
                    }
                }
                await printPreviewDialog(
                    { title: $t('Cashier Shift Report')+" #" + doc.name, doctype: "Cashier Shift", name: doc.name }
                )

                router.push({ name: "Home" });
                //for disable close shift in drawer menu
                gv.cashierShift = '';
            },
        },

    });

    //   get cashier shift summary
    cashierShiftSummary.value = createResource({
        url: "epos_restaurant_2023.api.api.get_close_shift_summary",
        params: {
            cashier_shift: cashierShiftInfo.data.name,
            show_system_closed_amount: (setting?.pos_setting?.show_system_closed_amount??0)
        },
        auto: true
    });
    watch(cashierShiftSummary.value, (currentValue, oldValue) => {

        cashierShiftSummary.value.data.forEach(function (d) {
            d.input_different_amount = d.input_close_amount - d.input_system_close_amount;
            d.different_amount = (d.input_close_amount - d.input_system_close_amount) / (d.exchange_rate == 0 ? 1: d.exchange_rate) ;

        });
        totalDifferentAmount.value = cashierShiftSummary.value.data.reduce((n, r) => n + r.different_amount, 0);
    }); 
})

async function onCloseShift() { 
    if (await confirm({ title: $t("Close Shift"), text: $t("msg.are you sure to close cashier shift") })) {
        doc.value.cash_float = cashierShiftSummary.value.data;
        cashierShiftResource.value.setValue.submit(doc.value)
    }
}
async function onChangeShiftName(){
    const result = await ChangeShiftNameModal({data:cashierShiftInfo.data});
    cashierShiftInfo.data.shift_name = result.shift_name
}
function onOpenReport() { 
    printPreviewDialog({ title:$t('Cashier Shift Report')+" #" + cashierShiftResource.value.doc.name, doctype: "Cashier Shift", name: cashierShiftResource.value.doc.name });
}

function getCashCountSetting() {
    getApi("utils.get_cash_count_setting").then(result => {
        cashCountSetting.value = result.message.cash_count_setting
        exchangeRates.value = result.message.exchange_rate_data
        mainCurrency.value = result.message.main_currency
        secondCurrency.value = result.message.second_currency
    })
}

function onOpenCashCount() {
    dialog.open(ComCashCount, {
        data: {
            cash_count_setting: JSON.parse(JSON.stringify(cashCountSetting.value)),
            doc: cashierShiftSummary.value.data,
            exchange_rates: exchangeRates.value,
            mainCurrency: mainCurrency.value,
            secondCurrency: secondCurrency.value
        },
        props: {
            header: $t("Cash Count"),
            style: {
                width: '50vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {
                cashCountSetting.value = data.cash_count_setting
                const updatedCurrencies = new Set();
                cashierShiftSummary.value.data.forEach(d => {
                    if (updatedCurrencies.has(d.currency)) return;
                    const matched = data.cash_count_setting.filter(
                        r => r.currency === d.currency
                    );
                    if (matched.length > 0) {
                        d.input_close_amount = matched.reduce(
                            (n, r) => n + (r.total_note * r.value || 0), 0
                        );
                        d.total_cash_count = d.input_close_amount;
                        updatedCurrencies.add(d.currency);
                    }
                });
                doc.value.cash_count = data.cash_count_setting;
            }
        }
    });
}

</script>