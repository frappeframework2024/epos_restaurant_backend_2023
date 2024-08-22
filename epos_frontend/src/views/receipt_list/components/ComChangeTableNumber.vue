<template>
    <ComModal @onClose="onClose(false)" :isPrint="false"
        :hide-ok-button="true" :hide-close-button="true">
        <template #title>
            {{ $t('Change Table') }} 
        </template>
        <template #content>
            {{ params.data.sale }}
            <v-autocomplete v-model="model" hint="Room Number" @update:search="customFilter" :items="states" label="Room Number"
               prepend-icon="mdi-city" item-title="tbl_number" item-value="name">

            </v-autocomplete>
        </template>
    </ComModal>

</template>
<script setup>
import { inject, ref, onMounted } from 'vue'
const tableList = ref([])
const model = ref({
            "name": "",
            "tbl_number": "U07",
        })
const isLoading = ref(false)
const frappe = inject('$frappe');
const gv = inject('$gv');
const call = frappe.call();
const db = frappe.db();
const props = defineProps({
  params: {
    type: Object,
    required: true,
  }
})
onMounted(() => {

})
function customFilter (itemTitle) {
    console.log(itemTitle)
    isLoading.value = true 
    call.get("epos_restaurant_2023.configuration.doctype.tables_number.tables_number.get_table_number_list",{
        txt:itemTitle
       }).then((res)=>{
        tableList.value=res.message
        isLoading.value = false
       }).catch((res)=>{
        isLoading.value = false
    })
    isLoading.value = false
}

</script>
<style>
/* .p-dialog-mask{
        z-index: 99999!important;
    } */
</style>