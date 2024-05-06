<template>
    <ComModal :mobileFullscreen="true" @onClose="onClose()" width="500px" :hideOkButton="true" titleOKButton="Print">
      <template #title>
        {{$t('Switch POS Profile')}}
      </template>
      <template #content>
        <template v-if="posProfiles">
          <v-btn v-for="pos in posProfiles" class="my-2" height="80px" color="primary" elevated variant="flat" @click="onPOSProfileClick(pos.name)" block
           prepend-icon="mdi-network-pos"  elevation="2" 
           size="x-large" >
            {{pos.name}}
          </v-btn>
        </template>
        <template v-else>
          {{$t("No POS Profile")}}
        </template>
      </template>
    </ComModal>
  </template>
<script setup>
import { defineEmits,confirm, i18n,ref,inject} from "@/plugin";
import ComModal from "./ComModal.vue";
import { createToaster } from "@meforma/vue-toaster";
const gv = inject('$gv')
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const { t: $t } = i18n.global;
const emit = defineEmits(["resolve"])
const toaster = createToaster({position:"top"});

const posProfiles = ref([])
db.getDocList("POS Profile",{
  fields: ['name'],
  filters: [['name', '!=', localStorage.getItem("pos_profile")],['is_edoor_profile', '=', 0],["business_branch","=",gv.setting.business_branch]],
}).then((docs) => {
  posProfiles.value=docs
}).catch((error) => console.error(error));

async function onPOSProfileClick(profile){
  if (await confirm({ title: $t("Switch POS Profile"), text: $t("Please make sure to switch the POS profile.") })) {
       call.get("epos_restaurant_2023.api.api.get_system_settings",{
        pos_profile:profile,
        device_name: localStorage.getItem("device_name"),
       }).then((result)=>{
        console.log(result)
          localStorage.removeItem("__tblLayoutIndex")
          localStorage.setItem("pos_profile",profile)
          localStorage.setItem("table_groups",JSON.stringify(result.message.table_groups || null))
          localStorage.setItem("setting",JSON.stringify(result.message))
          //Reload Window
          location.reload();
            const apkipa = localStorage.getItem('apkipa');
            if ((apkipa || 0) == 1) {
                if ((localStorage.getItem('flutterWrapper') || 0) == 1) {
                    flutterChannel.postMessage(JSON.stringify({ "action": "mobile_reload" }));
                }
                else {
                    window.ReactNativeWebView.postMessage("mobile_reload");
                }

            }
          emit('resolve', false);
       }).catch((error)=>{
          emit('resolve', false);
       })
    }
}
function onClose() { 
    emit('resolve', false);
  }
</script>