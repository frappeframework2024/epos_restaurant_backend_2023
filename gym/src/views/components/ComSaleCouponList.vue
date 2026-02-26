<template>
    <div class="grid m-3">

        <div class="col-8">
            <h2>Coupon List</h2>
        </div>
        <div class="col-4 text-right">
            <Button icon="pi pi-refresh" @click="onRefreshClick()" class=" mx-2" text rounded aria-label="Filter" />
            <Button @click="onCheckInSaleCoupon" severity="success" class="mx-2">
                <span class="pi pi-sign-in mr-2"></span>
                Check In
            </Button>
            <Button @click="onAddCoupon">
                Sale Coupon
            </Button>
        </div>
    </div>
    <div>
        <div class="m-3 p-4 bg-white rounded">

            <div class="table-wrapper">
                <DataTable v-model:filters="filters"  dataKey="name" filterDisplay="row"  :value="saleCouponList" tableStyle="min-width: 50rem" tableClass="coupon__table">
                    <Column header="Coupon #" field="coupon_number">
                        <template #filter="{ filterModel, filterCallback }">
                            <InputText type="text" v-model="filterModel.value" @input="onFilter(filterModel,filterCallback())"
                                class="p-column-filter" placeholder="Search by Coupon#" />
                        </template>
                        <template #body="slotProps">
                            {{ slotProps.data.coupon_number }}
                        </template>
                    </Column>
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

                            {{ moment(slotProps.data.expiry_date).format("DD-MM-yyyy") }}
                            <br />

                        </template>
                    </Column>
                    <Column header="Used">
                        <template #body="slotProps">
                            {{ slotProps.data.visited_count }} of {{ slotProps.data.limit_visit }}
                        </template>
                    </Column>
                    <Column header="Status" style="width: 200px">
                        <template #body="slotProps">
                            <div class="flex flex-wrap align-items-center">

                                <Chip v-if="slotProps.data.coupon_type == 'Membership '" class="bg-primary m-0"
                                    :label="slotProps.data.coupon_type" size="small" icon="pi pi-id-card" />
                                <Chip v-else :label="slotProps.data.coupon_type" size="small" icon="pi pi-id-card"
                                    class="m-1" />
                                <Chip v-if="slotProps.data.docstatus == 1" label="Submitted" icon="pi pi-verified"
                                    size="small" class="m-1 bg-green-500" />
                                <Chip label="Expired" style="height: 16px !important;" class="bg-red-500 text-100"
                                    v-if="moment().isAfter(moment(slotProps.data.expiry_date))" />
                            </div>

                        </template>
                    </Column>
                    <Column header="Action" class="text-center">
                        <template #body="slotProps">
                            <Button type="button" outlined rounded class="mx-1" v-if="slotProps.data.docstatus != 1"
                                icon="pi pi-pencil" @click="onEditClick(slotProps.data)" aria-haspopup="true"
                                aria-controls="overlay_menu" />
                            <Button type="button" outlined rounded class="mx-1" v-if="slotProps.data.docstatus == 0"
                                severity="success" icon="pi pi-verified" @click="onSubmit(slotProps.data.name)"
                                aria-haspopup="true" aria-controls="overlay_menu" />


                        </template>
                    </Column>

                </DataTable>
            </div>


        </div>
    </div>
    <ConfirmDialog></ConfirmDialog>
</template>

<script setup>
import moment from 'moment'
import { useToast } from "primevue/usetoast";
import ComCheckInSaleCoupon from './ComCheckInSaleCoupon.vue';
import { inject, ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable';
import ConfirmDialog from 'primevue/confirmdialog';
import Chip from 'primevue/chip';
import InputText from 'primevue/inputtext';
import Column from 'primevue/column';
import ComAddSaleCoupon from './ComAddSaleCoupon.vue';
import Button from 'primevue/button';
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { FilterMatchMode } from 'primevue/api';
const confirm = useConfirm();
const toast = useToast();
const dialog = useDialog();
const frappe = inject("$frappe")
const db = frappe.db();
const call = frappe.call();
const loading = ref(false)
const saleCouponList = ref([])
const menu = ref();
const filters = ref({
    coupon_number: { value: '', matchMode: FilterMatchMode.CONTAINS }
});
const toggle = (event) => {
    menu.value.toggle(event);
};

function onEditClick(data) {
    dialog.open(ComAddSaleCoupon,
        {
            onClose: (opt) => {
                getListSaleCoupon()
            },
            data: {
                saleCoupon: data
            },
            props: {
                header: 'Sale Coupon',
                style: {
                    width: '50vw',

                },
                breakpoints: {
                    '960px': '75vw',
                    '640px': '90vw'
                },

                modal: true
            }
        });
}

function onSubmit(docname) {

    confirm.require({
        message: `Are you sure want to submit this document?`,
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        rejectClass: 'p-button-secondary p-button-outlined',
        rejectLabel: 'Cancel',
        acceptLabel: 'Submit',
        accept: () => {
            call.post("epos_restaurant_2023.coupon.doctype.sale_coupon.sale_coupon.submit_sale_coupon", { "docname": docname }).then((resp) => {
                toast.add({ severity: 'success', summary: 'Validation', detail: "Submit success.", life: 3000 });
            }).catch((err) => {
                if (err.httpStatus == 403) {
                    toast.add({ severity: 'error', summary: 'Validation', detail: err._error_message, life: 3000 });
                } else {

                    toast.add({ severity: 'error', summary: 'Validation', detail: JSON.parse(JSON.parse(err["_server_messages"])), life: 3000 });
                }

            })
        },
        reject: () => {
            isSaving.value = true
        }
    });
}

function onFilter(keyword,filterCallback){
    getListSaleCoupon(keyword)
    filterCallback()
}

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

                },
                breakpoints: {
                    '960px': '75vw',
                    '640px': '90vw'
                },

                modal: true
            }
        });
}
function onCheckInSaleCoupon() {
    dialog.open(ComCheckInSaleCoupon,
        {
            onClose: (opt) => {
                getListSaleCoupon()
            },
            props: {
                header: 'Check In Coupon',
                style: {
                    width: '50vw',

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
function getListSaleCoupon(keyword="") {
    loading.value = true;
    db.getDocList('Sale Coupon', {
        fields: ['*'],
        filters: keyword == "" ? [] : [ ["name", "like", `%${keyword.value}%`]],
        limit: 100,
        orderBy: {
            field: 'creation',
            order: 'DESC',
        }
    }).then((docs) => {
        saleCouponList.value = docs
        loading.value = false
    }).catch((err) => {
        if (error.httpStatus == 403) {
            toast.add({ severity: 'error', summary: 'Validation', detail: err._error_message, life: 3000 });
        }

        saleCouponList.value = []
        loading.value = false
    })
}

</script>

<style>
.p-submenu-header {
    display: none
}

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

.table-wrapper {
    height: 450px;
    overflow: auto;
}
</style>