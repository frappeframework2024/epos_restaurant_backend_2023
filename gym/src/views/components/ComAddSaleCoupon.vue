<template>
    <div class="position-relative">
        <div class="grid coupon_input_info" style="margin-bottom: 30px;">
            <div class="col-12">
                <FileUpload name="file" :customUpload="true" @upload="onAdvancedUpload($event)" :multiple="true"  accept="jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.xls,.xlsx" :maxFileSize="1000000000">
                    <template #header="{ chooseCallback, uploadCallback, clearCallback, files }">
                        <div class="flex flex-wrap justify-content-between align-items-center flex-1 gap-2">
                            <div class="flex gap-2">
                                <Button @click="chooseCallback()" icon="pi pi-images" rounded outlined></Button>
                                <Button @click="uploadEvent(uploadCallback)" icon="pi pi-cloud-upload" rounded outlined severity="success" :disabled="!files || files.length === 0"></Button>
                                <Button @click="clearCallback()" icon="pi pi-times" rounded outlined severity="danger" :disabled="!files || files.length === 0"></Button>
                            </div>
                            <ProgressBar :value="totalSizePercent" :showValue="false" :class="['md:w-20rem h-1rem w-full md:ml-auto', { 'exceeded-progress-bar': totalSizePercent > 100 }]"
                                ><span class="white-space-nowrap">{{ totalSize }}B / 1Mb</span></ProgressBar
                            >
                        </div>
                    </template>
                    <template #empty>
                        <p>Drag and drop files to here to upload.</p>
                    </template>
                </FileUpload>
            </div>
            <div class="col-6 lg:col-4">
                <label>Coupon Number <span class="text-red-500">*</span></label><br/>
                <InputText style="width: 100%;" v-model="saleCoupon.coupon_number"/>
            </div>
            <div class="col-6 lg:col-4">
                <label>Coupon Type</label><br/>
                <Dropdown v-model="selectedCouponType" editable :options="couponType" placeholder="Select Coupon Type" class="w-full" />
            </div>
            <div class="col-6 lg:col-4" v-if="selectedCouponType=='Membership'">
                <label>Membership</label><br/>
                <AutoComplete style="width: 100%;" inputStyle="width:100%" showOnFocus v-model="selectedMember" @focus="memberFocus" inputId="ac" optionLabel="label"  :suggestions="items" @complete="search">
                    <template #option="slotProps">
                        {{ slotProps.option.label }}
                        <br/>
                        <span class="text-600 text-xs">
                            {{ slotProps.option.description }}
                        </span>
                        
                    </template>
                </AutoComplete>
            </div>
            <div v-else class="col-6 lg:col-4">
                <label for="ac">Member Name  <span class="text-red-500">*</span></label><br/>
                <InputText v-model="saleCoupon.member_name" style="width: 100%;"/>
            </div>
            <div class="col-6 lg:col-4">
                <label for="ac">Phone Number</label><br/>
                <InputText v-model="saleCoupon.phone_number" style="width: 100%;"/>
            </div>
            <div class="col-6 lg:col-4">
                <label>Price <span class="text-red-500">*</span></label><br/>
                <InputNumber v-model="price" inputId="stacked-buttons" showButtons mode="currency" currency="USD" style="width: 100%;"/>
            </div>
            <div class="col-6 lg:col-4">
                <label>Limit Visit</label><br/>
                <InputNumber v-model="limitVisit" inputId="minmax-buttons" mode="decimal" showButtons :min="0" :max="100" style="width: 100%;"/>
            </div>
            
            
            <div class="col-6 lg:col-4">
                <label>Expiry Date <span class="text-red-500">*</span></label><br/>
                

                <Calendar style="width: 100%;"  @date-select="expiryChange" :modelValue="expiry_date" showIcon :showOnFocus="false" />
            </div>
        </div>
        <div class="flex justify-content-end mt-5 bg-white p-2" style="position: absolute;bottom: 0;width: 100%;left: 0;">
            <div class="card flex flex-wrap gap-2">
                <Button @click="onSave()" label="Save" icon="pi pi-check" />
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
    import {ref,inject,watch } from 'vue'
    import SaleCoupon from "../SaleCoupon.vue";
    import { useToast } from "primevue/usetoast";
import moment from 'moment';
    const isSaving = ref(false)
    const toast = useToast();
    const frappe = inject("$frappe")
    const db = frappe.db();
    const call = frappe.call();
    const items = ref([]);
    const saleCoupon = ref({})
    const selectedMember = ref(undefined)
    const price = ref(0)
    const expiry_date = ref()
    const limitVisit = ref(0)
    const VisitBalance = ref(0)
    const selectedCouponType = ref("Individual")
    const couponType = ref([
        'Individual',
        'Membership'
    ])
    const dialogRef = inject('dialogRef');

    const search = (event) => {
        call.get("frappe.desk.search.search_link",{ 
            txt: event.query,
            doctype: "Customer",
            ignore_user_permissions: 0,
            reference_doctype: "Sale Coupon"
         }).then((res)=>{
            items.value = res.message
         })
    }
    function chooseCallback(event){
        console.log("chooseCallback",event)
    }
    function uploadCallback (event){
        console.log("uploadCallback",event)
    }
    function clearCallback(event){
        console.log("clearCallback",event)
    }
    const uploadEvent = (callback) => {
    totalSizePercent.value = totalSize.value / 10;
    callback();
};
    function memberFocus(event){
        call.get("frappe.desk.search.search_link",{ 
            txt: "",
            doctype: "Customer",
            ignore_user_permissions: 0,
            reference_doctype: "Sale Coupon"
         }).then((res)=>{
            items.value = res.message
         })
    }
    function expiryChange(event){
        expiry_date.value = event;
        saleCoupon.value.expiry_date = moment(event).format('YYYY-MM-DD')
    }
    function onSave(){
        isSaving.value=true
        saleCoupon.value.price = price.value
        if (!saleCoupon.value.coupon_number){
            toast.add({ severity: 'warn', summary: 'Validation', detail: 'Please enter Coupon Number', life: 3000 });
            return
        }
        if (!saleCoupon.value.membership){
            toast.add({ severity: 'warn', summary: 'Validation', detail: 'Please select membership or Member name', life: 3000 });
            return
        }
        db.createDoc('Sale Coupon',saleCoupon.value).then((doc) => {
            toast.add({ severity: 'success', summary: 'Sucecss', detail: 'Coupon saved succeess.', life: 3000 });
            dialogRef.value.close();
            isSaving.value=true;
        })
        .catch((error) => {
            toast.add({ severity: 'error', summary: 'Validation', detail: JSON.parse(JSON.parse(error['_server_messages'])[0]).message, life: 3000 })
            isSaving.value=true;
        });
    }
    function closeDialog(){
        dialogRef.value.close();
    }
    const onAdvancedUpload = () => {
        toast.add({ severity: 'info', summary: 'Success', detail: 'File Uploaded', life: 3000 });
    };
    watch(selectedMember, async (member) =>{
        saleCoupon.value.membership=member.value
    })
    
    watch(limitVisit, async (value) =>{
        if (value <= 0){
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
</style>