<template>
  <div class="grid p-3 print-barcode">
    <div class="flex-1 w-full flex align-items-center justify-content-center m-3">


      <Fieldset class="w-full m-2" :legend="preview_title">
        <div class="flex justify-content-between">
          <div>

            <div class="flex gap-2 align-items-center">
              <Select v-model="templateName" editable :options="templates" optionLabel="template_name"
                @change="onSelectTemplate" optionValue="template_name" placeholder="Select Template"
                class="w-full md:w-56" />
              <Checkbox v-model="isDefault" :binary="true" :trueValue="1" :falseValue="0" />
              <p>Default</p>
            </div>

            <Button :loading="loading" @click="SaveTemplate">Save</Button>
          </div>
          <div class="col-6 text-right">
            <div class="flex justify-content-end">
             
              <div class="mx-2">
                <Select empty v-if="doc.product_price && route.query.doctype=='Product'" v-model="selectedBarcode"  :options="doc.product_price" 
                @change="onProductPriceSelected"  placeholder="Barcode"
                class="w-full md:w-56 text-left" >
                <template #option="slotProps">
                  <div>
                    <div class="text-right">
                      <span>{{ slotProps.option.price_rule }} / {{ slotProps.option.unit }}</span>
                      <div class="text-sm text-color-secondary ml-1 border-top-1">{{ slotProps.option.barcode }} / {{ getCurrencyAmount(slotProps.option.price) }}</div>
                    </div>
                     
                      
                  </div>
              </template>
              <template #value="{value}">
                <div class="text-right">
                  <span>{{ value.price_rule }} / {{ value.unit }}</span>
                  <div class="text-sm text-color-secondary ml-1 border-top-1">{{ value.barcode }} / {{ getCurrencyAmount(value.price) }}</div>
                </div>
                  
              </template>
              </Select>
              </div>
            <Button label="Print" icon="pi pi-print" @click="onPrint" />
            </div>
            
          </div>
        </div>
        <br />
        <table style="width: 100%;">
          <tr>
            <td class="p-2" style="border-color: #ccc;vertical-align: top;max-width: 132px;min-width: 132px;">
              <div style="border: 1px solid #ccc;background: rgb(204 204 204 / 20%)" class="border-round p-2">
                <div>
                  <InputText class="w-full" v-model.number="keyword" placeholder="Search Field" />
                </div><br />
                <div style="height: 300px; width: 100%; overflow: auto">
                  <template v-if="meta_data" v-for="(f, index) in filteredFields" :key="f.fieldname">
                    <div class=" p-1 field-options flex justify-content-between">
                      {{ f.label }}
                        <Button style="height: 10px;font-size: 10px;" label="Select" @click="onAddElement(f)" />
                      
                    </div>

                  </template>

                </div>
              </div>
            </td>
            <td style="border-color: #ccc;vertical-align: top;">
              <!-- {{ doc.product_price }} -->
              <div class="flex justify-content-center h-full w-full align-items-center" style="min-height:15rem">
                <div id="print-area" :style="{
                  height: data.height + data.unit,
                  width: data.width + data.unit,
                  border: '1px solid red',
                  overflow: 'hidden',
                  position: 'relative',
                }">
                  <div v-if="isPrint" v-for="(e, index) in data.elements" :key="e.fieldname + index" :style="{
                    position: 'absolute',
                    left: e.x + 'px',
                    top: e.y + 'px',
                    height: e.height + 'px',
                    width: e.width + 'px',
                    overflow: 'hidden',
                    fontSize: e.font_size + 'px',
                    justifyContent: e.justify_content,
                    alignItems: e.align_items,
                    display: 'flex',
                    transform: `rotate(${e.rotation}deg)`,
                    lineHeight: '12px'
                  }">
                    <template v-if="e.fieldtype == 'Barcode'">
                      <div :style="{
                        height: e.height + 'px', width: e.width + 'px',
                        overflow: 'hidden'
                      }">
                        <img style="width: 100%;height: 100%"
                          :src="`http://bwipjs-api.metafloor.com/?bcid=code128&text=` + doc[e.fieldname]" />
                      </div>
                    </template>
                    <template v-else>
                      <span v-if="e.fieldtype == 'Currency'">
                        {{ getCurrencyAmount(doc[e.fieldname]) }}
                      </span>
                      <span v-else> {{ ( getValueFromPath(doc, e.fieldname)) }}</span>
                    </template>
                  </div>

                  <DraggableResizableVue v-else v-for="(e, idx) in data.elements" :key="e.fieldname + idx"
                    v-model:x="e.x" v-model:y="e.y" v-model:h="e.height" v-model:w="e.width" v-model:active="e.isActive"
                    @click="onSelectElement(e)" :style="[
                      textStyle,
                      {
                        fontSize: e.font_size + 'px',
                        fontFamily: e.font_type.value,
                      },
                    ]">
                    <div :style="{
                      transform: `rotate(${e.rotation}deg)`,
                      height: '100%',
                      width: '100%',
                    }">
                      <template v-if="e.fieldtype === 'Barcode'">
                        <div style="height: 100%; width: 100%; overflow: hidden">
                          <img style="width: 100%; height: 100%"
                            :src="`http://bwipjs-api.metafloor.com/?bcid=code128&text=` + doc[e.fieldname]" />
                        </div>
                      </template>
                      <template v-else>
                        <div :style="{
                          overflow: 'hidden',
                          height: '100%',
                          justifyContent: e.justify_content,
                          alignItems: e.align_items,
                          display: 'flex',
                          fontSize: e.font_size + 'px',
                        }
                          ">
                          <span v-if="e.fieldtype == 'Currency'">
                            {{ getCurrencyAmount(getValueFromPath(doc,e.fieldname)) }}
                          </span>
                          <span v-else> {{ getValueFromPath(doc, e.fieldname) }}</span>
                        </div>
                      </template>
                    </div>
                  </DraggableResizableVue>

                </div>
              </div>
              <div class="border-bottom-1 mt-5" style="border-color: #ccc;"></div>
              <br />
              <div style="border: 1px solid rgb(204, 204, 204); background: rgba(204, 204, 204, 0.2);"
                class="border-round p-2">
                <label>Height : </label>
                <InputText v-model.number="data.height" class="" />
                <Slider v-model="data.height" :min="50" :max="500" class="my-3" />

                <label>Width : </label>
                <InputText v-model.number="data.width" class="" />
                <Slider v-model="data.width" class="my-3" :min="50" :max="500" />

                <label>Unit : </label>
                <Select v-model="data.unit" :options="['mm', 'cm', 'in', 'px']" class="w-sm" />
              </div>
            </td>
            <td v-if="selectedElement"
              style="border-color: #ccc;vertical-align: top;max-width: 132px;min-width: 132px;">
              <div style="border: 1px solid #ccc;background: rgb(204 204 204 / 20%);" class="border-round p-2">
                <h3>Element Property:</h3>
                <div class="">
                  <div>
                    <label>Font Size: </label>
                    <InputText v-model.number="selectedElement.font_size" />
                    <Slider v-model="selectedElement.font_size" class="w-3 my-3" :min="8" :max="36" />

                    <div class="field">
                      <label for="fontFamily">Font Type:</label>
                      <Dropdown v-model="selectedElement.font_type" :options="fontFamily" optionLabel="label"
                        placeholder="Select a Font" class="input-dropdown mx-2 w-auto" />
                    </div>

                    <div>
                      Text Rotation :
                      <Knob v-model="selectedElement.rotation" :max="360" size="60" :step="90" />
                    </div>
                  </div>
                  <div>

                    <div class="flex gap-2">
                      <label for="bold">Bold:</label>
                      <input type="checkbox" id="bold" v-model="isBold" />
                      <label for="italic">Italic:</label>
                      <input type="checkbox" id="italic" v-model="isItalic" />
                    </div>
                    <div>
                      <label>Data Type:</label>
                      <Select v-model="selectedElement.fieldtype"
                        :options="['Data', 'Currency', 'Barcode', 'Int', 'Float']" class="w-full md:w-56" />
                    </div>
                    <div>text align</div>
                    <Select v-model="selectedElement.justify_content" :options="['center', 'left', 'right']"
                      class="w-full md:w-56" />

                    <div>
                      align item
                      <Select v-model="selectedElement.align_items" :options="['center', 'start', 'end']"
                        class="w-full md:w-56" />
                    </div>

                    <br />
                    <Button label="Delete" @click="onDelete" />
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </table>
      </Fieldset>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, createUpdateDoc, getDocList } from "@/plugin";

