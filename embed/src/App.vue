<template>
  <div>
  
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
