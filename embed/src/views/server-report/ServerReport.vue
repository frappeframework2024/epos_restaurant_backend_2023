<template>
    <Splitter    state-key="report_server_backend_spliter_state" state-storage="local">
            <SplitterPanel :size="20" class="pa-4 left-side-panel overflow-y-auto wrapper-sidebar-report" style="height:99vh">
                <ComReportTree   :root_report="root_report" @onSelectReport="onSelectReport" />
            </SplitterPanel>
            <SplitterPanel :size="80" class="pa-4">
                
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
import { getApi,ref,useRoute } from '@/plugin';
import { onMounted } from 'vue';
 
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import ComReportTree from  "@/views/server-report/ComReportTree.vue";
import reportpng from "@/assets/images/report.png"
const setting =ref({})
const selectedReport = ref()
const route = useRoute();
const root_report =  ref(route.query.root_report)
function onSelectReport(p) { 
 
    selectedReport.value = p
    let report_params = [
        {name: 'printed_by', values: [setting.value.full_name] },
        {name: 'username', values: [setting.value.user] },
        {name: 'property', values: [setting.value.property] },
        {name: 'start_date', values: [setting.value.working_day.posting_date] },
        {name: 'end_date', values: [setting.value.working_day.posting_date] },
    ] 
    
    if(selectedReport.value.filter_default_value){
        const default_filter = JSON.parse(selectedReport.value.filter_default_value)
 
        if( default_filter.start_date){
            report_params = report_params.filter(r=>r.name!='start_date')
            report_params.push({name: 'start_date', values: [get_date_by_timestamp(default_filter.start_date)] })
        }
        if( default_filter.end_date){
           
            report_params = report_params.filter(r=>r.name!='end_date')
            report_params.push({name: 'end_date', values: [get_date_by_timestamp(default_filter.end_date)] })
        
        }
       
        if (default_filter.row_group){
            report_params.push({name: 'row_group', values: [default_filter.row_group] })
        }
        if (default_filter.order_by){
            report_params.push({name: 'order_by', values: [default_filter.order_by] })
        }
        if (default_filter.group_by){
            report_params.push({name: 'group_by', values: [default_filter.group_by] })
        }
        if (default_filter.show_package_breakdown){
            report_params.push({name: 'show_package_breakdown', values: [default_filter.show_package_breakdown] })
            
        }
        if (default_filter.show_all_breakdown){
            report_params.push({name: 'show_all_breakdown', values: [default_filter.show_all_breakdown] })
        }
        if (default_filter.show_all_breakdown){
            report_params.push({name: 'show_all_breakdown', values: [default_filter.show_all_breakdown] })
        }
        if (default_filter.status){
            report_params.push({name: 'status', values: [default_filter.status] })
        }
        if (default_filter.group_by_date){
            report_params.push({name: 'group_by_date', values: [default_filter.group_by_date] })
        }
        if (default_filter.group_by_date){
            report_params.push({name: 'group_by_date', values: [default_filter.group_by_date] })
        }
        if (default_filter.show_chart){
            report_params.push({name: 'show_chart', values: [default_filter.show_chart] })
        }
        if (default_filter.show_summary){
            report_params.push({name: 'show_summary', values: [default_filter.show_summary] })
        }
        if (default_filter.show_occupy_only){
            report_params.push({name: 'show_occupy_only', values: [default_filter.show_occupy_only] })
        }
         

    }
 
    $("#main_server_report_viewer_backend").boldReportViewer({
        reportServerUrl:setting.value.server_report_url,
        reportServiceUrl: setting.value.report_service_url,
        reportPath: selectedReport.value.server_report_path,
        serviceAuthorizationToken: "bearer " + setting.value.server_report_token,
        parameters: report_params,
        printMode:true,
        zoomFactor: 1.25,
        enableViewState: true,  // Enables the Save View feature
    toolbarSettings: {
        items: ej.ReportViewer.ToolbarItems.All,
        showSaveView: true,  // Shows Save View button on the toolbar
        showViewList: true,  // Enables selecting a saved view
    },
        reportLoaded: function(event) {
            setTimeout(() => {
                let property  = document.querySelector("#main_server_report_viewer_Param_101")
             
            }, 5000);
          
        }
    });
} 

function get_date_by_timestamp(timestap){

    if (timestap === "current_working_date") {
        return setting.value.working_day.posting_date;
    } else if (timestap === "today") {
        return moment().format("YYYY-MM-DD");
    } else if (timestap === "previous_working_day") {
        return moment(setting.value.working_day.posting_date).add(-1, "days").format("YYYY-MM-DD");
    } else if (timestap === "start_mtd") {
        return moment(setting.value.working_day.posting_date).startOf("month").format("YYYY-MM-DD");
    } else if (timestap === "end_mtd") {
        return moment(setting.value.working_day.posting_date).endOf("month").format("YYYY-MM-DD");
    } else if (timestap === "start_current_mtd") {
        return moment().startOf("month").format("YYYY-MM-DD");
    } else if (timestap === "end_current_mtd") {
        return moment().endOf("month").format("YYYY-MM-DD");
    }  else if (timestap === "start_ytd") {
        return moment(setting.value.working_day.posting_date).startOf("year").format("YYYY-MM-DD");
    } else if (timestap === "end_ytd") {
        return moment(setting.value.working_day.posting_date).endOf("year").format("YYYY-MM-DD");
    } else {
        return setting.value.working_day.posting_date;
    }
}


    onMounted(()=>{
        document.querySelector("#main_server_report_viewer_backend").style.height = window.innerHeight -4 + "px";
        getApi("api.get_server_report_setting").then(r=>{
            setting.value = r.message
        })

    })
</script>
