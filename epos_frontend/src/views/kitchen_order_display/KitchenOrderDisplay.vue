<template>

  <div class="w-full h-full bg-slate-100">
    <div class="grid-cols-1 md:grid-flow-col xl:grid-cols-5 grid p-2 gap-2">
      <ComFilterSaleType />
      <ComKodKpi />
    </div>
    <div class="bg-white border p-2">
      <div class="flex w-full gap-2">
        <div class="h-full shadow-md rounded-lg border p-2" :style="{ width: 100 - kod.setting.column_width_summary + '%'}">
          <MasonryWall :items="kod.pending_orders" :columnWidth="kod.setting.column_width" :gap="10">
            <template #default="{ item }">
              <ComKodBill :data="item" />
            </template>
          </MasonryWall>
          <div v-if="kod.pending_orders.length < 1" class="text-slate-500 m-auto flex w-full h-full flex-col">
            <div class=" m-auto">
  <v-icon  style="font-size: 50px;" >mdi-inbox</v-icon>
              <div class="text-center">{{ $t('No Data') }} </div>   
            </div>    
          </div>  

        </div>
        <div v-if="kod.setting.show_item_status" :style="{ width: kod.setting.column_width_summary + '%'}" >
          <ComSummaryItemStatus />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>

import { inject, ref, onMounted, onUnmounted, i18n } from '@/plugin';

import ComKodBill from "@/views/kitchen_order_display/components/ComKodBill.vue"
import ComSummaryItemStatus from "@/views/kitchen_order_display/components/ComSummaryItemStatus.vue"
import ComKodKpi from "@/views/kitchen_order_display/components/ComKodKpi.vue"
import ComFilterSaleType from "@/views/kitchen_order_display/components/ComFilterSaleType.vue"
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
  if (args.screen_name == kod.screen_name) {
    if (args.message) {
      toaster.warning(args.message);
    }
    kod.getKODData()
    if (localStorage.getItem("is_window") == "1") {
      window.chrome.webview.postMessage(JSON.stringify({ action: "play_sound" }));
    } 

      if ((localStorage.getItem('flutterWrapper') || 0) == 1) {
        flutterChannel.postMessage(JSON.stringify({ action: "play_sound" }));
      }
   
  }
})



onMounted(() => {
  kod.business_branch = setting.pos_setting.business_branch
  kod.screen_name = screen_name
  kod.getKODData()

  setInterval(function () {
    kod.getKODData()
  }, 1000 * 60)
})

onUnmounted(() => {
  socket.off('SubmitKOD');
})

</script>
<style scoped>
.masonry-container {
  display: flex;
  flex-flow: column wrap;
  align-content: space-between;
  height: 1300px;
  counter-reset: items;
}
</style>
