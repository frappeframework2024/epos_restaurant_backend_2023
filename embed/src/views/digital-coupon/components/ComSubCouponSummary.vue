<template>
    <div class="col-6">
        <div class="flex gap-2">
            <div>
                <ComIcon icon="couponNumberIcon" height="26px"></ComIcon>
            </div>
            <div>
                <p>Coupon Number</p>
                <p class="list-value">10500</p>
            </div>
        </div>
    </div>
</template>
<script setup>
import ComIcon from '@/components/ComIcon.vue'
const props = defineProps({
    value: {
        type: any,
        default: ''
    },
    label: String,
    icon: String
    
})
</script>