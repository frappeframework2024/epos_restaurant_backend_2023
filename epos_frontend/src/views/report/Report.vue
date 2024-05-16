 <template>
    <PageLayout class="pb-4" :title="`${$t(activeReport.doc_type)} #${activeReport.report_id}`" icon="mdi-chart-bar" full>
        <template #action>
            <v-btn v-if="showPrintPopUp" @click="onPrintWithChoosePrinter()"> {{$t("Choose Printer") }}</v-btn>
            <v-btn  @click="onExport()">{{ $t("PDF") }}</v-btn>
            <v-btn icon="mdi-printer" @click="onPrint()"></v-btn>
        </template>
    <v-row> 
        <v-navigation-drawer v-model="drawer" location="left" temporary style="width:90%">
            <v-card :subtitle="$t('Working Day and Cashier Shift Report')">
                <v-card-text class="report-list-container"> 
                    <ComPlaceholder :loading="workingDayReports === null " :is-not-empty="workingDayReports?.length > 0">
                        <template v-for="(c, index) in workingDayReports" :key="index">
                            <v-card :color="activeReport.report_id == c.name ? 'info' : 'default'" :variant="activeReport.report_id == c.name || c.cashier_shifts.find(r=>r.name == activeReport.report_id) ? 'tonal' : 'text'" class="bg-gray-200 my-2 subtitle-opacity-1" @click="onWorkingDay(c)">
                                <template v-slot:title>
                                    <div class="flex justify-between">
                                        <div>{{ c.name }}</div>
                                        <div>
                                            <v-chip v-if="c.is_closed" color="error" size="small"
                                                variant="elevated">{{ $t('Closed') }}</v-chip>
                                            <v-chip v-else color="success" size="small" variant="elevated">{{ $t('Opening') }}</v-chip>
                                        </div>
                                    </div>
                                </template>
                                <template v-slot:subtitle>
                                    <div>
                                        <div><v-icon icon="mdi-calendar" size="x-small" /> <span class="font-bold">{{
                                            c.posting_date
                                        }}</span> {{ $t('was opening by') }} <span class="font-bold">{{ c.owner }}</span></div>
                                        <div v-if="c.is_closed">
                                            <v-icon icon="mdi-calendar-multiple" size="x-small" /> <span
                                                class="font-bold">{{ c.closed_date }}</span> {{ $t('was closed by') }} <span
                                                class="font-bold">{{ c.modified_by }}</span>
                                        </div>
                                        <div><v-icon icon="mdi-note-text" size="x-small"></v-icon> {{ $t('Total Shift') }}: <span
                                                class="font-bold">{{getCashierShifts(c).length }}</span></div>
                                    </div>
                                </template>
                            </v-card>
                            <div v-if="activeReport.report_id == c.name || getCashierShifts(c).find(r=>r.name == activeReport.report_id)">
                                <div class="-m-1">
                                    <v-btn :color="item.name == activeReport.report_id ? 'info' : 'default'" variant="tonal" stacked class="m-1" v-for="(item, index) in getCashierShifts(c)" :key="index" @click="onCashierShift(item)">
                                        <div>{{ moment(item.creation).format('h:mm:ss A') }}</div>
                                        <div class="text-xs">#{{ item.name }}</div>
                                    </v-btn>
                                </div>
                            </div>
                            <div class="pt-2">
                                <hr/>
                            </div>
                        </template>
                    </ComPlaceholder>
                </v-card-text>
            </v-card>
        </v-navigation-drawer> 

        <v-col md="3" class="d-none d-md-block"> 
            <v-card :subtitle="$t('Working Day and Cashier Shift Report')">
                <v-card-text class="report-list-container"> 
                    <ComPlaceholder :loading="workingDayReports === null " :is-not-empty="workingDayReports?.length > 0">
                        <template v-for="(c, index) in workingDayReports" :key="index">
                            <v-card :color="activeReport.report_id == c.name ? 'info' : 'default'" :variant="activeReport.report_id == c.name || c.cashier_shifts.find(r=>r.name == activeReport.report_id) ? 'tonal' : 'text'" class="bg-gray-200 my-2 subtitle-opacity-1" @click="onWorkingDay(c)">
                                <template v-slot:title>
                                    <div class="flex justify-between">
                                        <div>{{ c.name }}</div>
                                        <div>
                                            <v-chip v-if="c.is_closed" color="error" size="small"
                                                variant="elevated">{{ $t('Closed') }}</v-chip>
                                            <v-chip v-else color="success" size="small" variant="elevated">{{ $t('Opening') }}</v-chip>
                                        </div>
                                    </div>
                                </template>
                                <template v-slot:subtitle>
                                    <div>
                                        <div><v-icon icon="mdi-calendar" size="x-small" /> <span class="font-bold">{{
                                            c.posting_date
                                        }}</span> {{ $t('was opening by') }} <span class="font-bold">{{ c.owner }}</span></div>
                                        <div v-if="c.is_closed">
                                            <v-icon icon="mdi-calendar-multiple" size="x-small" /> <span
                                                class="font-bold">{{ c.closed_date }}</span> {{ $t('was closed by') }} <span
                                                class="font-bold">{{ c.modified_by }}</span>
                                        </div>
                                        <div><v-icon icon="mdi-note-text" size="x-small"></v-icon> {{ $t('Total Shift') }}: <span
                                                class="font-bold">{{getCashierShifts(c).length }}</span></div>
                                    </div>
                                </template>
                            </v-card>
                            <div v-if="activeReport.report_id == c.name || getCashierShifts(c).find(r=>r.name == activeReport.report_id)">
                                <div class="-m-1">
                                    <v-btn :color="item.name == activeReport.report_id ? 'info' : 'default'" variant="tonal" stacked class="m-1" v-for="(item, index) in getCashierShifts(c)" :key="index" @click="onCashierShift(item)">
                                        <div>{{ moment(item.creation).format('h:mm:ss A') }}</div>
                                        <div class="text-xs">#{{ item.name }}</div>
                                    </v-btn>
                                </div>
                            </div>
                            <div class="pt-2">
                                <hr/>
                            </div>
                        </template>
                    </ComPlaceholder>
                </v-card-text>
            </v-card>
        </v-col> 
        <v-col md="9">
            <!-- Hamburger Nav -->
            <div class="d-flex justify-between items-center d-block d-md-none" style="padding: 0rem 1rem 0rem 0rem">
                <v-app-bar-nav-icon variant="text" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
                <v-icon icon="mdi-refresh" size="small" @click="onRefresh"/>
            </div>
            <!-- Hamburger Nav -->
            <v-card>
                <template #title>
                    <div class="px-1 py-2 -m-1">
                        <v-row>
                            <v-col> 
                                <div class="overflow-x-auto">
                                    <div v-if="cashierShiftReports?.length > 0 && activeReport.name == 'Cashier Shift'"> 
                                        <v-btn v-for="(r, index) in cashierShiftReports.sort((a, b) => a.sort_order - b.sort_order )" :key="index" :color="activeReport.preview_report == r.name ? 'info' : 'default'" class="m-1" @click="onPrintFormat(r)">{{$t(r.title)  }}</v-btn>
                                    </div>
                                    <div v-else-if="workingDay?.length > 0 && activeReport.name == 'Working Day'">                                    
                                        <v-btn v-for="(r, index) in workingDay.sort((a, b) => a.sort_order - b.sort_order )" :key="index" class="m-1" :color="activeReport.preview_report == r.name ? 'info' : 'default'" @click="onPrintFormat(r)">{{ $t(r.title)  }}</v-btn>
                                    </div> 
                                </div>
                            </v-col> 
                            <v-col cols="12" lg="5">
                                <div class="overflow-x-auto">
                                    <div class="d-block d-md-flex items-center col-4"> 
                                        <v-select 
                                        prepend-inner-icon="mdi-content-paste"
                                        density="compact"
                                        v-model="activeReport.letterhead"
                                        :items= gv.setting.letter_heads
                                        item-title="name"
                                        item-value="name"
                                        hide-no-data
                                        hide-details
                                        variant="solo"
                                        class="mx-1 mb-2 mb-md-0"
                                        @update:modelValue="onRefresh"
                                        ></v-select>
                                        <v-select 
                                        prepend-inner-icon="mdi-google-translate"
                                        density="compact"
                                        v-model="activeReport.lang"
                                        :items="lang" 
                                        item-title="language_name"
                                        item-value="language_code"
                                        hide-no-data
                                        hide-details
                                        variant="solo"
                                        class="mx-1"
                                        @update:modelValue="onRefresh"
                                        ></v-select>
                                        <v-icon class="d-none d-md-block mx-1" icon="mdi-refresh" size="small" @click="onRefresh"/>
                                    </div>
                                </div>
                            </v-col>
                        </v-row>
                        <div class="flex pt-2 px-2 items-center border-t border-gray-300 mt-2" v-if="activeReport.preview_report == 'Working Day Inventory Transaction' || activeReport.preview_report == 'Cashier Inventory Transaction'">
                            <div class="flex-grow">
                                <div style="max-width: 250px;">
                                    <ComAutoComplete v-model="filter.product_category" doctype="Product Category" variant="solo" @onSelected="onFilter"/> 
                                </div>
                            </div>
                            <div class="flex-none">
                                <v-btn prepend-icon="mdi-filter" color="primary" @click="onFilter">{{ $t('Filter') }}</v-btn>
                            </div>
                        </div>
                    </div>
                </template>
                <v-card-text style="height: calc(100vh - 230px)">
                    <iframe v-if="(activeReport.doc_type !='')" id="report-view" height="100%" width="100%" :src="printPreviewUrl"></iframe>
                </v-card-text>
            </v-card>
        </v-col>
    </v-row>
