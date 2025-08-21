<template>
    <ComModal :persistent="true" :fullscreen="mobile" @onClose="onClose()" :hide-ok-button="true" :hide-close-button="true">
        <template #title>
            <div>{{ $t('Voucher') }}</div>
        </template>
        <template #content>
            <div>
                <div class="mb-2">
                    <ComInput autofocus :placeholder="$t('Search')" keyboard v-model="search" v-debounce="onSearch" @onInput="onSearch"/>
                </div>
                <div style="white-space: pre-line;font-family: Arial;font-size: 15px;margin-top: -5px;">{{ voucher_info }}</div>
                <div style="color: red;font-family: Arial;font-size: 15px;margin-top: -5px;">{{ error_msg }}</div>
            </div>
        </template>
        <template #action>
             <v-btn v-if="gv.setting.pos_setting.show_voucher_minimum_overwrite == 1" :disabled="error_type != 3" variant="flat" @click="onOverwrite()" color="primary" style="font-family: Arial;">
                {{ $t('Overwrite') }}
            </v-btn>
            <v-btn :disabled="disable == 1" variant="flat" @click="onOK()" color="primary" style="font-family: Arial;">
                {{ $t('Ok') }}
            </v-btn>
        </template>
    </ComModal>
</template>
<script setup>
import { defineEmits, ref, i18n,inject,onMounted} from '@/plugin'
import { useDisplay } from 'vuetify';
const { t: $t } = i18n.global; 
const emit = defineEmits(['resolve'])
const { mobile } = useDisplay()  
let search = ref()
let error_msg = ref()
let disable = ref(1)
let voucher_amount = ref(0)
let voucher_info = ref()
let voucher_customer = ref("")
let error_type = ref(0)
let voucher_name = ref("")
const sale = inject("$sale")
const gv = inject('$gv')
const frappe = inject("$frappe")
const numberFormat = inject("$numberFormat")
const call = frappe.call()
const props = defineProps({
    params: Object
})
const format = ref("#,###,##0.00##")
onMounted(() => {
    const currency_setting = gv.setting?.currencies.find(r => r.name == gv.setting?.default_currency)
    if (currency_setting) {
        format.value = currency_setting.pos_currency_format
    }
})
function onSearch(keyword) {
    search.value = keyword;
    if((keyword || "") != ""){
        call.get('epos_restaurant_2023.api.api.get_voucher_info',{"name":search.value}).then((result) => {
        let voucher = result.message
        voucher_amount.value = voucher.amount
        voucher_name.value = voucher.name
        voucher_customer.value = voucher.customer
        if(voucher.name == "Not Found"){
             clear_msg()
            error_msg.value = "Voucher Not Found"
            error_type.value = 1
        }
        else{
            if(voucher.is_expired == 1){
                clear_msg()
               error_msg.value = "Voucher Expired"
               error_type.value = 2
            }
            else if(voucher.used == 1){
                clear_msg()
                error_msg.value = "Voucher Already Used"
                error_type.value = 4
            }
            else if(voucher.min_bill_amount > sale.sale.grand_total){
                clear_msg()
                error_msg.value = "Below Minimum Amount"
                error_type.value = 3
            }
            else{
                disable.value = 0
                error_msg.value = ""
                voucher_info.value = "Expired Date: " + voucher.expired_date
                voucher_info.value += "\nVoucher Amount: " + numberFormat(format.value, voucher.amount)
                error_type.value = 5
            }
        }
    })
    }
    else{
        clear_msg()
    }
}
function clear_msg(){
    disable.value = 1
    error_msg.value = ""
    voucher_info.value = ""
}
function onOverwrite(){
    gv.authorize("overwrite_voucher_minimum_amount_required_password", "allow_overwrite_voucher_minimum_amount","Overwrite").then(async (v) => {
    if(v){
        disable.value = 0
        }
    })
}
function onClose() {
    emit('resolve', false)
}
function onOK() {
    if(sale.sale.grand_total<voucher_amount.value){
        voucher_amount.value = sale.sale.grand_total
    }
    emit('resolve', {"voucher_amount":voucher_amount.value,"voucher_name":voucher_name.value,"voucher_customer":voucher_customer.value})
}
</script>