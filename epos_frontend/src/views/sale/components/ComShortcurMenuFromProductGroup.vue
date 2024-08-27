<template>
    <div class="bg-white" :class="mobile ? 'px-2' : 'p-2'" id="shortcut_menu" v-if="shortcut?.length > 0"> 
        <div ref="scrollContainer" :class="mobile ? 'menu-cat-scroll wrap-sm' : 'flex-wrap flex -my-1 justify-center'" v-if="shortcut">
            <v-btn 
                class="flex-shrink-0 m-1"
                rounded="pill"
                variant="tonal"
                size="small"
                v-bind:style="{'background-color':'red'}"
                @click="onShortCutMenuClick('All Product Categories')">
                <span v-bind:style="{'color':'#fff'}">{{ $t('All Product Categories') }}</span>
            </v-btn> 
            <v-btn 
                class="flex-shrink-0 m-1"
                v-for="(m, index) in shortcut" :key="index"
                rounded="pill"
                variant="tonal"
                size="small"
                v-bind:style="{'background-color':m.background_color}"
                @click="onShortCutMenuClick(m.name)">
                <span v-bind:style="{'color':m.text_color}">{{m.name}}</span>
            </v-btn> 
 
        </div>
    </div>
</template>
<script setup>
    import {  inject, ref, onMounted, onUnmounted } from '@/plugin'
    import {useDisplay}  from 'vuetify'
    const product = inject("$product")
    const frappe = inject("$frappe")
    const db = frappe.db();
    const {mobile} = useDisplay()
    const shortcut = ref([])

    const scrollContainer = ref(null)
    const isDown = ref(false)
    let startX
    let scrollLeft
 
    db.getDocList("Product Category",{
        fields:["name","background_color","background_color"],
        filters:[
        ["show_in_pos_shortcut_menu","=","1"],
        ["allow_sale","=","1"]
    ]
    })
    .then((docs)=>{
        shortcut.value = docs
    })
    .catch((error)=>{
   
    })
  
    function onShortCutMenuClick(name) {
       product.getProductMenuByProductCategory(name)
    } 

    const onTouchStart = (e) => {
        isDown.value = true;
        startX = e.touches[0].pageX - scrollContainer.value.offsetLeft;
        scrollLeft = scrollContainer.value.scrollLeft;
    }

    const onTouchMove = (e) => {
        if (!isDown.value) return;
        e.preventDefault();
        const x = e.touches[0].pageX - scrollContainer.value.offsetLeft;
        const walk = (x - startX) * 2; // Adjust scroll speed by multiplying
        scrollContainer.value.scrollLeft = scrollLeft - walk;
    }

    const onTouchEnd = () => {
        isDown.value = false;
    };

    onMounted(() => {
        setTimeout(() => {
            if (scrollContainer.value) {
                scrollContainer.value.addEventListener('touchstart', onTouchStart);
                scrollContainer.value.addEventListener('touchmove', onTouchMove);
                scrollContainer.value.addEventListener('touchend', onTouchEnd);
            }
        }, 500)
    })

    onUnmounted(() => {
        if (scrollContainer.value) {
            scrollContainer.value.removeEventListener('touchstart', onTouchStart);
            scrollContainer.value.removeEventListener('touchmove', onTouchMove);
            scrollContainer.value.removeEventListener('touchend', onTouchEnd);
        }
    })

</script>
<style scoped>
.wrap-sm {
    width: calc( 100vw - 22px);
}
.menu-cat-scroll {
    width: 100%;
    overflow-x: scroll;
    white-space: nowrap;
}

</style>