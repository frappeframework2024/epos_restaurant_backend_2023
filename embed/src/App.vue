<template>
  <div>
    <input type="number" v-model="pixel" placeholder="Enter pixels" />
    <p>{{ pixel }} pixels is approximately {{ centimeters.toFixed(2) }} cm</p>
  </div>

  <router-view />
</template>

<script setup>
import { ref, computed } from "vue";

const pixel = ref("");
function pxToCm(px) {
  const ppi = 96; // pixels per inch (standard screen resolution)
  const inches = px / ppi; // convert pixels to inches
  const cm = inches * 2.54; // convert inches to centimeters
  return cm;
}

const centimeters = computed(() => pxToCm(pixel.value));
</script>