</PageLayout>
</template>
<script setup>
import { inject, computed,ref,saleDetailDialog,onUnmounted, reactive,i18n} from '@/plugin'
import Enumerable from 'linq'
import PageLayout from '@/components/layout/PageLayout.vue';
import { createToaster } from '@meforma/vue-toaster';
import { onMounted } from 'vue';
 
const socket = inject("$socket");
const gv = inject('$gv');
const frappe = inject('$frappe');
const moment = inject('$moment');

const pos_profile = localStorage.getItem("pos_profile");
const serverUrl = window.location.protocol + "//" + window.location.hostname + (window.location.protocol =="https:"? "": (":"+ gv.setting.pos_setting.backend_port));


const call = frappe.call();
const db = frappe.db();
const toaster = createToaster({ position: "top-right" });
const { t: $t } = i18n.global; 
 
let filter = reactive({
    product_category: 'All Product Categories',
    product_category_filter: ''
})
const activeReport = ref({
    name: 'Working Day',
    preview_report: '',
    print_report_name: '',
    report_id: '',
    doc_type: '',
    lang: 'en',
    letterhead: 'Default Letter Head',
    filter: {
        product_category : ''
    }
})
const workingDay = ref(null)
const drawer = ref(false)

const printPreviewUrl = computed(()=>{
    return `${serverUrl}/printview?doctype=${activeReport.value.doc_type}&name=${activeReport.value.report_id}&product_category=${activeReport.value.filter.product_category}&pos_profile=${pos_profile}&outlet=${gv.setting.outlet}&format=${activeReport.value.preview_report}&no_letterhead=0&show_toolbar=0&letterhead=${activeReport.value.letterhead}&settings=%7B%7D&_lang=${activeReport.value.lang}`
})


