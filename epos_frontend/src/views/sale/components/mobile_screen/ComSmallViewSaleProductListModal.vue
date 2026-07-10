<template>
    <div>
        <ComLoadingDialog v-if="sale.loading"/>
        <ComModal :saleOrderListCustom="!isDefaultTeplate" :fullscreen="true" :hideCloseButton="true" :hideOkButton="true" :fill="true" :isShowBarMoreButton="false" @onClose="onClose()">
        <template #title>
            {{ $t('Bill') }}# {{ params.title }} 
        </template>
        <template #bar_custom>
            <v-btn v-if="params.data?.from_table" icon @click="onAddNewOrder()" v-bind="props">
                <v-icon>mdi-plus</v-icon>
            </v-btn>
            <ComPrintBillButton doctype="Sale" :title="$t('Print Bill')" :isMobile="true" :isToolbar="true" />
        </template>
        <template #content>
            <template v-if="!gv.device_setting.is_order_station"> 
                <div class="m-1">
                    <ComSelectCustomer/>
                    <div class="w-full saletable justify-between px-3 flex flex-wrap p-1 rounded-md mt-1" v-if="sale.sale?.tbl_number"> 
                        <div class="font-bold" > {{$t('Table #')}} :</div>
                        <div> {{ sale.sale.tbl_number }} </div>
                    </div>
                </div>
            </template>
            <ComGroupSaleProductList/>
        </template>
        <template #action> 
            <ComSmallSaleSummary @onClose="onGoHome()" @onSubmitAndNew="onSubmitAndNew()"/> 
        </template>
    </ComModal>
    </div>
</template>
<script setup>
import { defineProps, defineEmits, inject,useRouter,onUnmounted,onMounted ,computed} from '@/plugin'
import ComGroupSaleProductList from '../ComGroupSaleProductList.vue';
import ComPrintBillButton from '../ComPrintBillButton.vue';
import ComSelectCustomer from '../ComSelectCustomer.vue';
import ComSmallSaleSummary from './ComSmallSaleSummary.vue'; 
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';

const router = useRouter();

const props = defineProps({
    params: Object
})
const socket = inject('$socket');
const sale = inject('$sale');
const gv = inject('$gv');
const emit = defineEmits(['resolve']);
const tableLayout = inject("$tableLayout");

onMounted(()=>{
    const backup_sale = JSON.parse(JSON.stringify(sale.sale))
    sale.saleNetworkLock(backup_sale)
});

const isDefaultTeplate = computed(()=>{
    return (gv.device_setting?.main_sale_screen??"Default") == "Default";
})

function onGoHome(){
    if(onRedirectSaleType()){
        if (gv.setting.table_groups.length > 0) {
            sale.sale = {};
            router.push({ name: 'TableLayout' }).then(()=>{
                tableLayout.getSaleList();
                emit('resolve', true)
            });
        }
        else {
            sale.newSale()
            let template = (gv.device_setting?.main_sale_screen??"Default");
            if(template == "Default"){
                router.push({  name: "AddSale"}).then(()=>{
                    emit('resolve', true);
                });
            }else {
                const result = template.toLowerCase().replace(/\s+/g, '-');
                let _template = result;
                router.push({ 
                    name: "SaleOrder",
                    query: { menu: _template }
                }).then(()=>{
                    emit('resolve', true);
                });
            }            
        }
        socket.emit("ShowOrderInCustomerDisplay", {},"", sale.customer_display_key);
    }
}

function onRedirectSaleType(){
    const redirect_sale_type = localStorage.getItem("redirect_sale_type") || null
    if(redirect_sale_type){
        router.push({name: 'AddSaleNoTable', params: {sale_type: redirect_sale_type}}).then(()=>{
            emit('resolve', false)
        });
        return false;
    }
    return true;
}

function onSubmitAndNew(){
    onRedirectSaleType()
}

function onClose() {
    emit('resolve', false)
}

function onAddNewOrder(){
    if (!sale.isBillRequested()) {
        sale.no_loading = true;
        let template = (gv.device_setting?.main_sale_screen??"Default") ;
        if(template == "Default"){
            router.push({ 
                name: "AddSale",
                params: {
                    name: sale.sale.name
                }
            }).then(()=>{
                emit('resolve', true)
            });

        }else {
           const result = template.toLowerCase().replace(/\s+/g, '-');
                let _template = result;
            router.push({ 
                name: "SaleOrder",
                params: {
                    name: sale.sale.name
                },
                query: { menu: _template }
            }).then(()=>{
                emit('resolve', true)
            });
        }  
    }
}

const onEventListener = async function (e) {
    if (e.isTrusted && typeof (e.data) == 'string') {
        if(e.data == "close_modal"){
            emit('resolve', true);
        }
        
    }
};

window.addEventListener('message', onEventListener, false);

onUnmounted(() => {
    window.removeEventListener('message', onEventListener, false);
}) 

</script>