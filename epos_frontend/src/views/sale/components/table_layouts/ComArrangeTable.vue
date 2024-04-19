<template>
    <template v-for="g in tableLayout.table_groups">
        <v-window-item :value="g.key"
            v-bind:style="{ 'background-image': 'url(' + g.background + ')', 'min-height': `calc(100vh - ${!tableStatusColor && tableLayout.table_groups.length <= 1 ? 118 : 174}px)`, 'background-size': '100% 100%' }"
            class="bg-center overflow-auto relative table-bg">
            <Vue3DraggableResizable v-for="(t, index) in g.tables" :key="index" v-model:x="t.x" v-model:y="t.y" :w="t.w"
                :h="t.h" :draggable="true" :resizable="true" @resize-end="tableLayout.onResizeEnd(t)($event)">

                <div class="flex items-center justify-center h-full"
                    v-bind:style="{ 'background-color': '#002ac1', 'color': '#fff', 'overflow': 'hidden', 'border-radius': `${t.shape == 'Circle' ? '100%' : ''}` }">
                    {{ t.tbl_no }}
                </div>
            </Vue3DraggableResizable>
        </v-window-item>

    </template>



</template>
<script setup>
import Vue3DraggableResizable from 'vue3-draggable-resizable'
import { inject } from '@/plugin';

const tableLayout = inject("$tableLayout");
tableLayout.tab = localStorage.getItem("__tblLayoutIndex")


</script>
<style scoped>
@media (max-width: 1920.98px) {
    .table-bg {
        background-size: 1920px 1080px !important;
        background-attachment: local;
        background-position: center center;
    }
}

@media (min-width: 1921px) {
    .table-bg {
        background-size: 100% 100vh !important;
        background-attachment: local;
        background-position: center center;
    }
}
</style>