<template>
    <PageLayout :title="$t('Voucher Top-Up')" icon="mdi-wallet-plus" full>
        <template #action>
            <v-btn  prepend-icon="mdi-wallet-plus" type="button" @click="onAddVoucherTopUp">
              {{ $t("Add Top-Up") }}
            </v-btn>
        </template>
        <ComTable :headers="headers" doctype="Voucher" @callback="onCallback" />
  </PageLayout>
</template>
<script setup>
import { ref, AddVoucherTopUpDialog,VoucherTopUpDetailDialog,i18n,inject,customerDetailDialog } from '@/plugin'
import PageLayout from '@/components/layout/PageLayout.vue';
import ComTable from '@/components/table/ComTable.vue';


const { t: $t } = i18n.global; 
const gv = inject("$gv")
async function onAddVoucherTopUp() {
    
    gv.authorize("add_voucher_top_up_required_password","add_voucher_top_up").then(async (v)=>{
        if(v){
            const result = await AddVoucherTopUpDialog ({title: $t("Add New"), value:  '',authUser:v});   
            if (result == true){
                onCallback()
            }
        }
    })
    
}


async function onCallback(data) {
    if(data){
        if (data.fieldname == 'name'){
        const result = await VoucherTopUpDetailDialog({
            name: data.data.name
        });
    }else if (data.fieldname == 'customer'){
       await customerDetailDialog({
            name: data.data.customer
        });
    }
    }
    
        
        
        
    
}

const headers = ref([
    { title: $t('Voucher'), align: 'start', key: 'name', callback: true },
    { title: $t('Customer'), align: 'start', key: 'customer' ,callback: true},
    { title: $t('Customer Name'), align: 'start', key: 'customer_name' },
    { title: $t('Phone'), align: 'start', key: 'phone'},
    { title: $t('Amount'),fieldtype : 'Currency', align: 'end', key: 'actual_amount'},
    { title: $t('Credit Amount'),fieldtype : 'Currency' ,align: 'end', key: 'credit_amount'}
])


</script>