import Slider from "primevue/slider";
import Select from "primevue/select";
import InputText from "primevue/inputtext";
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
const selectedBarcode = ref({})
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
const preview_title = ref("Preview");
const doc = ref({});
const selectedElement = ref(null);
const isPrint = ref(false);
const templates = ref([{ template_name: "Default Template" }, { template_name: "Template Name 2" }])
const filteredFields = computed(() => {
  return meta_data.value?.fields?.filter(
    (r) =>
      r.hidden === 0 &&
      r.fieldtype !== "Check" &&
      r.fieldtype !== "Tab Break" &&
      r.fieldtype !== "Section Break" &&
      r.fieldtype !== "Column Break" &&
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
    key: f.fieldname,
    fieldname: f.fieldname,
    fieldtype: f.fieldtype,
    x: 0,
    y: 0,
    width: 75,
    height: 25,
    font_size: 14,
    font_type: fontFamily.value[0],
    rotation: 0,
    justify_content: 'center',
    align_items: 'center'
  });
}
function onAddBarcodeElement(f, p, idx) {
  data.value.elements.push({
    fieldname: `${p.parentfield}[${idx}].barcode`,
    fieldtype: "Data",
    child_doc: 1,
    x: 0,
    y: 0,
    width: 75,
    height: 25,
    font_size: 14,
    font_type: fontFamily.value[0],
    rotation: 0,
    justify_content: 'center',
    align_items: 'center'
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
    let divContents = document.querySelector("#print-area");
    divContents.style.borderStyle  = 'none'
    divContents = divContents.outerHTML
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
            border:0px
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

function SaveTemplate() {
  loading.value = true
  data.value.elements.forEach((r)=>{
    r.filename = r.key
  })
  let name = templates.value.find(r => r.template_name == templateName.value)
  if (name) {
    name = name.name
  } else {
    name = undefined
  }
  createUpdateDoc('Barcode Template', {
    name: name,
    template_name: templateName.value,
    document_type: doctype.value,
    template: data.value,
    is_default: isDefault.value,
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

function getValueFromPath(obj, path) {
  const value = path.split('.').reduce((acc, part) => {
    if (acc === undefined || acc === null) {
      const index = data.value.elements.findIndex(el => el.fieldname === path);
      if (index !== -1) {
        data.value.elements.splice(index, 1);
      }
    };
    let match = part.match(/(\w+)\[(\d+)\]/);
    if (match) {
      let arr = acc[match[1]];
      let index = parseInt(match[2]);
      acc = Array.isArray(arr) && arr.length > index ? arr[index] : undefined
      // acc = acc[match[1]][parseInt(match[2])];
    } else {
      acc = acc[part];
    }
    return acc;
  }, obj);

  return value
}

function onProductPriceSelected(selected) {
  console.log("selected ",selected)
  console.log("product_price",doc.value.product_price[0])
  const selectedIdx = doc.value.product_price.findIndex(item => item.barcode === selected.value.barcode);
  console.log("selectedIdx",selectedIdx)
  data.value.elements.forEach(ele => {
    if (ele.key == 'product_code'){
      ele.fieldname = `${selected.value.parentfield}[${selectedIdx}].barcode`
    }
    if (ele.key == 'price'){
      ele.fieldname =  `${selected.value.parentfield}[${selectedIdx}].price`
    }
    if (ele.key == 'unit'){
      ele.fieldname =  `${selected.value.parentfield}[${selectedIdx}].unit`
    }
  }); 
  console.log("`${selected.value.parentfield}[${selectedIdx}].price`",`${selected.value.parentfield}[${selectedIdx}].price`)
  console.log("data.value1",getValueFromPath(doc.value,`${selected.value.parentfield}[${selectedIdx}].price`))
  console.log("data",data.value)
}


function onSelectTemplate(selected) {
  let default_template = templates.value.find(r => r.template_name == selected.value)
  if (!default_template) {
    default_template = JSON.parse(templates.value[0].template)
  }
  if (default_template) {
    isDefault.value = default_template.is_default
    data.value = JSON.parse(default_template.template)
  }
}

function getTemplates(skipGetDefault = false) {
  getDocList("Barcode Template", {
    filters: [['document_type', '=', doctype.value]],
    fields: ["template_name", "name", "is_default", "template"]
  }).then(result => {
    templates.value = result
    if (!skipGetDefault) {
      if (templates.value) {
        let default_template = templates.value.find(r => r.is_default == 1)


        if (!default_template) {
          default_template = JSON.parse(templates.value[0].template)
        }

        if (default_template) {

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
    if (doc.value.doctype=="Product"){
      preview_title.value = "Preview " + doc.value.product_name_en
      if (doc.value.product_price.length > 0){
        selectedBarcode.value = doc.value.product_price[0]
      }
    }
    
    getTemplates()
  });




});
</script>

<style scoped>
/* #print-area {
  border: 1px solid red;
} */

.print-barcode table {
  border-collapse: collapse;
  width: 100%;
}

.print-barcode th,
.print-barcode td {
  border: 1px solid black;
  padding: 8px;
  text-align: left;
}

.print-barcode th {
  background-color: #f2f2f2;
}
.field-options{
  border-radius: 3px;
}
.field-options:hover{
  background-color: #e7e7e7;
  transition-duration: 250ms;
}
</style>
