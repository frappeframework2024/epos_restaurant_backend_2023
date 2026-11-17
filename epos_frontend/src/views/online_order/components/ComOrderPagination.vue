<template>
  <div class="oo-pagination">
    <button
      type="button"
      class="oo-btn"
      :disabled="page <= 1 || loading"
      @click="$emit('changePage', page - 1)"
    >
      Previous
    </button>

    <button
      v-for="pageNum in visiblePages"
      :key="pageNum"
      type="button"
      class="oo-btn oo-page-btn"
      :class="{ 'oo-page-active': pageNum === page }"
      :disabled="loading"
      @click="$emit('changePage', pageNum)"
    >
      {{ pageNum }}
    </button>

    <button
      type="button"
      class="oo-btn"
      :disabled="isNextDisabled"
      @click="$emit('changePage', page + 1)"
    >
      Next
    </button>
  </div>
</template>

<script setup>
defineProps({
  page: {
    type: Number,
    required: true,
  },
  visiblePages: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  isNextDisabled: {
    type: Boolean,
    default: true,
  },
});

defineEmits(['changePage']);
</script>