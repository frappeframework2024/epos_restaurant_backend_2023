<template>select ed product info

{{ sale?.selected_sale_product }}
<hr/>
<h1>Product Info</h1>
{{ sale?.selected_product }}
</template>
<script setup>
    import { inject,ref,watch } from '@/plugin';
    const sale = inject("$sale")

</script>