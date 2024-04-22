<template>
   
        <ComKodKpiBox
      name="New Order"
      :quantity="kod.kpi.new_order"
      iconName="mdi-new-box"
      bgColorClass="bg-green"
      :iconSize="30"
    />
    <ComKodKpiBox
      name="Pending Order"
      :quantity="kod.kpi.pending_order"
      iconName="mdi-timer-sand"
      bgColorClass="bg-red-400"
      :iconSize="30"
    />
    <ComKodKpiBox
      name="Processing Order"
      :quantity="kod.kpi.processing_order"
      iconName="mdi-progress-clock"
      bgColorClass="bg-sky-500"
      :iconSize="30"
    />
    <ComKodKpiBox
      name="Done"
      :quantity="kod.kpi.done"
      iconName="mdi-checkbox-marked"
      bgColorClass="bg-blue-500"
      :iconSize="30"
    />
</template>
<script setup>
import ComKodKpiBox from "@/views/kitchen_order_display/components/ComKodKpiBox.vue"
    import { inject } from 'vue';
    const kod = inject("$kod")
</script>