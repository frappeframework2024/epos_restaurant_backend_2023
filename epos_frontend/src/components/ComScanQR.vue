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
import { defineEmits, ref, i18n,inject,createToaster} from '@/plugin'
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
const toaster = createToaster({ position: "top-right" });
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
    let param = props.params;
    let request_params = {
        "property_code":gv.setting.property_code, //required
        "pos_config":gv.setting.pos_config, //required
        "payment_amount": Number( param.payment_amount), //required
        "currency":param.currency, // required
        "lifetime":6,  //default None mean 30days
        // "deeplink":false, //default false
        // "image":false, //default false
        "response":{ //this custom data callback when ABA success payment
            "pos_profile": gv.setting.pos_profile,
            "station_name":gv.device_setting.name,
            "invoice_id": sale.sale.name,
        }
    }
     const resp = await call.post("epos_restaurant_2023.api.payway.aba_generate_qr", request_params);

    if(resp){        
        sale.sale.show_aba_khqr = true
        sale.sale.aba_khqr_data = resp.message;
        socket.emit("ShowOrderInCustomerDisplay", sale.sale,"", sale.customer_display_key);
        sale.sale.show_aba_khqr = undefined;
        sale.sale.aba_khqr_data = undefined;
    }else{
        toaster.warning($t(resp.message.message));
        onClose();
    }

})
</script>