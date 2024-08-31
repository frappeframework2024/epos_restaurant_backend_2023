<template>
  <div class="grid p-3">
    <div
      class="flex-1 w-full flex align-items-center justify-content-center m-3"
    >
{{ productCode }}

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
                  }"
                >
                  <template v-if="e.fieldtype == 'Barcode'">
                    <div :style="{ height: e.height + 'px',width: e.width + 'px',
                    overflow: 'hidden'}">
                      <img style="width: 100%;height: 100%" :src="url" />
                    </div>
                  </template>
                  <template v-else>
                    {{ doc[e.fieldname] }}
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
                        <img style="width: 100%; height: 100%" :src="url" />
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
                        {{ doc[e.fieldname] }}
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

                <label>Barcode Type:</label>
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
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
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

const route = useRoute();
const frappe = new FrappeApp();
const db = frappe.db();
const call = frappe.call();
const keyword = ref("");
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

const url = computed(() => {
  const text = doc.value[selectedElement.value.fieldname] || "";

  return `http://bwipjs-api.metafloor.com/?bcid=code128&text=${encodeURIComponent(
    text
  )}`;
});

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
  });
});
</script>

<style scoped>
#print-area {
  border: 1px solid red;
}
</style>
