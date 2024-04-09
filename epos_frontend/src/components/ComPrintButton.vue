<template>
    <v-btn v-if="loading" class="ma-2"  icon="mdi-printer" :loading="loading" ></v-btn>
    <template v-else>
        <v-btn v-if="printFormatResource.length==1"  class="grow" variant="flat" color="info"  :loading="loading" @click="onPrintReport(printFormatResource[0])" >
        {{ title }}
        </v-btn>
        <v-menu v-else>
        <template v-slot:activator="{ props }"> 
            <v-btn v-if="title==''" icon @click="$emit('onClose')" :loading="loading" v-bind="props">
                <v-icon>mdi-printer</v-icon>
            </v-btn>
            <v-btn v-else  @click="$emit('onClose')" :loading="loading" v-bind="props">
                {{ title }}
            </v-btn>

            
        </template>
        <v-list v-if="printFormatResource">
            <v-list-item v-for="(r, index) in printFormatResource" :key="index"  @click="onPrintReport(r)">
                <v-list-item-title>{{ r.name }}</v-list-item-title>
            </v-list-item>

        </v-list>
    </v-menu>
    </template>
       
</template>
<script setup>
    import {defineProps,defineEmits,onMounted,ref,inject,computed} from "@/plugin"
    const gv = inject("$gv")
    const frappe = inject("$frappe")
    const call = frappe.call();
    const loading = ref(false)


    const props = defineProps({
        doctype:String,
        title:{
            type:String,
            default:""
        }
    });
    const printFormatResource = ref([])
    const emit = defineEmits(["onPrint"]);
    onMounted(() => {
	    loading.value=true
        call.get("epos_restaurant_2023.api.api.get_pos_print_format",{
        business_branch:gv.business_branch,
        doctype:props.doctype
    }).then((result) =>{
        
        printFormatResource.value = result.message 
        loading.value=false
    })
    });

   

    function onPrintReport(r){
         emit('onPrint', r);
    }

</script>