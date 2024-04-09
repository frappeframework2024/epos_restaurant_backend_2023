<template>
    <PageLayout :title="$t('Table Layout')" full icon="mdi-cart-outline">
 
        <template #centerCotent>
            
            <ComTableGroupTabHeader :tableSaleColor="table_status_color"/>
        </template>
        <template #action>
            <ComTableLayoutActionButton @onShowHide="onTableStatusHidden"/>
        {{ isShowTableStatus() }} 
        </template>
        <template v-if="tableLayout.table_groups">
            <v-window v-model="tableLayout.tab">
                <ComArrangeTable  v-if="tableLayout.canArrangeTable"/>
                <ComRenderTableNumber v-else :tableStatusColor="table_status_color"/>
            </v-window>
        </template> 
    </PageLayout>
    <ComSaleStatusInformation v-if="table_status_color && getKeyIndex"/>  
</template>
<script setup>
import PageLayout from '../../components/layout/PageLayout.vue'; 
import { inject, createResource, useRouter,createToaster,onMounted , onUnmounted,ref,i18n} from "@/plugin";
import ComTableGroupTabHeader from './components/table_layouts/ComTableGroupTabHeader.vue'; 
import ComTableLayoutActionButton from './components/table_layouts/ComTableLayoutActionButton.vue';
import ComArrangeTable from './components/table_layouts/ComArrangeTable.vue';
import ComRenderTableNumber from './components/table_layouts/ComRenderTableNumber.vue';
import ComSaleStatusInformation from '@/views/sale/components/ComSaleStatusInformation.vue';
import { computed } from 'vue';

const { t: $t } = i18n.global; 

const toaster = createToaster({position:"top-right"});
const tableLayout = inject("$tableLayout");
const socket = inject("$socket");

const getKeyIndex = ref(false)

const table_status_color = ref(false);
const router = useRouter(); 
if(localStorage.getItem("__tblLayoutIndex")==null){
    localStorage.setItem("__tblLayoutIndex",tableLayout.table_groups[0].key) 
}

const tabIndex = computed(()=>{
    tableLayout.tab = localStorage.getItem("__tblLayoutIndex");
})

socket.on("RefreshTable", () => {
  tableLayout.getSaleList(); 
})


//on init
onMounted(async ()=>{ 
    tableLayout.tab = localStorage.getItem("__tblLayoutIndex")

    let tableGroupLength = JSON.parse(localStorage.getItem("table_groups"))
    if (tableGroupLength.length == 1) {
        getKeyIndex.value = true
    }else {
        getKeyIndex.value = false
    }
     
    


    localStorage.removeItem('make_order_auth');
    const cashierShiftResource = createResource({
        url: "epos_restaurant_2023.api.api.get_current_cashier_shift",
        params: {
            pos_profile: localStorage.getItem("pos_profile")
        }
    });

    await cashierShiftResource.fetch().then(async (v) => {
        if (v==null) {
            toaster.warning($t('msg.Please start shift first'))
            router.push({ name: "Home" });
        }
    });
})

function onTableStatusHidden (value) { 
    localStorage.setItem('table_status_color', value) 
    table_status_color.value = value;
}

function isShowTableStatus(){
    try{
        const s = localStorage.getItem("table_status_color");
        if(s == null){
            table_status_color.value = false;
        }
        table_status_color.value = (s=="true"?true:false);
    }catch(e)
    {
        table_status_color.value = false;
    }
   
}


tableLayout.getSaleList()
 

showHiddentTable();
 

function showHiddentTable() {

    const container = document.getElementsByClassName("v-window__container");

    tableLayout.table_groups.forEach(function (g) {
        g.tables.forEach(function (t) {

            if (t.x < 0) {
                t.x = 0;
            }

            if (t.y < 0) {
                t.y = 0
            }

        })
    })
}



onUnmounted(()=>{
    socket.off('RefreshTable');      
});
 
if(localStorage.getItem('redirect_sale_type')){
    localStorage.removeItem('redirect_sale_type')
}

</script> 