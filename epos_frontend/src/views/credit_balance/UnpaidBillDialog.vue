<template>
    <ComModal :fullscreen="true" :hideOkButton="true" @onClose="onClose" @onPrint="onPrint" :isPrint="actionName == 'Print'">
        <template #title>
            {{ $t('Unpaid Bill') }}: {{ props.params.data }}
        </template>
        <template #content>
            <ComLoadingDialog v-if="isLoading" />
            <v-row>
                    <v-col col="6">
                        <v-btn :color="actionName == 'Sale' ?'primary' : ''" class="ma-2" @click="actionClick('Sale')">{{ $t("Sale List") }}</v-btn>
                        <v-btn :color="actionName == 'Print' ?'primary' : ''" class="ma-2" @click="actionClick('Print')">{{ $t("Print") }}</v-btn>
                        <v-btn v-if="saleList.balance > 0"  :color="actionName == 'Payment' ?'primary' : ''" class="ma-2"  @click="actionClick('Payment')">{{ $t("Payment") }}</v-btn>
                    </v-col>
                    <v-col col="2">
                        <div id="arrival_dialog" role="button" class="border p-2 rounded">
                            <span> 
                                <div class="d-flex justify-space-between">
                                    <div class="d-flex">
                                        <span><h2 title="Checked-in" style="color:#21c2b5;font-size: 24px"><CurrencyFormat :value="saleList.total_amount" /></h2></span><span><h2 class="px-1" style="color:#21c2b5"></h2></span>

                                    </div>
                                    <svg viewBox="0 0 24 24" height="24px" width="24px" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M6.55281 1.60553C7.10941 1.32725 7.77344 1 9 1C10.2265 1 10.8906 1.32722 11.4472 1.6055L11.4631 1.61347C11.8987 1.83131 12.2359 1.99991 13 1.99993C14.2371 1.99998 14.9698 1.53871 15.2141 1.35512C15.5944 1.06932 16.0437 1.09342 16.3539 1.2369C16.6681 1.38223 17 1.72899 17 2.24148L17 13H20C21.6562 13 23 14.3415 23 15.999V19C23 19.925 22.7659 20.6852 22.3633 21.2891C21.9649 21.8867 21.4408 22.2726 20.9472 22.5194C20.4575 22.7643 19.9799 22.8817 19.6331 22.9395C19.4249 22.9742 19.2116 23.0004 19 23H5C4.07502 23 3.3148 22.7659 2.71092 22.3633C2.11331 21.9649 1.72739 21.4408 1.48057 20.9472C1.23572 20.4575 1.11827 19.9799 1.06048 19.6332C1.03119 19.4574 1.01616 19.3088 1.0084 19.2002C1.00194 19.1097 1.00003 19.0561 1 19V2.24146C1 1.72899 1.33184 1.38223 1.64606 1.2369C1.95628 1.09341 2.40561 1.06931 2.78589 1.35509C3.03019 1.53868 3.76289 1.99993 5 1.99993C5.76415 1.99993 6.10128 1.83134 6.53688 1.6135L6.55281 1.60553ZM3.00332 19L3 3.68371C3.54018 3.86577 4.20732 3.99993 5 3.99993C6.22656 3.99993 6.89059 3.67269 7.44719 3.39441L7.46312 3.38644C7.89872 3.1686 8.23585 3 9 3C9.76417 3 10.1013 3.16859 10.5369 3.38643L10.5528 3.39439C11.1094 3.67266 11.7734 3.9999 13 3.99993C13.7927 3.99996 14.4598 3.86581 15 3.68373V19C15 19.783 15.1678 20.448 15.4635 21H5C4.42498 21 4.0602 20.8591 3.82033 20.6992C3.57419 20.5351 3.39761 20.3092 3.26943 20.0528C3.13928 19.7925 3.06923 19.5201 3.03327 19.3044C3.01637 19.2029 3.00612 19.1024 3.00332 19ZM19.3044 20.9667C19.5201 20.9308 19.7925 20.8607 20.0528 20.7306C20.3092 20.6024 20.5351 20.4258 20.6992 20.1797C20.8591 19.9398 21 19.575 21 19V15.999C21 15.4474 20.5529 15 20 15H17L17 19C17 19.575 17.1409 19.9398 17.3008 20.1797C17.4649 20.4258 17.6908 20.6024 17.9472 20.7306C18.2075 20.8607 18.4799 20.9308 18.6957 20.9667C18.8012 20.9843 18.8869 20.9927 18.9423 20.9967C19.0629 21.0053 19.1857 20.9865 19.3044 20.9667Z" fill="#0F0F0F"></path> <path d="M5 8C5 7.44772 5.44772 7 6 7H12C12.5523 7 13 7.44772 13 8C13 8.55229 12.5523 9 12 9H6C5.44772 9 5 8.55229 5 8Z" fill="#0F0F0F"></path> <path d="M5 12C5 11.4477 5.44772 11 6 11H12C12.5523 11 13 11.4477 13 12C13 12.5523 12.5523 13 12 13H6C5.44772 13 5 12.5523 5 12Z" fill="color:#21c2b5"></path> <path d="M5 16C5 15.4477 5.44772 15 6 15H12C12.5523 15 13 15.4477 13 16C13 16.5523 12.5523 17 12 17H6C5.44772 17 5 16.5523 5 16Z" fill="#0F0F0F"></path> </g></svg>
                                </div>
                                <p>{{ $t('Total Amount') }}</p>
                            </span> 
                        </div></v-col>
                    <v-col  col="2"><div id="arrival_dialog" role="button" class="border p-2 rounded">
                            <span> 
                                <div class="d-flex justify-space-between">
                                    <div class="d-flex">
                                        <span><h2 title="Checked-in" style="color:#0b4e7f;font-size: 24px;"><CurrencyFormat :value="saleList.total_paid" /></h2></span><span><h2 class="px-1" style="color:#21c2b5"></h2></span>

                                    </div>
                                    <svg fill="#000000" height="24px" width="24px" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round">
                                        
                                    </g><g id="SVGRepo_iconCarrier"> <title>coins</title> <path d="M28.5 23h-12.246c0.359-0.619 0.634-1.29 0.816-2h11.43c0.553 0 1 0.447 1 1 0 0.552-0.447 1-1 1zM28.5 20h-11.236c0.041-0.328 0.069-0.661 0.069-1 0-0.34-0.028-0.672-0.069-1h11.236c0.553 0 1 0.447 1 1 0 0.552-0.447 1-1 1zM28.5 17h-11.43c-0.183-0.71-0.457-1.381-0.816-2h12.246c0.553 0 1 0.447 1 1 0 0.552-0.447 1-1 1zM28.5 14h-12.928c-0.65-0.811-1.453-1.493-2.369-2h15.297c0.553 0 1 0.447 1 1 0 0.552-0.447 1-1 1zM28.5 11h-16c-0.553 0-1-0.448-1-1 0-0.553 0.447-1 1-1h16c0.553 0 1 0.447 1 1 0 0.552-0.447 1-1 1zM28.5 8h-16c-0.553 0-1-0.448-1-1 0-0.553 0.447-1 1-1h16c0.553 0 1 0.447 1 1 0 0.552-0.447 1-1 1zM16.5 19c0 3.866-3.135 7-7 7s-7-3.134-7-7 3.134-7 7-7c3.865 0 7 3.134 7 7zM11.978 19.761c-0.101-0.239-0.231-0.447-0.394-0.624s-0.348-0.329-0.556-0.456c-0.208-0.127-0.42-0.24-0.637-0.341-0.217-0.1-0.429-0.194-0.637-0.284-0.208-0.089-0.395-0.185-0.559-0.287s-0.296-0.219-0.394-0.35c-0.098-0.131-0.147-0.286-0.147-0.466 0-0.12 0.022-0.234 0.065-0.342 0.044-0.107 0.11-0.2 0.2-0.277 0.089-0.076 0.201-0.137 0.334-0.18 0.133-0.044 0.29-0.065 0.469-0.065 0.229 0 0.439 0.027 0.631 0.083 0.191 0.057 0.36 0.118 0.506 0.187 0.146 0.068 0.269 0.131 0.369 0.189s0.173 0.086 0.219 0.086 0.082-0.012 0.109-0.037c0.026-0.025 0.048-0.064 0.062-0.119 0.015-0.054 0.024-0.123 0.031-0.206 0.006-0.084 0.009-0.187 0.009-0.308 0-0.108-0.002-0.199-0.006-0.271s-0.012-0.134-0.021-0.182c-0.011-0.048-0.023-0.087-0.037-0.116-0.016-0.029-0.043-0.064-0.085-0.105s-0.127-0.094-0.256-0.155c-0.129-0.062-0.277-0.118-0.443-0.167-0.167-0.050-0.346-0.089-0.537-0.118-0.039-0.006-0.079-0.004-0.118-0.009v-1.034h-0.984v1.034c-0.181 0.024-0.356 0.060-0.526 0.109-0.331 0.096-0.618 0.24-0.862 0.434s-0.438 0.438-0.581 0.73c-0.144 0.294-0.215 0.634-0.215 1.021 0 0.337 0.050 0.627 0.149 0.868s0.23 0.451 0.391 0.628c0.161 0.177 0.342 0.328 0.546 0.455 0.204 0.128 0.415 0.241 0.631 0.341s0.427 0.194 0.631 0.284 0.386 0.186 0.546 0.287c0.161 0.103 0.291 0.219 0.391 0.35 0.1 0.132 0.15 0.289 0.15 0.472 0 0.159-0.029 0.303-0.087 0.433s-0.143 0.237-0.253 0.325c-0.11 0.088-0.244 0.155-0.402 0.203-0.159 0.048-0.337 0.072-0.538 0.072-0.304 0-0.572-0.034-0.803-0.103s-0.43-0.145-0.597-0.229c-0.167-0.083-0.303-0.158-0.409-0.228-0.106-0.068-0.188-0.103-0.247-0.103-0.042 0-0.079 0.012-0.109 0.034-0.032 0.023-0.057 0.062-0.075 0.116-0.019 0.055-0.032 0.125-0.041 0.213s-0.013 0.196-0.013 0.325c0 0.192 0.012 0.339 0.034 0.441 0.023 0.103 0.062 0.181 0.116 0.234s0.142 0.115 0.265 0.186 0.276 0.137 0.459 0.201c0.183 0.063 0.395 0.118 0.634 0.164 0.239 0.045 0.499 0.067 0.778 0.067 0.012 0 0.023-0.002 0.036-0.002v0.963h0.983v-1.092c0.047-0.012 0.097-0.018 0.143-0.031 0.362-0.108 0.679-0.27 0.95-0.484s0.485-0.481 0.644-0.802c0.158-0.321 0.236-0.693 0.236-1.118 0.001-0.323-0.049-0.604-0.148-0.844zM15.572 24h12.928c0.553 0 1 0.447 1 1 0 0.552-0.447 1-1 1h-15.297c0.916-0.507 1.719-1.189 2.369-2z"></path> </g></svg>
                                </div>
                                <p>{{ $t('Total Paid') }}:</p>
                            </span> 
                        </div></v-col>
                    <v-col  col="2"><div id="arrival_dialog" role="button" class="border p-2 rounded">
                            <span> 
                                <div class="d-flex justify-space-between">
                                    <div class="d-flex">
                                        <span><h2 title="Checked-in" style="color:#ed610b;font-size: 24px"><CurrencyFormat :value="saleList.balance" /></h2></span><span><h2 class="px-1" style="color:#21c2b5"></h2></span>

                                    </div>
                                    <svg height="24px" width="24px" version="1.1" id="_x32_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512" xml:space="preserve" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <path class="st0" d="M511.814,273.543c0.068-0.202,0.135-0.388,0.186-0.59h-0.448L428.664,82.365c0,0,0,0,0.017,0 c10.713,0.794,19.604,1.536,26.129,2.17l1.672-17.924c-26.965-2.491-91.989-7.269-162.399-8.688 c-1.342-8.188-5.242-15.584-10.848-21.19c-6.94-6.957-16.623-11.279-27.235-11.279c-10.613,0-20.321,4.322-27.26,11.279 c-5.598,5.605-9.507,13.001-10.824,21.19C147.498,59.342,82.44,64.12,55.492,66.611l1.672,17.924 c6.543-0.634,15.416-1.376,26.146-2.17L0.43,272.953H0c0.042,0.202,0.126,0.388,0.177,0.59l-0.161,0.363l0.338,0.152 c12.546,39.848,49.794,68.73,93.787,68.73c43.976,0,81.208-28.882,93.77-68.73l0.329-0.152l-0.152-0.346l0.009-0.017 c0.042-0.202,0.118-0.388,0.168-0.59h-0.439L104.298,80.87c0,0,0,0,0.008,0c31.482-2.043,72.352-4.162,115.054-4.973 c1.874,5.851,5.141,11.111,9.38,15.357c4.904,4.93,11.22,8.526,18.261,10.215v299.817c-7.058,0-13.601,0-18.844,0 c-7.404,0-12.2,0-12.208,0h-7.666l-1.216,7.556c0,0.094-1.621,9.448-6.256,18.81c-2.296,4.686-5.302,9.338-8.966,12.942 c-3.69,3.605-7.86,6.188-13.095,7.354l-7.04,1.57v37.028h168.552v-8.982v-28.046l-7.032-1.57 c-5.302-1.182-9.532-3.833-13.272-7.531c-2.76-2.769-5.175-6.138-7.159-9.658c-2.997-5.277-5.024-10.908-6.256-15.129 c-0.625-2.11-1.039-3.884-1.292-5.082c-0.135-0.592-0.219-1.056-0.27-1.334l-0.051-0.304l-0.016-0.05l-1.208-7.573h-7.674 c0,0-13.997,0-31.043,0V101.469c7.042-1.688,13.339-5.284,18.244-10.215c4.247-4.246,7.522-9.506,9.405-15.357 c42.668,0.811,83.571,2.93,115.045,4.973c0.009,0,0.009,0,0.009,0l-83.53,192.083h-0.447c0.067,0.202,0.135,0.388,0.186,0.59 l-0.161,0.363l0.346,0.152c12.528,39.848,49.793,68.73,93.77,68.73c43.985,0,81.224-28.882,93.779-68.73l0.33-0.152l-0.152-0.346 V273.543z M94.141,327.372c-28.83,0-55.382-15.315-70.334-39.004h140.626C149.498,312.057,122.964,327.372,94.141,327.372z M171.01,272.953H17.248L94.116,96.159L171.01,272.953z M288.883,419.26c1.165,4.23,3.014,9.819,5.859,15.754 c2.921,6.044,6.898,12.494,12.503,18.117c4.061,4.086,9.101,7.699,15.036,10.156v5.276h-132.58v-5.276 c5.943-2.457,10.976-6.071,15.036-10.156c4.204-4.204,7.497-8.898,10.105-13.533c3.909-6.949,6.349-13.77,7.86-18.937 c0.135-0.48,0.262-0.928,0.388-1.401c1.504,0,3.2,0.017,5.066,0.017c7.421-0.017,17.425-0.017,27.834-0.017 C269.035,419.26,281.428,419.26,288.883,419.26z M272.936,75.636c-0.735,1.047-1.528,2.009-2.423,2.904 c-3.723,3.724-8.814,6.011-14.512,6.011c-5.708,0-10.798-2.287-14.546-6.011c-0.87-0.895-1.697-1.857-2.407-2.904 c-2.262-3.31-3.605-7.295-3.605-11.651c0-2.229,0.338-4.339,1.006-6.332c0.996-3.107,2.743-5.91,5.006-8.206 c3.748-3.715,8.838-6.011,14.546-6.011c5.699,0,10.789,2.296,14.512,6.011c2.288,2.296,4.036,5.099,5.04,8.206 c0.667,1.993,0.996,4.103,0.996,6.332C276.548,68.341,275.214,72.327,272.936,75.636z M417.858,327.372 c-28.823,0-55.366-15.315-70.317-39.004H488.15C473.232,312.057,446.689,327.372,417.858,327.372z M340.964,272.953l76.894-176.793 l76.886,176.793H340.964z"></path> </g> </g></svg>
                                            </div>
                                <p>{{ $t('Balance') }}:</p>
                            </span> 
                        </div></v-col>
                </v-row>
           
                <v-row v-if="actionName == 'Sale'">
                    <v-col v-for="s in saleList.sales" cols="12" md="3">
                        <v-card>
                            <template v-slot:title>
                                
                                {{ $t("Bill") }}#: {{ s.custom_bill_number || s.name}}
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
                <div v-else-if="actionName == 'Print'" class="mt-3"  style="width: 100%; height: 100%;">
                    <iframe id="print"  :src="`${printPreview}`"  style="width: 100%; height: 100%;"/>
                </div>
                <div v-else-if="actionName == 'Payment'" class="mt-3"  style="width: 100%; height: 100%;">
                    <iframe :src="`${serverUrl}/app/bulk-sale-payment/new-bulk-sale-payment?customer=${props.params.data}&cashier_shift=${current_cashier_shift.name}&working_day=${current_cashier_shift.working_day}`" height="100%"
                    width="100%" />
                </div>
                
                

        </template>
    </ComModal>
