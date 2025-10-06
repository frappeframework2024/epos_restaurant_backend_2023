<template>
  
    <h2 class="font-bold mb-2">{{ t("Recent transaction") }}</h2>
  <div class="flex flex-column gap-2 transaction-list">
  
    
    <div v-for="(d,index) in dates" :key="index">
    <h2 class="mt-2 px-2">{{ getDate(d) }}</h2>
    
    
        <div v-for="ct in getDataByDate(d)" :key="ct.name" class="my-2">
                <ComCouponTransactionCard :data="ct"/>
        </div>
        
    </div>
  </div>
  
</template>
<script setup>
 
import { computed } from "vue"
import ComCouponTransactionCard from "@/views/digital-coupon/components/ComCouponTransactionCard.vue"
import dayjs from "dayjs"


const props = defineProps({
  couponInfo: Object,
   transactions: {
    type: Array,
    default: () => []
  },
})


const dates = computed(()=>{
    const d =   props.transactions?.map(x=>x.posting_date);
    return  [...new Set(d)]
  .sort((a, b) => new Date(b) - new Date(a));

})

const t = window.t;

function getDate(d){
    if(d==dayjs().format("YYYY-MM-DD")) return t("Today")
    if (d == dayjs().subtract(1, "day").format("YYYY-MM-DD")) return t("Yesterday")
    return dayjs(d).format("DD-MM-YYYY")
}

function getDataByDate(d){
    return props.transactions.filter(x=>x.posting_date == d)
}




</script>


 

 


<!-- <template> 
  <h2 class="font-bold mb-2">{{ t("Recent transaction") }}</h2>
  <div class="flex flex-column gap-2 transaction-list">
    <div v-for="(item, index) in transactions" :key="index" @click="openTransactionDetail(item.name)">
      <div class="transaction-item flex justify-content-between gap-3 border-round-xl p-3 align-items-center">
        <div class="flex gap-3 align-items-center">
          <div>
            <div class="transaction-icon">
              <ComIcon icon="arrowDownRightIcon" />
            </div>
          </div>
          <div>
            <p><strong>{{ item.pos_profile }}</strong></p>
            <p><small class="text-xs">
              {{ item.transaction_date ? dayjs(item.transaction_date).format('DD-MM-YY h:mm A') : '-' }}
            </small></p>
          </div>
        </div>
        <div class="text-right">
          <p class="text-1xl tran-price white-space-nowrap">
            <strong><currencyFormat :value="item.coupon_amount || 0"/></strong>
          </p>
          
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>

</script> -->