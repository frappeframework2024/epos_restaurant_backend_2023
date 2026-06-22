<template>
    <ComModal :persistent="true" :fullscreen="mobile" @onClose="onClose()" :hide-ok-button="true" :hide-close-button="true">
        <template #title>
            <div>{{ $t('Coupon') }}</div>
        </template>
        <template #content>
            <div>
                <div class="mb-2">
                    <ComInput autofocus :placeholder="$t('Search')" keyboard v-model="search" v-debounce:250="onSearch" @onInput="onSearch"/>
                </div>
                <div style="font-family: Arial;font-size: 15px;margin-top: -5px;">{{ msg }}</div>
                <div style="color: red;font-family: Arial;font-size: 15px;margin-top: -5px;">{{ error_msg }}</div>
            </div>
        </template>
        <template #action>
            <v-btn :disabled="disable === true && overwrite_disable === false" variant="flat" @click="onOK()" color="primary" style="font-family: Arial;">
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
let voucher_data = ref()
let disable = ref(true)
let overwrite_disable = ref(false)
let msg = ref()
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
    overwrite_disable.value = props.params?.overwrite_disable ?? false
})
function onSearch(keyword) {
    search.value = keyword;
    if((keyword || "") != ""){
        const current_coupon_payment = sale.sale.payment?.reduce((sum, p) => p.coupon_code === keyword? sum + Number(p.amount || 0): sum,0) ?? 0;
        let payment_amount = sale.paymentInputNumber == 0 ? current_coupon_payment:parseFloat(sale.paymentInputNumber);
        console.log(current_coupon_payment)
        call.get('epos_restaurant_2023.api.api.check_valid_sale_product_as_coupon',
        {"date":sale.sale.posting_date,"coupon_code":search.value,"total_coupon_payment":current_coupon_payment,"payment_amount":payment_amount}).
        then((result) => {
            msg.value = null
            error_msg.value = null
            voucher_data.value = result.message
            if(result.message && result.message.data){
                msg.value = "Remaining Amount: " + numberFormat(format.value, parseFloat(result.message.data.remaining_amount))
                if(parseFloat(result.message.data.remaining_amount) <= 0){
                    disable.value = true
                    return
                }
            }
            if(result.message && result.message.error){
                error_msg.value = result.message.error
            }
            disable.value = error_msg.value == null ? false : true
        })
    }
    else{
        voucher_data.value = null
        error_msg.value = null
        msg.value = null
        disable.value = true
    }
}
function onClose() {
    emit('resolve', false)
}
function onOK() {
    if (overwrite_disable.value == true) {
        emit('resolve');
    }
    else{
         emit('resolve', {"coupon_code":search.value,"remaining_amount":voucher_data.value.data.remaining_amount})
    }
}
   
</script>