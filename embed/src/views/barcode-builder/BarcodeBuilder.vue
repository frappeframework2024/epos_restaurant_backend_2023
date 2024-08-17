<template>
  <h1>barcode builder sss hello</h1>

  <input type="number" v-model="setting.height" />
  <input type="number" v-model="setting.width" />
  <input type="text" v-model="setting.product_code" />

  <div
    class="barcode-container"
    :style="{ height: setting.height + 'px', width: setting.width + 'px' }"
  >
    {{ setting.product_name_en }}

    <img
      style="width: 100%"
      :src="
        'https://barcodeapi.org/api/code128/' +
        setting.product_code +
        setting.price
      "
    />
  </div>
  {{ setting.price }}
  {{ setting.company }}
  <button @click="onPrint">Print</button>
</template>
<script setup>
import { ref } from "vue";
const setting = ref({
  height: 100,
  width: 170,
  product_code: "12548728",
  product_name_en: "Worman",
  price: "$50.75",
  company: "Angkor Shop",
});

function onPrint() {
  const divContents = document.querySelector(".barcode-container").outerHTML;
  var a = window.open("", "", "height=600, width=800");
  a.document.write("<html>");
  a.document.write(divContents);
  a.document.write("</body></html>");
  setTimeout(function () {
    a.document.close();
    a.print();
  }, 1000);
}
</script>
<style scoped>
.barcode-container {
  border: solid 1px red;
  text-align: center;
}
</style>
