<template>
    <ComModal @onClose="onClose" @onOk="onClick()" titleOKButton="Stop Timer">
        <template #title>
            {{ $t('Stop Timer') }}
        </template>
        <template #content>
            Time IN
            <input type="datetime-local" v-model="saleProduct.time_in" >
            Time OUT
            <input type="datetime-local" v-model="saleProduct.time_out" >
        </template>
    </ComModal>
</template>
<script setup>
import { ref,inject,onMounted } from '@/plugin'
import { defineEmits } from 'vue';
import { useDisplay } from 'vuetify';
import moment from '@/utils/moment.js';
import { computed } from 'vue';

const frappe = inject("$frappe")
const call = frappe.call()
const { mobile } = useDisplay()
const props = defineProps({
    params: Object
})


const emit = defineEmits(["click"])

const saleProduct=computed(()=>props.params)

function onClick() {
    emit("resolve",date.value);
}

function onClose() {
    emit("resolve", false);
}
call.post("epos_restaurant_2023.api.api.get_time_product_estimate_price", { sp: saleProduct }).then((result) => {
    est_price.value = result.message
})
</script>