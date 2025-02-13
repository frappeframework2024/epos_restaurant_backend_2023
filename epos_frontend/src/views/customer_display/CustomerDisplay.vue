<template>
    <div class="wrap h-screen">
        <template v-if="!show_thankyou">
            <v-row class="h-full !m-0">
                <v-col class="h-full !p-0 a" cols="hide" xs="12" sm="7" md="7" lg="7" xl="7">
                    <ComCustomerDisplaySliceshow />
                </v-col>
                <v-col class="h-full !p-0" cols="12" xs="12" sm="5" md="5" lg="5" xl="5    ">
                    <ComCustomerDisplayOrderList :data="data" />
                </v-col>
            </v-row>
        </template>
        <template v-else>
            <ComCustomerDisplayThankyou :data="dataThankYou" />
        </template>
    </div>
</template>
<script setup>
import { inject } from '@/plugin';
import { ref } from 'vue';
import ComCustomerDisplaySliceshow from './ComCustomerDisplaySliceshow.vue';
import ComCustomerDisplayThankyou from './ComCustomerDisplayThankyou.vue';
import ComCustomerDisplayOrderList from './ComCustomerDisplayOrderList.vue';
const data = ref({})
const dataThankYou = ref({})
const socket = inject("$socket")
const gv = inject("$gv");
const show_thankyou = ref(false)


/// key = business branch + pos profile + device id
socket.on("ShowOrderInCustomerDisplay", async (arg, show, key) => {
 
    const device_setting = JSON.parse(localStorage.getItem("device_setting"));
	const device_id = device_setting?.device_id||"";
    const pos_profile = localStorage.getItem("pos_profile");
    const business_branch = decodeURIComponent(gv.setting?.business_branch);
    const _key = `${business_branch}_${pos_profile}_${device_id}`;
    console.log({"pub": _key, "sub":key});


    

    if(key == _key){
        data.value = arg;
        if (Object.entries(data.value).length > 0) {
            dataThankYou.value = JSON.parse(JSON.stringify(data.value))
        }

        if (show == 'paid') {
            show_thankyou.value = true
            await setTimeout(onHideThankYou, 50000)
        }
        else if (show == "new") {
            onHideThankYou()
        }
    }

})

function onHideThankYou() {
    show_thankyou.value = false
}
</script>
<style scoped></style>