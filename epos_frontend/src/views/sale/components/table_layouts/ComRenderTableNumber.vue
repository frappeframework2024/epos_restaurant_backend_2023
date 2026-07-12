<template>
    <template v-for="g in tableLayout.table_groups">
        <v-window-item :value="g.key"
            v-bind:style="{ 'background-image': 'url(' + g.background + ')', 'min-height': `calc(100vh - ${!tableStatusColor && tableLayout.table_groups.length <= 1 ? 118 : 174}px)`, 'background-size': '100% 100%', 'min-width': 'calc(100vw - 0px)' }"
            class="bg-center overflow-auto relative table-bg" v-if="!mobile">
            <!-- <v-img :src="g.background" alt="Table Plan Background" aspect-ratio="16/9" class="elevation-3" :lazy-src="g.background"></v-img> -->
            <template v-for="(t, index) in g.tables" :key="index">
           
                <div   v-bind:style="{ 'height': t.h + 'px', 'width': t.w + 'px', 'left': t.x + 'px', 'top': t.y + 'px', 'background-color': t.background_color, 'position': 'absolute', 'box-sizing': 'border-box','border-radius':t.shape == 'Circle' ? '' : '10px' }"
                    class="text-center text-gray-100 cursor-pointer" :class="t.shape == 'Circle' ? 'shape-circle' : ''"
                    @click="onTableClick(t)">
                    <v-badge :content="t.sales?.length" color="error" style="float: right;"
                        v-if="t.sales?.length > 1"></v-badge>
                    <div class="flex items-center justify-center h-full">
                        <div>
                            <div :style="{ fontSize: (t.font_size || 15) + 'px' }">
                                <span class="font-bold">{{ t.tbl_no }}</span>
                                <span v-if="t.guest_cover">({{t.guest_cover }} )</span>
                            </div>
                            <div v-if="t.grand_total && gv.setting.show_total_amount_on_table">
                                <CurrencyFormat :value="t.grand_total"></CurrencyFormat>
                            </div>
                            <div class="text-xs" v-if="t.customer_name && t.customer_name != 'General' && t.sales?.length > 0">
                                 {{ t.customer_name }}
                                 <template v-if="t.phone_number">
                                    <br/>
                                    {{ (t.phone_number ||"") != "" ? (t.phone_number ||"")  : "" }}
                                 </template>
                            </div> 

                             <div v-if="t.creation && gv.setting.show_time_ago_on_table" class="text-xs">                                
                                <template v-if="t.is_reservation">                                    
                                    
                                    {{ getTimeFormat(t.creation) }}
                                </template>
                                <template v-else><v-icon icon="mdi-clock" size="x-small"></v-icon>
                                    {{ getTimeDifference(t.creation) }}
                                </template> 
                                
                            </div>
                           
                        </div>
                    </div>
                </div>
            </template>
        </v-window-item>

        <v-window-item v-else :value="g.key" v-bind:style="{ 'min-height': 'auto' }" class="mt-2 mb-4">
            <v-row>
                <v-col cols="6" v-for="(t, index) in g.tables" :key="index">
                   
                    <div v-bind:style="{ 'height': '100px', 'background-color': t.background_color }"
                        class="text-center text-gray-100 cursor-pointer  rounded-lg" @click="onTableClick(t)">
                        <v-badge :content="t.sales?.length" color="error" style="float:right;" class="mr-2"
                            v-if="t.sales?.length > 1"></v-badge>
                        <div class="flex items-center justify-center h-full">
                            <div>
                                <div :style="{ fontSize: (t.font_size || 15) + 'px' }">
                                    <span class="font-bold">{{ t.tbl_no }}</span>
                                    <span v-if="t.guest_cover">({{ t.guest_cover }})</span>
                                </div> 
                                <div v-if="t.grand_total && gv.setting.show_total_amount_on_table">
                                    <CurrencyFormat :value="t.grand_total"></CurrencyFormat>
                                </div>

                                 <div class="text-xs" v-if="t.customer_name && t.customer_name != 'General' && t.sales?.length > 0">
                                    {{ t.customer_name }}
                                    <template v-if="t.phone_number">
                                        <br/>
                                        {{ (t.phone_number ||"") != "" ? (t.phone_number ||"")  : "" }}
                                    </template>
                                </div> 

                                <div v-if="t.creation && gv.setting.show_time_ago_on_table" class="text-xs">                                
                                    <template v-if="t.is_reservation">                                    
                                        
                                        {{ getTimeFormat(t.creation) }}
                                    </template>
                                    <template v-else><v-icon icon="mdi-clock" size="x-small"></v-icon>
                                        {{ getTimeDifference(t.creation) }}
                                    </template> 
                                    
                                </div>
                            </div>
                        </div>
                    </div>
                </v-col>
            </v-row>
        </v-window-item>
    </template>
