<template>
    <ComModal  fullscreen :loading="loading"  @onClose="onClose" @onOk="onSave" width="960px">
        <template #title>
            {{ params.title }}
            
        </template>
        <template #content>
        <div class="grid grid-cols-3 gap-3 w-full mt-3">
         <div class="col-6 w-full shadow-lg  pb-4 rounded-lg
         ">
            <div class="text-center text-lg bg-blue-100 rounded-t-lg
             p-3 font-bold mb-3"> Menu </div>
            <div class="px-3 mx-3">
                <tree v-if="posMenuData" :nodes="posMenuData" :config="config" @nodeFocus="onSelectNode"></tree>
            </div>
         </div>
         <div class="col-span-2 col-6 w-full shadow-lg pb-4 rounded-lg">
            <div class="text-center text-lg bg-blue-100 rounded-t-lg
             p-3 font-bold mb-3"> Edit Menu </div>
            <div v-if="selectedNode">
        <div class="px-3 mx-3">
            <div  class="grid  gap-3 w-full"> 
      
                    <div v-for="item in product.posMenuResource.data.filter(r=>r.parent==selectedNode.name && r.type != 'back')" :key="item.menu_product_name">
                        <div class="flex p-1 relative w-full bg-blue-50 rounded-lg shadow-xl border cursor-move">
                            <div class="absolute top-2 right-2 rounded-lg flex justify-center items-center bg-white text-black w-7 h-7"> {{ item.sort_order }} </div>
                            <div  class="overflow-hidden flex justify-center items-center  w-20 bg-white h-full rounded-lg h-20">
                                <img v-if="item.photo" class="w-auto" :src="item.photo" />
                                <span v-else class="mt-auto mb-auto text-xl h-18 text-slate-400">
                                    {{ getShortName(item?.name) }} 
                                </span>
                            </div>
                            <div class="relative mt-1 ms-2 text-sm">
                                <label>En Product Name</label><br>
                                <input style="border: 2px solid #c8c8c8;padding: 2px ;border-radius:5px;" class="border-2" type="text" v-model="item.name_en" />
                            </div>
                            <div class="relative mt-1 ms-2 text-sm">
                                <label>KH Product Name</label><br>
                                <input style="border: 2px solid #c8c8c8;padding: 2px ;border-radius:5px;" class="border-2" type="text" v-model="item.name_kh" />
                            </div>
                        </div>
                    </div>     
            </div> 
        </div>

</div>
         </div>
        </div>    

         
 
        </template>
    </ComModal>
</template>

<script setup>
import { ref, inject, onMounted, i18n } from '@/plugin'
import { watch } from 'vue'
import { createToaster } from "@meforma/vue-toaster";
import ComInput from '../../components/form/ComInput.vue';
import Tree from "vue3-treeview";
import "vue3-treeview/dist/style.css";
function getShortName(longName) {  
    if (longName === null || longName === undefined) {
    return ''; 
  }  
  const words = longName.split(' ');
  let shortName = '';
  for (let i = 0; i < Math.min(words.length, 2); i++) {
    shortName += words[i].charAt(0);
  }
  return shortName.toUpperCase();
}
const config = ref({
  roots: ["0"],
});


const posMenuData = ref()



const moment = inject('$moment')

const { t: $t } = i18n.global;

const toaster = createToaster({ position: "top-right" });
const gv = inject('$gv')
const product = inject('$product')
const frappe = inject('$frappe')
const call = frappe.call();
const db = frappe.db();
const device_setting = JSON.parse(localStorage.getItem("device_setting"));
 
const selectedNode = ref()
const props = defineProps({
    params: {
        type: Object,
        required: true,
    },
})

const emit = defineEmits(["resolve"])
 
let loading = ref(false)

onMounted(async () => {
    posMenuData.value = getPOSMenuData()
})
  

function getPOSMenuData(){
    const pos_menus =  product.posMenuResource.data.filter(r=>r.type!='back').map((item, index)  => ({
        name: item.name,
        text: item.name_en,
        name_kh: item.name_kh,
        parent: item.parent,
        type:item.type,
        index: index + 1
        }));
    
    pos_menus.unshift({
        name:product.setting.default_pos_menu,
        index:0,
        text:product.setting.default_pos_menu,
        name_kh:product.setting.default_pos_menu,
         type:"menu",
    })

    const nodeObject = pos_menus?.reduce((acc, item) => {
        acc[item.index] = {
            name: item.name,
            text: item.text || "",
            name_kh: item.name_kh || "",
            parent: item.parent || "",
            type: item.type,
            index: item.index.toString(),

        }; 
        if (item.type=="menu"){
            acc[item.index].children = pos_menus.filter(x=>x.parent == item.name && x.type=="menu").map(y=>y.index.toString())
        }
        return acc;
    }, {});
   
    return nodeObject
}
 

function onSelectNode(n){
    selectedNode.value = n
}
function onSave() {
     alert("save")
}
   
function onClose() {
    emit('resolve', false);
}
</script>


