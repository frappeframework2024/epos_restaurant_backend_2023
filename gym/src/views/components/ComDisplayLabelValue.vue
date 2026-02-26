<template>
    <div class="flex justify-content-between p-2 border-round-sm list-item">
        <div class="font-medium text-color-secondary">{{label}}</div>
        <div class="font-medium">{{value}}</div>
        
        
    </div>
</template>

<script setup>
const props = defineProps({
    label: String,
    value: {type: [String, Number]}
})
</script>

<style scoped>
    .list-item:hover{
        background-color: white;
        transition-duration: 200ms;
    }
</style>