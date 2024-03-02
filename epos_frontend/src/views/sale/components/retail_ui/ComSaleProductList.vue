<template>
  <v-table>
    <thead>
      <tr>
        <th class="text-left">
          មុខទំនិញ <br />
          Product Description
        </th>
        <th class="text-left">
          ចំនួន <br />
          Quantity
        </th>
        <th class="text-center">
          ឯកតា <br />
          Unit
        </th>
        <th class="text-right">
          តម្លៃ <br />
          Price
        </th>
        <th class="text-right">
          បញ្ចុះតម្លៃ <br />
          Discount
        </th>
        <th class="text-right">
          សរុបតម្លៃ <br />
          Amount
        </th>

      </tr>
    </thead>
    <tbody> 
      <tr v-for="sp  in sale.sale.sale_products"> 
        <td>
          <div class="d-flex align-center">
            <div>
              <avatar :name="sp.name || 'No Name'" v-bind="props" class="cursor-pointer mr-2" size="40"></avatar>
            </div>
            <div>
              <p>{{sp.name}}</p>
              <p>My Best Selling Product Name</p>
              <p class="italic underline" style="color:#ccc;">Note</p>
            </div>
          </div>
        </td>
        <td>
          <!-- <ComInput type="number" v-model="price" autofocus /> -->
          <div class="flex gap-2 border rounded justify-center">
            <div><v-icon icon="mdi-plus-circle-outline" color="green"></v-icon></div>
            <div>2</div>
            <div><v-icon icon="mdi-minus-circle-outline" color="red"></v-icon></div>
          </div>
        </td>
        <td class="text-center">
          <span class="link_line_action overflow-hidden">Can</span>
        </td>
        <td class="text-end">
          <span class="link_line_action overflow-hidden"><CurrencyFormat :value="25"/></span>
        </td>
        <td class="text-end">
          <span class="link_line_action overflow-hidden">10% / <CurrencyFormat :value="25"/></span>
        </td>
        <td class="text-end">
          <span class="link_line_action overflow-hidden"><CurrencyFormat :value="250"/></span>
        </td>

      </tr>
    </tbody>
  </v-table>
  <!-- {{ sale.sale.sale_products }} -->
</template>
<script setup>
import { ref, inject } from "@/plugin"
import ComCurrentUserAvatar from '@/components/layout/components/ComCurrentUserAvatar.vue'


const sale = inject("$sale")
</script>
<style scoped>
  .link_line_action {
      border: 1px dashed #4338ca;
      border-radius: 10px;
      padding: 0 5px;
      color: var(--bg-purple-cs);
      cursor: pointer;
      display: inline-block;
      width: 100%;
      white-space: nowrap;
      text-overflow: ellipsis;
  }
</style>