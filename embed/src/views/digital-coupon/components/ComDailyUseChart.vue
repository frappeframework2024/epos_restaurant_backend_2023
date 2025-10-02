<!-- MyChart.vue -->
<template>
  <VChart 
    class="chart" 
    :option="chartOption" 
    :autoresize="true"
  />
</template>

<script setup>
import { ref } from "vue";
import { use } from "echarts/core";
import VChart, { THEME_KEY } from "vue-echarts";

// import needed pieces from echarts
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from "echarts/components";

// register them
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
]);

 

const chartOption = ref({
  title: {
    text: "Example Bar Chart"
  },
  tooltip: {},
  legend: {
    data: ["Sales"]
  },
  xAxis: {
    data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  },
  yAxis: {},
  series: [
    {
      name: "Sales",
      type: "bar",
      data: [5, 20, 36, 10, 10, 20, 15]
    }
  ]
});
</script>

<style scoped>
.chart {
  width: 100%;
  height: 400px;
}
</style>
