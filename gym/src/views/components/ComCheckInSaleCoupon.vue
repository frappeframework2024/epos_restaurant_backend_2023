<template>
    <div>
        <div class="col-12">

        </div>
    </div>
    <div class="position-relative">
        <div class="grid coupon_input_info pb-6">
            <div class="col-12 lg:col-12">

                <label>Coupon Number <span class="text-red-500">*</span></label><br />
                <div class="flex">
                    <InputText style="width: 100%" v-model="coupon_number" />
                    <Button class="ml-3" @click="onGetCoupon" :loading="isSaving" icon="pi pi-check" />
                </div>
                
            </div>
            <div class="col-12 lg:col-12">
                    Empty
            </div>
        </div>
        <div class="flex justify-content-end mt-5  py-2"
            style="position: absolute;bottom: 0;width: 100%;left: 0;background-color: #efefef">
            <div class="card flex flex-wrap gap-2 mr-2">
                <Button @click="onCheckIn()" :loading="isSaving" label="Save" icon="pi pi-check" />
                <Button @click="closeDialog" label="Cancel" severity="danger" icon="pi pi-times" />
            </div>
        </div>
    </div>
    <Toast />
</template>

<script setup>
import InputText from "primevue/inputtext"
import Button from 'primevue/button';
import { ref, inject, watch } from 'vue'
import { useToast } from "primevue/usetoast";
import moment from 'moment';
const isSaving = ref(false)
const toast = useToast();
const frappe = inject("$frappe")
const call = frappe.call();
const items = ref([]);
const checkIn = ref({})
const selectedMember = ref(undefined)
const limitVisit = ref(0)
const VisitBalance = ref(0)
const dialogRef = inject('dialogRef');

const search = (event) => {
    call.get("frappe.desk.search.search_link", {
        txt: event.query,
        doctype: "Customer",
        ignore_user_permissions: 0,
        reference_doctype: "Sale Coupon"
    }).then((res) => {
        items.value = res.message
    })
}



async function onCheckIn() {
    isSaving.value = true
    isSaving.value = false
   
    
}
function closeDialog() {
    dialogRef.value.close();
}

watch(selectedMember, async (member) => {
    saleCoupon.value.membership = member.value
})

watch(limitVisit, async (value) => {
    if (value <= 0) {
        toast.add({ severity: 'error', summary: 'Validation', detail: error, life: 3000 })
        return
    }
    VisitBalance.value = value
    saleCoupon.value.limit_visit = value
    saleCoupon.value.balance = VisitBalance.value
})


</script>

<style>
.coupon_input_info label {
    margin-bottom: -11px;
    display: block;
}

.coupon_input_info .p-inputtext.p-component.p-inputnumber-input {
    width: 90%;
}
.file-wrapper-name{
    font-size:8pt; 
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    padding-left:4px;
    overflow: hidden;
    margin-top: 4px;
    text-overflow: ellipsis;
}
.remove-image{
    right: -18px;
    top: -19px;
}
.p-fileupload .p-fileupload-content{
    padding: 1rem;
}
</style>