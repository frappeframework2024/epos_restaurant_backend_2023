<template>
    <ComSaleCouponList/>
</template>
<script setup>
    import ComAddSaleCoupon from './components/ComAddSaleCoupon.vue';
    import Button from 'primevue/button';
    import { useDialog } from 'primevue/usedialog';

    const dialog = useDialog();
    import ComSaleCouponList from './components/ComSaleCouponList.vue';
    
</script>