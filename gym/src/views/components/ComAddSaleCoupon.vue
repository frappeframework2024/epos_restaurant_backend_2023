<template>
    <div>
        <div class="col-12">
            <FileUpload @select="onFilesSelected($event)" name="file" :customUpload="true" :multiple="true"
                accept="jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.xls,.xlsx" :maxFileSize="1000000000">
                <template #header="{ chooseCallback,files }">
                    <div class="flex flex-wrap justify-content-between align-items-center flex-1 gap-2">
                        <div class="flex gap-2">
                            <Button @click="chooseCallback" icon="pi pi-images" rounded outlined></Button>
                        </div>
                    </div>
                </template>
                <template #content="{ files,removeFileCallback }">
                    <div v-if="files.length > 0" class="flex gap-3  flex-wrap ">
                        <template v-for="d in selectdFile.files">
                           
                            <div class="relative flex justify-content-between flex-column align-items-center flex-wrap border-1 border-round-sm w-6rem border-300">
                                <img style="width:60px" :src="d.objectURL" class="mt-2"/>
                                <div class="text-xs text-center bg-cyan-50 text-600 p-2 border-300 file-wrapper-name w-full text-overflow-ellipsis" >
                                    {{ d.name }}
                                </div>
                                <Button @click="onRemoveImage(removeFileCallback,d)" class="absolute remove-image" size="small" severity="danger" text  rounded icon="pi pi-times" ></Button>
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
        <div class="grid coupon_input_info">

            <div class="col-6 lg:col-4">
                <label>Coupon Number <span class="text-red-500">*</span></label><br />
                <InputText style="width: 100%" v-model="saleCoupon.coupon_number" />
            </div>
            <div class="col-6 lg:col-4">
                <label>Coupon Type</label><br />
                <Dropdown v-model="selectedCouponType" editable :options="couponType" placeholder="Select Coupon Type"
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


                <Calendar style="width: 100%;" @date-select="expiryChange" :modelValue="expiry_date" showIcon
                    :showOnFocus="false" />
            </div>
        </div>
        <div class="flex justify-content-end mt-5 bg-white p-2"
            style="position: absolute;bottom: 0;width: 100%;left: 0;">
            <div class="card flex flex-wrap gap-2">
                <Button @click="onSave()" :loading="isSaving" label="Save" icon="pi pi-check" />
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
import { ref, inject, watch } from 'vue'
import SaleCoupon from "../SaleCoupon.vue";
import { useToast } from "primevue/usetoast";
import moment from 'moment';
const isSaving = ref(false)
const toast = useToast();
const frappe = inject("$frappe")
const call = frappe.call();
const items = ref([]);
const saleCoupon = ref({})
const selectedMember = ref(undefined)
const price = ref(0)
const expiry_date = ref()
const limitVisit = ref(0)
const VisitBalance = ref(0)
const selectedCouponType = ref("Individual")
const selectdFile=ref({})
const couponType = ref([
    'Individual',
    'Membership'
])
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
function expiryChange(event) {
    expiry_date.value = event;
    saleCoupon.value.expiry_date = moment(event).format('YYYY-MM-DD')
}
function onSave() {
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
    //Prepare Data To Save


    call.post()

    // const formdata = new FormData();
    // formdata.append("file", selectdFile.value.files[0],selectdFile.value.files[0].name);
    // const myHeaders = new Headers();
    // myHeaders.append("Authorization", "token b84df842943ec01:91cdd717594ca60");
    // myHeaders.append("Cookie", "full_name=Guest; sid=Guest; system_user=no; user_id=Guest; user_image=");
    //     const requestOptions = {
    // method: "POST",
    // headers: myHeaders,
    // body: formdata,
    // redirect: "follow"
    // };
    //     fetch("http://192.168.10.19:8080/api/method/upload_file", requestOptions)
    //     .then((response) => response.text())
    //     .then((result) => console.log(result))
    //     .catch((error) => console.error(error));
    // call.post("epos_restaurant_2023.gym.doctype.sale_coupon.sale_coupon.save_coupon_and_files",{
    //     file:formdata
    // }).then((res)=>{

    // })

    //db.createDoc('Sale Coupon',saleCoupon.value).then((doc) => {
   //     toast.add({ severity: 'success', summary: 'Sucecss', detail: 'Coupon saved succeess.', life: 3000 });
     //   const fileArgs = {
    //        /** If the file access is private then set to TRUE (optional) */
   //         "isPrivate": true,
   //         "doctype": "Sale Coupon",
            /** Docname associated with the file (mandatory if doctype is present) */
    //        "docname": doc.name,
   //     }
    //    file.uploadFile(
   //         selectdFile.value.files,
   //         fileArgs,
            /** Progress Indicator callback function **/
    //        (completedBytes, totalBytes) => console.log(Math.round((completedBytes / totalBytes) * 100), " completed")
     //   )
     //   .then(() => console.log("File Upload complete"))
      //  .catch(e => console.error(e))
  //      dialogRef.value.close();
  //      isSaving.value=false
 //   })
   // .catch((error) => {
    //    console.log(error)
        // toast.add({ severity: 'error', summary: 'Validation', detail: JSON.parse(JSON.parse(error['_server_messages'])[0]).message, life: 3000 })
       // isSaving.value=false
 //   }); 
    
}
function closeDialog() {
    dialogRef.value.close();
}
function onRemoveImage(callback , image){
    selectdFile.value.files = selectdFile.value.files.filter(obj => obj.name !== image.name)
    callback()
}
const onFilesSelected = (events) => {
    selectdFile.value = events
};
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