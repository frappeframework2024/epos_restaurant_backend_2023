<template>
    <div>
        <div class="col-12">

        </div>
    </div>
    <div class="position-relative">
        <div class="grid coupon_input_info pb-6">
            <div class="col-12 lg:col-12">

                <label>Coupon Number<span class="text-red-500">*</span></label><br />
                <div class="flex">
                    <InputText style="width: 100%" v-model="couponNumber" />
                    <Button class="ml-3" @click="onScanCoupon" :loading="isSaving" icon="pi pi-check" />
                </div>
                
            </div>
            <div class="col-12 lg:col-12">
                <div class="border-round-sm border-1 border-500 surface-50 p-2">
                    <Chip label="Expired" style="height: 24px !important;" class="bg-red-500 text-100" v-if="isExpired"/>
                    <div v-if="scanedCoupon">
                        <ComDisplayLabelValue label="Coupon Number" :value="scanedCoupon.coupon_number"/>
                        <ComDisplayLabelValue label="Member Name" :value="scanedCoupon.member_name"/>
                        <ComDisplayLabelValue label="Phone" :value="scanedCoupon.phone_number"/>
                        <ComDisplayLabelValue label="Limit Visit" :value="scanedCoupon.limit_visit"/>
                        <ComDisplayLabelValue label="Visited Count" :value="scanedCoupon.visited_count"/>
                        <ComDisplayLabelValue label="Balance" :value="scanedCoupon.balance"/>
                        <ComDisplayLabelValue label="Expriry Date" :value="moment(scanedCoupon.expiry_date).format('DD-MM-YYYY')"/>
                    </div>
                    <template v-if="scanedCoupon != undefined">
                        <div class="mt-2">
                            <label>Visit Count<span class="text-red-500">*</span></label><br />
                        <div class="flex">
                        <InputText  style="width: 100%" :modelValue="visitCount"
                                                    @update:modelValue="visitCountChange" />
                        </div>
                        </div>
                        
                    </template>
                    <template v-else>
                       <p class="text-center text-500">Please enter coupon Number for check in</p>
                    </template>
                   
                </div>
            </div>
        </div>
        <div class="flex justify-content-end mt-5  py-2"
            style="position: absolute;bottom: 0;width: 100%;left: 0;background-color: #efefef">
            <div class="card flex flex-wrap gap-2 mr-2">
                <Button @click="onCheckIn" :disabled="isExpired" :loading="isSaving" label="Save" icon="pi pi-check"/>
                <Button @click="closeDialog" label="Cancel" severity="danger" icon="pi pi-times" />
            </div>
        </div>
    </div>
    <ConfirmDialog></ConfirmDialog>
</template>

<script setup>
import ComDisplayLabelValue from "./ComDisplayLabelValue.vue";

import InputText from "primevue/inputtext"
import ConfirmDialog from 'primevue/confirmdialog';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import { ref, inject, watch } from 'vue'
import { useToast } from "primevue/usetoast";
import moment from 'moment';
import { useConfirm } from "primevue/useconfirm";
const confirm = useConfirm();
const isSaving = ref(false)
const toast = useToast();
const frappe = inject("$frappe")
const call = frappe.call();
const db = frappe.db();
const selectedMember = ref(undefined)
const limitVisit = ref(0)
const VisitBalance = ref(0)
const dialogRef = inject('dialogRef');
const scanedCoupon = ref(undefined)
const couponNumber = ref("")
const visitCount = ref(0)
const isExpired = ref(false)


async function onCheckIn() {
    if(visitCount <= 0){
        toast.add({ severity: 'warn', summary: 'Valivate', detail: 'Please enter visit count.', life: 3000 });
        return
    }
    if (scanedCoupon.value.balance < visitCount.value){
        toast.add({ severity: 'warn', summary: 'Valivate', detail: 'visit count cannot greater than visit balance.', life: 3000 });
        return
    }
    isSaving.value = true
    confirm.require({
        message: `Please verify this coupon #${ scanedCoupon.value.coupon_number} is correct?`,
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        rejectClass: 'p-button-secondary p-button-outlined',
        rejectLabel: 'Cancel',
        acceptLabel: 'Save',
        accept: () => {
            
            let dataToSave = JSON.parse(JSON.stringify(scanedCoupon.value))
            dataToSave.visited_count = visitCount.value
            db.createDoc('Check In Sale Coupon',dataToSave).then((res)=>{
                closeDialog()
                toast.add({ severity: 'success', summary: 'Success', detail: `${res.data.coupon_number} check in success.`, life: 3000 });
                isSaving.value = false
            }).catch((error)=>{
                toast.add({ severity: 'error', summary: "Check In Failed", detail: JSON.parse(JSON.parse(error["_server_messages"])).message , life: 3000 });
                isSaving.value = false
            })
        },
        reject: () => {
            isSaving.value = true
        }
    });

    
    isSaving.value = false   
}
function onScanCoupon(){
    call.get("epos_restaurant_2023.gym.doctype.sale_coupon.sale_coupon.get_coupon_by_number",{
        coupon_number:couponNumber.value
    }).then((resp)=>{
        scanedCoupon.value = resp.message
        isExpired.value = moment(scanedCoupon.value.expiry_date).isBefore(moment())
       
    })
}
function visitCountChange(value ){
    visitCount.value = value
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