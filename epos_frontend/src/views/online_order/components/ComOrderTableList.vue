<template>
  <div class="oo-table-wrap">
    <table class="oo-table">
      <thead>
        <tr>
          <th>Order</th>
          <th class="oo-text-center">Status</th>
          <th>Table</th>
          <th>Time</th>
          <th class="oo-text-right">Total</th>
          <th class="oo-text-right">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(order, idx) in orders"
          :key="order.id || idx"
          class="oo-table-row"
          @click="$emit('select', order)"
        >
          <td>
            <div class="oo-order-title">{{ getOrderTitle(order, idx) }}</div>
            <div v-if="getOrderCustomer(order)" class="oo-muted">
              {{ getOrderCustomer(order) }}
            </div>
          </td>
          <td class="oo-text-center">
            <span class="oo-status-pill" :class="normalizedStatus(order.status)">
              {{ order.status || '-' }}
            </span>
          </td>
          <td>{{ getOrderTable(order) || '-' }}</td>
          <td>{{ getOrderTime(order) || '-' }}</td>
          <td class="oo-text-right oo-font-semibold">
            {{
              getOrderTotal(order) !== null
                ? formatCurrency(getOrderTotal(order), order.currency)
                : '-'
            }}
          </td>
          <td class="oo-text-right">
            <button
              type="button"
              class="oo-btn oo-btn-small"
              @click.stop="$emit('select', order)"
            >
              View
            </button>
          </td>
        </tr>
      </tbody>
    </table>
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