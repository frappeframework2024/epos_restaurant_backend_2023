<template>
    <ComModal @onClose="onClose(false)" :loading="loading" :fullscreen="true" :hide-ok-button="true"
        :hide-close-button="true">
        <template #title>
            {{ params.title }}
        </template>

        <template #content>
            <div class="search-box my-0 mx-auto w-full">
                <ComInput autofocus keyboard variant="outlined" :placeholder="$t('Search...')"
                    prepend-inner-icon="mdi-magnify" v-model="keyword" v-debounce="onSearch" /> <br />
               
                    <v-row>
                        <v-col cols="3">
                            <div class="invs-det">
                                <v-select @update:modelValue="onSortField" v-model="sortOrder.field" label="Sort Order"
                                    item-title="label" item-value="fieldname"
                                    :items="meta?.fields?.filter(r => r.in_list_view == 1 || r.in_filter == 1 || r.fieldname == 'product_code' || r.bold == 1 || r.fieldname == 'modified')"></v-select>
                            </div>
                        </v-col>
                        <v-col cols="1">
                            <v-btn class="h-100 w-100" @click="onSortOrderBy('asc')">ASC</v-btn>
                        </v-col>
                        <v-col cols="1">
                            <v-btn class="h-100 w-100" @click="onSortOrderBy('desc')">DESC</v-btn>
                        </v-col>
                    </v-row>
                    <br />   <v-row v-if="data?.length>0">
                        <v-col cols="12">
                            <div style="height:calc(100vh - 225px);" class="overflow-auto">
                                <div class="flex flex-column h-100">
                                    <div>
                                        <v-table class="responsive-table" style="border-top: 1px solid #ccc">
                                            <thead>
                                                <tr>
                                                    <th class="text-left">{{$t("Photo")}}</th>
                                                    <th class="text-left">{{ $t("Product Code") }}</th>
                                                    <th class="text-left">{{$t("Product Name")}}</th>
                                                    <th class="text-left">{{$t("Category")}}</th>
                                                    <th class="text-right">{{$t("Price")}}</th>
                                                    <th class="text-center">{{$t("Unit")}}</th>
                                                    <th></th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(p, index) in data" :key="index">
                                                    <td class="text-left">
                                                        <div class="">
                                                            <div class="p-2">
                                                                <v-img v-if="p.photo" class="img-fluid-res rounded" :width="150" aspect-ratio="1"
                                                                    cover :src="p.photo"></v-img>
                                                                <v-img v-else class="img-fluid-res rounded" :width="150" aspect-ratio="1"
                                                                    cover :src="placeholderImage"></v-img>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td>{{ p.name }}
                                                        <template v-if="p.product_code_2"> <br/> {{ p.product_code_2 }}</template>
                                                        <template v-if="p.product_code_3"> <br/> {{ p.product_code_3 }}</template>
                                                    </td>
                                                    <td style="max-width: 30rem;" class="overflow-hidden">
                                                        <div class="">
                                                            <v-tooltip location="top" v-if="p.product_name_en != p.product_name_kh"
                                                                :text="`${p.product_name_en} ${p.product_name_kh}`">
                                                                <template v-slot:activator="{ props }">
                                                                    <div class="elp-pro-name" v-bind="props">{{p.product_name_en }} <template v-if="p.product_name_en != p.product_name_kh">{{p.product_name_kh }}</template>
                                                                    </div>
                                                                </template>
                                                            </v-tooltip>
                                                            <v-tooltip location="top" v-else :text="`${p.product_name_en}`"> 
                                                                <template v-slot:activator="{ props }">
                                                                    <div class="elp-pro-name" v-bind="props">{{
                                                                        p.product_name_en }} <template
                                                                            v-if="p.product_name_en != p.product_name_kh">{{
                                                                            p.product_name_kh }}</template>
                                                                    </div>
                                                                </template>
                                                            </v-tooltip>
                                                        </div>
                                                    </td>
                                                    
                                                    <td>{{ p.product_category }}</td>
                                                    <td class="text-right">
                                                        <CurrencyFormat :value="p.price" />
                                                    </td>
                                                    <td class="text-center">
                                                        {{ p.unit }}
                                                    </td>
                                                    <td>
                                                        <v-btn class="text-lg" @click="onSelectProduct(p)" >Select Product 
                                                            <span style="color:red; font-weight: bold;">{{ getTotalQuantityOrder(p) }}</span>
                                                        </v-btn>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </v-table>
                                    </div>
                                    <div>
                                        <!-- <template v-if="data.length > 0">
                                        <div class="text-center">
                                            <v-pagination
                                            v-model="page"
                                            :length="4"
                                            rounded="circle"
                                            ></v-pagination> 
                                        </div> 
                                    </template> -->
                                    </div>
                                </div>
                            </div>
                        </v-col>
                        <!-- <v-col v-if="selectedProduct">
                        <div class="h-100 p-2 pt-0"  >
                            <ComSearchSelectedProduct/>
                        </div>
                    </v-col> -->
                    </v-row>
                 
              
            </div>
        </template>
    </ComModal>
