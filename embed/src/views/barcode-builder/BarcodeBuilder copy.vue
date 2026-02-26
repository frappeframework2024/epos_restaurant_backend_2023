<template>
  height
  <InputText v-model.number="data.height" />
  <Slider v-model="data.height" :min="50" :max="500" class="w-56 mb-4" />
  width
  <InputText v-model.number="data.width" />
  <Slider v-model="data.width" class="w-56" :min="50" :max="500" />

  <hr />
  Unit
  <Select
    v-model="data.unit"
    :options="['mm', 'cm', 'in', 'px']"
    class="w-full md:w-56"
  />

  <Button label="Print" icon="pi pi-print" @click="onPrint" />

  <table>
    <tr>
      <td>
        <InputText v-model.number="keyword" placehoder="Search Field" />
        <div style="height: 300px; width: 300px; overflow: scroll">
          <div
            v-if="meta_data"
            v-for="(f, index) in meta_data?.fields?.filter(
              (r) =>
                r.hidden == 0 &&
                r.fieldtype != 'Check' &&
                r.fieldtype != 'Tab Break' &&
                r.label?.toLowerCase().includes(keyword.toLowerCase())
            )"
            :key="index"
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
            :key="index"
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
              <img
                :src="`http://bwipjs-api.metafloor.com/?bcid=code128&text=${
                  doc[e.fieldname]
                }`"
              />
            </template>
            <template v-else>
              {{ doc[e.fieldname] }}
            </template>
          </div>
          <draggable-resizable-vue
            v-else
            v-for="(e, idx) in data.elements"
            :key="idx"
            v-model:x="e.x"
            v-model:y="e.y"
            v-model:h="e.height"
            v-model:w="e.width"
            v-model:active="e.isActive"
            @click="onSelectElement(e)"
            :style="{ fontSize: e.font_size + 'px' }"
          >
            <template v-if="e.fieldtype == 'Barcode'">
              <img
                :src="`http://bwipjs-api.metafloor.com/?bcid=code128&text=${
                  doc[e.fieldname]
                }`"
              />
            </template>
            <template v-else>
              {{ doc[e.fieldname] }}
            </template>
          </draggable-resizable-vue>
        </div>
        <div v-if="selectedElement">
          element property
          <hr />
          font size:
          <InputText v-model.number="selectedElement.font_size" />
          <Slider
            v-model="selectedElement.font_size"
            class="w-56"
            :min="8"
            :max="20"
          />
          barcode type:
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
import { onMounted, ref } from "vue";
import Slider from "primevue/slider";
import Select from "primevue/select";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { FrappeApp } from "frappe-js-sdk";
import DraggableResizableVue from "draggable-resizable-vue3";

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

const selectedElement = ref();

const isPrint = ref(false);

function onAddElement(f) {
  data.value.elements.push({
    fieldname: f.fieldname,
    fieldtype: f.fieldtype,
    x: 0,
    y: 0,
    width: 75,
    height: 25,
    font_size: 14,
  });
}

function onDelete() {
  isPrint.value = true;
  alert("delete");
}
function onSelectElement(e) {
  selectedElement.value = e;
}
function onPrint() {
  isPrint.value = true;
  setTimeout(() => {
    const divContents = document.querySelector("#print-area").outerHTML;
    
    // Open a new window with custom height and width
    const printWindow = window.open("", "", "height=750px, width=750px");

    // Write HTML structure
    printWindow.document.write("<html><head>");
    printWindow.document.write(`
      <style>
        @media print {
          * {
            margin: 0;
            pading: 0;
            background:blue;
          }
            
        }
      </style>
    `);

    printWindow.document.write("</head><body>");
    printWindow.document.write(divContents);
    printWindow.document.write("</body></html>");

    // Close the document and trigger printing
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
/*#print-area {
  border: 1px solid red;
}*/
</style>
