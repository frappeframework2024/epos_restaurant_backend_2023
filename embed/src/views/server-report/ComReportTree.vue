<template>
    
    <div class="p-2">
        <div class="mb-3">
            <InputText class="w-full" v-model="keyword" @input="onSearch" :placeholder="'Search Report (min. 3 characters)'" />
        </div>
        <div v-if="!loading">
       
            <PanelMenu  :model="reportItems" class="w-full">
                <template #item="{ item }">
                   
                    <a v-ripple :style="{  borderRadius: '7px', backgroundColor: selectedReport?.name === item.name ? '#edf6fd' : 'transparent'}" class="flex align-items-center px-3 py-2 cursor-pointer" :class="[item.items.length>0 ? 'p-panelmenu-panel': '']" >
                        
                        <span :class="['pi pi-angle-right', 'text-primary']" v-if="item.items.length>0" />
                        <span :class="['ml-2', { 'font-semibold': item.items }]">{{ item.report_title }} 
                        </span>
                        <Badge  class="ml-auto" :value="item.items.length" v-if="item.items.length>0" />
                    </a>

    </template>
            </PanelMenu>
        </div>
    </div>

   

</template>
<script setup>
import { ref, getDocList, onMounted, computed } from "@/plugin"
 
import InputText from 'primevue/inputtext';

const emit = defineEmits(["onSelectReport","onTabClick"])
const selectedReport = ref()
import PanelMenu from 'primevue/panelmenu';
import { watch } from "vue";
 
const keyword = ref("")
const loading = ref(false)
const reportItems = ref([])
const allReports =ref([]) 
const filterReports =ref([]) 



const onSearch = debouncer(() => {
    if (keyword.value) {
        if(keyword.value.length>=3){
       // get all parent
       filterReports.value = allReports.value.filter(r=>r.is_group == 1)
        // get all child that match with fitler
        filterReports.value = [...filterReports.value,...allReports.value.filter(r=>r.is_group == 0 && (r.report_title?.toLowerCase() + " " +  r.keyword?.toLowerCase()).includes(keyword.value.toLowerCase()))]

        }
 
    } else {
        filterReports.value =  allReports.value
        
    }
    reportItems.value = buildTreeData()
   
   
}, 700);


function debouncer(fn, delay) {
  var timeoutID = null;
  return function () {
    clearTimeout(timeoutID);
    var args = arguments;
    var that = this;
    timeoutID = setTimeout(function () {
      fn.apply(that, args);
    }, delay);
  };
}
 
 


function onTabClick () {
    emit("onTabClick")
}


function buildTreeData(){
   
     
    if(filterReports.value){
        let tree_report_data = filterReports.value.filter(r=>r.parent_system_report == 'All Reports'  );
    tree_report_data.forEach(parent=>{
        parent.keyword  = parent.report_title 
        parent.items = getSubReportItem(parent)
    })
    if (keyword.value){
        
        return    tree_report_data.filter(r=>r.items.length>0)
         
    }else {
        return tree_report_data;
    }
   
}

   return []
    

}

function getSubReportItem(parent){
    
    let child_report_items = filterReports.value.filter(r=>r.parent_system_report==parent.name);
    child_report_items.forEach(ch =>{
        ch.items = getSubReportItem(ch);
        ch.keyword = parent.keyword + " " + ch.report_title
        if (ch.items.length==0 && ch.is_group == 0){
            ch.command= () => {
                selectedReport.value = ch;
                emit("onSelectReport",ch);
                }
        }

    })
    return  child_report_items;
}

onMounted(() => {
    loading.value = true;
     
    getDocList("System Report", {
        fields: ["name", "is_group", "report_title", "report_name","server_report_path", "filter_option", "parent_system_report","filter_default_value"],
        orderBy: {
            field: "sort_order",
            order: "asc"
        },
        limit: 1000,
    }).then((result) => {
        const translatedResults = result.map(item => ({
        ...item,
        report_title: item.report_title,
      }));
        allReports.value = translatedResults
        filterReports.value = translatedResults;
         
         reportItems.value = buildTreeData();
        loading.value = false;
    }).catch((err) => {
        loading.value = false;
    })

})

</script>
<style scoped>

 .ml-2 {
    margin-left: 0.15rem !important;
}

.font-semibold{
    font-weight: 300 !important;
}

.py-2{
   
    padding-top: 0.15rem !important;
    padding-bottom: 0.15rem !important;
}

 

</style>