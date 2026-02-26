<!-- SettingsItem.vue -->
<template>
  <div class="surface-card shadow-1 border-round p-3 mb-1 flex align-items-center justify-content-between cursor-pointer">
    <div class="flex align-items-center gap-3">
      <div :class="['w-3rem h-3rem flex justify-content-center align-items-center border-circle', bgColor]">
        <i :class="['pi', icon, iconColor, 'text-xl']"></i>
      </div>

      <div>
        <div class="font-medium">{{ t(title) }}</div>
        <small class="text-500">{{ t(subtitle) }}</small>
      </div>
    </div>
    <i class="pi pi-chevron-right text-500"></i>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'pi-lock' },
  iconColor: { type: String, default: 'text-orange-500' },
  bgColor: { type: String, default: 'bg-red-100' },
  title: { type: String, required: true },
  subtitle: { type: String, required: true }
})
const t = window.t;
</script>
