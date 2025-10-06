<template>
    <ComDialogContent>

        <div class="mb-4">
            <label for="employee_name">{{ t("Employee Name") }}</label>
            <InputText id="employee" v-model="doc.employee_name" fluid />

        </div>
        <div class="mb-4">
            <label for="phone_number">{{ t("Phone Number") }}</label>
            <InputText id="phone_number" v-model="doc.phone_number_1" fluid />

        </div>
    
        <div class="mb-4">
            <label for="email">{{ t("Email") }}</label>
            <InputText id="email" v-model="doc.email_address" fluid />

        </div>
        
        <div class="mb-4">
            <label for="address">{{ t("Address") }}</label>
            <InputText id="addresa" v-model="doc.address" fluid />

        </div>



        <template #footer>
             
            <Button class="w-full" type="button" :label="t('Save')"  :loading="saving"  @click="onSave" />


        </template>
    </ComDialogContent>
</template>
<script setup>
import Button from 'primevue/button'

import InputText from 'primevue/inputtext';
import { getDoc,updateDoc } from "@/plugin"
import { inject, onMounted, ref } from 'vue';

const dialogRef = inject("dialogRef")
const t = window.t;
const doc = ref({})

const loading = ref(false)
const saving = ref(false)

async function getEmployeeDoc() {
    loading.value = true;
    await getDoc("Employee", dialogRef.value.data.employee_code).then(result => {
        doc.value = result
    })

    loading.value = false;

}

async function onSave(){
    saving.value = true;
    await updateDoc("Employee",dialogRef.value.data.employee_code,doc.value).then(result=>{
        dialogRef.value.close("success");
           app.showSuccess(t("Update information successfully"))

    }).catch(err=>{
        saving.value = false;
    })
    

    
    saving.value = false;
}

onMounted(async () => {
    await getEmployeeDoc()
})

</script>