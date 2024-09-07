<template>
  <div class="grid p-3">
    <div
      class="flex-1 w-full flex align-items-center justify-content-center m-3"
    >


      <Fieldset class="w-full m-2" legend="Previews">
        <label>Height : </label>
        <InputText v-model.number="data.height" class="w-1" />
        <Slider v-model="data.height" :min="50" :max="500" class="w-2 my-3" />

        <label>Width : </label>
        <InputText v-model.number="data.width" class="w-1" />
        <Slider v-model="data.width" class="w-2 my-3" :min="50" :max="500" />

        <label>Unit : </label>
        <Select
          v-model="data.unit"
          :options="['mm', 'cm', 'in', 'px']"
          class="w-sm"
        />

        <Button label="Print" icon="pi pi-print" @click="onPrint" />

        <table border="1">
          <tr>
            <td>
              <InputText v-model.number="keyword" placeholder="Search Field" />
              <div style="height: 300px; width: 300px; overflow: scroll">
                <div
                  v-if="meta_data"
                  v-for="(f, index) in filteredFields"
                  :key="f.fieldname"
                >
                  {{ f.label }}
                  <Button label="Select" @click="onAddElement(f)" />
                </div>
              </div>
            </td>
            <td>
              {{ data }}
              <hr />
              {{ selectedElement }}
              <div
                id="print-area"
                :style="{
                  height: data.height + data.unit,
                  width: data.width + data.unit,
                  border: '1px solid red',
                  overflow: 'hidden',
                  position: 'relative',
                }"
              >
                <div
                  v-if="isPrint"
                  v-for="(e, index) in data.elements"
                  :key="e.fieldname + index"
                  :style="{
                    position: 'absolute',
                    left: e.x + 'px',
                    top: e.y + 'px',
                    height: e.height + 'px',
                    width: e.width + 'px',
                    overflow: 'hidden',
                    fontSize:e.font_size + 'px',
                    justifyContent: e.justify_content,
                    alignItems: e.align_items,
                    display:'flex',
                    transform: `rotate(${e.rotation}deg)`,
                    lineHeight:'12px'
                  }"
                >
                  <template v-if="e.fieldtype == 'Barcode'">
                    <div :style="{ height: e.height + 'px',width: e.width + 'px',
                    overflow: 'hidden'}">
                      <img style="width: 100%;height: 100%"  :src="`http://bwipjs-api.metafloor.com/?bcid=code128&text=`+doc[e.fieldname]"  />
                    </div>
                  </template>
                  <template v-else>
                    <span v-if="e.fieldtype=='Currency'">
                        {{ getCurrencyAmount(doc[e.fieldname]) }} 
                      </span>
                       <span v-else> {{ doc[e.fieldname] }}</span>
                  </template>
                </div>
                <DraggableResizableVue
                  v-else
                  v-for="(e, idx) in data.elements"
                  :key="e.fieldname + idx"
                  v-model:x="e.x"
                  v-model:y="e.y"
                  v-model:h="e.height"
                  v-model:w="e.width"
                  v-model:active="e.isActive"
                  @click="onSelectElement(e)"
                  :style="[
                    textStyle,
                    {
                      fontSize: e.font_size + 'px',
                      fontFamily: e.font_type.value,
                    },
                  ]"
                >
                  <div
                    :style="{
                      transform: `rotate(${e.rotation}deg)`,
                      height: '100%',
                      width: '100%',
                    }"
                  >
                    <template v-if="e.fieldtype === 'Barcode'">
                      <div style="height: 100%; width: 100%; overflow: hidden">
                        <img style="width: 100%; height: 100%" :src="`http://bwipjs-api.metafloor.com/?bcid=code128&text=`+doc[e.fieldname]" />
                      </div>
                    </template>
                    <template v-else>
                      <div
                       :style="{
                          overflow: 'hidden',
                          height: '100%',
                          justifyContent: e.justify_content,
                          alignItems: e.align_items,
                          display:'flex',
                          fontSize:e.font_size + 'px',
                       }
                        "
                      >
                      <span v-if="e.fieldtype=='Currency'">
                        {{ getCurrencyAmount(doc[e.fieldname]) }} 
                      </span>
                       <span v-else> {{ doc[e.fieldname] }}</span>
                      </div>
                    </template>
                  </div>
                </DraggableResizableVue>
              </div>
              <div v-if="selectedElement">
                <label>Element Property:</label>
                <hr />
                <label>Font Size:</label>
                <InputText v-model.number="selectedElement.font_size" />
                <Slider
                  v-model="selectedElement.font_size"
                  class="w-3 my-3"
                  :min="8"
                  :max="36"
                />

                <div class="field">
                  <label for="fontFamily">Font Type:</label>
                  <Dropdown
                    v-model="selectedElement.font_type"
                    :options="fontFamily"
                    optionLabel="label"
                    placeholder="Select a Font"
                    class="input-dropdown mx-2 w-auto"
                  />
                </div>

                <div>
                  Text Rotation :
                  <Knob
                    v-model="selectedElement.rotation"
                    :max="360"
                    size="60"
                    :step="90"
                  />
                </div>

                <div>
                  <label for="bold">Bold:</label>
                  <input type="checkbox" id="bold" v-model="isBold" />
                  <label for="italic">Italic:</label>
                  <input type="checkbox" id="italic" v-model="isItalic" />
                </div>

                <label>Data Type:</label>
                <Select
                  v-model="selectedElement.fieldtype"
                  :options="['Data', 'Currency', 'Barcode', 'Int', 'Float']"
                  class="w-full md:w-56"
                />