</template>

<script setup>

import { inject, ref, computed, onMounted, reactive, i18n,addModifierDialog,createResource } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
import ComSearchSelectedProduct from './ComSearchSelectedProduct.vue';
import placeholderImage from '@/assets/images/placeholder.webp'
const sale=inject("$sale")
const product=inject("$product")

const gv = inject("$gv")
const frappe = inject('$frappe');
const db = frappe.db()
const call = frappe.call();
const data = ref([])
const { t: $t } = i18n.global;
const keyword = ref("")
const toaster = createToaster({ position: "top-right" })
const loading = ref(false)
const selectedProduct = ref()
const meta = ref({})

const sortOrder = ref({ field: "product_name_en", order: "asc" })
let customerPromotion = computed({
    get() {
        return gv.getPromotionByCustomerGroup(sale.sale.customer_group)
    },
    set(newValue) {
        return newValue
    }
})
const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})

const emit = defineEmits(["resolve"])

function onSortOrderBy(type) {
    sortOrder.value.order = type
    onSearch()
}

function onSortField(field) {
    sortOrder.value.field = field
    onSearch()
}

function onSearch() {
    loading.value = true
    

    db.getDocList('Product', {
        fields: ['name',"product_code_2","product_code_3", 'product_name_en', 'product_name_kh', 'price', "photo", "product_category", 'prices','unit'],
        orFilters: [
            ["name", 'like', '%' + keyword.value + "%"],
            ["product_code_2", 'like', '%' + keyword.value + "%"],
            ["product_code_3", 'like', '%' + keyword.value + "%"],
            ["product_name_en", 'like', '%' + keyword.value + "%"],
            ["product_name_kh", 'like', '%' + keyword.value + "%"],
            ["Product Price", "barcode", "like", "%" + keyword.value + "%"]
        ],
        orderBy: sortOrder.value,
        limit:50
    })
        .then((docs) => {
            data.value = docs
            loading.value = false

        })
        .catch((error) => {
            loading.value = false
        });

}

function onClose(isClose) {
    emit('resolve', isClose);
}

