<template>

  <div :class="sale.sale?.sale_products?.length > 0 ? 'table-sale-product-scroll' : ' empty-no-scroll'"
    :style="sale.sale?.sale_products?.length > 0 ? 'max-height:calc(-429px + 100vh)' : ''">
    <v-table>
      <thead class="h-head">
        <tr>
          <th class="text-left">
            មុខទំនិញ <br />
            Product Description
          </th>
          <th class="text-center">
            ចំនួន <br />
            Quantity
          </th>
          <th class="text-right">
            តម្លៃ <br />
            Price
          </th>
          <th class="text-right none-discount-field">
            បញ្ចុះតម្លៃ <br />
            Discount
          </th>
          <th class="text-right">
            សរុបតម្លៃ <br />
            Amount
          </th>
          <th class="text-center">
          </th>

        </tr>
      </thead>
      <tbody class="table-pro">
        <template v-if="sale.sale?.sale_products?.length > 0">
          <tr v-for="sp  in sale.getSaleProducts(undefined)" @click="sale.onSelectSaleProduct(sp)"
            :class="sp.selected ? 'selected' : ''">
            <td>
              <div class="d-flex align-center gap-3">
                <div> 
                  <v-avatar :image="sp?.product_photo" v-bind="props" v-if="sp?.product_photo"
                    class="cursor-pointer"></v-avatar> 
                  <v-avatar :image="placeholderImage" v-bind="props" v-else
                    class="cursor-pointer"></v-avatar>
                </div>
                <div style="white-space: break-spaces;"> 
                  <p>{{ sp.product_code }} </p>  
                  <p>
                    {{ sp.product_name }} 
                    <v-chip v-if="sp.quantity<0" variant="outlined" color="red">{{ $t("Return") }}</v-chip>
                    <v-tooltip activator="parent" location="start">{{ sp.product_name }} </v-tooltip>
                  </p>  
                  <p>
                    {{ sp.product_name_kh }}
                    <v-tooltip activator="parent" location="start">{{ sp.product_name_kh }} </v-tooltip>
                  </p> 

                  <div class="visib-dis">
                    <template v-if="sp.discount">Discount: 
                        <span class="" v-if="sp.discount_type == 'Percent'">
                          {{ sp.discount }} % /
                        </span>  
                        <CurrencyFormat :value="sp.discount_amount" />
                    </template>
                  </div> 
                  <p v-if="!sp.note" class="italic underline" style="color:#ccc;" @click="sale.onSaleProductNote(sp)">
                    {{ $t("Add Note") }}</p>
                  <p v-else class="italic" @click="sale.onSaleProductNote(sp)">{{ sp.note }}</p>
                </div>
              </div>
            </td>
            <td class="text-center">
              <div class="flex justify-center">
                <div class="flex gap-2 border rounded justify-center py-1" >
                  <div><v-icon size="small" icon="mdi-minus-circle-outline" color="red" @click="onUpdateQuantity(sp, -1)"></v-icon>
                  </div>
                  <div class="text-sm link_line_action overflow-hidden" @click="onChangeQTY(sp)">{{ sp.quantity }}</div>
                  <div><v-icon size="small" icon="mdi-plus-circle-outline" color="green" @click="onUpdateQuantity(sp, 1)"></v-icon>
                  </div>

                </div>

              </div>
            </td> 
            <td class="text-end">
              <template v-if="!sp.is_free">
                <span class="link_line_action overflow-hidden" style="width:auto"
                  @click="sale.onChangePrice(sp, gv, numberFormat)">
                  <CurrencyFormat :value="sp.price" />
                </span> 
                <span><ComProductUnit :sale_product="sp" /> </span> 
              </template>
              <template v-else>
                <p>
                  <v-chip color="green" variant="tonal" size="small">
                    Free
                  </v-chip>
                </p>
              </template>
            </td>
            <td class="text-end none-discount-field">
              <ComHappyHour :saleProduct="sp" v-if="sp.is_render"/>
              <span class="" style="width:auto">
                <template v-if="!sp.is_free">
                  <span v-if="sp.discount" class="link_line_action overflow-hidden w-auto">
                    <span v-if="sp.discount_type == 'Percent'">
                      {{ sp.discount }} % /
                    </span> 
                    <CurrencyFormat :value="sp.discount_amount" />
                  </span>

                  <!-- <template v-else><span style="width:auto;" class="link_line_action overflow-hidden">{{ $t("Apply Discount") }}</span></template> -->
                  <span v-else class="w-auto link_line_action overflow-hidden"><v-icon color="blue-darken-2" icon="mdi-sale" size="small"></v-icon></span>
                </template>

                <v-menu activator="parent">
                  <v-list>
                    <v-list-item @click="onSaleProductDiscount(sp, 'Percent')">
                      <v-list-item-title>{{ $t("Discount Percent") }} (%)</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="onSaleProductDiscount(sp, 'Amount')">
                      <v-list-item-title>{{ $t("Discount Amount") }} ($)</v-list-item-title>
                    </v-list-item>
                    <v-divider v-if="sp.discount > 0" inset></v-divider>
                    <v-list-item v-if="sp.discount > 0" @click="onSaleProductCancelDiscount(sp)">
                      <v-list-item-title class="text-orange-700">{{ $t("Cancel Discount") }}</v-list-item-title>
                    </v-list-item>

                  </v-list>
                </v-menu>
              </span>
            </td>
            <td class="text-end">
              <span style="min-width:4rem">
                <CurrencyFormat :value="sp.amount" />
              </span>
            </td>
            <td class="text-center op-option-btn">
              <v-btn class="ma-2 hidden-delete-btn" icon="mdi-delete" color="red"  variant="text"  @click="sale.onRemoveItem(sp, gv, numberFormat)">
                  </v-btn> 
              <v-menu>
                <template v-slot:activator="{ props }">

                  <v-btn class="ma-2" icon="mdi-dots-vertical" variant="text"  v-bind="props">
                  </v-btn>
                </template>
                <v-list> 
                  <v-list-item @click="onSaleProductDiscount(sp, 'Percent')" class="menu-hidden-an">
                      <v-list-item-title>{{ $t("Discount Percent") }} (%)</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="onSaleProductDiscount(sp, 'Amount')" class="menu-hidden-an">
                      <v-list-item-title>{{ $t("Discount Amount") }} ($)</v-list-item-title>
                    </v-list-item>
                    <v-divider v-if="sp.discount > 0" inset></v-divider>
                    <v-list-item v-if="sp.discount > 0" @click="onSaleProductCancelDiscount(sp)" class="menu-hidden-an">
                      <v-list-item-title class="text-orange-700">{{ $t("Cancel Discount") }}</v-list-item-title>
                    </v-list-item> 
                  <v-list-item v-if="sp.quantity > 0" @click="onReturn(sp)">
                    <v-list-item-title>{{ $t("Mark as Return Product") }}</v-list-item-title>
                  </v-list-item> 
                  <v-list-item v-else @click="onReturn(sp)">
                    <v-list-item-title>{{ $t("Mark as Selling Product") }}</v-list-item-title>
                  </v-list-item> 
                   
                  <v-list-item @click="sale.onRemoveItem(sp, gv, numberFormat)" class="menu-hidden-an">
                    <v-list-item-title>{{ $t("Remove Item") }}</v-list-item-title>
                  </v-list-item>   

                  <!-- free -->
                   
                  <v-list-item :title="$t('Mark as Free Item')" v-if="!sp.is_free"
                      @click="onSaleProductFree(sp)"></v-list-item>

                  <v-list-item v-else @click="sale.onSaleProductCancelFree(sp)"> 
                      <v-list-item-title class="text-red-700">{{ $t('Cancel Free') }}</v-list-item-title>
                  </v-list-item> 
                <!-- end free --> 
                </v-list>
              </v-menu> 
            </td>
          </tr>
        </template>

        <template v-else>
          <tr class="empty-data-st">
            <td colspan="6">
              <div class="text-center"><v-icon icon="mdi-cart-outline" color="blue"></v-icon></div>
              <div class="text-center">There is no product selected, please search or scan barcode</div>
            </td>
          </tr>
        </template>
      </tbody>
    </v-table>
  </div>
