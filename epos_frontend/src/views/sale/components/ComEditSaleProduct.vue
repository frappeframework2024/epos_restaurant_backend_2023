<template>
    <ComDialogContent :hideButtonClose="false" :loading="loading" @onOK="onOK" @onClose="onClose">
        <div class="flex flex-col lg:flex-row">
            <div v-if="data?.photo" class="flex">
                <v-img class="rounded" style="box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;" :lazy-src="data.photo"
                    :width="500" aspect-ratio="4/3" :src="data.photo"></v-img>
            </div>
            <div class="md:px-5 w-100 variant-rep">
                <h1 class="font-extrabold">{{ data?.name }} - {{ data?.product_name_en }}</h1>
                <br/>
                <template v-if="data?.variants?.length > 0">
                    <div class="border rounded-md w-100 p-3"
                        style="border-color: #ccc !important;background: aliceblue;">
                        <template v-if="data?.variants" v-for="(item, index) in data.variants" :key="index">
                            <h1 v-if="item?.variants.length > 0" class="mb-2 font-semibold">{{ item.variant_name }}</h1>
                            <template v-for="i in item.variants" v-if="item?.variants">
                                <v-chip class="mr-2 mb-2" @click="getItemsVariant(index, item, i)" v-if="i.selected"
                                    color="success" variant="tonal">
                                    <v-icon icon="mdi-checkbox-marked-circle-outline" start></v-icon>
                                    {{ i.variant }}
                                </v-chip>
                                <v-chip class="mr-2 mb-2" @click="getItemsVariant(index, item, i)" v-else variant="tonal">
                                    {{ i.variant }}
                                </v-chip>
                            </template>
                            <div class="ma-4"></div>
                        </template>
                    </div>
                    <br />
                </template>
                <div v-if="data?.prices?.length > 0" class="border rounded-md w-100 p-3"
                    style="border-color: #ccc !important;background: aliceblue;">
                    <h1 class="mb-2 font-semibold">Portion</h1>
                    <template v-for="(item, index) in data?.prices" :key="index">
                        <v-chip class="mr-2 mb-2" v-if="item.selected" color="success" variant="tonal" @click="onSelectPortion(item)">
                            <v-icon icon="mdi-checkbox-marked-circle-outline" start></v-icon>
                            {{ item.portion }}
                            <CurrencyFormat :value="item.price" />
                        </v-chip>
                        <v-chip class="mr-2 mb-2" v-else variant="tonal" @click="onSelectPortion(item)">
                            {{ item.portion }}
                            <CurrencyFormat :value="item.price" />

                            
                        </v-chip>
                    </template>
                </div>
                <br/>
                <h1 class="mb-2 font-semibold">Quantity</h1>
                <input v-if="data.is_return" max="-1" class="border rounded-md pa-1 ps-2" style="border-color: #ccc !important;background: aliceblue;" type="number" v-model="data.quantity"/>
                <input v-else :min="1" class="border rounded-md pa-1 ps-2" style="border-color: #ccc !important;background: aliceblue;" type="number" v-model="data.quantity"/>
                <div class="ma-4"></div>
                <h1 class="mb-2 font-semibold">Note</h1>
                <v-textarea class="rounded-md w-100" label="Note" v-model="data.note"></v-textarea>
            </div>
        </div>
    
    </ComDialogContent>
</template>

<script setup>
import { VDataTable } from 'vuetify/labs/VDataTable'
import { ref, inject, onMounted, postApi, computed, createToaster, getApi } from "@/plugin"
import ComDialogContent from "@/components/ComDialogContent.vue"
const dialogRef = inject('dialogRef');
const data = ref({})
const selectedData = ref({})
const toaster = createToaster({ position: 'top-right' })
const saleProduct = ref()
const sale = inject("$sale")
const prices = ref()
const selected = ref([])
const selectedProduct = ref({})

const loading = ref(false)

