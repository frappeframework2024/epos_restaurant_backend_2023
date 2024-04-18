<template>
    <v-card :subtitle="$t('Working Day and Cashier Shift Report')">
        <v-card-text class="report-list-container"> 
            <ComPlaceholder :loading="workingDayReports === null " :is-not-empty="workingDayReports?.length > 0">
                <template v-for="(c, index) in workingDayReports" :key="index">
                    <v-card :color="activeReport.report_id == c.name ? 'info' : 'default'" :variant="activeReport.report_id == c.name || c.cashier_shifts.find(r=>r.name == activeReport.report_id) ? 'tonal' : 'text'" class="bg-gray-200 my-2 subtitle-opacity-1" @click="onWorkingDay(c)">
                        <template v-slot:title>
                            <div class="flex justify-between">
                                <div>{{ c.name }}</div>
                                <div>
                                    <v-chip v-if="c.is_closed" color="error" size="small"
                                        variant="elevated">{{ $t('Closed') }}</v-chip>
                                    <v-chip v-else color="success" size="small" variant="elevated">{{ $t('Opening') }}</v-chip>
                                </div>
                            </div>
                        </template>
                        <template v-slot:subtitle>
                            <div>
                                <div><v-icon icon="mdi-calendar" size="x-small" /> <span class="font-bold">{{
                                    c.posting_date
                                }}</span> {{ $t('was opening by') }} <span class="font-bold">{{ c.owner }}</span></div>
                                <div v-if="c.is_closed">
                                    <v-icon icon="mdi-calendar-multiple" size="x-small" /> <span
                                        class="font-bold">{{ c.closed_date }}</span> {{ $t('was closed by') }} <span
                                        class="font-bold">{{ c.modified_by }}</span>
                                </div>
                                <div><v-icon icon="mdi-note-text" size="x-small"></v-icon> {{ $t('Total Shift') }}: <span
                                        class="font-bold">{{getCashierShifts(c).length }}</span></div>
                            </div>
                        </template>
                    </v-card>
                    <div v-if="activeReport.report_id == c.name || getCashierShifts(c).find(r=>r.name == activeReport.report_id)">
                        <div class="-m-1">
                            <v-btn :color="item.name == activeReport.report_id ? 'info' : 'default'" variant="tonal" stacked class="m-1" v-for="(item, index) in getCashierShifts(c)" :key="index" @click="onCashierShift(item)">
                                <div>{{ moment(item.creation).format('h:mm:ss A') }}</div>
                                <div class="text-xs">#{{ item.name }}</div>
                            </v-btn>
                        </div>
                    </div>
                    <div class="pt-2">
                        <hr/>
                    </div>
                </template>
            </ComPlaceholder>
        </v-card-text>
    </v-card>
</template>
<script setup>
import { inject } from '@/plugin'
const props = defineProps({
    workingDayReports:Object,
    activeReport:Object
})
const moment = inject('$moment');
const pos_profile = localStorage.getItem("pos_profile");
const emit = defineEmits(["onWorkingDay", "onCashierShift"])

function getCashierShifts(working_day){
    return working_day.cashier_shifts.filter((r)=>r.pos_profile==pos_profile);
}

function onWorkingDay(value) {
    emit('onWorkingDay', value)
}
function onCashierShift(item) {
    emit('onWorkingDay', item)
}
</script>