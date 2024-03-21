<template lang="">
    <div>
        <ComModal  :loading="is_loading" :mobileFullscreen="true" @onClose="onClose"  width="1200px" :hideOkButton="true">
    <template #title>
      {{props.params.title}}
    </template>
    <template #content>
      <v-text-field :label="input_label" variant="solo" v-model="keyword" v-debounce="onSearch"></v-text-field>
      <v-container>
        <v-row v-if="!is_loading" cols="12" class="d-flex flex-wrap">
        <v-col class="my-2" v-for="img in image_list" lg=3 >
          <div class=" d-flex align-stretch flex-column elevation-1 pa-4">
            <v-img
              class="image-wraper"
              :src="img"
              :lazy-src="img"
            ></v-img>
            <v-btn @click="chooseImage(img)" class="mt-2">
              {{$t("Choose")}}
            </v-btn>
          </div>
        </v-col>
        

      </v-row>
      <div class="text-center" v-else>
        <v-progress-circular  indeterminate :size="47"></v-progress-circular>
        <p class="mt-2">
          {{$t("Loading")}}
        </p>
          
      </div>
      </v-container>
      
    </template>
  </ComModal>
    </div>
</template>
<script setup>
import {defineEmits,ref,inject,onMounted,i18n,watch} from "@/plugin"
const { t: $t } = i18n.global; 
const emit = defineEmits(["resolve","reject"])
const props = defineProps({
  params: {
    type: Object,
    required: true,
  }
})
const frappe = inject("$frappe")
const call = frappe.call()
let keyword = ref(props.params.keyword)
let image_list = ref([])
let is_loading=ref(false)
onMounted(() => {
  loadImage()
});

watch(keyword, (newValue, oldValue) => {
      console.log(`Message changed from "${oldValue}" to "${newValue}"`);
    });

function loadImage(){
  is_loading.value=true;
	call.post('epos_restaurant_2023.api.api.search_image_from_google', {
    "keyword":keyword.value
  }).then((res)=>{
    image_list.value = res.message
    is_loading.value=false
  }).catch(()=>{
    is_loading.value=false
  })
}

const onSearch = debouncer((key) => {
  loadImage()
}, 700);

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

function chooseImage(url){
  emit('resolve', {image:url});
}
function onClose() {
  emit('reject', false);
}



const input_label=ref($t('Keyword'))
</script>
<style>
    .image-wraper{
      height:250px;
    }
</style>