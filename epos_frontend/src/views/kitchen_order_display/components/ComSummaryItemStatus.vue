<template>
<div>
    <div class="shadow w-full rouend-lg h-full p-2">
        <div class="font-bold">
            Pending Item
            <div v-for="(p, index) in kod.pending_order_items" :key="index">
                <ComKodMenuItem :data="p"/>
            </div>
            <h1>Processing</h1>
            <div style="background: blue;" v-for="(p, index) in kod.pending_order_items.filter(r=>r.kod_status=='Processing')" :key="index">
                <ComKodMenuItem :data="p"/>
            </div>
            <h1>Recent Done</h1>
            <div style="background:red;" v-for="(p, index) in kod.recent_done_order_items" :key="index">
                <ComKodMenuItem :data="p"/>
            </div>
        </div>
</div>
</div>
</template>
<script setup>
import { ref,inject } from 'vue';
import ComKodMenuItem from "@/views/kitchen_order_display/components/ComKodMenuItem.vue"

const currentTab = ref(1);
const kod = inject("$kod")

</script>