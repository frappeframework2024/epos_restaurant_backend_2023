<template>
 

  <div class="flex flex-column h-full">
    <!-- Header -->
    <div class="bg-primary p-4 text-center flex flex-column align-items-center justify-content-center">
      <Avatar 
        :image="homeData?.user_info?.photo" 
        size="xlarge" 
        class="mb-3 border-circle" 
         shape="circle"
         v-if="homeData?.user_info?.photo"
      />
      <Avatar v-else :label="avatarLetter" class="mr-2 bg-green-400" size="xlarge" shape="circle"  />
        

      <h2 class="m-0 text-white">{{ homeData?.user_info?.full_name }}</h2>
      <span class="text-white-alpha-80" v-if="homeData?.user_info?.position">{{ homeData?.user_info?.position }}</span>
      <small class="text-white-alpha-70">{{ homeData?.user_info?.employee_code }}</small>
    </div>

    <!-- Profile Options -->
    <div class="p-3 h-full">
     <ComButtonListSetting
  icon="pi-user"
  iconColor="text-primary"
  bgColor="bg-blue-100"
  title="Update Profile"
  subtitle="Edit your personal information"
  @click="onEditUserInformtion"
/>

<ComButtonListSetting
  icon="pi-lock"
  iconColor="text-orange-500"
  bgColor="bg-red-100"
  title="Change Password"
  subtitle="Update your security credentials"
  @click="goToPassword"
/>

<ComButtonListSetting
  icon="pi-globe"
  iconColor="text-green-500"
   bgColor="bg-green-100"
  title="App Language"
  subtitle="Change the language used"
  @click="goToLanguage"
/> 
          <!-- Sign Out -->
    <div class="mt-3" >
      <Button 
        :label="t('Sign Out')" 
        icon="pi pi-sign-out" 
        class="p-button-danger w-full"
        @click="onSignOut"
        :loading="signing_out" 
      />
    </div>
    </div>
  </div>
</template>

<script setup>
import ComButtonListSetting from '@/views/digital-coupon/components/ComButtonListSetting.vue'
import Avatar from 'primevue/avatar';
import {useHome} from "@/hooks/ecoupon/useHome.js"
import Button from 'primevue/button';
import { computed, onMounted, ref } from 'vue';
import { useDialog } from 'primevue/usedialog'
import ComEditInfo from "@/views/digital-coupon/my-accounts/ComEditInfo.vue"
import ComChangePassword from "@/views/digital-coupon/my-accounts/ComChangePassword.vue"
import ComChangeLang from "@/views/digital-coupon/my-accounts/ComChangeLang.vue"
import {getApi} from "@/plugin"
const dialog = useDialog();
import { FrappeApp } from 'frappe-js-sdk';
const frappe = new FrappeApp();
const auth = frappe.auth()
const signing_out = ref(false)

const {homeData} = useHome()

const avatarLetter = computed(() => {
  if (homeData.value?.user_info?.full_name){
    return homeData.value?.user_info?.full_name.charAt(0) || ""
  }
  return "NA"
}
)

const onEditUserInformtion = () => {
    dialog.open(ComEditInfo, {
        data: homeData.value.user_info,
        props: {
            header: t('Edit Information'),
            style: {
                width: '50vw',
            },
            breakpoints:{
                '960px': '75vw',
                '640px': '95vw'
            },
            modal: true
        },
        onClose: (options) => {

    }
    });
}
const goToPassword = () => {
    dialog.open(ComChangePassword, {
        props: {
            header: t('Change Password'),
            style: {
                width: '50vw',
            },
            breakpoints:{
                '960px': '75vw',
                '640px': '95vw'
            },
            modal: true
        },
        onClose: (options) => {

    }
    });
}
const goToLanguage = () => {
    dialog.open(ComChangeLang, {
        props: {
            header: t('Change Language'),
            style: {
                width: '50vw',
            },
            breakpoints:{
                '960px': '75vw',
                '640px': '95vw'
            },
            modal: true
        },
        onClose: (options) => {

    }
    });
}


function onSignOut(){
  signing_out.value =true;
  auth
  .logout()
  .then(() => {
    
    window.location = "/login"
  })
  .catch((error) => {
    signing_out.value = false;
  });
}


onMounted(async ()=>{
  if (!homeData.value.user_info){
await getApi("management_coupon.get_user_info").then(result=>{
    homeData.value.user_info = result.message;
    
  })
  }
  
})


</script>
