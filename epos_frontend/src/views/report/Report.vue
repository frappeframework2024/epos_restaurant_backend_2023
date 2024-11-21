 <template>
    <ComLoadingDialog v-if="isLoading" />
    <PageLayout class="pb-4" :title="`${$t(activeReport.doc_type)} #${activeReport.report_id}`" icon="mdi-chart-bar" full>
        <template #action>
            <template v-if="allowPreviewReport">
                <v-btn v-if="showPrintPopUp" @click="onPrintWithChoosePrinter()"> {{$t("Choose Printer") }}</v-btn>
                <v-btn  @click="onExport()">{{ $t("PDF") }}</v-btn>
                <v-btn icon="mdi-printer" @click="onPrint()"></v-btn>
            </template>
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
                                    <v-btn  :color="item.name == activeReport.report_id ? 'info' : 'default'" variant="tonal" stacked class="m-1" v-for="(item, index) in getCashierShifts(c)" :key="index" @click="onCashierShift(item)">
                                        <div>{{ moment(item.creation).format('h:mm:ss A') }}</div>
                                        <div class="text-xs">#{{ item.name }} </div>
                                        <div>
                                            <v-chip v-if="item.is_closed" color="error" size="x-small" variant="elevated">{{ $t('Closed') }}</v-chip>
                                            <v-chip v-else color="success" size="x-small" variant="elevated">{{ $t('Opening') }}</v-chip>
                                        </div>
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
                                        }}</span> {{ $t('was opening by') }} <span class="font-bold">{{ c.created_by??c.owner }}</span></div>
                                        <div v-if="c.is_closed">
                                            <v-icon icon="mdi-calendar-multiple" size="x-small" /> <span
                                                class="font-bold">{{ c.closed_date }}</span> {{ $t('was closed by') }} <span
                                                class="font-bold">{{ c.closed_by?? c.modified_by }}</span>
                                        </div>
                                        <div><v-icon icon="mdi-note-text" size="x-small"></v-icon> {{ $t('Total Shift') }}: <span
                                                class="font-bold">{{getCashierShifts(c).length }}</span></div>
                                    </div>
                                </template>
                            </v-card>
                            <div v-if="activeReport.report_id == c.name || getCashierShifts(c).find(r=>r.name == activeReport.report_id)">
                                <div class="-m-1">
                                    <v-btn  :color="item.name == activeReport.report_id ? 'info' : 'default'" variant="tonal" stacked class="m-1" v-for="(item, index) in getCashierShifts(c)" :key="index" @click="onCashierShift(item)">
                                        <div>{{ moment(item.creation).format('h:mm:ss A') }}</div>
                                        <div class="text-xs">#{{ item.name }}</div>
                                        <div>
                                            <v-chip v-if="item.is_closed" color="error" size="x-small" variant="elevated">{{ $t('Closed') }}</v-chip>
                                            <v-chip v-else color="success" size="x-small" variant="elevated">{{ $t('Opening') }}</v-chip>
                                        </div>
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
                                        <v-icon  class="d-none d-md-block mx-1" icon="mdi-refresh" size="small" @click="onRefresh"/>
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


                <v-card-text style="height: calc(100vh - 290px)">
                   
                    <template v-if="allowPreviewReport">
                        <iframe  v-if="(activeReport.doc_type !='') " 
                            id="report-view" 
                            height="100%" 
                            width="100%" 
                            :src="printPreviewUrl"  
                            @load="onIframeLoad"
                            @error="onIframeError"></iframe>
                    </template>
                    <template v-else>
                        <div style="height: calc(100vh - 300px);">
                            <div class="report_container_error">
                                <div style="margin-bottom: 45px;">
                                    <svg fill="#7c7c7c"  version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-6 -6 72.00 72.00" xml:space="preserve" width="136px" height="136px" transform="rotate(0)matrix(1, 0, 0, 1, 0, 0)" stroke="#7c7c7c" stroke-width="0.72"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round" stroke="#CCCCCC" stroke-width="0.12"></g><g id="SVGRepo_iconCarrier"> <g> <g> <path d="M56.5,49L56.5,49V1c0-0.6-0.4-1-1-1h-45c-0.6,0-1,0.4-1,1v14h2V2h43v46h-9c-0.6,0-1,0.4-1,1v9h-33V43h-2v16 c0,0.6,0.4,1,1,1h35c0.3,0,0.5-0.1,0.7-0.3l10-10c0.1-0.1,0.1-0.2,0.2-0.3v-0.1C56.5,49.2,56.5,49.1,56.5,49z M46.5,50h6.6 l-3.3,3.3l-3.3,3.3L46.5,50L46.5,50z"></path> <path d="M16.5,38h6h4v-2h-3V17c0-0.6-0.4-1-1-1h-6c-0.6,0-1,0.4-1,1v6h-5c-0.6,0-1,0.4-1,1v4h-5c-0.6,0-1,0.4-1,1v8 c0,0.6,0.4,1,1,1h6H16.5z M17.5,18h4v18h-4V24V18z M11.5,25h4v11h-4v-7V25z M5.5,30h4v6h-4V30z"></path> <path d="M50.5,24V7c0-0.6-0.4-1-1-1h-21c-0.6,0-1,0.4-1,1v17c0,0.6,0.4,1,1,1h21C50.1,25,50.5,24.6,50.5,24z M48.5,12h-12V8h12V12 z M34.5,8v4h-5c0-1.6,0-4,0-4H34.5z M29.5,14h5v9h-5C29.5,23,29.5,18.3,29.5,14z M36.5,23v-9h12v9H36.5z"></path> <rect x="28.5" y="28" width="21" height="2"></rect> <rect x="28.5" y="33" width="21" height="2"></rect> <rect x="28.5" y="38" width="21" height="2"></rect> <rect x="14.5" y="6" width="6" height="2"></rect> <rect x="14.5" y="11" width="9" height="2"></rect> <rect x="14.5" y="43" width="7" height="2"></rect> <rect x="24.5" y="43" width="7" height="2"></rect> <rect x="34.5" y="43" width="7" height="2"></rect> <rect x="14.5" y="48" width="7" height="2"></rect> <rect x="24.5" y="48" width="7" height="2"></rect> <rect x="34.5" y="48" width="7" height="2"></rect> <rect x="14.5" y="53" width="7" height="2"></rect> <rect x="24.5" y="53" width="7" height="2"></rect> <rect x="34.5" y="53" width="7" height="2"></rect> </g> </g> </g></svg>
                                </div>
                                <span class="report_title_error">{{ $t("Not Allow Preview") }}</span>
                                <div class="report_dp_error">
                                    <span>{{ $t("System not allow preview report during status opening") }}</span>
                                </div>	
                            </div>
                        </div>
                    </template>
                </v-card-text>
            </v-card>
        </v-col>
    </v-row>
