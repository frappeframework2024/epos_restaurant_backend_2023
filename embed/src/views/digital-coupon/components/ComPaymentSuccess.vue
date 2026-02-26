<template>
    <ComDialogContent> 
 <div class="pt-4">
  
        <div class="w-11 mx-auto flex flex-column gap-4">
           
            <div class="amount-card">

                <!-- <i class="pi pi-receipt text-red-500 text-6xl mb-2"></i> -->
                 <div class="success-wrapper">
             <svg :width="size" :height="size" viewBox="0 0 120 120">
                <circle class="circle" cx="60" cy="60" r="46" :fill="color"/>
                <path class="check" d="M40 62 L54 76 L80 48" stroke="#fff" stroke-width="8" fill="none"/>
            </svg>
            </div>
                <div class="amount text-7xl text-center text-red-500">
                    <currencyFormat :value="data?.original_used_amount" />
                </div>
                <div class="label text-3xl text-center">{{t('Payment Amount')}}</div>
            </div>
    
            <div class="card">
                <div class="mb-3">
                    <div class="section-label icon-text">
                        <i class="pi pi-map-marker text-green-500"></i> {{t('Store')}}
                    </div>
                    <div class="section-value">{{data?.pos_profile}}</div>
                </div>
    
                <hr>
    
           
    
                <div class="mb-3">
                    <div class="section-label icon-text">
                        <i class="pi pi-calendar text-green-500"></i> {{t('Date & Time')}}
                    </div>
                    <div class="section-value">
                        {{ data?.transaction_date ? dayjs(data?.transaction_date).format('DD-MM-YY h:mm A') : '-' }}
                    </div>
                </div>
    
                <hr> 
    
                <div>
                    <div class="section-label icon-text">
                        <i class="pi pi-wallet text-green-500"></i> {{ t("Balance After") }}
                    </div>
                    <div class="balance"><currencyFormat :value="data?.current_balance" /></div>
                </div>
                 <hr>
    
                <div class="mb-3">
                    <div class="section-label icon-text">
                        <i class="pi pi-hashtag text-green-500"></i> {{ t("Transaction ID") }}
                    </div>
                    <div class="section-value">{{ data?.used_transaction_id }}</div>
                </div>
            </div>
        </div>
    </div>
    



        <br/>
        <template #footer>
            <Button severity="secondary" class="w-full" icon="pi pi-cancel" @click="onClose">
                {{ t("Close") }} ({{ countdown }}s)
            </Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { inject,onMounted, getDoc,getApi, ref } from '@/plugin'
 
import Button from 'primevue/button'
import dayjs from "dayjs";
const data = ref()
 
const dialogRef = inject('dialogRef')

const countdown = ref(15);
let intervalId = null;

function stopCountdown() {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}


const onClose = () => {
    stopCountdown()
    dialogRef.value.close()

}

const countDownCloseDialog = () => {
 

stopCountdown()

  intervalId = setInterval(() => {
    countdown.value -= 1;
 

    if (countdown.value <= 0) {
        stopCountdown()
      dialogRef.value.close();   
     
    }
  }, 1000);
};

onMounted(async () => {
 data.value = dialogRef.value.data.data;
  countDownCloseDialog()
})

defineProps({
  color: { type: String, default: "#10B981" },
  size: { type: [Number,String], default: 120 }
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
 .circle { transform-origin:60px 60px; opacity:0; animation:ci 0.6s cubic-bezier(.2,.9,.3,1) forwards;}
      @keyframes ci {0%{transform:scale(0.6);opacity:0}60%{transform:scale(1.05);opacity:1}100%{transform:scale(1);opacity:1}}
      .check { stroke-dasharray:100; stroke-dashoffset:100; animation:dc 0.45s cubic-bezier(.2,.9,.3,1) 0.28s forwards; stroke-linecap:round; stroke-linejoin:round;}
      @keyframes dc { to{stroke-dashoffset:0} }

      .success-wrapper {
  display: flex;
  justify-content: center; /* horizontal center */
  align-items: center;     /* vertical center */
   
}
</style>