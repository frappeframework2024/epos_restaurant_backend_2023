<template>
  
    <div class="w-full h-full bg-slate-100">
      <v-btn :loading="kod.loading" @click="kod.getKODData(setting.pos_setting.business_branch, screen_name)">Refresh</v-btn>
        <ComKodKpi />
       
<div class="bg-white border px-2 pt-2">
        <div class="grid grid-cols-4 gap-2">
<div class="col-span-3">
    <div class="masonry-container gap-2 pe-5">
      
      <ComKodBill v-for="(d, index) in kod.pending_orders" :key="index" :data="d" />
    </div>
</div>
<div class="col-span-1">
<ComSummaryItemStatus />
</div>
</div>

    </div>

    

    </div>
   
    
 
</template>
<script setup>

import { inject,  ref, onMounted, onUnmounted, i18n } from '@/plugin';

import ComKodBill from "@/views/kitchen_order_display/components/ComKodBill.vue"
import ComSummaryItemStatus from "@/views/kitchen_order_display/components/ComSummaryItemStatus.vue"
import ComKodKpi from "@/views/kitchen_order_display/components/ComKodKpi.vue"
const socket = inject("$socket");
const gv = inject("$gv")
const kod = inject("$kod")
const currentTab = ref(1);
const setting = JSON.parse(localStorage.getItem("setting"))
const screen_name = JSON.parse(localStorage.getItem("device_setting")).default_kod
const audioRef = ref(null);
const { t: $t } = i18n.global;
socket.on("SubmitKOD", (args) => {
    if(args.screen_name == screen_name){
     
      kod.getKODData(setting.pos_setting.business_branch, screen_name)
       
    }
    
})



onMounted(()=>{
  kod.business_branch =  setting.pos_setting.business_branch
  kod.screen_name = screen_name
    kod.getKODData()

  setInterval(function(){
    kod.getKODData()
  }, 1000*60)
})

onUnmounted(() => {
    socket.off('SubmitKOD');
})

</script>
<style scoped>
.masonry-container{
  display: flex;
  flex-flow: column wrap;
  align-content: space-between;
  height: 80vh;
  counter-reset: items;
  overflow: auto
}
</style>
