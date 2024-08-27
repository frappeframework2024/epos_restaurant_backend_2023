<template>
height
<InputText v-model.number="data.height" />
<Slider v-model="data.height" :min="50" :max="500" class="w-56 mb-4" />
width
<InputText v-model.number="data.width" />
<Slider v-model="data.width" class="w-56" :min="50" :max="500"/>

<hr>
Unit 
<Select v-model="data.unit" :options="['mm','cm','in','px']"  class="w-full md:w-56" />

<Button label="Print" icon="pi pi-print" @click="onPrint" />
  <div id="print-area" :style="{height:data.height + data.unit, width:data.width + data.unit,border:'1px solid red',overflow:'hidden'}" >

  </div>
</template>
<script setup>
import {ref} from "vue"
import Slider from 'primevue/slider';
import Select from 'primevue/select';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { FrappeApp } from "frappe-js-sdk";

const frappe = new FrappeApp();
const db = frappe.db();

  const data = ref({
    height:94,
    width:132,
    unit:"px"
  })

  db.getDoc('Product', '36')
  .then((doc) => console.log(doc))
  .catch((error) => console.error(error));

function onPrint() {
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
  }, 1000);
}

</script>
<style scoped>
  #print-area {
    border: 1px solid red;
  }
</style>