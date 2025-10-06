<template> 
    <div class="pt-4">
        <div class="w-11 mx-auto flex flex-column gap-4">
            <a href="#" class="back" @click="goBack()">
                <i class="pi pi-arrow-left"></i> {{t('Back')}}
            </a>
    
            <h2 class="mb-3">{{t('Transaction Details')}}</h2>
    
            <div class="amount-card">
                <i class="pi pi-receipt text-red-500 text-6xl mb-2"></i>
                <div class="amount text-7xl">
                    <currencyFormat :value="data?.coupon_amount" />
                </div>
                <div class="label text-3xl  ">{{t('Payment Amount')}}</div>
            </div>
    
            <div class="card">
                <div class="mb-3">
                    <div class="section-label icon-text">
                        <i class="pi pi-map-marker text-green-500"></i> {{t('Store')}}
                    </div>
                    <div class="section-value">{{data.pos_profile}}</div>
                </div>
    
                <hr>
    
                <!-- <div class="mb-3">
                    <div class="section-label icon-text">
                        <i class="pi pi-tag text-green-500"></i> Description
                    </div>
                    <div class="section-value">Lunch - Pad Thai & Spring Rolls</div>
                </div> -->
    
                <!-- <hr> -->
    
                <div class="mb-3">
                    <div class="section-label icon-text">
                        <i class="pi pi-calendar text-green-500"></i> {{t('Date & Time')}}
                    </div>
                    <div class="section-value">
                        {{ data.transaction_date ? dayjs(data.transaction_date).format('DD-MM-YY h:mm A') : '-' }}
                    </div>
                </div>
    
               
    
                <hr> 
    
                <div>
                    <div class="section-label icon-text">
                        <i class="pi pi-wallet text-green-500"></i> {{ t("Balance After") }}
                    </div>
                    <div class="balance"><currencyFormat :value="balanceAfter" /></div>
                </div>
                 <hr>
    
                <div class="mb-3">
                    <div class="section-label icon-text">
                        <i class="pi pi-hashtag text-green-500"></i> {{ t("Transaction ID") }}
                    </div>
                    <div class="section-value">{{ data.name }}</div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { getDoc,getApi, ref } from '@/plugin'
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

import dayjs from "dayjs";

const t = window.t
const route = useRoute()
const loading = ref(false)
const data = ref({})

const balanceAfter = ref(0)


function goBack(){
    history.go(-1);
}

onMounted(async () => {
  
    await  getDoc("Coupon Transaction", route.params.id).then(doc => {
        data.value = doc
        
        loading.value = false  
    }).catch(error => {
        loading.value = false
    })


    await getApi("management_coupon.get_use_coupon_transaction_balance_after",{
        transaction_id: data.value.name
    }).then(x=>{
        balanceAfter.value = x.message
    })
})


</script>

<style scoped>
.card {
    background: #fff;
    border-radius: .75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    padding: 1.5rem;
}

.amount-card {
    background: #fff5f5;
    border-radius: .75rem;
    text-align: center;
    padding: 2rem 1rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.amount {
    font-size: 2rem;
    font-weight: 700;
    color: #ef4444;
}

.label {
    font-size: 0.9rem;
    color: #64748b;
    margin-top: 0.25rem;
}

.section-label {
    color: #64748b;
    font-size: 0.85rem;
}

.section-value {
    color: #0f172a;
    font-weight: 600;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1rem 0;
}

.icon-text {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.balance {
    color: #16a34a;
    font-weight: 700;
}

.back {
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    margin-bottom: 1rem;
}

.back:hover {
    text-decoration: underline;
}
</style>