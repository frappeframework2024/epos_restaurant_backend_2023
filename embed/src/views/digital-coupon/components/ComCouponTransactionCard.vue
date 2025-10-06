<template> 
 
  <div class="flex flex-column gap-2" @click="openTransactionDetail">

      <div class="transaction-item flex justify-content-between gap-3 border-round-xl p-3 align-items-center">
        <div class="flex gap-3 align-items-center">
          <div>
            <div class="transaction-icon">
              <ComIcon icon="arrowDownRightIcon" />
            </div>
          </div>
          <div>
            <p><strong>{{ data.pos_profile }}</strong></p>
            <p><small class="text-xs">
              {{ data.transaction_date ? dayjs(data.transaction_date).format('DD-MM-YY h:mm A') : '-' }}
            </small></p>
            
          </div>
        </div>
        <div class="text-right">
          <p class="text-1xl tran-price white-space-nowrap text-red-500">
            <strong><currencyFormat :value="data.coupon_amount || 0"/></strong>
          </p>
          
        </div>
      </div>
    </div>
  
</template>
<script setup>
import { useRouter } from 'vue-router';
import dayjs from "dayjs";


const router = useRouter();
const t = window.t;

const openTransactionDetail = () => {
  router.push({ name: 'eCouponTransactionDetail', params: { id: props.data.name} });
};

const props = defineProps({
    data:Object
})

</script>