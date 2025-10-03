<template>
    <img v-if="icon == 'couponNumberIcon'" :style="{'height' : height}" :class="class" :src="couponNumberIcon"/>
    <img v-if="icon == 'calendarIcon'" :style="{'height' : height}" :class="class" :src="calendarIcon"/>
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

</script>