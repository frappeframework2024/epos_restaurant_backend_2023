<template>
  <div class="grid p-3">
    <div
      class="flex-1 w-full flex align-items-center justify-content-center m-3"
    >
      <Fieldset class="w-full m-2" legend="Barcode">
        <div class="field">
          <label for="fontSize">Font Size:</label>
          <InputNumber inputId="fontSize" class="input-dropdown mx-2 w-4" />
          <Slider :max="36" class="my-3 w-4" />
        </div>

        <div class="preview-controls">
          Include Text:
          <input type="checkbox" />
          Bold:
          <input type="checkbox" />

          Italic:
          <input type="checkbox" />
        </div>
      </Fieldset>

      <Fieldset class="w-full m-2" legend="Previews">
        <label>Height:</label>
        <InputText v-model.number="data.height" />
        <Slider v-model="data.height" :min="50" :max="500" class="w-4 my-3" />

        <label>Width:</label>
        <InputText v-model.number="data.width" />
        <Slider v-model="data.width" class="w-4 my-3" :min="50" :max="500" />

        <label>Unit:</label>
        <Select
          v-model="data.unit"
          :options="['mm', 'cm', 'in', 'px']"
          class="md:w-56"
        />
      </Fieldset>
    </div>
  </div>

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
            }"
          >
            <template v-if="e.fieldtype == 'Barcode'">
              <div style="height: 100%; width: 100%; overflow: hidden">
                <img style="width: 100%" :src="url" />
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
            :style="{
              fontSize: e.font_size + 'px',
              fontFamily: e.font_type.value,
            }"
          >
            <template v-if="e.fieldtype == 'Barcode'">
              <div style="height: 100%; width: 100%; overflow: hidden">
                <img style="width: 100%; height: 100%" :src="url" />
              </div>
            </template>
            <template v-else>
              <div style="overflow: hidden; height: 100%">
                {{ doc[e.fieldname] }}
              </div>
            </template>
          </DraggableResizableVue>
        </div>
        <div v-if="selectedElement">
          <label>Element Property:</label>
          <hr />
          <label>Font Size:</label>
          <InputText v-model.number="selectedElement.font_size" />
          <Slider
            v-model="selectedElement.font_size"
            class="w-56"
            :min="8"
            :max="20"
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
          <label>
            <input type="checkbox" v-model="selectedElement.include_text" />
            Include Text
          </label>
          <div>
            Text Alignment:
            <Dropdown
              v-model="selectedElement.alignX"
              :options="alignX"
              optionLabel="label"
            />
          </div>

          <div>
            Text Adjustment:
            <Dropdown
              v-model="selectedElement.alignY"
              :options="alignY"
              optionLabel="label"
            />
          </div>

          <div class="field">
            <label for="rotate">Rotate:</label>
            <Dropdown
              v-model="selectedElement.rotate"
              :options="rotate"
              optionLabel="label"
              class="input-dropdown mx-2 w-auto"
            />
          </div>

          <label>Barcode Type:</label>
          <Select
            v-model="selectedElement.fieldtype"
            :options="['Data', 'Currency', 'Barcode', 'Int', 'Float']"
            class="w-full md:w-56"
          />

          <Button label="Delete" @click="onDelete" />
        </div>
      </td>
    </tr>
  </table>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import Slider from "primevue/slider";
import Select from "primevue/select";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Button from "primevue/button";
import Fieldset from "primevue/fieldset";
import Dropdown from "primevue/dropdown";
import DraggableResizableVue from "draggable-resizable-vue3";
import { FrappeApp } from "frappe-js-sdk";

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

const fontFamily = ref([
  { label: "Arial", value: "Arial, sans-serif" },
  { label: "Courier New", value: "'Courier New', monospace" },
  { label: "Lucida Sans", value: "'Lucida Sans', sans-serif" },
  { label: "Verdana", value: "Verdana, sans-serif" },
]);

const rotate = ref([
  { label: "0°", value: "N" },
  { label: "90°", value: "R" },
  { label: "180°", value: "L" },
  { label: "270°", value: "I" },
]);

const alignX = ref([
  { label: "Left", value: "left" },
  { label: "Right", value: "right" },
  { label: "Center", value: "center" },
  { label: "Off-Right", value: "offright" },
  { label: "Off-Left", value: "offleft" },
  { label: "Justify", value: "justify" },
]);

const alignY = ref([
  { label: "Center", value: "center" },
  { label: "Below", value: "below" },
  { label: "Above", value: "above" },
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
    rotate: rotate.value[0],
    include_text: false,
    alignX: alignX.value[2],
    alignY: alignY.value[1],
  });
}

const url = computed(() => {
  if (!selectedElement.value || selectedElement.value.fieldtype !== "Barcode")
    return "";

  const text = doc.value[selectedElement.value.fieldname] || "";
  const rotate = selectedElement.value.rotate.value; // Ensure it's a string

  const includeTextParam = selectedElement.value.include_text
    ? "&includetext"
    : "";
  const textxalign = selectedElement.value.alignX.value;
  const textyalign = selectedElement.value.alignY.value;

  return `http://bwipjs-api.metafloor.com/?bcid=code128&text=${encodeURIComponent(
    text
  )}&rotate=${rotate}${includeTextParam}&textxalign=${textxalign}&textyalign=${textyalign}`;
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
          * {
            margin: 0;
            padding: 0;
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
      doctype: "Product",
    })
    .then((result) => {
      meta_data.value = result.message;
    });

  db.getDoc("Product", "36").then((result) => {
    doc.value = result;
  });
});
</script>

<style scoped>
#print-area {
  border: 1px solid red;
}
</style>
