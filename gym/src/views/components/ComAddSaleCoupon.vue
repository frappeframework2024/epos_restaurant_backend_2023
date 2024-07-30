<template>
    <div>
        <div class="col-12">
            <FileUpload @select="onFilesSelected($event)" name="file" :customUpload="true" :multiple="true"
                accept=".jpeg,.png,.gif,.pdf,.doc,.docx,.xls,.xlsx" :maxFileSize="1000000000">
                <template #header="{ chooseCallback, files }">
                    <div class="flex flex-wrap justify-content-between align-items-center flex-1 gap-2">
                        <div class="flex gap-2">
                            <Button @click="chooseCallback" icon="pi pi-images" rounded outlined></Button>
                        </div>
                    </div>
                </template>
                <template #content="{ files, removeFileCallback }">
                    <div v-if="files.length > 0" class="flex gap-3  flex-wrap ">
                        <template v-for="d in selectdFile.files">

                            <div
                                class="relative flex justify-content-between flex-column align-items-center flex-wrap border-1 border-round-sm w-6rem border-300">
                                <img style="width:60px" :src="d.objectURL" class="mt-2" />
                                <div
                                    class="text-xs text-center bg-cyan-50 text-600 p-2 border-300 file-wrapper-name w-full text-overflow-ellipsis">
                                    {{ d.name }}
                                </div>
                                <Button @click="onRemoveImage(removeFileCallback, d)" class="absolute remove-image"
                                    size="small" severity="danger" text rounded icon="pi pi-times"></Button>
                            </div>

                        </template>

                    </div>
                </template>
                <template #empty>
                    <p class="text-center text-600">Drag and drop files to here to upload.</p>
                </template>
            </FileUpload>
        </div>
    </div>
    <div class="position-relative">
        <div class="grid coupon_input_info pb-6">

            <div class="col-6 lg:col-4">
                <label>Coupon Number <span class="text-red-500">*</span></label><br />
                <InputText style="width: 100%" v-model="saleCoupon.coupon_number" :disabled="saleCoupon.name" />
            </div>
            <div class="col-6 lg:col-4">
                <label>Coupon Type</label><br />
                <Dropdown v-model="selectedCouponType" :options="couponType" placeholder="Select Coupon Type"
                    class="w-full" />
            </div>
            <div class="col-6 lg:col-4" v-if="selectedCouponType == 'Membership'">
                <label>Membership</label><br />
                <AutoComplete style="width: 100%;" inputStyle="width:100%" showOnFocus v-model="selectedMember"
                    @focus="memberFocus" inputId="ac" optionLabel="label" :suggestions="items" @complete="search">
                    <template #option="slotProps">
                        {{ slotProps.option.label }}
                        <br />
                        <span class="text-600 text-xs">
                            {{ slotProps.option.description }}
                        </span>

                    </template>
                </AutoComplete>
            </div>
            <div v-else class="col-6 lg:col-4">
                <label for="ac">Member Name <span class="text-red-500">*</span></label><br />
                <InputText v-model="saleCoupon.member_name" style="width: 100%;" />
            </div>
            <div class="col-6 lg:col-4">
                <label for="ac">Phone Number</label><br />
                <InputText v-model="saleCoupon.phone_number" style="width: 100%;" />
            </div>
            <div class="col-6 lg:col-4">
                <label>Price <span class="text-red-500">*</span></label><br />
                <InputNumber v-model="price" inputId="stacked-buttons" showButtons mode="currency" currency="USD"
                    style="width: 100%;" />
            </div>
            <div class="col-6 lg:col-4">
                <label>Limit Visit</label><br />
                <InputNumber v-model="limitVisit" inputId="minmax-buttons" mode="decimal" showButtons :min="0"
                    :max="100" style="width: 100%;" />
            </div>


            <div class="col-6 lg:col-4">
                <label>Expiry Date <span class="text-red-500">*</span></label><br />
                <Calendar dateFormat="dd-mm-yy" style="width: 100%;" @date-select="expiryChange" :modelValue="expiry_date" showIcon
                    :showOnFocus="false" />
            </div>
            <div class="col-12">
                <div class="flex justify-content-between py-2 align-items-center font-medium border-round-sm" style="background-color: #efefef">
                    <div class="mx-2">Payment</div>
                    <div class="mx-2"><Button @click="onAddPaymentClick()" rounded outlined icon="pi pi-plus" size="small"/></div>
                </div>
                <table class="w-full">

                    <thead>
                        <tr>
                            <th class="text-left">Payment Type</th>
                            <th>Amount</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(payment,idx) in payments" :key="idx">
                            <td >
                                <AutoComplete typeahead style="width: 100%;" inputStyle="width:100%" showOnFocus
                                    v-model="payment.payment_type"  @complete="searchPaymentType" inputId="ac" optionLabel="value"
                                    :suggestions="paymentTypes" >
                                    <template #option="slotProps">
                                        {{ slotProps.option.value }}
                                        <br />
                                        <span class="text-600 text-xs">
                                            <template v-if="slotProps.option.exchange_rate != 1">
                                                {{ slotProps.option.exchange_rate }},
                                            </template>
                                            {{ slotProps.option.currency }}
                                        </span>

                                    </template>
                                </AutoComplete>
                            </td>
                            <td>
                                <InputNumber v-model="payment.input_amount" inputId="stacked-buttons" style="width: 100%;" />
                            </td>
                            <td class="text-center">
                                <Button @click="onRemovePayment(idx)" severity="danger" rounded text outlined  icon="pi pi-trash" size="small"/>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="flex justify-content-end mt-5  py-2"
            style="position: absolute;bottom: 0;width: 100%;left: 0;background-color: #efefef">
            <div class="card flex flex-wrap gap-2 mr-2">
                <Button @click="onSave()" :loading="isSaving" label="Save" icon="pi pi-check" />
                <Button @click="onSave(true)" :loading="isSaving" label="Save & Submit" icon="pi pi-check" />
                <Button @click="closeDialog" label="Cancel" severity="danger" icon="pi pi-times" />
            </div>
        </div>
    </div>
    <Toast />
