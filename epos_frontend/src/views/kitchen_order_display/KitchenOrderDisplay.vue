<template>
  
    <div class="w-full h-full bg-slate-100">

        <ComKodKpi />
       
<div class="bg-white border p-2">
        <div class="grid grid-cols-4 gap-2">
<div class="col-span-3">
    <div class="grid grid-cols-3 gap-2 pe-5">
      
     
    </div>
    <MasonryWall :items="kod.pending_orders" :columnWidth="300" :gap="10">
    <!-- Slot for rendering each item in the masonry wall -->
    <template #default="{ item }">
<ComKodBill :data="item" />
      
    </template>
  </MasonryWall>
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
import { createToaster } from '@meforma/vue-toaster';
const socket = inject("$socket");
const gv = inject("$gv")
const kod = inject("$kod")

const currentTab = ref(1);
const setting = JSON.parse(localStorage.getItem("setting"))
const screen_name = JSON.parse(localStorage.getItem("device_setting")).default_kod
const audioRef = ref(null);
const { t: $t } = i18n.global;
const toaster = createToaster({ position: "top-right" });

 
socket.on("SubmitKOD", (args) => {
    console.log(args);
    if(args.screen_name == screen_name){
      if(args.message){
        toaster.warning(args.message);
      }
      
      kod.getKODData()
       
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
  height: 1300px;
  counter-reset: items;
}
</style>
