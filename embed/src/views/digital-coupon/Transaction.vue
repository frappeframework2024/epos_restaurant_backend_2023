<template> 
    <div class="coupon-transaction-header py-3">
        <div class="flex align-items-center gap-2">
            <div>
                <div><ComIcon icon="transactionIcon" height="40px"></ComIcon></div></div>
            <div>
                <h2>{{ t("Transactions") }}</h2>
                <p>{{t("Your payment history")}}</p>
            </div>
        </div>
    </div> 
    
    <div style="margin-top: 7rem"> 
        <div v-for="(d,index) in dates" :key="index">
            <h2 class="mt-4 px-4">{{ getDate(d) }}</h2> 
            <div v-for="ct in getDataByDate(d)" :key="ct.name" class="my-2 px-4">
                <ComCouponTransactionCard :data="ct" />
            </div> 
        </div>
    </div>
</template>
<script setup>

import { useHome } from "@/hooks/ecoupon/useHome.js"
import { computed, onMounted } from "vue"
import ComCouponTransactionCard from "@/views/digital-coupon/components/ComCouponTransactionCard.vue"
import dayjs from "dayjs"
const { couponTransactionData, getCouponTransaction } = useHome()
const dates = computed(() => {
  const d = couponTransactionData.value?.map(x => x.posting_date);
  return [...new Set(d)]
    .sort((a, b) => new Date(b) - new Date(a));

})

const t = window.t;

function getDate(d) {
  if (d == dayjs().format("YYYY-MM-DD")) return t("Today")
  if (d == dayjs().subtract(1, "day").format("YYYY-MM-DD")) return t("Yesterday")
  return dayjs(d).format("DD-MM-YYYY")
}

function getDataByDate(d) {
  return couponTransactionData.value.filter(x => x.posting_date == d)
}
onMounted(async () => {
  await getCouponTransaction()
})



</script>

<style scoped>
.coupon-transaction-header {
    background-color: #ffffff26;
    padding: 10px; 
    box-shadow: #0000003d 0 3px 8px;
    margin-bottom: 1rem;
    border: 1px solid rgba(255, 255, 255, .8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    position: fixed;
    top: 0;
    z-index: 1000;
    width: 100%;
   
}
</style>
 

 