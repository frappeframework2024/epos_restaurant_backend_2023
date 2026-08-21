<template>
    
    <ComModal
        title="Resend to Printer"
        titleOKButton="Send"
        :loading="isSending"
        :fullscreen="false"
        @onClose="onClose"
        @onOk="onSend"
    >
      <template #title>
            {{$t("Re-Send")  }}
        </template>
         <template #content>       
            <div class="resend-dialog">
                <button class="summary-bar" type="button" @click="toggleAll">
                    <span class="summary-title">
                        <span class="printer-icon">▣</span>
                        <strong>{{ totalProducts }} {{ $t("products with printers") }}</strong>
                    </span>

                    <span class="select-all">
                        {{ allSelected ? "✓" : "☐" }} {{ $t("Select all") }}
                    </span>
                </button>

                <section
                    v-for="group in orderGroups"
                    :key="group.key"
                    class="order-group"
                >
                    <button
                        class="order-header"
                        type="button"
                        @click="toggleGroup(group)"
                    >
                        <span>
                            <span class="clock-icon">◷</span>
                            {{ formatTime(group.orderTime) }} -
                            {{ group.orderBy }}
                        </span>

                        <span class="select-all">
                            {{ isGroupSelected(group) ? "✓" : "☐" }}
                            {{ $t("Select all") }}
                        </span>
                    </button>

                    <div class="product-list">
                        <article
                            v-for="product in group.products"
                            :key="product.key"
                            class="product-row"
                        >
                            <div class="product-name">
                                <span v-if="product.isChild" class="child-arrow">
                                    ↳
                                </span>

                                <strong>{{ product.product_name?.trim() }}</strong>
                                <span class="quantity">
                                    {{ product.quantity }} x
                                </span>
                            </div>

                            <div class="printer-list">
                                <button
                                    v-for="printer in product.printers"
                                    :key="printer.printer"
                                    type="button"
                                    class="printer-chip"
                                    :class="{
                                        selected: isPrinterSelected(
                                            product,
                                            printer,
                                        ),
                                    }"
                                    @click="togglePrinter(product, printer)"
                                >
                                    {{
                                        isPrinterSelected(product, printer)
                                            ? "✓"
                                            : "☐"
                                    }}
                                    {{ printer.printer_name }}
                                </button>
                            </div>
                        </article>
                    </div>
                </section>

                <div v-if="!orderGroups.length" class="empty-state">
                    {{ $t("No products with printers found.") }}
                </div>
            </div>
         </template>
    </ComModal>
</template>

<script setup>

import { computed,  ref, watch, i18n,onMounted, inject} from "@/plugin";
import {createToaster} from '@meforma/vue-toaster'; 
const { t: $t } = i18n.global;
const toaster = createToaster({ position: "top-right" });

const sale = inject('$sale')
var frappe = inject("$frappe")
const call = frappe.call();
const isSending = ref(false);
const printServerUrl = sale.getPrintServerUrl();
const emit = defineEmits(["onClose", "onSend"]);

const data = ref({});
const selectedPrinters = ref({})

const orderGroups = computed(() => {
    const groups = new Map()

    Object.values(data.value|| {}).forEach((items) => {
        ;(items || []).forEach((item, index) => {
            if (!item.printers?.length) return

            const groupKey = `${item.order_time}-${item.order_by}`

            if (!groups.has(groupKey)) {
                groups.set(groupKey, {
                    key: groupKey,
                    orderTime: item.order_time,
                    orderBy: item.order_by,
                    products: [],
                })
            }

            groups.get(groupKey).products.push({
                ...item,
                key: `${item.sale_product_id}-${item.product_code}-${index}`,
                productIndex: index,
                productName: item.product_name?.trim() || "",
                parentName: item.parent_product_name?.trim() || "",
                isChild: Boolean(item.parent_product_name),
            })
        })
    })

    return Array.from(groups.values()).map((group) => {
        const products = group.products
        const parentMap = new Map()

        // Find parent products by product name.
        products.forEach((product) => {
            if (!product.isChild) {
                parentMap.set(product.productName, product)
            }
        })

        const childrenMap = new Map()
        const rootProducts = []

        products.forEach((product) => {
            if (product.isChild && parentMap.has(product.parentName)) {
                if (!childrenMap.has(product.parentName)) {
                    childrenMap.set(product.parentName, [])
                }

                childrenMap.get(product.parentName).push(product)
            } else {
                rootProducts.push(product)
            }
        })

        // Display every parent immediately followed by its children.
        const orderedProducts = []

        rootProducts
            .sort((a, b) => a.productIndex - b.productIndex)
            .forEach((product) => {
                orderedProducts.push(product)

                const children = childrenMap.get(product.productName) || []

                orderedProducts.push(
                    ...children.sort(
                        (a, b) => a.productIndex - b.productIndex,
                    ),
                )
            })

        return {
            ...group,
            products: orderedProducts,
        }
    })
})

