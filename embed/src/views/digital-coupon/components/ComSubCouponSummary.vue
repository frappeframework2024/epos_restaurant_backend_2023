<template>
    <div class="col-6">
        <div class="flex gap-2">
            <div>
                <ComIcon :icon="icon" height="26px"></ComIcon>
            </div>
            <div>
                <p class="text-xs">{{label || ''}}</p>
                <p class="list-value">{{value || 'None'}}</p>
            </div>
        </div>
    </div>
</template>
<script setup>
import ComIcon from '@/components/ComIcon.vue'
const props = defineProps({
    value: {
        type: Object,
        default: ''
    },
    label: String,
    icon: String
    
})

</script>