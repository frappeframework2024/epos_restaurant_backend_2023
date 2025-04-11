<template>
    <ComModal width="1000px" :loading="is_loading" @onClose="onClose" @onOk="onConfirm" titleOKButton="Confirm">
        
        <template #title>
            {{ $t('Stop Timer') }}
        </template>
        <template #content>
            <div class="d-block d-md-flex mb-3" style="justify-content: space-between;">
                <div>
                    <span class="ttl-size">{{ $t("Time In") }}: </span>
                    <input class="calendar-custom p-1 w-100" type="datetime-local" v-model="data.time_in" >
                </div>
                <div>
                    <span class="ttl-size">{{$t("Time Out")}}: </span>
                    <input class="calendar-custom p-1 w-100" type="datetime-local" v-model="data.time_out" >
                </div>
            </div>   
        </template>

    </ComModal>
</template>
<script setup>
import { ref,inject,onMounted,watch,createToaster ,i18n} from '@/plugin'
import { defineEmits } from 'vue'; 
import moment from '@/utils/moment.js'; 

const dialogRef = inject('dialogRef');
 

const emit = defineEmits(["click"])
const { t: $t } = i18n.global;

const data = ref(JSON.parse(JSON.stringify(dialogRef.value.data)))

console.log(data)

let is_loading=ref(false)

if (!data.value.time_out){
    data.value.time_out=moment(new Date).format('YYYY-MM-DD HH:mm')
}

if (!data.value.time_in){
    data.value.time_in=moment(new Date).format('YYYY-MM-DD HH:mm')
}
 

function onConfirm() {
    is_loading.value=true 
        dialogRef.value.close(
            { 
                time_in: moment(data.value.time_in).format('yyyy-MM-DD HH:mm:ss'),
                time_out: moment(data.value.time_out).format('yyyy-MM-DD HH:mm:ss'),
            }
        );
        is_loading.value=false 
}

function onClose() {
    dialogRef.value.close()
}
 
onMounted(() => { 
})

</script>
<style scoped>
    .calendar-custom{ 
        font-size: 24px;
        color: #3468C0; 
        border: 2px solid;
        border-radius: 5px;
    }
    .calendar-custom:focus-visible{
        outline: 0;
    }
    .ttl-size{
        font-size: 24px;
        color: #D63484;
    }
    table, th, td {
        border: 1px solid #E5E1DA;
    } 
    td, th{
        padding: 3px;
    }
    @media (max-width: 768px) {
        .calendar-custom{
            font-size: 18px;
        }
    }
</style>