<template>
    <ComModal :mobileFullscreen="true" @onClose="onClose()" width="1200px" :hideOkButton="true">
      <template #title>
        {{ $t('Redeem Item') }}
      </template>
      <template #content>
        {{ parkItemList }}
      </template>
    </ComModal>
  </template>
  <script setup>
  import {defineProps, defineEmits, ref, inject, createToaster, i18n, onMounted } from "@/plugin"
  import ComModal from "@/components/ComModal.vue";
  const moment = inject("$moment")
  
  const { t: $t } = i18n.global;
  
  const isLoading = ref(true);
  
  const frappe = inject("$frappe");
  const emit = defineEmits(["resolve"])
  const gv = inject('$gv');
  const toaster = createToaster({ position: "top-right" });
  
  const db = frappe.db();
  const call = frappe.call();
  
  const props = defineProps({
    params: {
      type: Object,
      required: true,
    }
  })
  const parkItemList = ref([])
  
  onMounted(() => {
    _onInit()
  });

  
  function _onInit() {
    isLoading.value = true;
    call.get("epos_restaurant_2023.selling.doctype.sale.sale.get_park_item_to_redeem", { business_branch: gv.setting.business_branch }).then((res) => {
        parkItemList.value=res.message
        isLoading.value = false;
    }).catch((err) => {
        isLoading.value = false;
    });
  }
  
  function onClose() {
    emit('resolve', false);
  }
  </script>