</template>

<script setup>
import { ref, inject } from "@/plugin"
import ComCurrentUserAvatar from '@/components/layout/components/ComCurrentUserAvatar.vue'
import ComProductUnit from '@/views/sale/components/retail_ui/ComProductUnit.vue'
import { createToaster } from '@meforma/vue-toaster';
import placeholderImage from '@/assets/images/placeholder.webp'
import ComHappyHour from '@/views/sale/components/happy_hour_promotion/ComHappyHour.vue';
import { i18n } from '@/i18n';

const { t: $t } = i18n.global;

const numberFormat = inject('$numberFormat');
const sale = inject('$sale');
const product = inject('$product');
const gv = inject('$gv');

const toaster = createToaster({ position: 'top-right', maxToasts: 2, duration: 3000 });
const frappe = inject('$frappe');
const db = frappe.db()




function onUpdateQuantity(sp, param) {

  param = param * ((sp.is_return || 0) == 0 ? 1 : -1)


  if (!sp.is_return) {
    if (sp.quantity <= 1 && param == -1) {
      return
    }
  } else {
    if (sp.quantity == -1 && param == 1) {
      return
    }
  }

  sale.updateQuantity(sp, sp.quantity + param)
}

function onReturn(sp) {
  sp.is_return = !sp.is_return 
  sale.updateQuantity(sp, sp.quantity * -1)

}