const printUrl = computed(()=>{
    return `${serverUrl}/printview?doctype=${activeReport.value.doc_type}&name=${activeReport.value.report_id}&product_category=${activeReport.value.filter.product_category}&pos_profile=${pos_profile}&outlet=${gv.setting.outlet}&format=${activeReport.value.print_report_name}&no_letterhead=0&show_toolbar=0&letterhead=${activeReport.value.letterhead}&settings=%7B%7D&_lang=${activeReport.value.lang}`
})

const lang = gv.setting.lang;

let workingDayReports = ref({});
let cashierShiftReports = ref([])


const showPrintPopUp = computed(()=>{
    if((localStorage.getItem("flutterWrapper")||0) == 0 &&  (localStorage.getItem("apkipa")||0) == 0){
        return true;
    }
    return false;
});


onMounted(()=>{
    // init data
    _onInit()
});


let working_day_print_format = [];
let cashier_shift_print_format = [];
let a = ref({})
async function _onInit() {
    // const param = {business_branch:gv.setting.business_branch, pos_profile:pos_profile}; 
    const param = {business_branch:gv.setting.business_branch, pos_profile:""}; 
    const result = await  call.get("epos_restaurant_2023.api.api.get_working_day_list_report",param).then((wd)=>{  
        if (wd.message.length > 0){
            let _reports = Enumerable.from(wd.message).orderByDescending("$.posting_date").thenByDescending("$.creation").toArray();  
            let _report_data = []
            _reports.forEach((_r)=>{
                let _report_by_pos_profiles = _r.cashier_shifts.filter((r)=>r.pos_profile==pos_profile);
                if((_report_by_pos_profiles?.length??0)>0){
                    _r.cashier_shifts = _report_by_pos_profiles;
                    _report_data.push(_r);
                }
                
            }) ;
            workingDayReports.value =    _report_data;
            activeReport.value.report_id = workingDayReports.value[0].name;

          return  db.getDocList("POS Print Format Setting",
            {
                fields: ['name', 'print_format_doc_type','sort_order','print_report_name','title'],
                filters: [
                    ["print_format_doc_type","in",["Working Day","Cashier Shift"]],
                    ["show_in_pos_report","=",1]
            ],
                orderBy: {
                    field: 'sort_order',
                    order: 'asc',
                }
            }).then(async (pf)=>{ 
                let _filters = []
                pf.forEach((p)=>{
                    _filters.push(p.name)
                });
                const print_format = await  db.getDocList("Print Format",{
                    fields:["*"],
                    filters: [["name","in",_filters]],
                }) 
                print_format.forEach((p)=>{
                    const _pf = pf.filter(x=>x.name==p.name);
                    p.print_report_name = _pf[0]?.print_report_name??"";
                    p.title = _pf[0]?.title??"";
                    p.sort_order = _pf[0]?.sort_order??0;
                })
                return print_format 
            })
        } 
    });
    
    result.forEach((r)=>{
        if(r.doc_type=="Working Day"){
            working_day_print_format.push(r);
        }else if(r.doc_type == "Cashier Shift"){
            cashier_shift_print_format.push(r);
        }
    }); 

    //check if working day print format have value     
    if(working_day_print_format.length > 0){
        working_day_print_format = working_day_print_format.sort((a, b) => a.sort_order - b.sort_order )

        activeReport.value.preview_report = working_day_print_format[0].name;
        activeReport.value.name = "Working Day";
        activeReport.value.doc_type = working_day_print_format[0].doc_type;
        activeReport.value.print_report_name = working_day_print_format[0].print_report_name || working_day_print_format[0].name;
        workingDay.value = working_day_print_format; 
    }


    //check if cashier shift print format have value
    if(cashier_shift_print_format.length>0){

        cashier_shift_print_format = cashier_shift_print_format.sort((a, b) => a.sort_order - b.sort_order );

        cashier_shift_print_format.forEach((cs)=>{
           const _data = {
                "name":cs.name,
                "doc_type":cs.doc_type,
                "print_report_name":cs.print_report_name,
                "title":cs.title,
            }
            cashierShiftReports.value.push(_data)
        })
    } 
    
}


