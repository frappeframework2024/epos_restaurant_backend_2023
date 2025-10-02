<template>
    <div>
        <!-- <h1>Hello this is my home page</h1>
            <ComDailyUseChart/>
        {{ homeData }} -->
    
    
        <div class="main w-11	mx-auto flex flex-column gap-4">
            <div>
                <ComUserProfile/>
            </div>
            <div>
                <div class="balance-wrapper p-4 border-round-xl flex flex-column justify-content-between gap-4">
                    <ComCouponDashboardKPI/>
                </div>
            </div>

            <div class="chart-wrapper p-4 border-round-xl">
                <ComCouponDataChart/>
            </div>
    
            <div class="transaction-wrapper p-4 border-round-xl">
                <ComCouponRecentTransaction/>
            </div>
    
            <!-- <div class="card flex justify-content-center my-5">
              <Button label="Submit" />
          </div> -->
    
        </div>
    
    </div>
</template>
<script setup>
import Button from 'primevue/button';
import { onMounted, ref } from 'vue';
import { useHome } from '@/hooks/ecoupon/useHome.js';
import ComDailyUseChart from "@/views/digital-coupon/components/ComDailyUseChart.vue"
import ComUserProfile from '@/views/digital-coupon/components/ComUserProfile.vue'
import ComCouponDashboardKPI from '@/views/digital-coupon/components/ComCouponDashboardKPI.vue'
import ComCouponDataChart from '@/views/digital-coupon/components/ComCouponDataChart.vue'
import ComCouponRecentTransaction from '@/views/digital-coupon/components/ComCouponRecentTransaction.vue'
const { getHomeData, homeData } = useHome()


onMounted(async () => {
  await getHomeData();
})
</script>
<style scoped>

</style>