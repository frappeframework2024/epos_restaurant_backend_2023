<template>
    <div>
        <div class="grid">
            <div class="col-8">
                <h2>Coupon List</h2>
            </div>
            <div class="col-4">
                <Button @click="onAddCoupon">
                    Sale Coupon
                </Button>
            </div>
        </div>
        <div>
            <ComSaleCouponList/>
        </div>
    </div>
</template>
<script setup>
    import ComAddSaleCoupon from './components/ComAddSaleCoupon.vue';
    import Button from 'primevue/button';
    import { useDialog } from 'primevue/usedialog';

    const dialog = useDialog();
    import ComSaleCouponList from './components/ComSaleCouponList.vue';
    function onAddCoupon(){
        dialog.open(ComAddSaleCoupon, {props: {
            header: 'Product List',
            style: {
                width: '50vw',
            },
            breakpoints:{
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        }});
    }
</script>
<style>
    
</style>