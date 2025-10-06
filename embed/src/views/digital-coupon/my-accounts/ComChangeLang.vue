<template>
  <div class="flex flex-column gap-3">
    <button 
      class="w-full p-2 border-round bg-green-100 hover:bg-green-200 flex align-items-center justify-content-center gap-2"
      @click="setLanguage('en')"
    >
    <img :src="UKFlage" width="40">
      {{t("English")}}
    </button>
    <button 
        class="w-full p-2 border-round bg-green-100 hover:bg-green-200 flex align-items-center justify-content-center gap-2"
        @click="setLanguage('km')"
        >
        <img :src="cambodiaFlag" width="40" />
        <span>{{ t("ភាសាខ្មែរ") }}</span>
    </button>
  </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";
 
import cambodiaFlag from '@/assets/images/Flag_of_Cambodia.svg.png'
import UKFlage from '@/assets/images/Flag_of_the_United_Kingdom.svg.png'
const { locale } = useI18n();

function setLanguage(lang) {
  locale.value = lang;               
  localStorage.setItem("lang", lang);  
  location.reload();  
              
}

</script>
