<template>
    <ComModal :loading="loading"  @onClose="onClose" @onOk="onSave()" width="960px">
        <template #title>
            {{ params.title }}
            
        </template>
        <template #content>
            <tr  class="bg-blue-50 rounded-lg shadow-lg border cursor-move p-2">
                <td class="w-20"> 
                    <div style="border: 2px solid #b1b1b1;" class="overflow-hidden flex justify-center items-center m-2  w-20 bg-white h-full rounded-lg h-20">  
                    <img v-if="params.item.photo" class="w-auto" :src="params.item.photo"   />
                        <span v-else class="mt-auto mb-auto text-xl h-18 text-slate-400">
                            {{ getShortName(params.item?.name) }} 
                        </span>
                    </div>
                </td>
                <td class="p-2">
                    <label>En Product Name</label>
                    <input class="border-2 input_text_style w-full" type="text" v-model="params.item.name_en" /></td>
                <td class="p-2">
                    <label>KH Product Name</label>
                    <input class="border-2 input_text_style w-full" type="text" v-model="params.item.name_kh" /></td>
                
                <td class="p-2">
                    <label>Price</label>
                    <input :readonly="params.prices.length>0" type="number" class="border-2 input_text_style w-full"  v-model="params.item.price" />
                </td>
            </tr>
            <tr v-if="params.prices.length>0">
                <td colspan="3">
                    <table>
                        <tbody>
                        <tr>
                            <th style="width: 20%;">{{ $t("Price Rule") }}</th>
                            <th style="width: 20%;">{{ $t("Portion") }}</th>
                            <th style="width: 20%;">{{ $t("Price") }}</th>
                        </tr>
                        <tr v-for="(p, pindex) in params.prices" :key="pindex" >
                            <td style="text-align: center;">{{ p.price_rule }}</td>
                            <td style="text-align: center;">{{ p.portion }}</td>

                            <td> <input style="text-align: center;"  @change="onUpdate(p)" type="number" class="border-2 input_text_style w-full"  v-model="p.price" /></td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>         
        </template>
    </ComModal>
</template>

<script setup>
import { i18n,postApi,ref } from '@/plugin'
import { createToaster } from "@meforma/vue-toaster";
import "vue3-treeview/dist/style.css";

let loading = ref(false)

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

const { t: $t } = i18n.global;
const toaster = createToaster({ position: "top-right" });
const props = defineProps({
    params: {
        item: Object,
        title: String,
        prices: Array
    },
})

const emit = defineEmits(["resolve"])

function onSave() {
    postApi("epos_restaurant_2023.inventory.doctype.product.product.update_single_product_info",{product:props.params.item,prices:props.params.prices},"",true,"")
    loading.value = true
    setTimeout(() => {
        window.location.reload();
        emit('resolve', true);
          }, 3000) 
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

