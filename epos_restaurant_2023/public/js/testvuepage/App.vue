
<template>
  <div>
	<h3>{{ dynamicMessage }}</h3>
    <h4>168 editing at epos_restaurant_2023/public/js/testvuepage/App.vue</h4>
  </div>
</template>

<script setup>
import { ref } from "vue"

const dynamicMessage = ref("Hello from App.vue")
</script>