text align
                <Select
                  v-model="selectedElement.justify_content"
                  :options="['center', 'left', 'right']"
                  class="w-full md:w-56"
                />
                
 align item
                <Select
                  v-model="selectedElement.align_items"
                  :options="['center', 'start', 'end']"
                  class="w-full md:w-56"
                />


                <Button label="Delete" @click="onDelete" />
              </div>
            </td>
          </tr>
        </table>
      </Fieldset>
    </div>
  </div>
 
  <Select v-model="templateName" editable :options="templates" optionLabel="template_name" @change="onSelectTemplate" optionValue="template_name" placeholder="Select Template" class="w-full md:w-56" />
  <Checkbox v-model="isDefault" :binary="true" :trueValue="1" :falseValue = "0"  /> Default
  
  <Button  :loading="loading" @click="SaveTemplate">Save</Button>

</template>

<script setup>
import { onMounted, ref, computed,createUpdateDoc,getDocList } from "@/plugin";

import Slider from "primevue/slider";
import Select from "primevue/select";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Knob from "primevue/knob";
import Button from "primevue/button";
import Fieldset from "primevue/fieldset";
import Dropdown from "primevue/dropdown";
import DraggableResizableVue from "draggable-resizable-vue3";
import { FrappeApp } from "frappe-js-sdk";
import { useRoute } from 'vue-router';
import Checkbox from 'primevue/checkbox';

import { useToast } from 'primevue/usetoast';
 
const toast = useToast();


const loading = ref(false)
const route = useRoute();
const frappe = new FrappeApp();
const db = frappe.db();
const call = frappe.call();
const keyword = ref("");
const templateName = ref("Default Template")
const isDefault = ref(0)
const data = ref({
  height: 94,
  width: 132,
  unit: "px",
  elements: [],
});
const productCode = computed(() => route.query.product_code);
const doctype = computed(() => route.query.doctype);
const meta_data = ref({});
const doc = ref({});
const selectedElement = ref(null);
const isPrint = ref(false);
const templates = ref([{template_name:"Default Template"},{template_name:"Template Name 2"}])
const filteredFields = computed(() => {
  return meta_data.value?.fields?.filter(
    (r) =>
      r.hidden === 0 &&
      r.fieldtype !== "Check" &&
      r.fieldtype !== "Tab Break" &&
      r.label?.toLowerCase().includes(keyword.value.toLowerCase())
  );
});

const isBold = ref(false);
const isItalic = ref(false);

const textStyle = computed(() => ({
  fontWeight: isBold.value ? "bold" : "normal",
  fontStyle: isItalic.value ? "italic" : "normal",
}));