</template>

<script setup>
import { ref, defineEmits, inject, useRouter, i18n, onMounted } from '@/plugin'
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
const serverUrl = window.location.protocol + "//" + "//" + window.location.hostname + (window.location.protocol == "https:" ? "" : (":" + gv.setting.pos_setting.backend_port));
const printPreview = ref(serverUrl + `/printview?doctype=Customer&name=${props.params.data}&trigger_print=1&format=Unpaid%20Customer&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en`)
//frappe api call
const call = frappe.call()
const saleList = ref([])
const myIframe = ref(null)
const iframe = document.getElementById('myIframe');
onMounted(() => {
    isLoading.value = true
    let bulk_url = "epos_restaurant_2023.selling.doctype.customer.customer.get_unpaid_bills";
    let param = props.params.data
    if (props.params.doctype == "Bulk Sale"){
        bulk_url = "epos_restaurant_2023.selling.doctype.customer.customer.recent_bills_payment"
        printPreview.value = serverUrl + `/printview?doctype=Customer&name=${props.params.data}&bulk_sale_payment_name=${props.params.bulk_sale}&trigger_print=1&format=Unpaid%20Customer&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en`
        param = props.params.bulk_sale
    }
    call.get(bulk_url, {
        name: param
    }).then((res) => {
        saleList.value = res.message
        isLoading.value = false
    }).catch((err) => {
        isLoading.value = false
    })
})

const current_cashier_shift = ref('') 
call.get("epos_restaurant_2023.api.api.get_current_cashier_shift",
    {
        pos_profile: localStorage.getItem("pos_profile")}
).then((r)=>{
    current_cashier_shift.value=r.message
})

function onClose() {
    
    emit("resolve", false)
}
function onPrint(){
    var iframe = document.getElementById('print');
    iframe.src = iframe.src;
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
                event.data.action == "AfterPayment"
                printPreview.value = printPreview.value + `&bulk_sale_payment_name=${event.data.name}&is_payment=1`
                actionName.value = "Print"
            })
        } 
        
    }
    
}

</script>
<style>
.product-content {
    max-height: 200px;
    overflow-y: auto;
}
.st0{fill:#000000;}
</style>