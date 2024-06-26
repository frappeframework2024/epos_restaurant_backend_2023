<template>
    <ComModal :fullscreen="true" @onClose="onClose">
        <template #title>
            {{ $t('Unpaid Bill') }}: {{ props.params.data }}
        </template>
        <template #content>
            <ComLoadingDialog v-if="isLoading" />
            
            <div class="summary-content">
                <v-row>
                    <v-col><div> {{ $t('Total Amount') }}:
                    <CurrencyFormat :value="saleList.total_amount" />
                </div></v-col>
                    <v-col> <div>{{ $t('Total Paid') }}:
                    <CurrencyFormat :value="saleList.total_paid" />
                </div></v-col>
                    <v-col>
                        <div>
                            {{ $t('Balance') }}:
                            <CurrencyFormat :value="saleList.balance" />
                        </div>
                    </v-col>
                </v-row>
                
               
               
            </div>
            <v-btn :color="actionName == 'Sale' ?'primary' : ''" class="ma-2" @click="actionClick('Sale')">{{ $t("Sale List") }}</v-btn>
            <v-btn :color="actionName == 'Print' ?'primary' : ''" class="ma-2" @click="actionClick('Print')">{{ $t("Print") }}</v-btn>
            <v-btn v-if="saleList.total_paid != saleList.total_amount"  :color="actionName == 'Payment' ?'primary' : ''" class="ma-2"  @click="actionClick('Payment')">{{ $t("Payment") }}</v-btn>
                <v-row v-if="actionName == 'Sale'">
                    <v-col v-for="s in saleList.sales" cols="12" md="3">
                        <v-card>
                            <template v-slot:title>
                                {{ $t("Bill") }}#: {{ s.custom_bill_number }}
                            </template>
                            <template v-slot:subtitle>
                                {{ $t("Table") }}: {{ s.tbl_number }} | {{ $t("Order") }}: {{ s.name }}
                            </template>
                            <div class="product-content">
                                <v-list v-for="i in s.sale_products" :lines="false" density="compact"
                                    class="pa-0">
                                    <v-list-item :title="i.product_code + '-' + i.product_name">
                                        <template v-slot:subtitle>
                                            <CurrencyFormat :value="i.price" /> x {{ i.quantity }} =
                                            <CurrencyFormat :value="i.total_revenue" />
                                        </template>
                                    </v-list-item>
                                </v-list>
                            </div>

                            <table style="width:100%">
                                <tr>
                                    <td class=" px-3 py-1">{{ $t("Grand Total") }}</td>
                                    <td class="text-right px-3 py-1">
                                        <CurrencyFormat :value="s.grand_total" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class=" px-3 py-1">{{ $t("Total Paid") }}</td>
                                    <td class="text-right px-3 py-1">
                                        <CurrencyFormat :value="s.total_paid" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class=" px-3 py-1">{{ $t("Balance") }}</td>
                                    <td class="text-right px-3 py-1">
                                        <CurrencyFormat :value="s.balance" />
                                    </td>
                                </tr>
                            </table>
                        </v-card>
                    </v-col>

                </v-row>
            
                <iframe v-else-if="actionName == 'Payment'" :src="`${serverUrl}/app/bulk-sale-payment/new-bulk-sale-payment?customer=${props.params.data}`" height="100%"
                    width="100%" />
                <iframe v-else-if="actionName == 'Print'" :src="`${printPreview}`" style="width: 100%; height: 100%;"/>

        </template>
    </ComModal>
</template>

<script setup>
import { ref, defineEmits, inject, useRouter, createDocumentResource, confirm, i18n, onMounted } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';
const socket = inject("$socket");
const { t: $t } = i18n.global;
const emit = defineEmits(["resolve", "reject"])
const sale = inject("$sale");
const gv = inject('$gv');
const router = useRouter();
const isLoading = ref(false);
const toaster = createToaster({ position: "top-right" })
const frappe = inject("$frappe");
const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})
const  actionName = ref("Sale")
const serverUrl = window.location.protocol + "//" + window.location.hostname + (window.location.protocol == "https:" ? "" : (":" + gv.setting.pos_setting.backend_port));
const printPreview = ref(serverUrl + `/printview?doctype=Customer&name=${props.params.data}&trigger_print=1&format=Unpaid%20Customer&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en`)
//frappe api call
const call = frappe.call()
const saleList = ref([])
const myIframe = ref(null)
const iframe = document.getElementById('myIframe');
onMounted(() => {
    isLoading.value = true
    call.get("epos_restaurant_2023.selling.doctype.customer.customer.get_unpaid_bills", {
        name: props.params.data
    }).then((res) => {
        saleList.value = res.message
        
        isLoading.value = false
    }).catch((err) => {
        isLoading.value = false
    })
})
function onClose() {
    emit("resolve", false)
}

async function actionClick(action){
    if (actionName.value != action){
        actionName.value = action
        if (action == "Payment"){
            window.addEventListener('message', async function  (event) {

                event.data.action == "AfterPayment"
                printPreview.value = printPreview.value + `&bulk_sale_payment_name=${event.data.data.name}&is_payment=1`
                actionName.value = "Print"
            });
        }else{
            window.removeEventListener('message', async function  (event) {
                console.log(event)
            })
        } 
        
    }
    
}

</script>
<style>
.product-content {
    height: 200px;
    overflow-y: auto;
}
</style>