</template>

<script setup>
import FileUpload from 'primevue/fileupload';
import InputText from "primevue/inputtext"
import InputNumber from "primevue/inputnumber";
import AutoComplete from 'primevue/autocomplete';
import Calendar from 'primevue/calendar';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import { ref, inject, watch,onMounted } from 'vue'

import { useToast } from "primevue/usetoast";
import moment from 'moment';
const isSaving = ref(false)
const toast = useToast();
const frappe = inject("$frappe")
const call = frappe.call();
const items = ref([]);
const paymentTypes = ref([]);
const saleCoupon = ref({})
const selectedMember = ref(undefined)
const price = ref(0)
const expiry_date = ref()
const limitVisit = ref(0)
const VisitBalance = ref(0)
const selectedCouponType = ref("Individual")
const selectdFile = ref({})
const payments = ref([{
        "payment_type": "",
        "payment_amount": 0
    }])
const couponType = ref([
    'Individual',
    'Membership'
])
const dialogRef = inject('dialogRef');

const search = (event) => {
    call.get("frappe.desk.search.search_link", {
        txt: event.query,
        doctype: "Customer",
        ignore_user_permissions: 1,
        reference_doctype: "Sale Coupon"
    }).then((res) => {
        items.value = res.message
    })
}

const searchPaymentType = (event) => {
    call.get("epos_restaurant_2023.epos_restaurant.doctype.payment_type.payment_type.get_payment_type", {
        txt: event.query
    }).then((res) => {
        paymentTypes.value = res.message
    })
}
onMounted(() => {
    const params = dialogRef.value.data;
    if(params){
        saleCoupon.value = params.saleCoupon
        expiry_date.value = moment(params.saleCoupon.expiry_date).format("DD-MM-YYYY")
        price.value = params.saleCoupon.price
        limitVisit.value = params.saleCoupon.limit_visit
        selectedCouponType.value = params.saleCoupon.coupon_type
        selectedMember.value = params.saleCoupon.membership
        call.get("epos_restaurant_2023.gym.doctype.sale_coupon.sale_coupon.get_sale_coupon_payment",{docname:params.saleCoupon.name}).then((res)=>{
            if (res.message.length > 0){
                payments.value = res.message
            }
            
        })

    }
})


