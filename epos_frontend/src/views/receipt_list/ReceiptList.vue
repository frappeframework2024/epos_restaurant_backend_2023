<template>
    <PageLayout :title="$t('Receipt List')" icon="mdi-file-chart" full>
      <ComReceiptListCard :headers="headers" doctype="Sale" extra-fields="customer_name,sale_status_color" @callback="onCallback" v-if="mobile"/>
      <ComTable :headers="headers" doctype="Sale" :default-filter="defaltFilter" extra-fields="customer_name,sale_status_color" @onFetch="onFetch" business-branch-field="business_branch" pos-profile-field="pos_profile" @callback="onCallback"  v-else>
          <template v-slot:kpi>
            <v-row no-gutters>
          <v-col cols="6" sm="3">
            <v-card class="pa-2 ma-2" elevation="2" color="primary">
              <div class="text-h6 text-center"><CurrencyFormat :value="summary.sub_total" /></div>
              <div class="text-body-1 text-center mt-2  text-sm">{{ $t('Sub Total') }}</div>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card class="pa-2 ma-2" elevation="2" color="warning">
              <div class="text-h6 text-center">
                <CurrencyFormat :value="summary.total_discount" />
              </div>
              <div class="text-body-1 text-center mt-2 text-sm">{{ $t('Total Discount') }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="3">
            <v-card class="pa-2 ma-2" elevation="2" color="success">
              <div class="text-h6 text-center">
                <CurrencyFormat :value="summary.grand_total" />
              </div>
              <div class="text-body-1 text-center mt-2 text-sm">{{ $t('Grand Total') }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="3">
            <v-card class="pa-2 ma-2" elevation="2" color="teal-darken-3">
              <div class="text-h6 text-center">
                <CurrencyFormat :value="summary.total_paid" />
              </div>
              <div class="text-body-1 text-center mt-2 text-sm">{{ $t('Total Paid') }}</div>
            </v-card>
          </v-col>
          
        </v-row>
          </template>
      </ComTable>
    </PageLayout>
</template>
<script setup>
import { ref, useRouter, saleDetailDialog, customerDetailDialog,i18n,inject} from '@/plugin'
import PageLayout from '@/components/layout/PageLayout.vue';
import ComTable from '@/components/table/ComTable.vue';
import {useDisplay} from 'vuetify' 
import ComReceiptListCard from './components/ComReceiptListCard.vue';
let summary = ref({})
const frappe = inject('$frappe');
const call = frappe.call();
const { t: $t } = i18n.global; 
const {mobile} = useDisplay()
async function onCallback(data) {
 
 if(data.fieldname=="name"){
  const name =  data.data.name;
  const result = await  saleDetailDialog({
      name:name
    });
    if (result=="delete_order"){
      window.parent.postMessage('refresh', '*');
    }
   
  }
  else if(data.fieldname == "customer"){
     customerDetailDialog({
        name: data.data.customer
    })
  }
}

function onFetch(_filters){
  let filters =[]
  Object.keys(_filters).forEach(key => {
    filters.push({[key]:_filters[key]})
  });
  console.log(JSON.stringify(filters) )
  call.get("epos_restaurant_2023.api.api.receipt_list_summary",{
    filter:JSON.stringify(filters)
  }
   
  ).then((res)=>{
    if (res.message.length > 0){
      summary.value = res.message[0]
    }
    
  })
}

const headers = ref([
  { title: $t('No'), align: 'start',key: 'name',callback: true},
  { title: $t('Invoice No'), align: 'start',key: 'custom_bill_number',callback: true},
  { title: $t('Customer Name'), align: 'start', key: 'customer', template: '{customer}-{customer_name}', callback: true },
  { title: $t('Table'), align: 'start', key: 'tbl_number' },
  { title: $t('Date'), align: 'center', key: 'posting_date', fieldtype: "Date" },
  { title: $t('Qty'), align: 'center', key: 'total_quantity', },
  { title: $t('Grand Total'), align: 'end', key: 'grand_total', fieldtype: "Currency" },
  { title: $t('Total Discount'), align: 'end', key: 'total_discount', fieldtype: "Currency" },
  { title: $t('Total Paid'), align: 'end', key: 'total_paid_with_fee', fieldtype: "Currency" },
  { title: $t('Balance'), align: 'end', key: 'balance', fieldtype: "Currency" },
  { title: $t('Status'), align: 'center', key: 'sale_status', fieldtype: "Status", color_field:"sale_status_color" },
])

 
</script>