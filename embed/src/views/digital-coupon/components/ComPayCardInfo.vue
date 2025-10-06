<template>
    <ComDialogContent> 
        <div class="p-grid p-ai-start p-pt-3"> 
            <div class="p-col-12 p-md-5">
                <div class="card-preview p-shadow-3 flex flex-column gap-3">
                    <div class="flex justify-content-between align-items-center">
                        <div>
                            <div class="label">{{t('Coupon Holder')}}</div>
                            <div class="value">{{data?.user_info?.full_name || ""}}</div>
                        </div>
                        <div class="">
                            <ComIcon icon="qrCodeIcon" height="20px"></ComIcon>
                        </div>
                    </div>
                    <div class="flex justify-content-center align-items-center">
                        <div>
                            <h1 class="text-xl">{{t('Scan to Pay')}}</h1>
                        </div>
    
                    </div>
                    <div>
                        <div class="qrcode text-center flex justify-content-center">
                            <div>
                                <!-- <ComIcon icon="qrCodeIcon" height="150px"></ComIcon> -->
    
                                <div class="qr-frame"> 
                                    <div v-if="!loading" class="overlay-loading-dialog">
                                        <div class="is-loading-page text-white flex justify-content-center flex-column align-items-center">
                                            <div><i class="pi pi-spin pi-spinner" style="font-size:35px"></i></div>
                                            <div class="text-sm">Loading....</div>
                                        </div>
                                    </div>    
                                    <div>
                                        <div class="corner top-left"></div>
                                        <div class="corner top-right"></div>
                                        <div class="corner bottom-left"></div>
                                        <div class="corner bottom-right"></div>
                                    </div>
     
                                    <Image class="text-center" width="250" @load="onLoading" :src="qrGenerateURL" alt="QR Code"/>
                                </div>
                                
                            </div>
                        </div>
                        <div class="card-number text-center">{{ t("Coupon Number") }}: {{data?.coupon_info?.coupon_number}}</div>
                    </div>
                    <div class="card-bottom p-d-flex p-jc-between p-ai-center flex justify-content-between">
                        <div>
                            <div class="label">{{t('Issue Date')}}</div>
                            <div class="value">{{dayjs(data?.coupon_info?.posting_date).format('DD-MM-YYYY')}}</div>
                        </div>
                        <div>
                            <div class="label">{{t('Used Amount')}}</div>
                            <div class="value text-right">
                                <currencyFormat :value="data?.coupon_info?.use_amount" />
                            </div>
                        </div>
                        <div>
                            <div class="label">{{t('Balance Amount')}}</div>
                            <div class="value text-right">
                                <currencyFormat :value="balance" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div> 
        <br/>
        <template #footer>
            <Button severity="secondary" class="w-full" icon="pi pi-cancel" @click="onClose">
                {{t("Close")}} ({{ countdown }}s)
            </Button>
        </template>
    </ComDialogContent>
</template>

<script setup>
import { onMounted, onUnmounted, ref, inject, computed } from 'vue'
import Image from 'primevue/image';
import Button from 'primevue/button'
import dayjs from "dayjs";
import {useHome} from "@/hooks/ecoupon/useHome.js"
const socket = inject("$socket");

const {homeData} = useHome()

socket.on("RefreshData", (arg) => {
 if(arg.action=="use_coupon_successfully"){
 
    if(arg.data.coupon_number == homeData.value.coupon_info.coupon_number){
 stopCountdown();
   dialogRef.value.close(arg.data);
    }
   
 }
    
})


 
const dialogRef = inject('dialogRef')
const data = ref({})
const loading = ref(false)

const countdown = ref(60);
let intervalId = null;

const balance = computed(() => (data.value?.coupon_info?.coupon_amount ?? 0) - (data.value?.coupon_info?.use_amount ?? 0))



const qrGenerateURL = computed(() =>
  `/api/method/epos_restaurant_2023.api.management_coupon.get_managment_qr_for_payment?coupon_number=${data.value?.coupon_info?.coupon_number}&timespan=${dayjs()}`

)



const onClose = () => {
   stopCountdown();
    dialogRef.value.close()

}

function stopCountdown() {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}


const countDownCloseDialog = () => {
 

  stopCountdown()

  intervalId = setInterval(() => {
    countdown.value -= 1;

   

    if (countdown.value <= 0) {
        alert("close me")
      stopCountdown()
    dialogRef.value.close();   
    }
  }, 1000);
};

onMounted(() => {
  data.value = dialogRef.value.data

  countDownCloseDialog()
})


const onLoading = () => {
    loading.value = true
}

onUnmounted(() => {
      stopCountdown();
  socket.off("RefreshData");

  
});

</script>

<style scoped>
.card-dialog .title {
    margin: 0;
    font-size: 1.05rem
}

.card-dialog .muted {
    color: var(--surface-500)
}


.card-preview {
    background: linear-gradient(135deg, #2b6cb0 0%, #4f46e5 100%);
    color: #fff;
    border-radius: 12px;
    padding: 18px;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.card-preview .chip {
    width: 48px;
    height: 36px;
    background: rgba(255, 255, 255, 0.14);
    border-radius: 6px;
    padding: 4px;
}

.card-preview .card-brand {
    font-size: 0.9rem;
    margin-top: 6px
}

.card-preview .card-number {
    font-family: 'Courier New', monospace;
    letter-spacing: 2px;
    font-size: 1.1rem;
    margin-top: 8px
}

.card-preview .label {
    font-size: 0.7rem;
    opacity: 0.9
}

.card-preview .value {
    font-weight: 600;
    font-size: 0.85rem
}


.hint {
    color: var(--surface-600);
    font-size: 0.85rem
}


@media (max-width: 640px) {
    .card-preview {
        min-height: 150px
    }
}


.p-dialog.card-dialog {
    max-width: 840px;
    width: 92%
}


.p-inputtext {
    min-height: 2.6rem
}


.p-inputtext:focus,
.p-button:focus {
    outline: 3px solid rgba(79, 70, 229, 0.12);
    outline-offset: 2px
}

.qr-frame {
    position: relative;
    width: 250px;
    height: 250px;
    padding: 20px;
    /* background: white;
    border: 4px solid #0a3a4d; */
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.qr-frame img {
    width: 100%;
    border-radius: 8px;
}

/* Decorative corners */
.corner {
    position: absolute;
    width: 20px;
    height: 20px;
    border: 4px solid #00c8ff;
}

.corner.top-left {
    top: 8px;
    left: 8px;
    border-right: none;
    border-bottom: none;
}

.corner.top-right {
    top: 8px;
    right: 8px;
    border-left: none;
    border-bottom: none;
}

.corner.bottom-left {
    bottom: 7px;
    left: 8px;
    border-right: none;
    border-top: none;
}

.corner.bottom-right {
    bottom: 7px;
    right: 8px;
    border-left: none;
    border-top: none;
}

.scan-text {
    margin-top: 16px;
    background: #00c8ff;
    color: white;
    font-weight: bold;
    padding: 8px 0;
    border-radius: 8px;
    font-family: sans-serif;
    font-size: 14px;
}
</style>