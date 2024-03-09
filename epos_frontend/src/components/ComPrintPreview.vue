<template>
    <ComModal @onClose="onClose(false)" :fullscreen="true" :isPrint="true" @onPrint="onPrint()"  :hide-ok-button="true" :hide-close-button="true">
        <template #title>
            {{ params.title }}
        </template>
        <template #bar_more_button>
          
        </template>
        <template #content>
            <v-card>

                <template #title>
                    <div class="px-1 py-2 -m-1"> 
                        <v-row>
                            <v-col>
                                <div style="overflow-x:auto;"> 
                                        <v-btn 
                                            v-for="(r, index) in gv.setting.reports.filter(r=>r.doc_type==params.doctype && r.show_in_pos == 1)" :key="index"  
                                            :color="activeReport.name == r.name ? 'info' : 'default'"
                                            class="m-1" @click="onViewReport(r)">{{ r.title }}</v-btn>
                                    
                                </div>
                            </v-col>
                            <v-col cols="12" md="6" lg="4"> 
                                <div class="flex items-center"  > 
                                    <v-select 
                                    prepend-inner-icon="mdi-content-paste"
                                    density="compact"
                                    v-model="selectedLetterhead"
                                    :items=gv.setting.letter_heads
                                    item-title="name"
                                    item-value="name"
                                    hide-no-data
                                    hide-details
                                    variant="solo"
                                    class="mx-1"
                                    ></v-select>
                                    <v-select 
                                    prepend-inner-icon="mdi-google-translate"
                                    density="compact"
                                    v-model="selectedLang"
                                    :items="gv.setting.lang" 
                                    item-title="language_name"
                                    item-value="language_code"
                                    hide-no-data
                                    hide-details
                                    variant="solo"
                                    class="mx-1"
                                
                                    ></v-select>
                                    <v-icon class="mx-1" icon="mdi-refresh" size="small" @click="onRefresh()"/>
                                </div>
                            </v-col>
                        </v-row>
                        <div class="flex pt-2 px-2 items-center border-t border-gray-300 mt-2" v-if="activeReport.title == 'Inventory Transaction'">
                            <div class="flex-grow">
                                <div style="max-width: 250px;">
                                    <ComAutoComplete v-model="filter.product_category" doctype="Product Category" variant="solo" @onSelected="onFilter"/> 
                                </div>
                            </div>
                            <div class="flex-none">
                                <v-btn prepend-icon="mdi-filter" color="primary" @click="onFilter">{{$t('Filter')}}</v-btn>
                            </div>
                        </div>
                    </div>
                </template>
                <v-card-text style="height: calc(100vh - 150px);">
                    <iframe id="report-view" height="100%" width="100%" :src="printPreviewUrl"></iframe>
                </v-card-text>
            </v-card>
        </template>
    </ComModal>
</template>
  
<script setup>

import { inject, ref,computed,saleDetailDialog, onUnmounted,reactive,i18n } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
const gv = inject("$gv")

const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + gv.setting.pos_setting.backend_port;

const toaster = createToaster({ position: "top-right" });
const { t: $t } = i18n.global; 

const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})
const selectedLetterhead = ref(getDefaultLetterHead());
const selectedLang = ref(gv.setting.lang[0].language_code);
const activeReport = ref(gv.setting.reports.filter(r=>r.doc_type==props.params.doctype)[0]) ;
 
let filter = reactive({
    product_category: 'All Product Categories',
    product_category_filter: ''
})
const printPreviewUrl = computed(()=>{
    let  letterhead = "";
    if(selectedLetterhead.value==""){
           letterhead = getDefaultLetterHead();
    }else {
        letterhead = selectedLetterhead.value;
    }
    const url =`${serverUrl}/printview?doctype=${activeReport.value.doc_type}&name=${props.params.name}&format=${activeReport.value.name}&product_category=${activeReport.value.filter?.product_category || ''}&no_letterhead=0&show_toolbar=0&letterhead=${letterhead}&settings=%7B%7D&_lang=${selectedLang.value}`; 
    return url;
})


function getDefaultLetterHead(){
    let  letterhead = "";
    
           letterhead = gv.setting.letter_heads.filter(r=>r.is_default==1)[0]?.name;
        if(!letterhead){
            letterhead = "No Letterhead";
        }
   return letterhead;
}

const emit = defineEmits(["resolve"])



 
const triggerPrint = ref(0)


if (props.params.print) {
    triggerPrint.value = 1;
} else {
    triggerPrint.value = 0;
}
 
 
 
function onViewReport(r){
    activeReport.value = r; 
}

function onClose(isClose) {
    emit('resolve', isClose);
}

function onRefresh(){
  
    document.getElementById("report-view").contentWindow.location.replace(printPreviewUrl.value)
 
}

function onPrint() { 
    if ((localStorage.getItem("flutterWrapper") || 0) == 1) { 
        var printers = (gv.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
        if (printers.length <= 0) {
            // toaster.warning($t("Printer not yet configt for this device"))
        } else {
            let data ={
                action : "print_report",
                doc: props.params.doctype,
                name:props.params.name,
                print_format:activeReport.value.name,
                printer : {
                    "printer_name": printers[0].printer_name,
                    "ip_address": printers[0].ip_address,
                    "port": printers[0].port,
                    "cashier_printer": printers[0].cashier_printer,
                    "is_label_printer": printers[0].is_label_printer
                }
            }
           
            flutterChannel.postMessage(JSON.stringify(data));
        }
        toaster.success($t("Report is printing"))
    }
    else{
        if (localStorage.getItem("is_window")==1) {
            if(props.params.doctype =="Sale" && activeReport.value.pos_receipt_file_name !="" && activeReport.value.pos_receipt_file_name !=null){            
                window.chrome.webview.postMessage("doc");
                return;
            }            
        }
        if((localStorage.getItem("apkipa") ||0)==0){
            window.open(printPreviewUrl.value + "&trigger_print=1").print();
            window.close();
        }
    }

}


const reportClickHandler = async function (e) {
    if(e.isTrusted && typeof(e.data) == 'string'){
       
        const data = e.data.split("|")
        
        if(data.length>0){
      
            if(data[0]=="view_sale_detail"){
                saleDetailDialog({
            name:data[1]
            });
            
            }
        
        }
        
    }
};

function onFilter(){ 
    if(filter.product_category && filter.product_category != 'All Product Categories'){
        
        activeReport.value.filter = {
            product_category: filter.product_category
        }
   
        onRefresh()
    }else{
        activeReport.value.filter.product_category = ''
        onRefresh()
    }
}

window.addEventListener('message', reportClickHandler, false);

onUnmounted(() => {
    window.removeEventListener('message', reportClickHandler, false);
}) 

</script>

