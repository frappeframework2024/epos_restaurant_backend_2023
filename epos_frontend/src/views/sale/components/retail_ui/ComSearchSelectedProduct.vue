<template>

    <div style="height:calc(-241px + 100vh);" class="overflow-auto"> 
            <div>
                <div class="border p-3 rounded-md">
                    <div
                        class="product-image rounded-md overflow-hidden" style="width: 300px;">
                        <img class="h-100 w-100" style="object-fit: cover;"
                            src="https://images.unsplash.com/photo-1682687220777-2c60708d6889?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDF8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" />
                    </div>
                    <br />
                    <div class="text-center">
                        <strong>001</strong>
                        <br />
                        <strong>Spegati</strong>
                    </div>
                </div> 
                <div class="border p-2 rounded-md mt-3">
                    <ComLabelValue label="Quantity" :value="sale?.selected_sale_product?.quantity" />
                    <ComLabelValue label="Selling Price">
                        <CurrencyFormat :value="sale?.selected_sale_product?.price" />
                    </ComLabelValue>
                    <ComLabelValue label="Regular Price">
                        <CurrencyFormat :value="sale?.selected_sale_product?.regular_price" />
                    </ComLabelValue> 
                    <ComLabelValue label="Regular Price">
                        <CurrencyFormat :value="sale?.selected_sale_product?.regular_price" />
                    </ComLabelValue> 
                    <ComLabelValue label="Regular Price">
                        <CurrencyFormat :value="sale?.selected_sale_product?.regular_price" />
                    </ComLabelValue> 
                    <ComLabelValue label="Regular Price">
                        <CurrencyFormat :value="sale?.selected_sale_product?.regular_price" />
                    </ComLabelValue> 
                </div>
            </div> 

        <!-- <template v-else> 
            <div class="flex h-100 w-100 justify-center items-center">
                <div class="text-center n-data-str">
                    <v-icon icon="mdi-database-remove" color="red" size="large"></v-icon><br />
                    No Product Selected
                </div>
            </div> 
        </template> -->
    </div>




</template>

<script setup>
import { inject, ref, watch, onMounted, i18n } from '@/plugin';
import ComLabelValue from "@/views/sale/components/retail_ui/ComLabelValue.vue"

const { t: $t } = i18n.global;
const sale = inject("$sale") 
</script>

<style scoped>
.n-data-str {
    font-size: 30px;
}
</style>