function onSaleProductDiscount(sp, discount_type) {
  if (sp.allow_discount) {
    if (!sale.isBillRequested()) {
      gv.authorize("discount_item_required_password", "discount_item", "discount_item_required_note", "Discount Item Note", "", true).then((v) => {
        if (v) {
          sp.temp_discount_by = v.user;
          sp.temp_discount_note = v.note;
          
          sale.onDiscount(
            gv,
            `${sp.product_name} Discount`,
            sp.quantity * sp.price,
            sp.discount,
            discount_type,
            v.discount_codes,
            sp.discount_note,
            sp,
            v.category_note_name
          );
        }
      });
    }
  }
  else {
    toaster.warning($t('msg.This item is not allow to discount'));
  }
}



function onSaleProductCancelDiscount(sp) {

  sp.discount = 0;
  sp.discount_type = 'Percent'
  sp.happy_hour_promotion = ''
  sp.happy_hours_promotion_title = ''
  sale.updateSaleProduct(sp)
  sale.updateSaleSummary();

}


function onChangeQTY (sp) {
  if ( sale.dialogActiveState == false) {
            sale.dialogActiveState = true;
            sale.onChangeQuantity(sp, gv)
        }
}


function onSaleProductFree(sp) { 
    if (!sale.isBillRequested()) {
        gv.authorize("free_item_required_password", "free_item", "free_item_required_note", "Free Item Note", sp.product_code).then((v) => {
            if (v) { 
                sp.free_note = v.note;
                sp.free_by = v.user;
                sale.onSaleProductFree(sp);
            }
        });


    }
}




</script>

<style>
.selected,
.item-list:hover {
  background-color: #ffebcc !important;
}


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

tr:nth-child(even) {
  background-color: #f2f2f2;
}

.table-sale-product-scroll {
  overflow-y: auto;
  position: relative;
}

.empty-data-st {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.empty-data-st .mdi-cart-outline {
  font-size: 5rem;
}

.empty-no-scroll {
  overflow-y: auto;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-sale-product-scroll .v-table>.v-table__wrapper>table {
  overflow: hidden !important;
}
@media (max-width: 1207px) {
  .none-discount-field, .hidden-delete-btn {
    display: none;
  } 
  .table-pro tr td.op-option-btn {
    width:50px
  }
}
.table-pro tr td,
.h-head tr th {
  padding: 0 6px !important;
}
.op-option-btn .v-btn--icon.v-btn--density-default {
  width: auto !important;
  height: auto !important;
}
@media (min-width: 1206.98px) {
  .visib-dis{
    display: none;
  }
}

@media (min-width: 1206.98px) {
  .menu-hidden-an {
    display: none !important;
  }
}
</style>