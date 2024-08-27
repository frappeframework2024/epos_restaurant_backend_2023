<template>
  <div>
    <input
      v-model="barcode_api.type"
      placeholder="Enter barcode type (e.g., code128)"
    />
    <input v-model="barcode_api.text" placeholder="Enter text for barcode" />
    <input
      v-model.number="barcode_api.scale"
      type="number"
      placeholder="Enter scale (e.g., 3)"
    />
    <input
      v-model="barcode_api.bar_rotate"
      placeholder="Enter rotation (e.g., N)"
    />
    <label>
      <input type="checkbox" v-model="barcode_api.include_text" />
      Include Text
    </label>

    <img :src="barcodeUrl" alt="Barcoded" />

    <router-view />
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

// Reactive data for barcode parameters
const barcode_api = ref({
  type: "code128",
  text: "",
  bar_rotate: "N",
  scale: 3,
  include_text: false,
});

// Computed property to generate the barcode URL dynamically
const barcodeUrl = computed(() => {
  const encodedText = encodeURIComponent(barcode_api.value.text);
  const includeTextParam = barcode_api.value.include_text ? "&includetext" : "";
  return `http://bwipjs-api.metafloor.com/?bcid=${barcode_api.value.type}&text=${encodedText}&scale=${barcode_api.value.scale}&rotate=${barcode_api.value.bar_rotate}${includeTextParam}`;
});
</script>