function onSelectPortion(p) {

    data.value.prices.find(r => r.selected).selected = false
    p.selected = true


}




const onGetProductByVariantDebounce = debounce(getProductByVariant, 700);

function getProductByVariant() {
    if (data.value.variants.flatMap(item => item.variants).filter(r => r.selected).length != data.value.variants.length) {

        return
    }
    selectedProduct.value = null

    postApi("product.get_product_by_variant", {
        variant: selectedData.value,
        product_code: data.value.variant_of ? data.value.variant_of : data.value.name
    }).then((r) => {

        if (r.message) {
            selectedProduct.value = r.message
            const prices = JSON.parse(r.message.prices)

            if (prices.length > 0) {
                data.value.prices = prices
            } else {

                data.value.prices = [{ unit: r.message.unit, price: r.message.price, portion: r.message.unit }]
            }
            data.value.prices[0].selected = true
        }

    })

}
function debounce(func, wait) {
    let timeout;

    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

onMounted(() => {
    loading.value = true
    getApi("product.get_product_option", {
        product_code: dialogRef.value.data.product_code,
        business_branch: sale.sale.business_branch,
        price_rule: sale.sale.price_rule
    }).then(result => {
        data.value = result.message
        prices.value = data.value.prices
        data.value.quantity = 1

        if (dialogRef.value.data.sale_product) {
            
            saleProduct.value = dialogRef.value.data.sale_product
            selectedData.value = saleProduct.value.selected_variant
            data.value.variants?.forEach((r, index) => {

                r.variants.find(r => r.variant == selectedData.value["variant_" + (index + 1)].variant_value).selected = true

            })
            
            data.value.quantity = saleProduct.value.quantity 
            data.value.note = saleProduct.value.note
            data.value.is_return = saleProduct.value.is_return
            

            // set selection for unit
            if (data.value.prices) {
                // clear selection first
                let selectedPrice = data.value.prices.find(r => r.selected == true)
                if (selectedPrice) {
                    selectedPrice.selected = false
                }
                selectedPrice = data.value.prices.find(r => r.unit == saleProduct.value.unit)
                if (selectedPrice) {
                    selectedPrice.selected = true

                }
            }

        }

        loading.value = false
    }).catch(error => {
        loading.value = false
    })




})



function getItemsVariant(index, variant, i) {

    selectedData.value['variant_' + (index + 1)] = { variant_name: variant.variant_name, variant_value: i.variant }
    data.value.variants[index].variants.filter(r => r.selected).forEach(x => x.selected = false)
    i.selected = true
    onGetProductByVariantDebounce()


}

function onOK() {

    if(data.value.variants){
        if (data.value.variants.flatMap(item => item.variants).filter(r => r.selected).length != data.value.variants.length) {
            toaster.warning("Please select all variant")
            return
        }
    }
    

    
    if (data.value.variants) {
        loading.value = true
        postApi("product.get_product_by_variant", {
            variant: selectedData.value,
            product_code: data.value.variant_of ? data.value.variant_of : data.value.name
        }).then((r) => {
            r.message.selected_variant = selectedData.value
            const selected_price = data.value.prices.find(r => r.selected)
            r.message.unit = selected_price.unit
            r.message.price = selected_price.price
            r.message.portion = selected_price.portion
            r.message.quantity = data.value.quantity
            r.message.note = data.value.note
            dialogRef.value.close({product:r.message})
            loading.value = false

        }).catch(error => {
            loading.value = false
        })
    }else {
        const selected_price = data.value.prices.find(r => r.selected)
        dialogRef.value.close({updatedData:{
            price:selected_price.price,
            unit:selected_price.unit,
            portion:selected_price.portion,
            quantity : data.value.quantity,
            note : data.value.note

        }})
    }

}
const onClose = () => {
    dialogRef.value.close()
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

@media (max-width: 767.98px) {
    .variant-rep {
        margin-top: 20px;
    }
}
</style>