<template>
    <div>
        <DataTable :value="saleCouponList" tableStyle="min-width: 50rem">
            <Column field="coupon_number" header="Coupon #"></Column>
            <Column field="posting_date" header="Posting Date">
                <template #body="slotProps">
                    {{ moment(slotProps.data.posting_date).format("DD-MM-yyyy") }}
                    
                </template>
            </Column>
            <Column field="member_name" header="Member Name">
                <template #body="slotProps">
                    <div class="flex flex-column">
                        <div>
                            {{ slotProps.data.member_name }}
                        </div>
                        <div>
                            <Chip v-if="slotProps.data.coupon_type == 'Membership '" class="bg-primary" :label="slotProps.data.coupon_type" size="small" icon="pi pi-id-card" />
                            <Chip v-else :label="slotProps.data.coupon_type" size="small" icon="pi pi-id-card" />
                        </div>
                    </div>
                   
                </template>
            </Column>
            <Column field="price" header="Quantity"></Column>
            <Column field="expiry_date" header="Expiry Date">
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
</template>

<script setup>
    import moment from 'moment'
    import {inject,ref,onMounted} from 'vue'
    import DataTable from 'primevue/datatable';
    import Chip from 'primevue/chip';
    import Column from 'primevue/column';
    const frappe = inject("$frappe")
    const db = frappe.db();
    const loading =ref(false)
    const saleCouponList = ref([])
    
    onMounted(()=>{
        loading.value = true;
        db.getDocList('Sale Coupon', {
            fields: ["name", "coupon_number", "posting_date", "modified", "coupon_type", "membership", "member_name",
                "phone_number", "price", "expiry_date", "visited_count", "limit_visit"],
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
    })
    
</script>

<style lang="css" scoped>

</style>