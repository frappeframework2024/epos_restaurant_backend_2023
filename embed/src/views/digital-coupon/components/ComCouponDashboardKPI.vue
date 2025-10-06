<template>   
        <div>
            <p>{{t('Available Balance')}}</p>
            <h1 class="font-bold text-5xl"><currencyFormat :value="balance"/></h1>
        </div>
        <div>
            <div class="flex justify-content-between mb-1">
                <p class="font-bold">{{ t("Used Amount") }}: <span class="text-red-600"><currencyFormat :value="homeData?.coupon_info?.use_amount || 0" /></span></p>
                <p class="font-bold">{{ t("Coupon Amount") }}: <currencyFormat :value="homeData?.coupon_info?.coupon_amount || 0" /></p>
            </div>
            <ProgressBar :value="usedCouponPercent"></ProgressBar>
        </div>
        <div class="info-list">
            <div class="grid">
                <ComSubCouponSummary :value="homeData?.coupon_info?.coupon_number" :label="t('Coupon Number')" icon="couponNumberIcon"/>
                <ComSubCouponSummary :value="dayjs(homeData?.coupon_info?.issue_date).format('DD-MM-YYYY')" :label="t('Issue Date')" icon="calendarIcon"/>
                <ComSubCouponSummary :value="dayjs(homeData?.coupon_info?.expired_date).format('DD-MM-YYYY')" :label="t('Expired Date')" icon="calendarIcon"/>
                <ComSubCouponSummary :value="`${usedCouponPercent} %`" :label="t('Usage')" icon="couponUsageIcon"/>
            </div>
        </div>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
import ProgressBar from 'primevue/progressbar';
import { useHome } from '@/hooks/ecoupon/useHome.js';
import ComSubCouponSummary from '@/views/digital-coupon/components/ComSubCouponSummary.vue'
import { computed, ref } from 'vue';
import dayjs from "dayjs";

const { t,locale } = useI18n()
const { getHomeData, homeData } = useHome()

const usedCouponPercent = computed(() => {
    const use_amount = homeData?.value?.coupon_info?.use_amount ?? 0
    const coupon_amount = homeData?.value?.coupon_info?.coupon_amount ?? 0

  if (coupon_amount <= 0) return 0
  return parseInt (Math.abs((use_amount / coupon_amount) * 100));
})
 
const balance = computed(()=>{
    return (homeData?.value?.coupon_info?.coupon_amount || 0)  - (homeData?.value?.coupon_info?.use_amount  || 0)
})
 
</script>