function memberFocus(event) {
    call.get("frappe.desk.search.search_link", {
        txt: "",
        doctype: "Customer",
        ignore_user_permissions: 0,
        reference_doctype: "Sale Coupon"
    }).then((res) => {
        items.value = res.message
    })
}
function onAddPaymentClick() {
    payments.value.unshift({
        "payment_type": "",
        "payment_amount": 0
    })
}

function expiryChange(event) {
    expiry_date.value = event;
    saleCoupon.value.expiry_date = moment(event).format('YYYY-MM-DD')
}

function onRemovePayment(idx){
    payments.value.splice(idx,1)
}
async function onSave(is_submit=false) {
    isSaving.value = true
    saleCoupon.value.price = price.value
    if (!saleCoupon.value.coupon_number) {
        toast.add({ severity: 'warn', summary: 'Validation', detail: 'Please enter Coupon Number', life: 3000 });
        isSaving.value = false
        return
    }
    if (!saleCoupon.value.membership && saleCoupon.value.coupon_type == "Membership") {
        toast.add({ severity: 'warn', summary: 'Validation', detail: 'Please select membership or Member name', life: 3000 });
        isSaving.value = false
        return
    }
    if (!expiry_date.value){
        toast.add({ severity: 'warn', summary: 'Validation', detail: 'Please select expiry date', life: 3000 });
        isSaving.value = false
        return
    }
    let data_to_save = JSON.parse(JSON.stringify(saleCoupon.value))
    data_to_save.coupon_type = selectedCouponType.value
    data_to_save.payments=[]
    payments.value.forEach((row)=>{
        if (row.input_amount > 0){
            data_to_save.payments.push({"payment_type":row.payment_type.value,"currency":row.payment_type.currency,"exchange_rate":row.payment_type.exchange_rate,"input_amount":row.input_amount,})
        } 
    })
    if (data_to_save.payments.length <= 0 && is_submit == true){
        toast.add({ severity: 'warn', summary: 'Validation', detail: 'Please enter payment amount', life: 3000 });
        isSaving.value = false
        return
    }

    //Prepare Data To Save
    call.post("epos_restaurant_2023.gym.doctype.sale_coupon.sale_coupon.insert_sale_coupon",{"data":data_to_save,"is_submit":is_submit==false?0:1}).then((res)=>{
        toast.add({ severity: 'success', summary: 'Sucecss', detail: 'Coupon saved succeess.', life: 3000 });
        isSaving.value = false
        closeDialog()
        selectdFile.value.files.forEach(_file => {
            call.post("upload_file", {
                file: _file,
                file_name: _file.name,
                doctype: "Sale Coupon",
                folder: "Home/Attachments",
                docname: doc.name,
                is_private: 1
            })
        });
    }).catch((err)=>{
        isSaving.value = false
        toast.add({ severity: 'error', summary: 'Validation', detail: JSON.parse(JSON.parse(err['_server_messages'])[0]).message, life: 3000 })
    })
    
    

}
function closeDialog() {
    dialogRef.value.close();
}
function onRemoveImage(callback, image) {
    selectdFile.value.files = selectdFile.value.files.filter(obj => obj.name !== image.name)
    callback()
}
const onFilesSelected = (events) => {
    selectdFile.value = events
};
watch(selectedMember, async (member) => {
    saleCoupon.value.membership = member
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

.file-wrapper-name {
    font-size: 8pt;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    padding-left: 4px;
    overflow: hidden;
    margin-top: 4px;
    text-overflow: ellipsis;
}

.remove-image {
    right: -18px;
    top: -19px;
}

.p-fileupload .p-fileupload-content {
    padding: 1rem;
}
</style>