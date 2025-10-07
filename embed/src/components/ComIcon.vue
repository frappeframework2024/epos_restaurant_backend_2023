<template>
    <img v-if="icon == 'couponNumberIcon'" :style="{'height' : height}" :class="class" :src="couponNumberIcon"/>
    <img v-if="icon == 'calendarIcon'" :style="{'height' : height}" :class="class" :src="calendarIcon"/>
    <img v-if="icon == 'couponUsageIcon'" :style="{'height' : height}" :class="class" :src="couponUsageIcon"/>
    <img v-if="icon == 'arrowDownRightIcon'" :style="{'height' : height}" :class="class" :src="arrowDownRightIcon"/>
    <img v-if="icon == 'homeIcon'" :style="{'height' : height}" :class="class" :src="homeIcon"/>
    <img v-if="icon == 'transactionIcon'" :style="{'height' : height}" :class="class" :src="transactionIcon"/>
    <img v-if="icon == 'myAccountIcon'" :style="{'height' : height}" :class="class" :src="myAccountIcon"/>
    <img v-if="icon == 'qrCodeIcon'" :style="{'height' : height}" :class="class" :src="qrCodeIcon"/>
    <img v-if="icon == 'emptyDataIcon'" :style="{'height' : height}" :class="class" :src="emptyDataIcon"/>
</template>
<script setup>
const theme =window.theme
const props = defineProps({
    icon: {
        type: String,
        default: ''
    },
    class: {
        type: String,
        default: ''
    },
    height: String
})
import couponNumberIcon from '@/assets/svg/coupon_number.svg'
import calendarIcon from '@/assets/svg/calendar.svg'
import couponUsageIcon from '@/assets/svg/usage_icon.svg'
import arrowDownRightIcon from '@/assets/svg/arrow_down_right.svg'
import homeIcon from '@/assets/svg/home_icon.svg'
import transactionIcon from '@/assets/svg/transaction_icon.svg'
import myAccountIcon from '@/assets/svg/my_account_icon.svg'
import qrCodeIcon from '@/assets/svg/qr_code.svg'
import emptyDataIcon from '@/assets/svg/empty_data.svg'

</script>