function getCashierShifts(working_day){   
    return working_day.cashier_shifts.filter((r)=>r.pos_profile==pos_profile);
}
 
 
 

function onCashierShift(data){

    if(data && data.name){
        activeReport.value.name = 'Cashier Shift'
        activeReport.value.report_id = data?.name
        activeReport.value.preview_report = cashierShiftReports.value[0]?.name
        activeReport.value.doc_type = cashierShiftReports.value[0]?.doc_type 
        activeReport.value.print_report_name = cashierShiftReports.value[0]?.print_report_name || cashierShiftReports?.value[0]?.name
    }else{
        toast.error($t('Report is unavailable.'), { position: 'top' });
    }
}
function onPrintFormat(value){
    activeReport.value.preview_report = value.name;
    activeReport.value.print_report_name = value.print_report_name || value.name
    onRefresh()
  
}

function onWorkingDay(working_day){ 
    activeReport.value.name = 'Working Day';
    activeReport.value.report_id = working_day.name;
    activeReport.value.preview_report = workingDay.value[0]?.name;
    activeReport.value.doc_type = workingDay.value[0]?.doc_type ;
    const print_report_name = workingDay.value.filter(r=>r.name == working_day.name);
    
    activeReport.value.print_report_name = workingDay[0]?.print_report_name || workingDay[0]?.name;
}

