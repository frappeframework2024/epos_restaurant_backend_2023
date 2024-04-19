<template>
    <div class="grid-cols-4 grid p-2 gap-2">
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
      bgColorClass="bg-lime-300"
      :iconSize="30"
    />
    <ComKodKpiBox
      name="Done"
      :quantity="kod.kpi.done"
      iconName="mdi-checkbox-marked"
      bgColorClass="bg-green-300"
      :iconSize="30"
    />
        </div>
</template>
<script setup>
import ComKodKpiBox from "@/views/kitchen_order_display/components/ComKodKpiBox.vue"
    import { inject } from 'vue';
    const kod = inject("$kod")
</script>