<template>
    <ComModal  fullscreen :loading="loading"  @onClose="onClose" @onOk="onSave" width="960px">
        <template #title>
            {{ params.title }}
            
        </template>
        <template #content>
        <div class="grid grid-cols-3 gap-3 w-full mt-3">
         <div class="col-6 w-full shadow-lg  pb-4 rounded-lg" >
            <div class="text-center text-lg bg-blue-100 rounded-t-lg
             p-3 font-bold mb-3"> Menu </div>
            <div class="mx-3" style="max-height: 80vh;overflow: auto;">
                <tree v-if="posMenuData" :nodes="posMenuData" :config="config" @nodeFocus="onSelectNode"></tree>
            </div>
         </div>
         <div class="col-span-2 col-6 w-full shadow-lg pb-4 rounded-lg">
            <div class="text-center text-lg bg-blue-100 rounded-t-lg
             p-3 font-bold mb-3"> Edit Menu </div>
            <div v-if="selectedNode">
        <div class="px-3 mx-3">
            <div  class="grid  gap-3 w-full" style="max-height: 80vh;overflow: auto;"> 
            <div v-sortable>
                <div :data-name="a.sort_order" v-for="(a, index) in product.posMenuResource.data.filter(r=>r.parent==selectedNode.name && r.type != 'back')" :key="index" class="list-group">
                    <div class="list-group-item">{{ a.name }}</div>
                </div>
            </div>
                <table>

                    <tr  v-for="item in product.posMenuResource.data.filter(r=>r.parent==selectedNode.name && r.type != 'back')" :key="item.menu_product_name" class="bg-blue-50 rounded-lg shadow-lg border cursor-move p-2">
                        <td class="w-20"> 
                            <div style="border: 2px solid #b1b1b1;" class="overflow-hidden flex justify-center items-center m-2  w-20 bg-white h-full rounded-lg h-20">  
                            <img v-if="item.photo" class="w-auto" :src="item.photo"   />
                                <span v-else class="mt-auto mb-auto text-xl h-18 text-slate-400">
                                    {{ getShortName(item?.name) }} 
                                </span>
                            </div>
                        </td>
                        <td class="p-2">
                            <label>En Product Name</label>
                            <input class="border-2 input_text_style w-full" type="text" v-model="item.name_en" /></td>
                        <td class="p-2">
                            <label>KH Product Name</label>
                            <input  class="border-2 input_text_style w-full" type="text" v-model="item.name_kh" /></td>
                    </tr>
                </table>
    
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
<style scoped>
.input_text_style{
    border: 1px solid rgb(200, 200, 200);
    padding: 5px;
    border-radius: 6px;
    background: white;
}
::v-deep .node-wrapper {
    border-radius: 10px;
    padding: 7px;
    cursor: pointer;
    }
::v-deep .node-wrapper:focus {
    background-color: rgb(172, 207, 254);
}
::v-deep .tree-node{
    background-color: rgb(219 234 254);
    border-radius: 10px;
}
::v-deep .node-wrapper:hover{
    background-color: rgb(172, 207, 254); 
}
</style>