</template>
<script setup>
import { inject, useRouter, createToaster, selectSaleOrderDialog, keyboardDialog,tableReservationDialog, smallViewSaleProductListModal, i18n,ref } from '@/plugin';
import { useDisplay } from 'vuetify';
const { t: $t } = i18n.global;
const router = useRouter();
const { mobile, platform } = useDisplay()
const toaster = createToaster({ position: "top-right" });
const tableLayout = inject("$tableLayout");
const gv = inject("$gv");
const sale = inject("$sale");
const socket = inject("$socket");
const frappe = inject("$frappe");
const moment = inject("$moment");
const product = inject("$product"); 
const props = defineProps({
    tableStatusColor: Boolean
});
const call = frappe.call();
const db = frappe.db();
const is_processing = ref(false)
tableLayout.tab = localStorage.getItem("__tblLayoutIndex"); 

function getTimeDifference(date) {
    const now = Date.now();
    const diff = now - moment(date).toDate();
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    if (minutes <= 0 && hours <= 0){
        return "just now"
    }else{
        if (hours == 0) {
            return `${minutes} mn`;
        }
        return `${hours} h ${minutes} mn`;
    }
}

function getTimeFormat(date) {
    return moment(date).format("hh:mm A");
 
}

async function  validateNewtowkSaleLock(table){ 
    is_processing.value = true;  
    const value = await tableLayout.validateNewtowkSaleLock(table).catch((r)=> 
    {
        is_processing.value = false;   
    });
    is_processing.value = false;   
    return value 
}

function onTableClick(table, guest_cover) {
    product.loading_default_menu_from_table = 1
    if(is_processing.value){
        toaster.warning($t("Sale network lock processing"))
        return
    }
    gv.authorize("open_order_required_password", "make_order").then(async (v) => {
        if (v) {
            const make_order_auth = { "username": v.username, "name": v.user, discount_codes: v.discount_codes };
            if (table.sales.length == 0) { 
                localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));
                newSale(table);
            }
            else if (table.sales.length == 1) {
                if(table.sales[0].is_reservation){     
                         
                    const conf = await tableReservationDialog({"sale":table.sales[0]});
                    if(conf){
                        if(conf.action == "new_order"){
                            localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));
                            newSale(table);
                        }else if(conf.action =="checked_in"){                            
                            onConvertToSale(conf.doc);                             
                        }
                    }
                  

                }else{
                    if(await validateNewtowkSaleLock(table)){ 
                        return 
                    }
                    if (mobile.value) { 
                        await sale.LoadSaleData(table.sales[0].name).then(async (_sale) => {
                            localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));
                            const result = await smallViewSaleProductListModal({ title: sale.sale.name ? sale.sale.name : $t('New Sale'), data: { from_table: true } });
                            if (result) {
                                tableLayout.getSaleList();
                            } else {
                                localStorage.removeItem('make_order_auth');

                                socket.emit("ShowOrderInCustomerDisplay",{},"", sale.customer_display_key);
                            }
                        });
                    }
                    else { 
                        localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth)); 
                        let template = (gv.device_setting?.main_sale_screen??"Default") ;

                        if(template  == "Default"){
                            router.push({ 
                                name: "AddSale",
                                params: {
                                    name: table.sales[0].name
                                }
                            });
                        }else {
                            const result = template.toLowerCase().replace(/\s+/g, '-');
                            let _template = result;
                            router.push({ 
                                name: "SaleOrder",
                                params: {
                                    name: table.sales[0].name
                                },
                                query: { menu: _template }
                            });
                        } 
                    }
                } 

            }
            else {
                
                sale.sale.table_id = table.id;
                sale.sale.tbl_number = table.tbl_no;
                const saleList = table.sales.filter(r=>(r.is_reservation||0)===0);
                const reservation = table.sales.filter(r=>(r.is_reservation||0)===1);
                const result = await selectSaleOrderDialog({reservation: reservation.length >0 ? reservation[0]:undefined, data: saleList, table: table, make_order_auth: make_order_auth });
                if (result) {
                    localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));
                    if (result.action == "new_sale") {
                        newSale(table);
                    }else if(result.action =="checked_in"){                            
                        onConvertToSale(result.doc);                             
                    }
                }
            }
            return;
        }
    });
}