async function onSelectProduct(d){
    call.get("epos_restaurant_2023.api.product.get_product_by_barcode",{barcode:d.name}).then(async (result)=>{
        const p = result.message
        const portions = JSON.parse(p.prices)?.filter(r => (r.branch == sale.sale.business_branch || r.branch == '') && r.price_rule == sale.sale.price_rule);
         if (portions?.length == 1) {
             p.price = portions[0].price
             p.unit = portions[0].unit
         }

         if (portions?.length > 1) {
             product.setSelectedProduct(p);

             let productPrices = await addModifierDialog();

             if (productPrices) {
                 if (productPrices.portion != undefined) {
                     p.price = productPrices.portion.price;
                     p.portion = productPrices.portion.portion;
                     p.unit = productPrices.portion.unit
                 }
                 
             } else {
                 return;
             }
         } else {
             p.modifiers = "";
             p.modifiers_data = "[]";
             p.portion = "";
         }
         sale.addSaleProduct(p);
         // ***apply promotion discount***
         sale.sale.customer_default_discount = result.default_discount;

        if (sale.promotion) {
            customerPromotion.value = gv.getPromotionByCustomerGroup(sale.sale.customer_group)
            //sale.promotion.customer_groups.filter(r=>r.customer_group_name_en == result.customer_group).length > 0
            if (customerPromotion.value && customerPromotion.value.length > 0) {
                customerPromotion.value.forEach((r) => {
                    toaster.info(`${$t('msg.This customer has happy hour promotion')} ${r.promotion_name} : ${((r.percentage_discount || 0))}%`);
                })
                updateProductAfterSelectCustomer(customerPromotion.value)
            }
            else {
                onClearPromotionProduct()
            }

        }
        console.log(customerPromotion.value)
        if ((customerPromotion.value || []).length <= 0) {
            sale.sale.discount_type = "Percent";
            sale.sale.discount = parseFloat(customerPromotion.value.percentage_discount);
            toaster.info($t('msg.This customer has default discount') + " " + sale.sale.discount + '%');
        }
        sale.updateSaleSummary();

         /// ***end apply promtion discount***
         
         toaster.success($t("Add product to order successfully"))
    })     
}

function updateProductAfterSelectCustomer(pro) {
    const promotions = JSON.parse(JSON.stringify(pro))
    if (sale.sale.sale_products.length > 0) {
        let product_checks = []
        sale.sale.sale_products.forEach((r) => {
            product_checks.push({
                product_code: r.product_code,
                order_time: r.order_time
            })
        })
        createResource({
            url: 'epos_restaurant_2023.api.promotion.get_promotion_products',
            auto: true,
            params: {
                products: product_checks,
                promotions: promotions
            },
            onSuccess(doc) {
                if (doc) {
                    onClearPromotionProduct()
                    /// update products promotion
                    doc.product_promotions.forEach(r => {
                        let sale_products = sale.sale.sale_products.filter(x => x.product_code == r.product_code)
                        sale_products.forEach((s) => {
                            if (moment(s.order_time).format('HH:mm:ss') == r.order_time && s.is_free == false) {
                                s.discount_type = 'Percent'
                                s.discount = r.percentage_discount
                                s.happy_hours_promotion_title = r.promotion_title
                                s.happy_hour_promotion = r.promotion_name
                            }
                            sale.updateSaleProduct(s)
                        })
                    })

                    // remove expire promotion
                    if (doc.expire_promotion.length > 0) {
                        doc.expire_promotion.forEach((p) => {
                            toaster.warning(`${p.promotion_name} ${$t('msg.was expired')}`)
                            const index = gv.promotion.findIndex(r => r.name == p.name)
                            if (index > -1) {
                                gv.promotion.splice(index, 1);
                                sale.promotion.splice(index, 1);
                            }
                        })

                    }
                } else {
                    gv.promotion = null
                    sale.promotion = null
                }
                sale.updateSaleSummary();
            }
        });
    }
}


onMounted(() => {
 
    call.get("epos_restaurant_2023.api.api.get_meta", { "doctype": "Product" }).then((data) => {
        meta.value = data.message
    }) 
})

function getTotalQuantityOrder(data) {
    const qty = sale.sale?.sale_products?.filter(r => r.product_code == data.name).reduce((n, d) => n + (d.quantity || 0), 0);
    console.log(qty)
    if (qty == undefined) {
        return ""
    }
    if (qty == 0) {
        return ""
    } else {
        return " (" + qty + ")"
    }
}

</script>

<style>
.elp-pro-name {
    width: 25rem;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.invs-det .v-input__details {
    display: none !important;
}
@media (max-width:1024.98px) {
    .elp-pro-name {
        width: 13rem;
    }
    .img-fluid-res {
        width: 90px !important;
    }
    .responsive-table tr th, 
    .responsive-table tr td{
        padding: 0 5px !important;
    }
}
</style>