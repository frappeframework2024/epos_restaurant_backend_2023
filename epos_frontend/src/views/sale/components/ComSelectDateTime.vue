<template>
    <ComModal @onClose="onClose" @onOk="onClick()" titleOKButton="Set Time In">
        <template #title>
            {{ $t('Timer') }}
        </template>
        <template #content>
            <div>
                <v-alert type="info"
                    text="Please enter the time when the player started playing the game. If the player has not started playing yet, please click on the ‘Set Time In Later’ button."
                ></v-alert>
            </div>
            {{ time_in }}
            <input type="datetime-local" v-model="time_in.data" >
        </template>
        <template #action>
                <v-btn variant="flat" type="button" color="primary" :disabled="loading" v-if="!hideOkButton" @click="setTimeLaterClick()">
                       {{$t("Set Time In Later")  }}
                    </v-btn>
        </template>
    </ComModal>
</template>
<script setup>
import { ref,computed } from '@/plugin'
import { defineEmits } from 'vue';
import { useDisplay } from 'vuetify';
import moment from '@/utils/moment.js';

const { mobile } = useDisplay()

const props = defineProps({
    params:Object
})

const time_in=computed(()=>props.params)


// const date = ref("2024-01-09 13:49");
const default_date = moment(new Date).format('YYYY-MM-DD HH:mm')
const date =  ref(default_date)
const emit = defineEmits(["click"])




function onClick() {
    emit("resolve",date.value);
}
function setTimeLaterClick() {
    emit("resolve",'Set Later');
}
function onClose() {
    emit("resolve", false);
}
</script> 