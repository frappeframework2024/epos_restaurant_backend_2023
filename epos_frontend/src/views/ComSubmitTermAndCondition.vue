<template>
    <v-dialog fullscreen v-model="open">

        <v-card>
            <v-card-text>
                <h1>{{ term }}</h1>
            </v-card-text>
            <v-card-actions>
                <v-btn color="error" @click="decline">{{ 'Reject' }}</v-btn>
                <v-btn color="success" @click="confirm">{{ 'Accept' }}</v-btn>
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
async function onOpen() {
    const result = await comPopup2Dialog({
        text: "Do you like my name is pheakdey?"
    });
    if (result) { 
        // const data =JSON.parse(result.toString()) 
        // alert(data.name)
    }
}
</script>