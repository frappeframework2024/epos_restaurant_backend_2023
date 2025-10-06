<template>
    <div class="card justify-center">
       
       <form @submit.prevent="changePassword">
            <div class="field mb-4">
                <label class="block mb-2 font-medium">{{t("Current Password")}}</label>
                <input 
                v-model="oldPassword"
                type="password" 
                class="p-inputtext w-full border-1 border-gray-400 border-round-md p-2"
                required
                />
            </div>
            <div class="field mb-4">
                <label class="block mb-2 font-medium">{{t("New Password")}}</label>
                <input 
                v-model="newPassword"
                type="password" 
                class="p-inputtext w-full border-1 border-gray-400 border-round-md p-2"
                required
                />
            </div>

             <div class="field mb-5">
                <label class="block mb-2 font-medium">{{t("Confirm New Password")}}</label>
                <input
                v-model="confirmPassword"
                type="password" 
                class="p-inputtext w-full border-1 border-gray-400 border-round-md p-2"
                required
                />
            </div>
             
            <Button :loading="loading" @click="changePassword" :label="t('Change Password')" class="w-full" severity="success"/>
       </form>
    </div> 
</template>

<script setup>
import {ref} from 'vue'
import { getApi,inject } from "@/plugin";
 import Button from 'primevue/button';

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const getpass = ref('')
const loading = ref(false)
const dialogRef = inject('dialogRef')
async function changePassword(){

    loading.value = true;
   await getApi("management_coupon.change_password", {
        old_password: oldPassword.value,
        new_password: newPassword.value,
        confirm_password: confirmPassword.value
    })
    .then(result => {
       dialogRef.value.close()
       app.showSuccess("Change Password Success!!")
    })
    .catch(err => {
        console.error(err);
        loading.value = false;
    });
}
</script>