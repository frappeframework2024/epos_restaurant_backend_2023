<template>
    <!-- {{data.variant}} -->
    <template v-if="data?.variant" v-for="item in data.variant">
       
        <h1 v-if="item?.variants.length > 0" class="mb-2 font-medium">{{ item.variant_name }}</h1>
        <ul class="d-flex gap-2">
            <li @click="getItemsVariant(i)" v-if="item?.variants" v-for="i in item.variants">{{ i.variant }}</li>
        </ul>
        <br/>
    </template>


</template>
<script setup>
   import {ref,inject, onMounted } from "@/plugin"
   const dialogRef = inject('dialogRef');
   const  data = ref()
    onMounted(()=>{
        data.value = dialogRef.value.data
    })

    function getItemsVariant(i) {
        console.log(i)
    }
</script>
<style scoped>
    ul li {
        border: 1px solid #ccc;
        padding: 5px;
        border-radius: 5px;
    }
    ul li.active {
        background: #000;
        color: #fff;
    }
</style>