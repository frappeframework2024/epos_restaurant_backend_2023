<template>
  <ComModal :mobileFullscreen="true" @onClose="onClose()" width="1200px" :hideOkButton="true">
    <template #title>
      {{ $t('Select Sale') }}
    </template>
    <template #content>
      <div>
        <div>
          <ComInput autofocus ref="searchTextField" keyboard class="m-2" v-model="search" :placeholder="$t('Search Sale')" />
        </div>
        <div class="overflow-auto px-2 pb-2">
          <ComPlaceholder :is-not-empty="getSaleList().length > 0">
            <v-row class="!-m-1">
              <v-col class="!p-0" cols="12" md="6" v-for="(s, index) in getSaleList()" :key="index">
                <ComSaleListItem :sale="s" @click="onSelect(s)" />
              </v-col>
            </v-row>
          </ComPlaceholder>
        </div>
      </div>
    </template>
  </ComModal>
</template>
<script setup>

import { ref, defineProps, defineEmits, inject,i18n ,onMounted} from '@/plugin' 
import ComInput from '@/components/form/ComInput.vue';
import { useDisplay } from 'vuetify'
import ComSaleListItem from './ComSaleListItem.vue';
import ComPlaceholder from '../../../components/layout/components/ComPlaceholder.vue';

import { createToaster } from "@meforma/vue-toaster"; 
const toaster = createToaster({ position: "top-right" });
const { mobile } = useDisplay();
const sale = inject("$sale");
const frappe = inject("$frappe");
const call = frappe.call()
const { t: $t } = i18n.global;

const searchTextField = ref(null)
const props = defineProps({
  params: {
    type: Object,
    required: true,
  }
})

const emit = defineEmits(["resolve", "reject"])

const open = ref(true);
const search = ref('')
let backup_sale;
onMounted(()=>{
  backup_sale = JSON.parse(JSON.stringify(sale.sale))
})

function getSaleList() {
  if (search.value) {
    return sale.tableSaleListResource?.data?.filter((r) => {
      return (String(r.name) + ' ' + String(r.customer_name) + String(r.phone_number)).toLocaleLowerCase().includes(search.value.toLocaleLowerCase());
    });
  } else {
    return sale.tableSaleListResource?.data || [];
  }
}


function onClose() {
  emit("resolve", false);
}

async function onSelect(c) { 

  if(await validateNewtowkSaleLock(c)){
    return;
  }
  emit("resolve", c);
}

async function validateNewtowkSaleLock(_sale){ 
 
 if(sale.setting.device_setting.use_sale_network_lock == 1 && _sale.name != backup_sale.name){      
     let param = {
         "table_id":_sale.table_id, 
         "sale":_sale.name,
         "table_name":_sale.tbl_number, 
         "pos_station":localStorage.getItem("device_name"), 
         "pos_profile":localStorage.getItem("pos_profile")
     }
    const resp = await call.post("epos_restaurant_2023.api.api.validate_sale_network_lock",{"param": param})     
    if(resp.message.status == 0){
         toaster.warning($t(resp.message.message))
         return true
    }else{

         //reset network lock on change current sale 
        let new_sale = {
              "table_id":_sale.table_id,  
              "table_name":_sale.tbl_number, 
              "sale":_sale.name,
              "pos_station":localStorage.getItem("device_name"), 
              "pos_profile":localStorage.getItem("pos_profile")
          }
        call.post("epos_restaurant_2023.api.api.reset_sale_network_lock_by_sale",{"old_sale": backup_sale.name, "new_sale":new_sale})   
        return false;
    }
 }
 return false
}


</script>