<template>
  <transition name="fade-slide">
    <div v-show="showBtn" class="MainScroll">
      <v-fab fab class="arrow-style" color="secondary" @click="scrollToTop">
        <v-icon>mdi-chevron-up</v-icon>
      </v-fab>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  target: {
    type: Object,
    default: null
  }
})

const showBtn = ref(false)

let timeout = null

const onScroll = () => {
  clearTimeout(timeout)
  timeout = setTimeout(() => {
    showBtn.value = (props.target?.scrollTop || window.scrollY || 0) > 200
  }, 50)
}

watch(() => props.target, (el, oldEl) => {
  if (oldEl) {
    oldEl.removeEventListener('scroll', onScroll)
  }

  if (el) {
    el.addEventListener('scroll', onScroll)
  } else {
    window.addEventListener('scroll', onScroll)
  }
}, { immediate: true })

onUnmounted(() => {
  props.target?.removeEventListener('scroll', onScroll)
  window.removeEventListener('scroll', onScroll)
})

const scrollToTop = () => {
  if (props.target) {
    props.target.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
</script>

<style scoped>
.MainScroll {
  position: fixed;
  bottom: 16px;
  right: 16px;
  z-index: 1000;
}

.arrow-style {
  background-color: rgb(176 0 32) !important;
  color: white;
  padding: 25px;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.arrow-style:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* ✅ Animation */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

@media (max-width: 600px) {
  .MainScroll {
    bottom: calc(60px + 40px);
  }
}
</style>