<template>
    <v-dialog v-model="open">

        <v-card>
            <v-card-text>
                <pre>{{ term }}</pre>
            </v-card-text>
            <v-card-actions class="justify-end">
                <v-btn @click="decline" style="background-color: #b00020;color: white;">{{ 'Reject' }}</v-btn>
                <v-btn @click="confirm" style="background-color: #16a34a;color: white;">{{ 'Accept' }}</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { defineProps, defineEmits, ref,onMounted ,inject} from '@/plugin'
import { comPopup2Dialog } from '../utils/dialog.ts';
const open = ref(true)
const frappe = inject("$frappe")
const db = frappe.db();
let term = ref("")
const props = defineProps({
    params: {
        type: Object,
        required: true
    },
})

onMounted(async () => { 
    let doc = await db.getDoc("Business Branch",props.params.business_branch)
    term.value = doc.term_and_condition
})

const emit = defineEmits(["resolve"])

function confirm() {
   emit('resolve', true);
}
function decline() {
    emit('resolve',false);
}
</script>