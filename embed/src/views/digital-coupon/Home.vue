<template>
    <div class="pt-4"> 
        <div class="w-11 mx-auto flex flex-column gap-4">
            <div>
                <ComUserProfile :data="homeData"/>
            </div>
            <div>
                <div class="balance-wrapper p-3 border-round-xl flex flex-column justify-content-between gap-4">
                    <ComCouponDashboardKPI/>
                </div>
            </div>

            <div class="">
                <Button class="w-full py-3" :label="t('Pay Now')" icon="pi pi-credit-card" @click="payNow"/>
            </div>

            <div class="chart-wrapper p-3 border-round-xl">
                <ComCouponDataChart :data="homeData?.chart_data" v-if="homeData?.chart_data"/>
            </div>
    
            <div class="transaction-wrapper p-3 border-round-xl">
                <!-- <ComCouponRecentTransaction  :transactions="homeData.recent_coupon_transaction" /> -->
                <ComCouponRecentTransaction  :transactions="homeData.recent_coupon_transaction" 
                :couponInfo="homeData.coupon_info" />
            </div> 

        </div>
    
    </div>
</template>
<script setup>
import Button from 'primevue/button';
import { useDialog } from 'primevue/usedialog'
import { onMounted, ref, inject } from 'vue';
import { useHome } from '@/hooks/ecoupon/useHome.js';

import ComUserProfile from '@/views/digital-coupon/components/ComUserProfile.vue'
import ComCouponDashboardKPI from '@/views/digital-coupon/components/ComCouponDashboardKPI.vue'
import ComCouponDataChart from '@/views/digital-coupon/components/ComCouponDataChart.vue'
import ComCouponRecentTransaction from '@/views/digital-coupon/components/ComCouponRecentTransaction.vue'
import ComPayCardInfo from '@/views/digital-coupon/components/ComPayCardInfo.vue'
import ComPaymentSuccess from '@/views/digital-coupon/components/ComPaymentSuccess.vue'

const { getHomeData, homeData } = useHome()
const dialog = useDialog()
const dialogRef = inject('dialogRef');
const t = window.t;

const payNow = () => {
    const dialogRef = dialog.open(ComPayCardInfo, {
        data: homeData,
        props: {
            header: t('Payment'),
            style: {
                width: '50vw',
            },
            breakpoints:{
                '960px': '75vw',
                '640px': '95vw'
            },
            modal: true
        },
        onClose: (options) => {

            if(options.data){
                viewPaymentSuccess(options.data)
            }
            getHomeData();

    }
    });
}

const viewPaymentSuccess = (data) => {
    dialog.open(ComPaymentSuccess, {
        data: {
            data:data
        },
        props: {
            header: t('Payment Successfully'),
            style: {
                width: '50vw',
            },
            breakpoints:{
                '960px': '75vw',
                '640px': '95vw'
            },
            modal: true
        },
        
    });
}



onMounted(async () => {
    await getHomeData();
})



</script>
<style scoped>

</style>