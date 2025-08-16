<template>
    <ComModal :persistent="true" :fullscreen="mobile" @onClose="onClose()" :hide-ok-button="true" :hide-close-button="true">
        <template #title>
            <div>{{ $t('Voucher') }}</div>
        </template>
        <template #content>
            <div>
                <div class="mb-2">
                    <ComInput autofocus :placeholder="$t('Search')" keyboard v-model="search" v-debounce="onSearch" />
                </div>
                <div style="color: red;font-family: Arial;font-size: 14px;margin-top: -5px;">{{ error_msg }}</div>
            </div>
        </template>
        <template #action>
            <v-btn :disabled="disable == 1" variant="flat" @click="onOK()" color="primary">
                {{ $t('Ok') }}
            </v-btn>
        </template>
    </ComModal>
</template>
<script setup>
import { defineEmits, ref, i18n,inject} from '@/plugin'
import { useDisplay } from 'vuetify';
const { t: $t } = i18n.global; 
const emit = defineEmits(['resolve'])
const { mobile } = useDisplay()  
let search = ref()
let error_msg = ref()
let disable = ref(1)
let voucher_amount = ref(0)
const sale = inject("$sale")
const gv = inject('$gv')
const frappe = inject("$frappe")
const call = frappe.call()
const props = defineProps({
    params: Object
})

function onSearch(keyword) {
    search.value = keyword;
    if((keyword || "") != ""){
        call.get('epos_restaurant_2023.api.api.get_voucher_info',{"name":search.value,"branch":gv.setting?.business_branch}).then((result) => {
        let voucher = result.message
        voucher_amount.value = voucher.amount
        if(voucher.name == "Not Found"){
            error_msg.value = "Voucher Not Found"
        }
        else{
            if(voucher.is_expired == 1){
               error_msg.value = "Voucher Expired"
            }
            else if(voucher.min_bill_amount > sale.sale.grand_total){
                error_msg.value = "Below Minimum Amount"
            }
            else{
                disable.value = 0
            }
        }
    })
    }
    else{
        error_msg.value = ""
    }
}
function onClose() {
    emit('resolve', false)
}
function onOK() {
    emit('resolve', {"voucher_amount":voucher_amount.value})
}
</script>