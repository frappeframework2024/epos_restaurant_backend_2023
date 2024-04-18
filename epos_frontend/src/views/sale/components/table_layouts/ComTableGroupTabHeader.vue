<template>
    <v-bottom-navigation align-tabs="center" v-if="tableLayout.table_groups && tableLayout.table_groups.length > 1">
        <v-row no-gutters>
            <v-col cols="12" md="6" lg="4" v-if="!mobile && tableSaleColor">
                <ComSaleStatusInformation />
            </v-col>
            <v-col cols="12" :md="tableSaleColor ? '6' : '12'" :lg="!mobile && tableSaleColor ? '4' : '12'">
                <v-tabs align-tabs="center" height="100%" v-model="tableLayout.tab" center-active>
                    <v-tab style="text-transform: none;" v-for="g in tableLayout.table_groups" :key="g.key"
                        :value="g.key" :disabled="tableLayout.tab == g.key" @click="onTabClick(g.key)">
                        {{ getGroupName(g) }}
                    </v-tab>
                </v-tabs>
            </v-col>
            <v-col cols="1" md="1" lg="4" v-if="!mobile && tableSaleColor"></v-col>
        </v-row>
    </v-bottom-navigation>
</template>
<script setup>
import { inject, ref } from '@/plugin';
import { useDisplay } from 'vuetify'
import ComSaleStatusInformation from '@/views/sale/components/ComSaleStatusInformation.vue';
const tableLayout = inject("$tableLayout");
const { mobile } = useDisplay()

const props = defineProps({
    tableSaleColor: Boolean
})

function getGroupName(g) {
    const l = localStorage.getItem("lang")
    if (l != null) {
        if (l == "km") {
            return g.table_group_kh;
        }
        else {
            return g.table_group;
        }
    }
    return g.table_group
}

function onTabClick(key) {
    localStorage.setItem("__tblLayoutIndex", key)
    tableLayout.tab = key;
}
</script>