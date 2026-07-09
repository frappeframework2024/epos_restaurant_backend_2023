<template>
  <v-dialog
    v-model="loadingVisible"
    persistent
    width="250"
    scrim="rgba(0,0,0,0.85)"
  >
    <v-card
      rounded="xl"
      elevation="16"
      class="loading-card pa-4"
    >
      <div class="d-flex flex-column align-center justify-center">

        <v-progress-circular
          indeterminate
          :size="48"
          :width="5"
          color="primary"
        />

        <div class="text-h6  mt-6 text-center">
          {{ loadingMessage }}
        </div>
 

      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import {
  loadingVisible,
  loadingMessage
} from "@/utils/loading.js";
</script>

<style scoped>
.loading-card {
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  background: rgba(var(--v-theme-surface), 0.96);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all .25s ease;
}
</style>