</PageLayout>
</template>
<script setup>
import { inject, computed,ref,saleDetailDialog,onUnmounted, reactive,i18n} from '@/plugin'
import Enumerable from 'linq'
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';
import PageLayout from '@/components/layout/PageLayout.vue';
import { createToaster } from '@meforma/vue-toaster';
import { onMounted } from 'vue';
 
const socket = inject("$socket");
const gv = inject('$gv');
const frappe = inject('$frappe');
const moment = inject('$moment');

const pos_profile = localStorage.getItem("pos_profile");

let port = gv.setting.pos_setting.use_backend_port == 0 ? `:${window.location.port}` : (window.location.protocol == "https:" ? "" : `:${gv.setting.pos_setting.backend_port}`)
const serverUrl = `${window.location.protocol}//${window.location.hostname}${port}`;

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

const isTransactionClosed = ref(0)

const workingDay = ref(null)
const isLoading  = ref(true)
const drawer = ref(false)

const printPreviewUrl = computed(()=>{
    isLoading.value = true;
    let param = getReportParam();
    const url =  `${serverUrl}/printview?doctype=${activeReport.value.doc_type}&name=${param.name}&product_category=${param.product_category}&pos_profile=${param.pos_profile}&outlet=${param.outlet}&format=${param.format}&no_letterhead=0&show_toolbar=0&letterhead=${param.letterhead}&settings=%7B%7D&_lang=${activeReport.value.lang}`
    return url;
})

const allowPreviewReport =computed(()=>{
    if(gv.setting?.pos_setting?.show_preview_report){
        return true
    }else{
        if(isTransactionClosed.value){
            return true
        }
        return false
    }
})



const getReportParam = (isPreview = true) =>{
    const format = isPreview ? activeReport.value.preview_report : activeReport.value.print_report_name;  
    const param = {
        "name": encodeURIComponent(activeReport.value.report_id),
        "product_category":encodeURIComponent(activeReport.value.filter.product_category),
        "pos_profile":encodeURIComponent(pos_profile),
        "outlet":encodeURIComponent(gv.setting.outlet),
        "format":encodeURIComponent(format),
        "letterhead":encodeURIComponent(activeReport.value.letterhead)
    } 
    return param;
}