const allProducts = computed(() =>
    orderGroups.value.flatMap((group) => group.products),
)

const totalProducts = computed(() => allProducts.value.length)

const allSelected = computed(
    () =>
        totalProducts.value > 0 &&
        allProducts.value.every((product) =>
            isProductSelected(product),
        ),
)

watch(
    orderGroups,
    () => {
        const selections = {}

        allProducts.value.forEach((product) => {
            selections[product.key] = product.printers.map(
                (printer) => printer.printer,
            )
        })

        selectedPrinters.value = selections
    },
    { immediate: true },
)

onMounted(async ()=>{
    try{
        const resp = await call.post("epos_restaurant_2023.api.mobile.v1.sale.get_sale_product_printers_by_sale_name",{
            "sale_name": sale.sale.name,
        });

        if(resp){ 
            data.value = resp.message;
        }

        
    }finally{
//
    }
});

function isProductSelected(product) {
    return (
        selectedPrinters.value[product.key]?.length ===
        product.printers.length
    )
}

function isPrinterSelected(product, printer) {
    return selectedPrinters.value[product.key]?.includes(printer.printer)
}

function togglePrinter(product, printer) {
    const current = selectedPrinters.value[product.key] || []

    selectedPrinters.value[product.key] = current.includes(printer.printer)
        ? current.filter((id) => id !== printer.printer)
        : [...current, printer.printer]
}

function toggleAll() {
    const select = !allSelected.value

    allProducts.value.forEach((product) => {
        selectedPrinters.value[product.key] = select
            ? product.printers.map((printer) => printer.printer)
            : []
    })
}

function isGroupSelected(group) {
    return group.products.every((product) => isProductSelected(product))
}

function toggleGroup(group) {
    const select = !isGroupSelected(group)

    group.products.forEach((product) => {
        selectedPrinters.value[product.key] = select
            ? product.printers.map((printer) => printer.printer)
            : []
    })
}

function formatTime(value) {
    if (!value) return ""

    const date = new Date(value.replace(" ", "T"))

    return date.toLocaleTimeString([], {
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
    })
}

 
function onClose() {
    emit("resolve", false);
}


async function onSend() {
    if(isSending.value){
        return;
    }
    isSending.value = true;

    const payload = allProducts.value
        .map((product) => {
            const printerIds = selectedPrinters.value[product.key] || []

            return {
                ...product,
                printer_ids: printerIds.join(","),
                printers: printerIds.join(","),
                // printers: product.printers.filter((printer) =>
                //     printerIds.includes(printer.printer),
                // ),
            }
        })
        .filter((product) => product.printers.length)

    // emit("onSend", payload)


     const body = {
        "doc":sale.sale,
        "data": payload,
        "print_server_url":printServerUrl,
    }

    if(payload.length>0){
        try{ 
            const resp = await call.post("epos_restaurant_2023.api.mobile.v1.sale.submit_resend_to_printer", body);
            if (resp){
               
                toaster.success($t("Product was re-send"));
                emit("resolve", false);
            }

        } finally{
            isSending.value = false;
        } 
    }else{
         isSending.value = false;
    }
}
</script>

<style scoped>
.resend-dialog {
    max-height: 68vh;
    overflow-y: auto;
    padding: 0 16px 72px;
    background: #f5fafb;
    color: #26363b;
}

.summary-bar,
.order-header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
}

.summary-bar {
    margin-bottom: 10px;
    padding: 12px;
    border: 1px solid #d8e1e3;
    border-radius: 8px;
    background: #fff;
}

.summary-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
}

.printer-icon,
.clock-icon {
    color: #159eaa;
    font-size: 17px;
}

.order-group {
    margin-bottom: 16px;
    border: 1px solid #d5dfe1;
    background: #f7fbfc;
}

.order-header {
    padding: 12px 10px;
    border: 0;
    border-bottom: 1px solid #d5dfe1;
    background: #ccebee;
    color: #44565b;
    font-size: 12px;
    font-weight: 600;
}

.product-row {
    padding: 10px 26px;
    border-bottom: 1px solid #d5dfe1;
}

.product-row:last-child {
    border-bottom: 0;
}

.product-name {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
}

.quantity {
    margin-left: auto;
    font-size: 12px;
    font-weight: 600;
}

.child-arrow {
    color: #64787c;
    font-size: 18px;
}

.printer-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

.printer-chip {
    padding: 7px 11px;
    border: 0;
    border-radius: 7px;
    background: #d9e5e7;
    color: #51666b;
    cursor: pointer;
    font-size: 12px;
}

.printer-chip.selected {
    background: #c9e9ec;
}

.select-all {
    color: #159eaa;
    font-size: 12px;
    white-space: nowrap;
}

.empty-state {
    padding: 32px;
    color: #718287;
    text-align: center;
}
</style>