<template>
    <div class="grid m-3">

        <div class="col-8">
            <h2>Coupon List</h2>
        </div>
        <div class="col-4 text-right">
            <Button icon="pi pi-refresh" @click="onRefreshClick()" class=" mx-2" text rounded aria-label="Filter" />
            <Button @click="onAddCoupon">
                Sale Coupon
            </Button>
        </div>
    </div>
    <div>
        <div class="m-3 p-4 bg-white rounded">
            <div class="grid m-3">

                <div class="col-3">
                    <div class="flex flex-column gap-2">
                        <label for="coupon_number">Coupon #</label>
                        <InputText id="coupon_number" @update="onSearchCouponNumber" :value="searchCouponNumber"
                            aria-describedby="coupon_number-help" />
                    </div>
                </div>
                <div class="col-3">
                    <div class="flex flex-column gap-2">
                        <label for="member_name">Member Name</label>
                        <InputText id="member_name" @update="onSearchMemberName" :value="searchMemberName"
                            aria-describedby="member_name-help" />

                    </div>
                </div>
            </div>
            <div class="table-wrapper">
                <DataTable :value="saleCouponList" tableStyle="min-width: 50rem" tableClass="coupon__table">
                <Column field="coupon_number" header="Coupon #"></Column>
                <Column field="posting_date" header="Posting Date">
                    <template #body="slotProps">
                        {{ moment(slotProps.data.posting_date).format("DD-MM-yyyy") }}
                    </template>
                </Column>
                <Column field="member_name" header="Member Name">
                    <template #body="slotProps">
                        <div class="flex gap-2 align-items-center">
                            <div>
                                {{ slotProps.data.member_name }}
                            </div>
                            <div>
                                <Chip v-if="slotProps.data.coupon_type == 'Membership '" class="bg-primary m-0"
                                    :label="slotProps.data.coupon_type" size="small" icon="pi pi-id-card" />
                                <Chip v-else :label="slotProps.data.coupon_type" size="small" icon="pi pi-id-card"
                                    class="m-0" />
                            </div>
                        </div>
                    </template>
                </Column>
                <Column header="Price" headerClass="qty__custom_header" bodyClass="text-right">
                    <template #body="slotProps">
                        {{ slotProps?.data.price }}
                    </template>
                </Column>
                <Column field="expiry_date" header="Expiry Date" headerClass="exd__custom_header"
                    bodyClass="text-center">
                    <template #body="slotProps">
                        {{ moment(slotProps.data.expriry_date).format("DD-MM-yyyy") }}
                    </template>
                </Column>
                <Column header="Used">
                    <template #body="slotProps">
                        {{ slotProps.data.visited_count }} of {{ slotProps.data.limit_visit }}
                    </template>
                </Column>
            </DataTable>
            </div>
                
            
        </div>
    </div>

</template>

<script setup>
import moment from 'moment'
import ScrollPanel from 'primevue/scrollpanel';
import { inject, ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable';
import Chip from 'primevue/chip';
import InputText from 'primevue/inputtext';
import Column from 'primevue/column';
import ComAddSaleCoupon from './ComAddSaleCoupon.vue';
import Button from 'primevue/button';
import { useDialog } from 'primevue/usedialog';
const first = ref(0);
const dialog = useDialog();
const frappe = inject("$frappe")
const db = frappe.db();
const loading = ref(false)
const saleCouponList = ref([])
const searchCouponNumber = ref([])

function onAddCoupon() {
    dialog.open(ComAddSaleCoupon,

        {
            onClose: (opt) => {
                getListSaleCoupon()
            },
            props: {
                header: 'Sale Coupon',
                style: {
                    width: '50vw',
                    height: '60vw',
                },
                breakpoints: {
                    '960px': '75vw',
                    '640px': '90vw'
                },

                modal: true
            }
        });
}

onMounted(() => {
    getListSaleCoupon()
})

function onRefreshClick() {
    getListSaleCoupon()
}
function getListSaleCoupon() {
    loading.value = true;
    db.getDocList('Sale Coupon', {
        fields: ["name", "coupon_number", "posting_date", "modified", "coupon_type", "membership", "member_name",
            "phone_number", "price", "expiry_date", "visited_count", "limit_visit"],
        page_length: 500,
        orderBy: {
            field: 'creation',
            order: 'DESC',
        }
    }).then((docs) => {
        saleCouponList.value = docs
        loading.value = false
    }).catch((rr) => {
        loading.value = false
    })
}

</script>

<style>
.coupon__table th {
    padding: 8px !important;
}

.coupon__table td {
    padding: 8px !important;
}

.coupon__table th {
    border: 0 !important;
}

.coupon__table .p-chip .p-chip-icon,
.coupon__table .p-chip .p-chip-text {
    font-size: 10px;
}

.coupon__table .p-chip {
    background-color: #007bff;
    color: #fff;
}

.coupon__table .qty__custom_header .p-column-header-content {
    justify-content: end;
}

.coupon__table td {
    font-size: 14px !important;
}

.coupon__table .exd__custom_header .p-column-header-content {
    justify-content: center;
}
.table-wrapper{
    height: 500px;
    overflow: auto;
}
</style>