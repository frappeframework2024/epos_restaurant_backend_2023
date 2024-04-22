<template>
  
    <div class="w-full h-full bg-slate-100">

        <ComKodKpi />
       
<div class="bg-white border p-2">
        <div :class="kod.setting.show_item_status ? 'grid-cols-4' : 'grid-cols' " class="grid gap-2">
<div class="col-span-3">
    <MasonryWall :items="kod.pending_orders" :columnWidth="kod.setting.column_width" :gap="10">
    <template #default="{ item }">
<ComKodBill :data="item" />
    </template>
  </MasonryWall>
</div>
<div v-if="kod.setting.show_item_status" class="col-span-1">
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
const flutterChannel = localStorage.getItem('flutterChannel');

 
socket.on("SubmitKOD", (args) => { 
    if(args.screen_name == kod.screen_name){
      if(args.message){
        toaster.warning(args.message);
      } 
      kod.getKODData()  
      if (localStorage.getItem("is_window") == "1") {       
          window.chrome.webview.postMessage(JSON.stringify({action:"play_sound"}));
      }else{
        if ((flutterChannel || 0) == 1) {
            flutterChannel.postMessage(JSON.stringify({action:"play_sound"}));
        }
      } 
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
