<!-- MyChart.vue -->
<template>
  <h2 class="font-bold mb-2">{{t("Daily use transactions")}}</h2>
    
  
    <div>
       
        <Chip v-for="w in weeks" @click="onChangeWeek(w)" class="mr-2">
            {{ t(w.title) }}
        </Chip>
    </div>

  <VChart 
    class="chart" 
    :option="chartOption" 
    :autoresize="true"
  />
</template>

<script setup>
import { computed, ref } from "vue";
import { use } from "echarts/core";
import VChart, { THEME_KEY } from "vue-echarts";
import {getThisWeekAndLastWeekDate} from "@/plugin"

import Chip from 'primevue/chip';

const t = window.t;

// import needed pieces from echarts
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from "echarts/components";
import dayjs from "dayjs";

const props = defineProps({
  data:Object
})


const weeks = ref(getThisWeekAndLastWeekDate())
const currentWeek = ref(weeks.value.find(x=>x.title == 'This Week'))
// register them
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
]);


function onChangeWeek(w){
   
    currentWeek.value = w
}
const chartOption = computed(()=>{
    return {
  tooltip: {},
  legend: {
    data: [t("Used Coupon Transaction")]
  },
  xAxis: {
    data:  props.data?.filter(x=>dayjs(x.date)>=currentWeek.value.start && dayjs(x.date)<=currentWeek.value.end ).map(d=>d.date),
    axisLabel: {
      formatter: (value) => t(dayjs(value).format("ddd") )
    }
  },
  yAxis: {},
  series: [
    {
      name: t("Used Coupon Transaction"),
      type: "bar",
      data: props.data?.filter(x=>dayjs(x.date)>=currentWeek.value.start && dayjs(x.date)<=currentWeek.value.end ).map(d=>d.value),
      itemStyle: {
            color: "#22c55e",
      borderRadius: [20, 20, 0, 0]  
    },
    emphasis: {
          focus: "series",
          itemStyle: {
            color: "#4ade80", // brighter green on hover
            shadowBlur: 15,
            shadowColor: "rgba(34, 197, 94, 0.5)", // soft green glow
          }
        }
    }
  ]
}
})
 
</script>

<style scoped>
.chart {
  width: 100%;
  height: 400px;
}
</style>