async function getDefaultTableMenu(table) {
    const db = frappe.db();
    await db.getDoc('Tables Number',table).then((doc) => {
        sale.sale.new_sale_default_pos_menu = doc.new_sale_default_pos_menu;
        sale.sale.submitted_default_pos_menu = doc.submitted_default_pos_menu;
    }).catch((error) => { console.log(error) });
}



async function newSale(table) {
    if(await validateNewtowkSaleLock(table)){ 
        return 
    }
    let guest_cover = 0;
    if (gv.setting.use_guest_cover == 1) {
        const result = await keyboardDialog({ title: $t('Guest Cover'), type: 'number', value: guest_cover });
        if (typeof result == 'number') {
            guest_cover = parseInt(result);
            if (guest_cover == undefined || isNaN(guest_cover)) {
                guest_cover = 0;
            }
        } else {
            return;
        }
    }
    sale.newSale();
    sale.sale.guest_cover = guest_cover;
    sale.sale.table_id = table.id
    sale.sale.tbl_number = table.tbl_no;
    if ((table.default_customer || "") != "") {
        sale.sale.customer = table.default_customer;
        sale.sale.customer_photo = table.customer_photo;
        sale.sale.customer_name = table.customer_name;
        sale.sale.customer_group = table.customer_group;
    }
    getDefaultTableMenu(table.id)
    let cust = await db.getDoc("Customer", sale.sale.customer)
    if(cust.default_discount > 0){
        sale.sale.discount_type = "Percent";
        sale.sale.discount = parseFloat(cust.default_discount);
    }else{  
        if (parseFloat(table.default_discount) > 0) {
            sale.sale.discount_type = table.discount_type;
            sale.sale.discount = parseFloat(table.default_discount);
            if (table.discount_type == "Percent") {
                toaster.info($t("msg.This table have discount", [table.default_discount + '%']))
            } else {
                toaster.info($t("msg.This table have discount", [(table.default_discount + ' ' + gv.setting.pos_setting.main_currency_name)]))
            }
        }
    }
    if (table.sale_type) {
        sale.sale.sale_type = table.sale_type
    }  
    if (table.price_rule) {
        sale.table_price_rule = table.price_rule;
        sale.price_rule = table.price_rule;
        sale.sale.price_rule = table.price_rule;
    }else{  
        sale.price_rule = gv.setting?.price_rule;
        sale.sale.price_rule = gv.setting?.price_rule;
    }
    if (gv.setting.price_rule != sale.sale.price_rule) {
        toaster.info($t('msg.Your current price rule is', [sale.sale.price_rule]));
    } 

    let template = gv.device_setting?.main_sale_screen??"Default";
    if( template == "Default"){
        router.push({ name: "AddSale" });
    }else {
        const result = template.toLowerCase().replace(/\s+/g, '-'); 
        let _template = result;

        router.push({ 
            name: "SaleOrder",
            query: { menu: _template }
        });
    }
}


