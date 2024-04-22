<template>
  <div class="bg-white rounded-lg flex item-center col-span-1 justify-center items-center">
    
    <v-chip-group
        v-model="kod.selected_sale_types"
        column
        multiple
      >
        <v-chip v-for="(s, index) in sale_types" :key="index"
        @click="onSelectSaleType"
        :value="s.name"
        color="blue-lighten-2"
          variant="outlined"
          filter
        >
      {{ s.name }}
      </v-chip>
        </v-chip-group>
  </div>
</template>
<script setup>
    import {  ref,inject ,i18n,onMounted } from '@/plugin';


const { t: $t } = i18n.global;
const sale_types = ref([])
 
 
  
const kod = inject("$kod");
const frappe = inject("$frappe");
const db = frappe.db();


function onSelectSaleType(){
    if(kod.loading){
      return
    }
    setTimeout(function(){
      kod.getKODData()
    },500)
}
onMounted(() => {
  db.getDocList("Sale Type",{
    orderBy: {
    field: 'name',
    order: 'asc',
  },
  }).then(r=>{
    sale_types.value = r
  })
})


</script>