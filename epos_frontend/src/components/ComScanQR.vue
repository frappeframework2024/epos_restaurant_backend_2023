<template>
    <v-dialog v-model="open" :width="mobile ? '100%' : '50%'" persistent :fullscreen="mobile">

        <v-card height="500" class="d-flex align-center justify-center" v-if="!sale.sale.show_aba_khqr" >
            <v-card-title>
                <v-btn v-if="timerCount <= 0" icon @click="onClose()" style="position: absolute; top: 8px; right: 8px;">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-card-title> 
                <img width="50" src="@/assets/images/loading.gif" />
                <div>{{ $t('Please wait') }}</div>
                <div>{{$t("Payment is processing QR")}}...</div>
                <div>{{ $t("This may be take a few seconds") }}</div> 
        </v-card>
        <template v-else> 
             <ComPayWayQRDisplayABATemplate :qrData="qrData" :remaining="autoClose" :showClose="timerCount <= 0" @onClose="onClose()" />
        </template>

    </v-dialog>
</template>
<script setup>
    import { defineEmits, ref, i18n,inject,createToaster,onMounted,onUnmounted ,watch} from '@/plugin';
    import { useDisplay } from 'vuetify'
    import socket from '@/utils/socketio'; 
    import ComPayWayQRDisplayABATemplate from '../views/sale/components/ComPayWayQRDisplayABATemplate.vue';
    const { mobile } = useDisplay();
    const { t: $t } = i18n.global; 
    const emit = defineEmits(['resolve'])
    const sale = inject("$sale")
    const gv = inject('$gv')
    const frappe = inject("$frappe")
    const call = frappe.call()
    const open = ref(true);

    const timerCount = ref(5);
    const autoClose = ref(90); //close in 90sec

    const toaster = createToaster({ position: "top-right" });

    const qrData = ref(null); 
    const props = defineProps({
        params: Object
    });

    const requestParam = ref({})

 

    watch(() => sale.payway_complete_payment,(newVal) => {
        if (newVal === true) {
            onClose(true)
        }
    });

    function onClose(success=false){
        open.value = false;
        sale.sale.show_aba_khqr = undefined
        sale.sale.aba_khqr_data = undefined;
        qrData.value = null;
        socket.emit("ShowOrderInCustomerDisplay", sale.sale,"", sale.customer_display_key);       
        if(!success){
            let _param = requestParam.value;
            call.post("epos_restaurant_2023.api.payway.aba_close_transaction", { 
                "tran_id": _param.tran_id,
                "property_code": _param.property_code,
                "pos_config": _param.pos_config,
                "invoice_id": _param.response.invoice_id
            }); 
        }

        emit('resolve',success);

        
    }

    let countdown = null;
    onMounted(async ()=>{
        let param = props.params;
        let request_params = {
            "tran_id": sale.getUniqueKey(gv.setting.payway_prefix_code),
            "property_code":gv.setting.property_code, //required
            "pos_config":gv.setting.pos_config, //required
            "payment_amount": Number( param.payment_amount), //required
            "currency":param.currency, // required
            // "lifetime":5, //5min ~ default None mean 30days
            // "deeplink":false, //default false
            "image":true, //default false
            "response":{ //this custom data callback when ABA success payment
                "pos_profile": gv.setting.pos_profile,
                "station_name":gv.device_setting.name,
                "invoice_id": param.sale_id,
                "temp_tran_id":param.temp_tran_id
            },
            "sale_payments":  sale.sale.payment //required
        }    
        requestParam.value = request_params;

        try{
            const resp = await call.post("epos_restaurant_2023.api.payway.aba_generate_qr", request_params); 
            if(resp){   
                sale.sale.show_aba_khqr = true ;
                qrData.value = {
                    "tran_id":resp.tran_id,
                    "bank_acc_name":resp.bank_acc_name,
                    "qr_image_custom":resp.qr_image_custom,
                    "qr_image":resp.qr_image,
                    "currency": param.currency,
                    "amount":Number(param.payment_amount),
                    "invoice_date": sale.sale.posting_date
                };
                sale.sale.aba_khqr_data =  qrData.value ;                  
                socket.emit("ShowOrderInCustomerDisplay", sale.sale,"", sale.customer_display_key);

                //timer count
                countdown = setInterval(()=>{
                    autoClose.value --;
                    if (timerCount.value > 0){
                         timerCount.value--;
                    }                   

                    if(autoClose.value <= 0){
                        clearInterval(countdown); 
                        countdown = null; 
                        onClose();                      
                    }
                    
                },1000);

                //
                startCheckTransaction();

            
 
            }

        } catch (err){
           setTimeout(()=>{
            let status_code = "";
            if(err.status_code){
                status_code = `(status code: ${err.status_code})`;
            }
            toaster.warning($t(`${err.message} ${status_code}`));
            onClose();    
           },1500)
        }
       
    });



   let timer = null;
    let stopped = false;

    async function poll() {
        if (stopped) return;
        if(requestParam.value){
            const p = requestParam.value
            const request_params = { 
                "tran_id": p.tran_id,//required
                "property_code":p.property_code, //required
                "pos_config":p.pos_config, //required
                "response":{ //required
                    "pos_profile": p.response.pos_profile,
                    "station_name":p.response.station_name,
                    "invoice_id": p.response.invoice_id,
                    "temp_tran_id":p.response.temp_tran_id
                }
            }
            try{
                const resp = await call.post("epos_restaurant_2023.api.payway.aba_check_transaction", request_params)
                if(resp){
                    if((resp.message ||"") != "" && (resp.message ||"").toLowerCase() != "pending"){
                        stopCheckTransaction();
                        return;
                    }
                } 
            }
            catch (err) {
                console.error("PayWay check failed", err);
            }
           
        }       
        timer = setTimeout(poll, 3000);
    }

    function startCheckTransaction() {
        stopped = false;
        poll();
    }

    function stopCheckTransaction() {
        stopped = true;
        clearTimeout(timer);
    }


    onUnmounted(() => {
        sale.payway_complete_payment = false;

        if (countdown) {
            clearInterval(countdown);
            countdown = null;
        }

        stopCheckTransaction();
    });

</script>



