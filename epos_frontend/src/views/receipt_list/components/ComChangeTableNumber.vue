<template>
    <ComModal @onClose="onClose()" :isPrint="false" @onOk="onSaveClick(168)" :loading="isSaving">
        <template #title>
            {{ $t('Change Table') }}: {{ params.data.sale.tbl_number }}
        </template>
        <template #content>
            <!-- {{props.params.data.sale}} -->
             
            <v-list>
                <v-list-item>
                    <v-list-item-title>
                        
                        <div class="flex justify-space-between">
                            <div class="text-subtitle-1 text-grey-darken-1">{{$t('Bill') }}: </div>
                            <div>{{ params.data.sale.custom_bill_number || params.data.sale.name }}</div>
                        </div>
                    </v-list-item-title>
                </v-list-item>
                <v-list-item>
                    <v-list-item-title>
                        
                        <div class="flex justify-space-between">
                            <div class="text-subtitle-1 text-grey-darken-1">{{$t('Total') }}: </div>
                            <div>
                                <CurrencyFormat :value="params.data.sale.grand_total" />
                            </div>
                        </div>
                    </v-list-item-title>
                </v-list-item>
                <v-list-item>
                    <v-list-item-title>
                        
                        <div class="flex justify-space-between">
                            <div class="text-subtitle-1 text-grey-darken-1">{{$t('Table') }}: </div>
                            <div >{{ params.data.sale.tbl_number }}</div>
                        </div>
                    </v-list-item-title>
                </v-list-item>
            </v-list>
            <v-autocomplete v-model="model" hint="Table Number" @update:search="customFilter" :items="tableList"
                label="Table Number" prepend-icon="mdi-table-chair" item-title="tbl_number" item-value="name">
                <template #item="{ item, props }">
                   
                        <v-list-item v-bind="props" @click="onItemSelected(item.raw)">
                            <v-list-item-content>
                            <v-list-item-title v-text="item.raw.tbl_number"></v-list-item-title>
                            <v-list-item-subtitle v-text="item.raw.tbl_group"></v-list-item-subtitle>
                        </v-list-item-content>
                        </v-list-item>
                        

                </template>
                
               <template #no-data>
                <div class="pa-2 text-center text-grey-darken-1">
                    Empty
                </div>
               </template>
            </v-autocomplete>
        </template>

    </ComModal>

</template>
<script setup>
import { inject, ref, onMounted,defineEmits } from 'vue'
import { createToaster } from "@meforma/vue-toaster";
const tableList = ref([])
const emit = defineEmits(["resolve"])
const props = defineProps({
    params: {
        type: Object,
        required: true,
    }
})
const model = ref({
    "name": props.params.data.sale.table_id,
    "tbl_number": props.params.data.sale.tbl_number,
})
const toaster = createToaster({ position: "top-right" });

const isLoading = ref(false)
const isSaving = ref(false)
const frappe = inject('$frappe');
const gv = inject('$gv');
const call = frappe.call();
const db = frappe.db();

onMounted(() => {

})
function onItemSelected($event){
    model.value = $event
}
function customFilter(itemTitle) {
    if (itemTitle == ""){
        return
    }
    isLoading.value = true
    call.get("epos_restaurant_2023.configuration.doctype.tables_number.tables_number.get_table_number_list", {
        txt: itemTitle
    }).then((res) => {
        tableList.value = res.message
        isLoading.value = false
    }).catch((res) => {
        isLoading.value = false
    })
    isLoading.value = false
}
function onSaveClick(){
    isSaving.value = true
    call.post("epos_restaurant_2023.selling.doctype.sale.sale.change_table_number",{
        data:{
            "tbl_name": model.value.name,
            "tbl_number": model.value.tbl_number,
            "sale": props.params.data.sale.name
}
    }).then((res)=>{
        toaster.success("Change table success");
        emit('resolve',true)
        isSaving.value = false
    }).catch((error)=>{
        toaster.error(error);
        isSaving.value = false
    })
    isSaving.value = false
}

function onClose(){
    emit('resolve',false)
}
</script>
