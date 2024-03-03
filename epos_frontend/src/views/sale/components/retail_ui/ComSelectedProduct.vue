<template>
    <!-- select ed product info -->
    <!-- {{ sale?.selected_sale_product }} -->
    <div>
        <template v-if="sale?.selected_sale_product">
            <div style="height:calc(-321px + 100vh);overflow-y:auto">
                <div class="border p-3 rounded-md">
                    <div v-if="sale?.selected_sale_product?.product_photo"
                        class="product-image rounded-md overflow-hidden " style="height: 200px;">
                        <img class="h-100 w-100" style="object-fit: cover;"
                            :src="sale?.selected_sale_product?.product_photo" />
                    </div>
                    <br />
                    <div class="text-center">
                        <strong>{{ sale?.selected_sale_product?.product_code }} / {{
            sale?.selected_sale_product?.product_name
        }}
                            <template
                                v-if="sale?.selected_sale_product?.product_name != sale?.selected_sale_product?.product_name_kh">{{
            sale?.selected_sale_product?.product_name_kh }}
                            </template>
                        </strong>
                        <br />
                        <strong>{{ sale?.selected_sale_product?.note }}</strong>
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
                    <ComLabelValue label="Sub Total">
                        <CurrencyFormat :value="sale?.selected_sale_product?.sub_total" />
                    </ComLabelValue>
                    <ComLabelValue :label="`Discount ${sale?.selected_sale_product?.total_discount}`">
                        <CurrencyFormat :value="sale?.selected_sale_product?.total_discount" />
                    </ComLabelValue>
                    <ComLabelValue label="Total Amount">
                        <CurrencyFormat :value="sale?.selected_sale_product?.total_revenue" />
                    </ComLabelValue>
                    <h2 style="font-size: 20px">Inventory</h2>
                    <ComLabelValue label="Warehouse 1" value="10 units">
                    </ComLabelValue>
                    <ComLabelValue label="Warehouse 2" value="10 units">
                    </ComLabelValue>
                    <ComLabelValue label="Total On Hand" value="10 units">
                    </ComLabelValue>
                </div>
            </div>
        </template>

        <template v-else>
            <div style="height:calc(-355px + 100vh)">
                <div class="flex h-100 w-100 justify-center items-center">
                    <div class="text-center n-data-str">
                        <v-icon icon="mdi-database-remove" color="red" size="large"></v-icon><br />
                        No Data
                    </div>
                </div>
            </div>
        </template>
    </div>





    <!-- <hr />
    <h1>Product Info</h1> -->
    <!-- {{ sale?.selected_product }} -->
</template>

<script setup>
import { inject, ref, watch, onMounted } from '@/plugin';
import ComLabelValue from "@/views/sale/components/retail_ui/ComLabelValue.vue"
const sale = inject("$sale") 
</script>

<style scoped>
.n-data-str {
    font-size: 30px;
}
</style>