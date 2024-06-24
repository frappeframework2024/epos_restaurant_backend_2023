<template>
    <ComModal :fullscreen="true" @onClose="onClose" :hideOkButton="true" :isPrint="true"
        :hideCloseButton="true">
        <template #title>
            {{ $t('Unpaid Bill') }}: {{ props.params.data }}
        </template>
        <template #content>
            <ComLoadingDialog v-if="isLoading" />
            <v-row>
                <v-col v-for="s in saleList" cols="12" md="3">
                    <v-card>
                        <template v-slot:title>
                            {{ $t("Bill") }}#: {{ s.custom_bill_number || s.name }}
                        </template>
                        <template v-slot:subtitle>
                            {{ $t("Table") }}: {{ s.tbl_number }}
                        </template>
                        <div class="product-content">
                            <v-list v-for="i in s.sale_products" :lines="false" density="compact" class="pa-0">

                                <v-list-item :title="i.product_code + '-' + i.product_name">
                                    <template v-slot:subtitle>
                                        <CurrencyFormat :value="i.price" /> x {{ i.quantity }} =
                                        <CurrencyFormat :value="i.total_revenue" />
                                    </template>
                                </v-list-item>
                            </v-list>
                        </div>

                        <table>
                            <tr>
                                <td>{{ $t("Grand Total") }}</td>
                                <td>
                                    <CurrencyFormat :value="s.grand_total" />
                                </td>
                            </tr>
                            <tr>
                                <td>{{ $t("Total Paid") }}</td>
                                <td>
                                    <CurrencyFormat :value="s.total_paid" />
                                </td>
                            </tr>
                            <tr>
                                <td>{{ $t("Balance") }}</td>
                                <td>
                                    <CurrencyFormat :value="s.balance" />
                                </td>
                            </tr>
                        </table>
                    </v-card>
                </v-col>
            </v-row>
        </template>
    </ComModal>
</template>

<script setup>
import { ref, defineEmits, inject, useRouter, createDocumentResource, confirm, i18n, onMounted } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';

const { t: $t } = i18n.global;
const emit = defineEmits(["resolve", "reject"])
const sale = inject("$sale");

const router = useRouter();
const isLoading = ref(false);
const toaster = createToaster({ position: "top-right" })
const frappe = inject("$frappe");
const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})
//frappe api call
const call = frappe.call()
const saleList = ref([])

onMounted(() => {
    isLoading.value = true
    call.get("epos_restaurant_2023.selling.doctype.customer.customer.get_unpaid_bills", {
        name: props.params.data
    }).then((res) => {
        saleList.value = res.message
        // emit('reload')
        isLoading.value = false
    }).catch((err) => {
        isLoading.value = false
    })
})
function onClose() {
    emit("resolve", false)
}

</script>
<style>
    .product-content{
        height: 200px;
        overflow-y: auto;
    }
</style>