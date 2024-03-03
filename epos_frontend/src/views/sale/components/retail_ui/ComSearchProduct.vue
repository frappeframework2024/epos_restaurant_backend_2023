<template>
    <ComModal @onClose="onClose(false)" :fullscreen="true" :hide-ok-button="true" :hide-close-button="true">
        <template #title>
            {{ params.title }}
        </template>

        <template #bar_more_button>

        </template>

        <template #content>
            <div class="search-box my-0 mx-auto" :class="small ? 'w-full' : 'max-w-[350px]'">
                <ComInput autofocus keyboard variant="outlined" :placeholder="$t('Search...')"
                    prepend-inner-icon="mdi-magnify" v-model="keyword" v-debounce="onSearch" />

                <hr>
                {{ keyword }}
                <div  v-for="(p, index) in data" :key="index" >
                    {{ p }}
                    <v-btn>Select Product</v-btn>
                    <hr>
                </div>
                
            </div>
        </template>
    </ComModal>
</template>

<script setup>

import { inject, ref, computed, onUnmounted, reactive, i18n } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
const gv = inject("$gv")
const frappe = inject('$frappe');
const db = frappe.db()
const data = ref([])
const { t: $t } = i18n.global;
const keyword = ref("")
const toaster = createToaster({ position: "top" })

const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})

const emit = defineEmits(["resolve"])

function onSearch() {
    db.getDocList('Product',{
        fields: ['name', 'product_name_en','product_name_kh','price',"photo","product_category",'prices'],
        orFilters:[
            ["name",'like','%' + keyword.value +"%"],
            ["product_name_en",'like','%' + keyword.value +"%"],
            ["product_name_kh",'like','%' + keyword.value +"%"],
            ["Product Price","barcode","like","%" + keyword.value + "%"]
        ]
    })
        .then((docs) => {
            data.value = docs

        })
        .catch((error) => console.error(error));

}

function onClose(isClose) {
    emit('resolve', isClose);
}



onUnmounted(() => {

})

</script>