function getCurrencyAmount(amount) {
  if (window.parent.frappe) {


    const text = window.parent.frappe.format(amount, { "fieldtype": "Currency" })

    const parser = new DOMParser();
    const doc = parser.parseFromString(text, 'text/html');

    return doc.querySelector('div').textContent.trim();


  }
  return amount



}
const fontFamily = ref([
  { label: "Arial", value: "Arial, sans-serif" },
  { label: "Courier New", value: "'Courier New', monospace" },
  { label: "Lucida Sans", value: "'Lucida Sans', sans-serif" },
  { label: "Verdana", value: "Verdana, sans-serif" },
]);

function onAddElement(f) {
  data.value.elements.push({
    fieldname: f.fieldname,
    fieldtype: f.fieldtype,
    x: 0,
    y: 0,
    width: 75,
    height: 25,
    font_size: 14,
    font_type: fontFamily.value[0],
    rotation: 0,
    justify_content:'center',
    align_items:'center'
  });
}

 
function onDelete() {
  const index = data.value.elements.indexOf(selectedElement.value);
  if (index > -1) {
    data.value.elements.splice(index, 1);
  }
  selectedElement.value = null;
}

function onSelectElement(e) {
  selectedElement.value = e;
}

function onPrint() {
 
  isPrint.value = true;
  setTimeout(() => {
    const divContents = document.querySelector("#print-area").outerHTML;

    const printWindow = window.open("", "", "height=750px, width=750px");

    printWindow.document.write("<html><head>");
    printWindow.document.write(`
      <style>
        @media print {
          * body{
            margin: 0;
            padding: 0;
            display:flex;
            justify-content: center;
            align-items:center;
          }
        }
      </style>
    `);
    printWindow.document.write("</head><body>");
    printWindow.document.write(divContents);
    printWindow.document.write("</body></html>");

    setTimeout(() => {
      printWindow.document.close();
      printWindow.print();
      isPrint.value = false;
    }, 1000);
  }, 1000);
}

function SaveTemplate(){
  loading.value = true
  let name = templates.value.find(r=>r.template_name == templateName.value)
  if (name){
    name = name.name
  }else {
    name = undefined
  }
  createUpdateDoc('Barcode Template', {
    name:name,
    template_name: templateName.value,
    document_type:doctype.value,
    template:data.value,
    is_default:isDefault.value,
  })
    .then((doc) => {
      loading.value = false
      getTemplates(true)

      toast.add({ severity: 'success', summary: "Save Template", detail: 'Save barcode template successfully', life: 3000 })
})
    .catch((error) => {
      loading.value = false
    });
    
}

function onSelectTemplate(selected){

  
      let default_template = templates.value.find(r=>r.template_name ==selected.value)
      if (!default_template){
        default_template = JSON.parse(templates.value[0].template)
      }
      
     if (default_template){
      isDefault.value = default_template.is_default
      data.value = JSON.parse(default_template.template)
     }

       
}

function getTemplates(skipGetDefault=false){
  getDocList("Barcode Template",{
    filters: [['document_type', '=', doctype.value]],
    fields:["template_name","name","is_default","template"]
  }).then(result=>{
    templates.value = result
    if(!skipGetDefault){
    if(templates.value){
      let default_template = templates.value.find(r=>r.is_default ==1)
      

      if (!default_template){
        default_template = JSON.parse(templates.value[0].template)
      }
      
     if (default_template){
     
      templateName.value = default_template.template_name
      isDefault.value = default_template.is_default
      data.value = JSON.parse(default_template.template)
     }
      
    }
     
    }
  })
}
onMounted(() => {
  call
    .get("epos_restaurant_2023.api.api.get_meta", {
      doctype: doctype.value,
    })
    .then((result) => {
      meta_data.value = result.message;
    });
    
  db.getDoc("Product", productCode.value).then((result) => {
    doc.value = result;
    getTemplates()
  });

  
  

});
</script>

<style scoped>
#print-area {
  border: 1px solid red;
}
</style>
