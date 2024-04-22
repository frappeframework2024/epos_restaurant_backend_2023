<template>
<div class="h-full shadow-md rounded-lg border">
    <div class=" w-full  h-full p-2">
        

<div class="text-sm font-medium text-center text-gray-500 border-b border-gray-200 dark:text-gray-400 dark:border-gray-700">
    <ul class="flex flex-wrap -mb-px">
    <li class="me-2">
      <a @click="activateTab('pending')" class="inline-block p-1  rounded-t-lg dark:text-blue-500 dark:border-blue-500" :class="{'active border-b-2 border-blue-600 text-blue-600 ': activeTab === 'pending' }">Pending
        <span class="inline-flex items-center justify-center w-4 h-4 text-xs font-semibold text-blue-800 bg-blue-200 rounded-full">
{{kod.pending_order_items.length}}
</span>
    </a>
    </li>
    <li class="me-2">
      <a @click="activateTab('processing')" class="inline-block p-1 rounded-t-lg dark:text-blue-500 dark:border-blue-500" :class="{'active border-b-2 border-blue-600 text-blue-600 ': activeTab === 'processing' }">Processing</a>
      <span class="inline-flex items-center justify-center w-4 h-4 text-xs font-semibold text-blue-800 bg-blue-200 rounded-full">
{{ kod.pending_order_items.filter(r=>r.kod_status=='Processing').length }}
</span>
    </li>
    <li class="me-2">
      <a @click="activateTab('done')" class="inline-block p-1 rounded-t-lg dark:text-blue-500 dark:border-blue-500" :class="{ 'active border-b-2 border-blue-600 text-blue-600 ': activeTab === 'done' }">Recent Done</a>
     
    </li>
  </ul>
</div>

        <div class="pt-2">
          <template v-if="activeTab === 'pending'">
            <div  v-for="(p, index) in kod.pending_order_items" :key="index">
                <ComKodMenuItem :isSummary="true"  :data="p"/>
                
            </div>  
            <div v-if="kod.pending_order_items.length <1" class="text-slate-500 m-auto flex w-full h-full mt-8 flex-col">
              <v-icon  style="font-size: 50px;" class=" m-auto">mdi-inbox</v-icon>
              <div class="text-center">No Data</div>             
            </div>  
          </template>  
          <template v-if="activeTab === 'processing'">
            <div  v-for="(p, index) in kod.pending_order_items.filter(r=>r.kod_status=='Processing')" :key="index">
                <ComKodMenuItem :isSummary="true" :data="p"/>
            </div>
            <div v-if="kod.pending_order_items.filter(r=>r.kod_status=='Processing').length <1" class="text-slate-500 m-auto flex w-full h-full mt-8 flex-col">
              <v-icon  style="font-size: 50px;" class=" m-auto">mdi-inbox</v-icon>
              <div class="text-center">No Data</div>             
            </div>  
          </template>
          <template v-if="activeTab === 'done'">
             <div  v-for="(p, index) in kod.recent_done_order_items" :key="index">
                <ComKodMenuItem :isSummary="true" :data="p"/>
            </div>
            <div v-if="kod.recent_done_order_items.length <1" class="text-slate-500 m-auto flex w-full h-full mt-8 flex-col">
              <v-icon  style="font-size: 50px;" class=" m-auto">mdi-inbox</v-icon>
              <div class="text-center">No Data</div>             
            </div> 
          </template>
           
        </div>
</div>
</div>
</template>
<script setup>
import { ref,inject } from 'vue';
import ComKodMenuItem from "@/views/kitchen_order_display/components/ComKodMenuItem.vue"
const activeTab = ref('pending');

const activateTab = (tab) => {
  activeTab.value = tab;
};
const currentTab = ref(1);
const kod = inject("$kod")

</script>