const printUrl = computed(()=>{
    let param = getReportParam(false);
    return `${serverUrl}/printview?doctype=${activeReport.value.doc_type}&name=${param.name}&product_category=${param.product_category}&pos_profile=${param.pos_profile}&outlet=${param.outlet}&format=${param.format}&no_letterhead=0&show_toolbar=0&letterhead=${param.letterhead}&settings=%7B%7D&_lang=${activeReport.value.lang}`
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

        isTransactionClosed.value = working_day_print_format[0]?.is_closed??0

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

    isLoading.value = false;
    
}

function onIframeLoad(){
    isLoading.value = false
}
function onIframeError(){
    isLoading.value = false
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
        activeReport.value.print_report_name = cashierShiftReports.value[0]?.print_report_name || cashierShiftReports?.value[0]?.name;

        isTransactionClosed.value = data?.is_closed??0;
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
    activeReport.value.print_report_name = workingDay[0]?.print_report_name || workingDay[0]?.name;

    isTransactionClosed.value = working_day?.is_closed??0;
}

function onRefresh(){
    if(document.getElementById("report-view")){
        document.getElementById("report-view").contentWindow.location.replace(printPreviewUrl.value)
    }
}

function onPrintWithChoosePrinter(){
     window.open(printUrl.value + "&trigger_print=1").print();
            window.close();
}
function onExport(){
    let exportUrl =   `${serverUrl}/api/method/frappe.utils.print_format.download_pdf?doctype=${activeReport.value.doc_type}&name=${activeReport.value.report_id}&pos_profile=${pos_profile}&outlet=${gv.setting.outlet}&product_category=${activeReport.value.filter.product_category}&format=${activeReport.value.print_report_name}&no_letterhead=0&show_toolbar=0&letterhead=${activeReport.value.letterhead}&settings=%7B%7D&_lang=${activeReport.value.lang}`
    window.open(exportUrl);
    window.close();
}


function onPrint(){ 
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

    let printers = (gv.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
    let _printer = undefined;
    if(printers.length>0){
        _printer = {
            "printer_name": printers[0].printer_name,
            "ip_address": printers[0].ip_address,
            "port": printers[0].port,
            "cashier_printer": printers[0].cashier_printer,
            "is_label_printer": printers[0].is_label_printer,
            "usb_printing": printers[0].usb_printing,
        }
    }

    if ((gv.setting?.device_setting?.use_server_network_printing||0)==1) {        
        if (printers.length <= 0) {
            // pass
        } else { 
            if(printers[0].usb_printing == 0){
                let network_data ={
                    action : "print_report",
                    doc: activeReport.value.doc_type,
                    name: activeReport.value.report_id,
                    print_format: activeReport.value.print_report_name,
                    pos_profile:pos_profile,
                    outlet:gv.setting.outlet,
                    letterhead:activeReport.value.letterhead,
                    printer : _printer
                }
   
                call.post("epos_restaurant_2023.api.network_printing_api.print_report_to_network_printer",{"data":network_data})            
                toaster.success($t("Report is printing"))
                return  
            }else if((localStorage.getItem("flutterWrapper") || 0) == 1){
                data.printer = _printer;
                socket.emit('PrintReceipt', JSON.stringify(data));
                toaster.success($t("Report is printing"))
                return  
            }
        } 
    }
    

    if(localStorage.getItem("is_window")==1){
        gv.onPrintWorkingDayAndCashierShift(activeReport.value.report_id,pos_profile, activeReport.value.doc_type)
        window.chrome.webview.postMessage(JSON.stringify(data));
    }else  if((localStorage.getItem("flutterWrapper") || 0) == 1){
        data.printer = _printer;
        flutterChannel.postMessage(JSON.stringify(data));
    }
    else{
        data.printer = _printer;
        socket.emit('PrintReceipt', JSON.stringify(data));
    }
    toaster.success($t("Report is printing")) 
   
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


.report_container_error{
    display: flex;
    align-items: center;
    justify-content: center;
    font-family:'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;
    flex-direction: column;
    color: #7c7c7c ;
}
.report_title_error{
    font-size: 30px;
    margin-top: -30px;
}
.report_dp_error{
    margin-top: 20px;
}
.report_icon-error-contact{
    margin-top: 5px;
}

</style>