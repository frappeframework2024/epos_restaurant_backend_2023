<template>
    <Splitter    state-key="report_server_backend_spliter_state" state-storage="local">
            <SplitterPanel :size="25" class="pa-4 left-side-panel overflow-y-auto wrapper-sidebar-report" style="height:99vh">
                <ComReportTree   @onSelectReport="onSelectReport" />
            </SplitterPanel>
            <SplitterPanel :size="75" class="pa-4">
                
                <div style="height:100vh" id="main_server_report_viewer_backend" class="flex align-items-center justify-content-center">
                    <div class="flex flex-column align-items-center gap-5" v-if="!selectedReport">
                        <img :src="reportpng" width="100" />
                        Please select a report to view your report.
                    </div>
                </div>
                
            </SplitterPanel>
        </Splitter>
        
</template>
<script setup>
import { getApi,ref } from '@/plugin';
import { onMounted } from 'vue';
 
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import ComReportTree from  "@/views/server-report/ComReportTree.vue";
import reportpng from "@/assets/images/report.png"
const setting =ref({})
const selectedReport = ref()
function onSelectReport(p) { 

selectedReport.value = p
let report_params = [
    {name: 'printed_by', values: [setting.value.full_name] },
    {name: 'property', values: [setting.value.property] },
    {name: 'start_date', values: ['2025-01-01'] },
    {name: 'end_date', values: [ getCurrentDate()] },
] 
function getCurrentDate() {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); 
    const day = String(date.getDate()).padStart(2, '0'); 
    return `${year}-${month}-${day}`;
}

$("#main_server_report_viewer_backend").boldReportViewer({
    reportServerUrl:setting.value.server_report_url,
    reportServiceUrl: setting.value.report_service_url,
    reportPath: selectedReport.value.server_report_path,
    serviceAuthorizationToken: "bearer " + setting.value.server_report_token,
    parameters: report_params,
    printMode:true,
    zoomFactor: 1,
    enableViewState: true,  // Enables the Save View feature
    toolbarSettings: {
        items: ej.ReportViewer.ToolbarItems.All,
        showSaveView: true,  // Shows Save View button on the toolbar
        showViewList: true,  // Enables selecting a saved view
    },
    reportLoaded: function(event) {
    }
});


} 



    onMounted(()=>{
        document.querySelector("#main_server_report_viewer_backend").style.height = window.innerHeight -4 + "px";
        getApi("api.get_server_report_setting").then(r=>{
            setting.value = r.message
        })

    })
</script>
