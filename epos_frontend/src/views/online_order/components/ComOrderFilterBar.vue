<template>
  <div class="oo-toolbar">
    <!-- STATUS TABS -->
    <div class="oo-status-tabs">
      <button
        v-for="tab in statusTabs"
        :key="String(tab.value)"
        type="button"
        class="oo-tab"
        :class="{ 'oo-tab-active': status === tab.value }"
        :disabled="loading"
        @click="emit('update:status', tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- DATE FILTER, VIEW TOGGLE & REFRESH -->
    <div class="oo-toolbar-actions">
      <div class="oo-date-filter">
        <DatePicker
          v-model="dateModel"
          dateFormat="dd/mm/yy"
          placeholder="dd/mm/yyyy"
          appendTo="self"
          showIcon
          iconDisplay="input"
          showClear
          :disabled="loading"
          class="oo-datepicker"
          panelClass="oo-datepicker-panel"
        />
      </div>

      <div class="oo-toggle-group" role="group" aria-label="Order view mode">
        
        <button
          type="button"
          class="oo-btn"
          :class="{ 'oo-active': viewMode === 'list' }"
          @click="emit('update:viewMode', 'list')"
        >
          <v-icon size="18" class="mr-1">mdi-format-list-bulleted</v-icon>
          List
        </button>
        <button
          type="button"
          class="oo-btn"
          :class="{ 'oo-active': viewMode === 'card' }"
          @click="emit('update:viewMode', 'card')"
        >
          <v-icon size="18" class="mr-1">mdi-view-grid-outline</v-icon>
          Card
        </button>
      </div>

      <button
        type="button"
        class="oo-btn oo-btn-brand"
        :disabled="loading"
        @click="emit('refresh')"
      >
        <v-icon size="18" class="mr-1" :class="{ 'mdi-spin': loading }">mdi-refresh</v-icon>
        Refresh
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import DatePicker from 'primevue/datepicker';

const props = defineProps({
  statusTabs: {
    type: Array,
    default: () => [],
  },
  status: {
    type: [String, null],
    default: 'submitted',
  },
  postingDate: {
    type: String,
    default: '',
  },
  viewMode: {
    type: String,
    default: 'card',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  lastUpdated: {
    type: String,
    default: '',
  },
});

const emit = defineEmits([
  'update:status',
  'update:postingDate',
  'update:viewMode',
  'refresh',
]);

function parseIsoDate(isoStr) {
  if (!isoStr || typeof isoStr !== 'string') return null;
  const parts = isoStr.split('-').map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
  const [year, month, day] = parts;
  return new Date(year, month - 1, day);
}

function formatIsoDate(dateObj) {
  if (!(dateObj instanceof Date) || Number.isNaN(dateObj.getTime())) return '';
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

const dateModel = computed({
  get() {
    return parseIsoDate(props.postingDate);
  },
  set(val) {
    emit('update:postingDate', val ? formatIsoDate(val) : '');
  },
});
</script>