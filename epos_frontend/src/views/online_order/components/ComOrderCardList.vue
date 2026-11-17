<template>
  <div class="oo-card-grid">
    <div
      v-for="(order, idx) in orders"
      :key="order.id || idx"
      class="oo-order-card"
      @click="$emit('select', order)"
    >
      <div class="oo-card-top">
        <div class="oo-order-title">{{ getOrderTitle(order, idx) }}</div>
        <span class="oo-status-pill" :class="normalizedStatus(order.status)">
          {{ order.status || 'unknown' }}
        </span>
      </div>

      <div class="oo-card-meta">
        <div v-if="getOrderTable(order)" class="oo-meta-item">
          <v-icon size="18" color="#d97706">mdi-table-chair</v-icon>
          <span>Table: <strong>{{ getOrderTable(order) }}</strong></span>
        </div>
        <div v-if="getOrderCustomer(order)" class="oo-meta-item">
          <v-icon size="18" color="#6b7280">mdi-account-outline</v-icon>
          <span>{{ getOrderCustomer(order) }}</span>
        </div>
        <div v-if="getOrderTime(order)" class="oo-meta-item">
          <v-icon size="18" color="#6b7280">mdi-clock-outline</v-icon>
          <span>{{ getOrderTime(order) }}</span>
        </div>
      </div>

      <div class="oo-card-footer">
        <span class="oo-total">
          {{
            getOrderTotal(order) !== null
              ? formatCurrency(getOrderTotal(order), order.currency)
              : ''
          }}
        </span>
        <span class="oo-view-link">
          View Details
          <v-icon size="18">mdi-chevron-right</v-icon>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  normalizedStatus,
  getOrderTitle,
  getOrderTable,
  getOrderCustomer,
  getOrderTime,
  getOrderTotal,
  formatCurrency,
} from '../utils/orderHelpers';

defineProps({
  orders: {
    type: Array,
    required: true,
  },
});

defineEmits(['select']);
</script>