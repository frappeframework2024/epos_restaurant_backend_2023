<template>
    <div>
        <v-autocomplete
        v-model="model"
        :hint="!isEditing ? 'Click the icon to edit' : 'Click the icon to save'"
        :items="states"
        :label="`State — ${isEditing ? 'Editable' : 'Readonly'}`"
        :readonly="!isEditing"
        prepend-icon="mdi-city"
        persistent-hint
      >
       
      </v-autocomplete>
    </div>
</template>
<script setup>
import {inject,ref,onMounted} from 'vue'
const dialogRef = inject("dialogRef")
const sale = dialogRef.value.data.sale
const tableList = ref([])
const model = ref({})
const frappe = inject('$frappe');
const gv = inject('$gv');
const call = frappe.call();
const db = frappe.db();
onMounted(()=>{
    call.get('epos_restaurant_2023.configuration.doctype.tables_number.tables_number.get_table_number_list', {txt: keyword.value }).then((result) => {
        tableList.value = result.values
    })
    .catch((error) => {
    }); 
})

    
</script>
<style>
    .p-dialog-mask{
        z-index: 99999!important;
    }
</style>