<template>
    <v-btn :loading="tableLayout.saleLoading" icon @click="onRefreshSale">
        <v-icon>mdi-cached</v-icon>
    </v-btn>
    <v-btn @click="UnlockTable" v-if="gv.setting.device_setting.use_sale_network_lock == 1">
        <svg  v-if="mobile" class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14v3m4-6V7a3 3 0 1 1 6 0v4M5 11h10a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1Z"/>
        </svg>
        <div v-else>
            Unlock Table
        </div>
    </v-btn>
    <template v-if="!mobile">
        <v-btn style="font-family: Khmer OS Siemreap;" @click="onViewPendingOrder">
            {{ $t('Pending Order') }}
        </v-btn> 
    </template> 
    {{ isShowTableStatus() }}
    <v-btn style="font-family: Khmer OS Siemreap;" :loading="tableLayout.saveTablePositionResource.loading" v-if="tableLayout.canArrangeTable"
        @click="onSaveTablePosition">
        {{ $t('Save Table Position') }}
    </v-btn>
    <v-menu>
        <template v-slot:activator="{ props }">
            <v-btn v-bind="props">
                <v-icon>mdi-dots-vertical</v-icon>  
            </v-btn>
        </template>
        <v-card>
            <v-list v-if="gv.setting?.pos_setting?.sale_types && gv.setting?.pos_setting?.sale_types.filter(r=>r.is_order_use_table == false).length > 0">
                <v-list-subheader>
                    <div style="font-family: Khmer OS Siemreap;">{{ $t('Change Sale Type') }}</div>
                </v-list-subheader>
                <template  v-for="(st, index) in gv.setting?.pos_setting.sale_types.filter(r=>r.is_order_use_table == false)" :key="index">
                    <v-list-item @click="onSaleType(st.name)">
                        <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ st.sale_type_name }}</div></v-list-item-title>
                    </v-list-item>
                </template>
            </v-list>
            <v-list>
                <template  v-if="device_setting?.allow_switch_pos_profile==1"> 
                    <v-list-subheader><div style="font-family: Khmer OS Siemreap;">{{ $t('POS Config') }}</div></v-list-subheader>
                    <v-list-item @click="onSwitchPOSProfile">
                        <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ $t('Switch POS Profile') }}</div></v-list-item-title>
                    </v-list-item>
                </template>

                <template  v-if="!mobile">
                    <v-list-subheader><div style="font-family: Khmer OS Siemreap;">{{ $t('Table Position') }}</div></v-list-subheader>
                    <v-list-item @click="onEnableArrageTable">
                        <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ $t('Arrange Table') }}</div></v-list-item-title>
                    </v-list-item>
                </template>

                <template v-if="mobile">
                    <v-list-item @click="onViewPendingOrder">
                        <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{$t('Pending Order')}}</div></v-list-item-title>
                    </v-list-item>
                   
                </template>
                
                <v-list-item @click="onShowHideSaleStatus">
                        <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ !status ? $t('Show Status'):$t("Hide Status") }}</div></v-list-item-title>
                </v-list-item>
                    
            </v-list>
        </v-card>
    </v-menu>
</template>
<script setup>
import {inject, pendingSaleListDialog,createToaster, useRouter,ref,SwitchPosProfileModal ,i18n} from '@/plugin';
import { useDisplay } from 'vuetify';
const { t: $t } = i18n.global;

const gv = inject('$gv');
const frappe = inject("$frappe");
const tableLayout = inject("$tableLayout");

const call = frappe.call();

const emit = defineEmits(['onShowHide']);
const router = useRouter();
const { mobile } = useDisplay();
const toaster = createToaster({position: 'top-right'});
const pos_profile = localStorage.getItem('pos_profile');
const device_setting = JSON.parse(localStorage.getItem("device_setting"));


let status = ref(false);
function onRefreshSale() { 
    tableLayout.getSaleList()
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function UnlockTable(){
  let param = {
        "sale":undefined,
        "table_id":undefined, 
        "table_name":undefined, 
        "pos_station":localStorage.getItem("device_name"), 
        "pos_profile": gv.setting.pos_profile
    }
    toaster.success($t("Unlocking table"))
    await call.post("epos_restaurant_2023.api.api.reset_all_sale_network_lock",{param:param})
    await delay(2000)
    toaster.success($t("All table unlocked"))
}

async function onSwitchPOSProfile(){ 
    gv.authorize("switch_pos_profile_required_password","allow_switch_pos_profile").then(async (u)=>{
        if(u){  
         await SwitchPosProfileModal({data:{
            "username":u.username,
            "password":u.__sys,
           }})                 
        }
    })   
}

function onEnableArrageTable(){
    tableLayout.canArrangeTable = true;
    tableLayout.tab = localStorage.getItem("__tblLayoutIndex");
   
}

async function onViewPendingOrder() {
   const workingDay = await getWorkingDay(); 
   const cashierShift = await getCashierShift();

    if(workingDay.name && cashierShift.name){
        const result = await pendingSaleListDialog({data:{working_day:workingDay.name, cashier_shift: cashierShift.name}});    
    }
    else{
        toaster.error($t("msg.System can not get current working day or cashier shift"))
    }
} 

async function onShowHideSaleStatus() { 
    status.value = !status.value;
    localStorage.setItem('table_status_color', status.value)
    emit('onShowHide',status.value)
}


function isShowTableStatus(){
    try{
        const s = localStorage.getItem("table_status_color");
        if(s == null){
            status.value = false;
        }
        status.value = (s=="true"?true:false);
    }catch(e)
    {
        status.value = false;
    }
   
}


function onSaveTablePosition() {
    tableLayout.saveTablePositionResource.params = {
        "device_name": localStorage.getItem("device_name"),
        "pos_profile": pos_profile,
        "table_group": JSON.parse(JSON.stringify(tableLayout.table_groups))
    };
    tableLayout.saveTablePositionResource.submit();
    tableLayout.canArrangeTable = false;

}


async function  getWorkingDay(){
  return await  call.get("epos_restaurant_2023.api.api.get_current_working_day",
    {
      business_branch: gv.setting?.business_branch
    }).then((resp)=>{return resp.message});
}

async function  getCashierShift(){
  return await  call.get("epos_restaurant_2023.api.api.get_current_cashier_shift",
    {
        pos_profile: pos_profile
    }).then((resp)=>{return resp.message});
} 
 
function onSaleType(name){
    router.push({name:'AddSaleNoTable',params:{sale_type: name}})
}
</script>