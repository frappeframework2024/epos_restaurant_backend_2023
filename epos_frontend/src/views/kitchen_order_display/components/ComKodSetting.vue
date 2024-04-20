<template>
    <v-dialog max-width="500">
    <template v-slot:activator="{ props: activatorProps }">
      <v-icon  v-bind="activatorProps">mdi-cog</v-icon>
     
    </template>
  
    <template v-slot:default="{ isActive }">
      <v-card :title="$t('Setting')">
        <v-card-text>
          hello
        </v-card-text>
  
        <v-card-actions>
          <v-spacer></v-spacer>
  
          <v-btn
            text="Close Dialog"
            @click="isActive.value = false"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
  
</template>
<script setup>
  import { inject,ref, i18n } from '@/plugin';
  const { t: $t } = i18n.global;

</script>