<template>
    <div class="empty-state">
    <v-icon size="64" color="grey-lighten-1">
    mdi-package-variant-closed
    </v-icon>

    <h2>{{ $t("No Products Found") }}</h2>
    <p>{{ $t("Try adjusting your search or check back later.") }}</p>
</div>
</template>

<script setup>
  import {i18n} from   '@/plugin';
  const { t: $t } = i18n.global;

</script>

<style scoped>

    /* empty data show  */
    /* Center perfectly */
    .empty-state {
    height: 100%;
    min-height: calc(100vh - 300px); /* account for padding */
    
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    text-align: center;
    color: #888;
    animation: fadeIn 0.4s ease;
    }

    .empty-state h2 {
    margin-top: 12px;
    font-size: 18px;
    color: #555;
    }

    .empty-state p {
    font-size: 14px;
    margin-top: 6px;
    color: #999;
    }

    /* Optional subtle animation */
    @keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
    }
</style>