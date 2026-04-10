<template>
    <div class="h-full">
        <div  class="h-full flex-col flex">
            <div class="mb-20" :class="mobile == true ? '' : 'overflow-auto'">
                <div class="pt-2">
                    <ComProductSearch :small="true" />
                    <ComMenu /> 
                </div>
            </div>
            <SaleOrderSammary/>
        </div>
    </div>
</template>
<script setup>
import { useDisplay } from 'vuetify';
const { mobile } = useDisplay();
import ComMenu from '../ComMenu.vue';
import ComProductSearch from '../ComProductSearch.vue';
import SaleOrderSammary from './ComSmallSaleOrderSammary.vue'; 

</script> 