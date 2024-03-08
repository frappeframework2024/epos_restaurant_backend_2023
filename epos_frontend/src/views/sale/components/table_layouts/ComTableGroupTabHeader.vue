<template>
    <!-- <v-tabs align-tabs="center" v-if="tableLayout.table_groups && tableLayout.table_groups.length > 1 && !mobile" v-model="tableLayout.tab">
        <v-tab v-for="g in tableLayout.table_groups" :key="g.key" :value="g.key">
            {{ getGroupName(g) }}
        </v-tab>
    </v-tabs> -->
 
    <v-bottom-navigation align-tabs="center" v-if="tableLayout.table_groups && tableLayout.table_groups.length > 1">
        <v-row no-gutters>
            <v-col cols="4">
                <ComSaleStatusInformation v-if="tableSaleColor"/>
            </v-col>
            <v-col>
                <v-tabs align-tabs="center" height="100%"  v-model="tableLayout.tab"  center-active>
                    <v-tab style="text-transform: none;" v-for="g in tableLayout.table_groups" :key="g.key" :value="g.key" :disabled="tableLayout.tab == g.key">
                        {{ getGroupName(g) }}
                    </v-tab>
                </v-tabs> 
            </v-col>
            <v-col cols="4"></v-col>
        </v-row>
    </v-bottom-navigation>  
 
</template>
<script setup>
import { inject } from '@/plugin';
import { useDisplay } from 'vuetify'
import ComSaleStatusInformation from '@/views/sale/components/ComSaleStatusInformation.vue';
const tableLayout = inject("$tableLayout");
const { mobile } = useDisplay()

const props = defineProps({
    tableSaleColor: Boolean
})


function getGroupName (g){
    const l = localStorage.getItem("lang")
    if(l!=null){
        if(l=="kh"){
            return g.table_group_kh;
        }
        else{
            return g.table_group;
        }
    }
    return g.table_group

}
</script>