function onRefresh(){
    document.getElementById("report-view").contentWindow.location.replace(printPreviewUrl.value)
}

function onPrintWithChoosePrinter(){
     window.open(printUrl.value + "&trigger_print=1").print();
            window.close();
}
function onExport(){
    var exportUrl =   `${serverUrl}/api/method/frappe.utils.print_format.download_pdf?doctype=${activeReport.value.doc_type}&name=${activeReport.value.report_id}&pos_profile=${pos_profile}&outlet=${gv.setting.outlet}&product_category=${activeReport.value.filter.product_category}&format=${activeReport.value.print_report_name}&no_letterhead=0&show_toolbar=0&letterhead=${activeReport.value.letterhead}&settings=%7B%7D&_lang=${activeReport.value.lang}`
    window.open(exportUrl);
    window.close();
}


function onPrint(){ 
    //if(activeReport.value.doc_type == "Cashier Shift" || activeReport.value.doc_type == "Working Day"){
       // gv.onPrintWorkingDayAndCashierShift(activeReport.value.report_id,pos_profile,activeReport.value.doc_type)
    //}
   
    if ((localStorage.getItem("flutterWrapper") || 0) == 1 || (gv.setting?.device_setting?.use_server_network_printing||0)==1) { 
        var printers = (gv.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
        if (printers.length <= 0) {
            // pass
        } else { 
            if(printers[0].usb_printing == 0){
                let data ={
                    action : "print_report",
                    doc: activeReport.value.doc_type,
                    name: activeReport.value.report_id,
                    print_format: activeReport.value.print_report_name,
                    pos_profile:pos_profile,
                    outlet:gv.setting.outlet,
                    letterhead:activeReport.value.letterhead,
                    printer : {
                        "printer_name": printers[0].printer_name,
                        "ip_address": printers[0].ip_address,
                        "port": printers[0].port,
                        "cashier_printer": printers[0].cashier_printer,
                        "is_label_printer": printers[0].is_label_printer,
                        "usb_printing": printers[0].usb_printing,
                    }
                }
                if((localStorage.getItem("flutterWrapper") || 0) == 1){
                    flutterChannel.postMessage(JSON.stringify(data));
                }else{
                    call.post("epos_restaurant_2023.api.network_printing_api.print_report_to_network_printer",{"data":data})
                }
                toaster.success($t("Report is printing"))
                return  
            }
        } 
    }
 
    if((localStorage.getItem("apkipa") ||0)==0){
        let data ={
            action : "print_report",                
            doc: activeReport.value.doc_type,
            name: activeReport.value.report_id,
            print_format: activeReport.value.print_report_name || '',
            pos_profile:pos_profile,
            outlet:gv.setting.outlet,
            letterhead:activeReport.value.letterhead,
            sale: {pos_profile:pos_profile},
            station: (gv.setting?.device_setting?.name) || "",
            station_device_printing: (gv.setting?.device_setting?.station_device_printing) || ""
        }
        if(localStorage.getItem("is_window")==1){
            window.chrome.webview.postMessage(JSON.stringify(data));
        }
        else{
            socket.emit('PrintReceipt', JSON.stringify(data));
        }
        toaster.success($t("Report is printing")) 
    }
} 
const reportClickHandler = async function (e) {
    if(e.isTrusted && typeof(e.data) == 'string'){
        const data = e.data.split("|")
        if(data.length>0){
            if(data[0]=="view_sale_detail"){
                saleDetailDialog({ name:data[1]});
            }
        }
    }
};

function onFilter(){ 
    if(filter.product_category && filter.product_category != 'All Product Categories'){
        activeReport.value.filter.product_category = filter.product_category
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
<style>
.subtitle-opacity-1 .v-card-subtitle {
    opacity: 1 !important;
}
.report-list-container{
    height:calc(100vh - 200px);
    overflow: auto;
}
.v-card-subtitle {
    white-space: normal !important;
}
</style>