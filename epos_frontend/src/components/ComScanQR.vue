<template>
    <v-dialog v-model="open" width="70%" @update:modelValue="onAction()">
        <v-card height="500" class="d-flex align-center justify-center">
            <v-card-title>
                <v-btn icon @click="onClose()" style="position: absolute; top: 8px; right: 8px;">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-card-title>
            <img src="@/assets/images/loading.gif" />
            <div>Please Wait</div>
            <div>Payment Is Processing...</div>
            <div>This May Take a Few Seconds</div>
        </v-card>
    </v-dialog>
</template>
<script setup>
import { defineEmits, ref, i18n,inject} from '@/plugin'
import { onMounted, onUnmounted } from 'vue';
const { t: $t } = i18n.global; 
const emit = defineEmits(['resolve'])
const sale = inject("$sale")
const gv = inject('$gv')
const frappe = inject("$frappe")
const numberFormat = inject("$numberFormat")
const call = frappe.call()
const open = ref(true)
import socket from '@/utils/socketio';
const props = defineProps({
    params: Object
})

function onClose(){
    open.value = false
    onAction(open.value)
}
function onAction(val) {
    if (!val) {
        socket.emit("ShowOrderInCustomerDisplay", sale.sale,"", sale.customer_display_key);
    }
}

onMounted(async ()=>{
     const resp = await call.post("epos_restaurant_2023.api.payway.aba_generate_qr", {
        "pos_config": "Main POS Config",
        "payment_amount ":0.01,
        "currency":"USD",
        "custom_field":{
            "field_name":"My Custom Field"
        },
        "return_params ":{
            "doc_name":sale.name
        }
    });

    if(resp){        
        sale.sale.show_aba_khqr = true
        sale.sale.aba_khqr_data = resp.message;
        socket.emit("ShowOrderInCustomerDisplay", sale.sale,"", sale.customer_display_key);
        sale.sale.show_aba_khqr = undefined;
            sale.sale.aba_khqr_data = undefined;
    }

})
</script>