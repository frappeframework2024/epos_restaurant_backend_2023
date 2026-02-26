<template>
    <v-dialog v-model="open">
        <v-card>
           <div v-html="message">
           </div>
            <v-card-actions class="justify-center" style="margin-top: 50px;">
                <v-btn @click="confirm" style="background-color: #16a34a;color: white;height: 50px;width: 100px;">{{ 'OK' }}</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { defineProps, defineEmits, ref,onMounted ,inject} from '@/plugin'
const open = ref(true)
const frappe = inject("$frappe")
const db = frappe.db();
let message = ref("")
const props = defineProps({
    params: {
        type: Object,
        required: true
    },
})

onMounted(async () => { 
    let doc = await db.getDoc("Business Branch",props.params.business_branch)
    if((props.params.order_limit || 0) == 1){
         message.value = doc.order_limit_message
    }
    if((props.params.time_limit || 0) == 1){
         message.value = doc.order_timer_limit_mesaage
    }
})

const emit = defineEmits(["resolve"])

function confirm() {
   emit('resolve', true);
}
</script>