async function onConvertToSale(reservation) {
  const params = {
    business_branch: gv.setting?.business_branch,
    pos_profile: localStorage.getItem("pos_profile")
  };

  call.get('epos_restaurant_2023.api.api.get_current_shift_information', params)
    .then(async (_res) => {
      const _data = _res.message;
      if (_data.cashier_shift == null) {
        toaster.warning($t("msg.Please start shift first"));
      } else if (_data.working_day == null) {
        toaster.warning($t("msg.Please start working day first"));
      } else {
        gv.authorize("open_order_required_password", "make_order").then(async (v) => {
          if (v) {
           
            const make_order_auth = { "username": v.username, "name": v.user, discount_codes: v.discount_codes };
            localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));

            await db.getDoc("Tables Number", reservation.table_id)
            .then(async (table) => {

              
            await sale.newSale(); 
            
              sale.sale.from_reservation = reservation.name;
              sale.sale.working_day = _data.working_day.name;
              sale.sale.posting_date = _data.working_day.posting_date;
              sale.posting_date = _data.working_day.posting_date;

              sale.sale.cashier_shift = _data.cashier_shift.name;
              sale.sale.shift_name = _data.cashier_shift.shift_name;

              sale.sale.guest_cover = (reservation.total_guest || 0);
              sale.sale.table_id = reservation.table_id;
              sale.sale.tbl_number = reservation.table_number;

              sale.sale.customer = reservation.guest;
              sale.sale.customer_photo = reservation.guest_photo;
              sale.sale.customer_name = reservation.guest_name;
              sale.sale.customer_group = reservation.guest_type;
              sale.sale.deposit = reservation.total_deposit;
             
              if (table.sale_type) {
                sale.sale.sale_type = table.sale_type
              }
              if (table.price_rule) {
                sale.table_price_rule = table.price_rule;
                sale.price_rule = table.price_rule;

                sale.sale.price_rule = table.price_rule;
              }
              else{  
                sale.table_price_rule = gv.setting?.price_rule;
                sale.price_rule = gv.setting?.price_rule;
                sale.sale.price_rule = gv.setting?.price_rule;
              }
              if (gv.setting.price_rule != sale.sale.price_rule) {
                toaster.info($t('msg.Your current price rule is', [sale.sale.price_rule]));
              }

              sale.sale.sale_status = "Hold Order";
              sale.action = "hold_order";
            
              if(reservation.reservation_product){
                await reservationProductConvert(reservation);
              }


              await sale.onSubmit().then(async (value) => {
                if (value) {
                  sale.sale = value;
                  call.get("epos_restaurant_2023.api.api.update_pos_reservation_and_sale_payment", {
                    reservation_name: reservation.name,
                    reservation_status: "Dine-in",
                    sale: value.name
                  }).then(() => {
                    
                    let template = (gv.device_setting?.main_sale_screen??"Default");
                    if(template == "Default"){
                      router.push({  name: "AddSale", params: { name: value.name }});
                    }else {
                      const result = template.toLowerCase().replace(/\s+/g, '-');
                      let _template = result;
                      router.push({ 
                        name: "SaleOrder",
                        params: { name: value.name },
                        query: { menu: _template }
                      });
                    } 

                  }).catch((err) => {
                   //
                  });
                }
              }).catch(() => {
                
              });
            }).catch((err) => {
              console.log(err)
              
            })

          }
        });
      }
    })
    .catch((error) => {
       
    });
}

async function reservationProductConvert(reservation) {

  const now = new Date();
  const make_order_auth = JSON.parse(localStorage.getItem('make_order_auth'));

  for (let p of reservation.reservation_product) {
    let _p = await db.getDoc("Product", p.product_code);
    let printers = [];
    _p.printers.forEach(_printer => {
      printers.push({
        "printer": _printer.printer_name,
        "actual_printer_name": _printer.actual_printer_name || _printer.printer_name,
        "group_item_type": _printer.group_item_type,
        "ip_address": _printer.ip_address,
        "port": _printer.port,
        "is_label_printer": _printer.is_label_printer,
        "usb_printing":_printer.usb_printing
      })
    });
    
    var saleProduct = {
      product_code: p.product_code,
      product_name: p.product_name,
      product_name_kh: p.product_name_kh,
      revenue_group: p.revenue_group,
      unit: p.unit,
      quantity: p.quantity,
      sub_total: 0,
      total_discount: 0,
      total_tax: 0,
      discount_amount: 0,
      sale_discount_amount: 0,
      note: '',
      regular_price: p.price,
      price: p.price,
      modifiers_price: 0,
      product_photo: p.product_photo,
      selected: false,
      modified: moment(now).format('yyyy-MM-DD HH:mm:ss.SSS'),
      creation: moment(now).format('yyyy-MM-DD HH:mm:ss.SSS'),
      append_quantity: _p.append_quantity,
      allow_discount: _p.allow_discount,
      allow_free: _p.allow_free,
      allow_change_price: _p.allow_change_price,
      is_open_product: _p.is_open_product,
      portion: "",
      modifiers: '',
      // modifiers_data: p.modifiers_data,
      is_free: 0,
      sale_product_status: "New",
      discount_type: "Percent",
      discount: 0,
      order_by: make_order_auth.name,
      order_time: moment(now).format('yyyy-MM-DD HH:mm:ss.SSS'),
      printers: JSON.stringify(printers),
      product_variants: [],
      is_combo_menu: _p.is_combo_menu,
      use_combo_group: _p.use_combo_group,
      product_tax_rule: "",
      is_require_employee: _p.is_require_employee,
      pos_reservation: reservation.name
    }

    sale.updateSaleProduct(saleProduct);
    sale.sale.sale_products.push(saleProduct);
    sale.updateSaleProduct(saleProduct);
  }

  sale.updateSaleSummary();
}

</script>
<style scoped>
.shape-circle {
    border-radius: 100%;
}

@media (max-width: 1920.98px) {
    .table-bg {
        background-size: 1920px 1080px !important;
        background-attachment: local;
        background-position: center center;
    }
}

@media (min-width: 1921px) {
    .table-bg {
        background-size: 100% 1080px !important;
        background-attachment: local;
        background-position: center center;
    }
}
</style>