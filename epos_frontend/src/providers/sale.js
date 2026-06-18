import Enumerable from 'linq'
import moment from '@/utils/moment.js';
import {
    ref, noteDialog, changeTaxSettingModal, SaleProductComboMenuGroupModal, keyboardDialog, keypadWithNoteDialog, createResource,
    createDocumentResource, addModifierDialog, useRouter, confirmDialog, selectEmployeeDialog, saleProductDiscountDialog, i18n,
    ComOrderLimitDialog, scanqrDialog,
    postApi

} from "@/plugin"
import { createToaster } from "@meforma/vue-toaster";
import socket from '@/utils/socketio';
import { FrappeApp } from 'frappe-js-sdk';

import NumberFormat from 'number-format.js';
const frappe = new FrappeApp();
const db = frappe.db()
const call = frappe.call()
const { t: $t } = i18n.global;
const toaster = createToaster({ position: "top-right" });

export default class Sale {
    
    constructor(router) {
        this.payway_complete_payment = false;
        this.close_payment_form = false;
        this.is_payment_first_load = false;
        this.load_menu_lang = false;
        this.loading = false;
        this.mobile = false;
        this.platform = {};
        this.promotion = null;
        this.working_day = "";
        this.cashier_shift = "";
        this.shift_name = "";
        this.setting = null;
        this.tbl_number = null;
        this.table_id = null;
        this.table_price_rule = null;
        this.price_rule = null;
        this.sale_type = '';
        this.customer = '';
        this.customer_photo = '';
        this.customer_name = '';
        this.customer_group = '';
        this.exchange_rate = 1;
        this.change_exchange_rate = 1;
        this.guest_cover = 0;
        this.orderTime = undefined;
        this.router=router;
        this.name = "";
        this.action = "";
        this.customer_display_key = "",
        this.pos_receipt = undefined;
        this.no_loading = false;
        this.sale = {
            sale_products: []
        };
        this.changed = 0
        this.vueInstance = null;
        this.vue = null;
        this.newSaleResource = null;
        this.saleResource = null;
        this.paymentInputNumber = "";
        this.isPrintReceipt = false;
        this.show_unit_in_select_portion = false;
        this.selected_sale_product = null;
        this.selected_product = null


        //use this variable to show toast after database submit in resource
        this.message = undefined;

        //user this variable to temporary store product that need to send to kitchen pritner 
        //before submit order or close order
        this.productPrinters = [];

        //temporary all sale products change bill
        this.changeTableSaleProducts = [];

        this.moveItemSaleProducts = [];

        //temporary all deleted sale product, we use this for send data to kitchen printers
        this.deletedSaleProducts = [];

        //sale product deleted show in screen sale item list
        this.deletedSaleProductsDisplay = [];

        this.reSendSaleProductKOT = [];

        //Move product item
        this.moveItemSaleProduct = [];

        //tempporary store autditrail list and will submit to database after submit
        //auditrail login is store in tabComment
        this.auditTrailLogs = [];
        this.auditTrailResource = createResource({
            url: "frappe.client.insert"
        });
        this.dialogActiveState = false;
        //use this resource to load sale list in current table number
        this.tableSaleListResource = null;
        this.orderChanged = false;
        this.printWaitingOrderAfterPayment = false;
        this.kod_messages = [] //key, screen, message
        this.createNewSaleResource();
    }
 

    createNewSaleResource()  {
        const parent = this;
        this.newSaleResource = createResource({
            url: "frappe.client.insert",
           async onSuccess(doc)  {
             await  parent.onProcessTaskAfterSubmit(doc);
                parent.action = "";
                if (parent.message != undefined) {
                    toaster.success(parent.message);
                    parent.message = undefined;
                }
                else {
                    toaster.success($t('msg.Update successfully'));
                }
            }
        })
    }

   async saleNetworkLock(_sale){
        if(this.setting.device_setting.use_sale_network_lock == 1 && _sale.table_id != undefined){ 
            let param = {
                "sale":_sale.name,
                "table_id":_sale.table_id,
                "table_name":_sale.tbl_number, 
                "pos_station":localStorage.getItem("device_name"), 
                "pos_profile": this.setting.pos_profile
            }
          await  call.post("epos_restaurant_2023.api.api.create_sale_network_lock",{"param": param})    
        }
    }

    async newSale() { 
 
        const now = new Date();
        const _now_format = moment(now).format('yyyy-MM-DD HH:mm:ss.SSSSSS');
        this.auditTrailLogs = [];
        this.deletedSaleProductsDisplay = [];
        const make_order_auth = JSON.parse(localStorage.getItem('make_order_auth'));
        const tax_rule = this.setting.tax_rule;
        this.orderChanged = false;
        this.selected_product = null
        this.selected_sale_product = null
        this.price_rule = (this.price_rule || this.table_price_rule) || this.setting?.price_rule; 
        this.sale = {
            doctype: "Sale",
            modified: _now_format,
            creation: _now_format,
            sale_status: "New",
            cashier_shift: this.cashier_shift,
            shift_name: this.shift_name,
            working_day: this.working_day,
            exchange_rate: this.exchange_rate,
            change_exchange_rate: this.change_exchange_rate,
            outlet: this.setting?.outlet,
            stock_location: this.setting?.stock_location,
            table_id: this.table_id,
            tbl_number: this.tbl_number,
            pos_profile: this.setting?.pos_profile,
            pos_station_name: localStorage.getItem("device_name"),
            customer: this.customer || this.setting?.customer,
            customer_photo: this.customer_photo || this.customer_name ? this.customer_photo : this.setting?.customer_photo,
            customer_name: this.customer_name || this.setting?.customer_name,
            customer_group: this.customer_group || this.setting?.customer_group,
            price_rule:  this.price_rule ,
            business_branch: decodeURIComponent(this.setting?.business_branch),
            sale_products: [],
            product_variants: [],
            sale_type: this.sale_type || this.setting?.default_sale_type,
            discount_type: "Percent",
            grand_total: 0,
            guest_cover: this.guest_cover,
            discount: 0,
            sub_total: 0,
            deposit: 0,
            payment: [],
            // posting_date: moment(new Date()).format('yyyy-MM-DD'),
            commission_type: "Percent",
            commission: 0,
            commission_note: '',
            commission_amount: 0,
            created_by: make_order_auth?.name || "",
            new_sale_default_pos_menu: "",
            submitted_default_pos_menu: ""
        } 
        this.onSaleApplyTax(tax_rule, this.sale);  
        //audit-trail 
        if ((this.name || "") == "") {
            const u = make_order_auth;
            let msg = `${u.name} was created new sale`;
            this.auditTrailLogs.push({
                doctype: "Comment",
                subject: "Create New Sale",
                comment_type: "Info",
                reference_doctype: "Sale",
                reference_name: "New",
                comment_by: u.name,
                content: msg,
                custom_item_description: '',
                custom_note: ''
            });
        }        
    }

    async LoadSaleData(name) { 
        this.auditTrailLogs = [];
        this.changeTableSaleProducts = [];
        this.moveItemSaleProducts = [];
        return new Promise(async (resolve) => {
            const parent = this;

            this.saleResource = createDocumentResource({
                url: "frappe.client.get",
                doctype: "Sale",
                name: name,
                setValue: {
                  async  onSuccess(doc) {
                        parent.sale = doc;
                        await   parent.onProcessTaskAfterSubmit(doc);
                        parent.action = "";
                        if (parent.message != undefined) {
                            toaster.success(parent.message);
                            parent.message = undefined;
                        }
                        else {
                            toaster.success($t('msg.Update successfully'));
                        }
                    },
                },
            });

            await this.saleResource.get.fetch().then(async (doc) => {
                this.onLoadDeleteSaleProducts(doc.name);
                this.sale = doc;
                this.__backup_sale = JSON.parse(JSON.stringify(doc))
                //aba PayWay set closed / cancel qr (expired)
                 if (this.sale.name && (this.sale.aba_transaction_id||"") != ""){
                    call.post("epos_restaurant_2023.api.payway.aba_close_transaction", { 
                        "property_code": this.setting.property_code,
                        "pos_config": this.setting.pos_config,
                        "invoice_id": this.sale.name
                    }); 
                }

                this.getDefaultTableMenu(doc.table_id)
                //add sale product to temp resend sale product to kitchen order
                let re_send_sale_product_kot = []
                this.reSendSaleProductKOT = []
                re_send_sale_product_kot = JSON.parse(JSON.stringify(this.sale.sale_products.filter((r) => (r.name ?? "") != "")));
                re_send_sale_product_kot.forEach((r)=>{
                    if(this.setting.pos_setting.combo_menu_print_captain_by_items_printer && r.is_combo_menu){
                        this.reSendSaleProductKOT.push(r);
                    }else{
                        if(((r.printers || "[]") != "[]")){
                            this.reSendSaleProductKOT.push(r);
                        }
                    } 
                }); 
                
                //add sale to move item
                this.moveItemSaleProduct = JSON.parse(JSON.stringify(this.sale.sale_products.filter((r) => (r.name ?? "") != "")));
                this.action = "";
                //check if current table dont hanve any sale list data then load it
                if (!this.tableSaleListResource?.data) {
                    this.getTableSaleList();
                }


                //
                socket.emit("ShowOrderInCustomerDisplay", this.sale,"", this.customer_display_key);

                resolve(doc);
                 
            });
            resolve(false);
        })
    }

    getTableSaleList() {
        const parent = this;
        this.tableSaleListResource = createResource({
            url: "frappe.client.get_list",
            params: {
                doctype: "Sale",
                fields: ["name", "creation", "grand_total", "total_quantity","seat_number", "tbl_group","table_id", "tbl_number", "guest_cover", "grand_total", "sale_status", "sale_status_color", "sale_status_priority", "customer", "customer_name", "phone_number", "customer_photo"],
                filters: {
                    pos_profile: localStorage.getItem("pos_profile"),
                    table_id: JSON.parse(localStorage.getItem("table_groups")) && JSON.parse(localStorage.getItem("table_groups")).length > 0 ? parent.sale.table_id : '',
                    docstatus: 0
                },
                limit_page_length: 500,
            },
            auto: true,
        })
    }

    async getDefaultTableMenu(table) {
        const db = frappe.db();
        await db.getDoc('Tables Number',table).then((doc) => {
          this.sale.new_sale_default_pos_menu = doc.new_sale_default_pos_menu;
          this.sale.submitted_default_pos_menu = doc.submitted_default_pos_menu;
        }).catch((error) => { console.log(error) });
    }

    getSaleProductGroupByKey(sort_order_type="asc") {
        if (!this.sale.sale_products) {
            return []
        } else {
            let type = sort_order_type.endsWith("_desc")
            let query = Enumerable.from(this.sale.sale_products).groupBy("{order_by:$.order_by,order_time:$.order_time}", "", "{order_by:$.order_by,order_time:$.order_time}", "$.order_by+','+$.order_time");
            query = type
            ? query.orderByDescending("$.order_time")
            : query.orderBy("$.order_time")
            return query.toArray()
        }
    }


    getReSendSaleProductGroupByKey() {
        if (!this.reSendSaleProductKOT) {
            return []
        } else {
            const group = Enumerable.from(this.reSendSaleProductKOT).groupBy("{order_by:$.order_by,order_time:$.order_time}", "", "{order_by:$.order_by,order_time:$.order_time}", "$.order_by+','+$.order_time");
            return group.orderByDescending("$.order_time").toArray();
        }
    }

    getSaleProductDeletedGroupByKey() {
        if (!this.deletedSaleProductsDisplay) {
            return []
        } else {

            const sale_products = this.deletedSaleProductsDisplay.filter((r) => r.show_in_list);

            const group = Enumerable.from(sale_products).groupBy("{order_by:$.order_by,order_time:$.order_time}", "", "{order_by:$.order_by,order_time:$.order_time}", "$.order_by+','+$.order_time");
            return group.orderByDescending("$.order_time").toArray();
        }
    }

    getReSendSaleProducts(groupByKey) {
        if (groupByKey) {
            return Enumerable.from(this.reSendSaleProductKOT).where(`$.order_by=='${groupByKey.order_by}' && $.order_time=='${groupByKey.order_time}'`).orderByDescending("$.modified").toArray()
        } else {
            return Enumerable.from(this.reSendSaleProductKOT).orderByDescending("$.modified").toArray()
        }
    }

    getMoveItemSaleProducts(groupByKey) {
        if (groupByKey) {
            return Enumerable.from(this.moveItemSaleProduct).where(`$.order_by=='${groupByKey.order_by}' && $.order_time=='${groupByKey.order_time}'`).orderByDescending("$.modified").toArray()
        } else {
            return Enumerable.from(this.moveItemSaleProduct).orderByDescending("$.modified").toArray()
        }
    }

    getSaleProducts(groupByKey,order_by="creation") {
        if (groupByKey) {
            return Enumerable.from(this.sale.sale_products).where(`$.order_by=='${groupByKey.order_by}' && $.order_time=='${groupByKey.order_time}'`).orderByDescending("$.modified").toArray()
        } else {
           let desc = order_by.endsWith("_desc")
            order_by = order_by.replace("_desc", "")

            let query = Enumerable.from(this.sale.sale_products)
            query = desc 
            ? query.orderByDescending(x => x[order_by])
            : query.orderBy(x => x[order_by])
            return query.toArray()
        }
    }

    async addSaleProduct(p) {
        //check for append quantity rule
        //product code, allow_append_qty,price, unit,modifier, portion, is_free,sale_product_status
        //and check system have feature to send to kitchen
        let strFilter = `$.is_timer_product == 0 && $.is_require_employee==0  && $.product_code=='${p.name}' && $.append_quantity ==1 && $.price==${p.price} && $.portion=='${this.getString(p.portion)}'  && $.modifiers=='${(p.modifiers || '')=='[]'?'':(p.modifiers || '')}'   && $.unit=='${p.unit}' && $.is_free==0 && $.note==''`
        if (!this.setting?.pos_setting?.allow_append_quantity_after_submit) {
            strFilter = strFilter + ` && $.sale_product_status == 'New'`
        }
        if (p.is_combo_menu && p.use_combo_group) {
            strFilter = strFilter + ` && $.combo_menu_data == '${p.combo_group_data}'`
        }
        if (p.is_open_product == 1) {
            strFilter = strFilter + ` && $.product_name== '${p.name_en}'`
        }
        let sp = Enumerable.from(this.sale.sale_products).where(strFilter).firstOrDefault()
        let is_new_sale_product = true;
        let new_sale_product;
        let prev_sale_product;
        if (sp != undefined) {
            // append quantity
            prev_sale_product = JSON.parse(JSON.stringify(sp));
            sp.quantity = parseFloat(sp.quantity) + 1;
            this.clearSelected();
            sp.selected = true;
            await this.applyPromotions(sp)
            this.updateSaleProduct(sp);
            is_new_sale_product = false;
            if (this.setting.table_groups.length == 0) {
                this.getSelectedProduct(sp)
                this.selected_sale_product = sp
            }

        } else {
            // add new record to sale product
            this.clearSelected();
            let tax_rule;
            if ((p.tax_rule ?? "") === "" || p.tax_rule === "None") {
                tax_rule = JSON.parse(JSON.stringify(this.setting.tax_rule));
                if ((this.sale.name ?? "") !== "" && (tax_rule.name ?? "") !== "") {
                    const sale_tax_rule_name = this.sale.tax_rule ?? "";
                    if (sale_tax_rule_name !== tax_rule.name) {
                        const match = this.setting.tax_rules.find(r => r.tax_rule === sale_tax_rule_name);
                        tax_rule = match ? JSON.parse(JSON.stringify(match.tax_rule_data)) : {};
                    }
                }
            } else {
                tax_rule = JSON.parse(p.tax_rule_data);
            }
            const make_order_auth = JSON.parse(localStorage.getItem('make_order_auth'));
            const now = new Date();
            const _now_format = moment(now).format('yyyy-MM-DD HH:mm:ss.SSSSSS');
            const saleProduct = {
                pos_profile:this.setting?.pos_profile,
                menu_product_name: p.menu_product_name,
                product_code: p.name,
                product_name: p.name_en,
                product_name_kh: p.name_kh,
                revenue_group: p.revenue_group,
                unit: p.unit,
                quantity: 1,
                sub_total: 0,
                total_discount: 0,
                total_tax: 0,
                discount_amount: 0,
                sale_discount_amount: 0,
                note: '',
                regular_price: p.price,
                price: p.is_timer_product ? 0 : p.price,
                modifiers_price: this.getNumber(p.modifiers_price),
                product_photo: p.photo,
                selected: true,
                modified: _now_format,
                creation: _now_format,
                append_quantity: p.append_quantity || 0,
                allow_discount: p.allow_discount || 0,
                allow_free: p.allow_free || 0,
                allow_change_price: p.allow_change_price || 0,
                allow_crypto_claim : p.allow_crypto_claim || 0,
                is_open_product: p.is_open_product || 0,
                kitchen_group:p.kitchen_group||"",
                kitchen_group_sort_order: p.kitchen_group_sort_order || 0,
                portion: this.getString(p.portion),
                modifiers: (p.modifiers || '') == "[]" ? "" : (p.modifiers || ''),
                modifiers_data: p.modifiers_data,
                is_free: 0,
                sale_product_status: "New",
                discount_type: "Percent",
                discount: p.discount || 0,
                order_by: make_order_auth.name,
                order_time: this.getOrderTime(),
                printers: p.printers,
                product_variants: [],
                is_combo_menu: p.is_combo_menu,
                use_combo_group: p.use_combo_group,
                combo_menu: p.combo_menu,
                combo_menu_data: (p.combo_menu_data || p.combo_group_data),
                product_tax_rule: (p.tax_rule == "None" ? "" : p.tax_rule),
                is_require_employee: p.is_require_employee || 0,
                is_timer_product: p.is_timer_product || 0,
                time_stop: 0,
                kod_status: "Pending",
                rate_include_tax : p.rate_include_tax||0,
                selected_variant : p.selected_variant,
                variant_of:p.variant_of,
                is_variant:p.is_variant,
                pos_note:p.pos_note,
                is_newly_added: 1
            }
            if (p.is_timer_product) {
                if (p.time_in) {
                    saleProduct.time_in = moment(p.time_in).format('yyyy-MM-DD HH:mm:ss');
                }
            }
            this.onSaleProductApplyTax(tax_rule, saleProduct);
            await this.applyPromotions(saleProduct)
            this.updateSaleProduct(saleProduct);
            new_sale_product = saleProduct;
            this.sale.sale_products.push(saleProduct);
            if (this.setting.table_groups.length == 0) {
                this.getSelectedProduct(saleProduct)
                this.selected_sale_product = saleProduct
            }
        }
        this.updateSaleSummary();
        const u = JSON.parse(localStorage.getItem('make_order_auth'));
        if (is_new_sale_product) {
            let item_description = `${new_sale_product.product_code}-${new_sale_product.product_name}${(new_sale_product.portion || "") == "" ? "" : `(${new_sale_product.portion})`} ${new_sale_product.modifiers}`;
            let msg = `${u.name} was create new sale item: ${item_description}`;
            this.auditTrailLogs.push({
                doctype: "Comment",
                subject: "New Sale Item",
                comment_type: "Info",
                reference_doctype: "Sale",
                reference_name: "New",
                comment_by: u.name,
                content: msg,
                custom_item_description: `${new_sale_product.quantity} x ${item_description}`,
                custom_note: '',
                custom_amount: new_sale_product.amount
            });

        } else {
            let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
            let msg = `${u.name} was append a quantity to item:  ${item_description} (from ${prev_sale_product.quantity} to ${sp.quantity})`;
            this.auditTrailLogs.push({
                doctype: "Comment",
                subject: "Append Quantity",
                comment_type: "Info",
                reference_doctype: "Sale",
                reference_name: "New",
                comment_by: u.name,
                content: msg,
                custom_item_description: `${(sp.quantity || 0) - prev_sale_product.quantity} x ${item_description}`,
                custom_note: '',
                custom_amount: sp.amount / ((sp.quantity || 0) == 0 ? 1 : sp.quantity)
            });
        }
    }

    getSelectedProduct(sp) {
        let sale = this
        if (sp.product_code != this.selected_sale_product?.product_code) {
            call.get('epos_restaurant_2023.api.product.get_product_detail_information', { product_code: sp.product_code })
                .then((data) => {
                    sale.selected_product = data.message
                })
        }
    }

    cloneSaleProduct(sp, quantity) {
        const u = JSON.parse(localStorage.getItem('make_order_auth'));
        const now = new Date();
        this.clearSelected();
        const sp_copy = JSON.parse(JSON.stringify(sp));
        sp_copy.selected = true;
        sp_copy.quantity = quantity - sp_copy.quantity;
        sp_copy.sale_product_status = "New";
        sp_copy.name = "";
        sp_copy.deleted_quantity = 0;
        sp_copy.order_by = u.name;
        sp_copy.order_time = this.getOrderTime();
        sp_copy.creation = moment(now).format('yyyy-MM-DD HH:mm:ss.SSS')
        sp_copy.modified = moment(now).format('yyyy-MM-DD HH:mm:ss.SSS')
        sp_copy.pos_reservation = "";
        sp_copy.is_newly_added = 1
        this.updateSaleProduct(sp_copy);
        this.sale.sale_products.push(sp_copy);
        this.updateSaleSummary();

        let item_description = `${sp_copy.product_code}-${sp_copy.product_name}${(sp_copy.portion || "") == "" ? "" : `(${sp_copy.portion})`} ${sp_copy.modifiers}`;
        let msg = `${u.name} was create new sale item: ${item_description}`;
        this.auditTrailLogs.push({
            doctype: "Comment",
            subject: "New Sale Item",
            comment_type: "Info",
            reference_doctype: "Sale",
            reference_name: "New",
            comment_by: u.name,
            content: msg,
            custom_item_description: `${sp_copy.quantity} x ${item_description}`,
            custom_note: '',
            custom_amount: sp_copy.amount
        });
    }

    getOrderTime() {
        if (!this.orderTime) {
            this.orderTime = moment(new Date()).format('yyyy-MM-DD HH:mm:ss.SSS');
            return this.orderTime;
        } else {
            return this.orderTime
        }
    }

    onSelectSaleProduct(sp) {
        this.clearSelected();
        sp.selected = true;
        // we check if user use retail system when user click on order product we get product information
        if (this.setting.use_retail_ui == 1) {
            this.getSelectedProduct(sp)
            this.selected_sale_product = sp
        }
    }

    clearSelected() {
        Enumerable.from(this.sale.sale_products).where(`$.selected==true`).forEach("$.selected=false");
    }

    async updateSaleProduct(sp) {
        const precision = (this.setting.pos_setting.main_currency_precision||2) // newline
        this.onRateIncludeTax(sp,false,false,false);
        //set property for re render comhappyhour check
        sp.is_render = false;
        //end
        sp.sub_total = sp.quantity * (sp.price + sp.modifiers_price);
        sp.discount = parseFloat(sp.discount)
        if (sp.discount) {
            if (sp.discount_type == "Percent") {
                sp.discount_amount = (sp.sub_total * sp.discount / 100);
            } else {
                sp.discount_amount = sp.discount;
            }
            sp.sale_discount_percent = 0;
            sp.sale_discount_amount = 0;
        } else {
            sp.discount_amount = 0;
            //check if sale have discount then add discount to sale
        }
        sp.discount_amount = parseFloat((sp.discount_amount + Number.EPSILON).toFixed(precision)); //new
        sp.discount_amount = Math.abs(sp.discount_amount || 0) * (sp.is_return ? -1 : 1)
        if (sp.sale_discount_percent) {
            sp.sale_discount_amount = (sp.sub_total * sp.sale_discount_percent / 100);
        }    
        
        
        sp.sale_discount_amount = Number((sp.sale_discount_amount + Number.EPSILON).toFixed(precision)); 

        sp.total_discount = sp.discount_amount + sp.sale_discount_amount; 


        this.onCalculateTax(sp);
 

        //re

        sp.amount = sp.sub_total - sp.discount_amount ;

        sp.total_revenue = (sp.sub_total - sp.total_discount);
        
        if(sp.rate_include_tax==0){
            sp.amount = sp.sub_total - sp.discount_amount + sp.total_tax ;
            sp.total_revenue = (sp.sub_total - sp.total_discount) + sp.total_tax;
        } else{
            //recalculate discount if rate include tax
            let re_calc_sale_discount_amount = 0;
            let price_before_tax = sp.sub_total - sp.total_tax;
            price_before_tax =Number((price_before_tax + Number.EPSILON).toFixed(precision)); 

            if (sp.sale_discount_percent > 0){
                re_calc_sale_discount_amount = price_before_tax * (sp.sale_discount_percent/100)
                re_calc_sale_discount_amount = Number((re_calc_sale_discount_amount + Number.EPSILON).toFixed(precision)); 
                sp.sale_discount_amount = re_calc_sale_discount_amount;
            }

            let re_calc_sale_product_discount_amount = 0;
            if(sp.discount > 0 && sp.discount_type=="Percent"){
                re_calc_sale_product_discount_amount = price_before_tax * (sp.discount/100);
                re_calc_sale_product_discount_amount = Number((re_calc_sale_product_discount_amount + Number.EPSILON).toFixed(precision)); 
                sp.discount_amount = re_calc_sale_product_discount_amount
            } 
            sp.total_discount = sp.discount_amount + sp.sale_discount_amount;

        }
        
        //
        if(sp.total_discount > 0 || sp.allow_crypto_claim == 0  || this.sale.sale_discount > 0){
            sp.crypto_able_amount = 0;
        }else{
            sp.crypto_able_amount = sp.amount
        }
        //set property for re render comhappyhour check
    }

    async applyPromotions(sp){
        if(this.promotion && this.promotion.length > 0){
            let product_checks=[]
            product_checks.push({
                product_code: sp.product_code,
                order_time: sp.order_time
            })
            let doc = await this.getPromotionProducts(product_checks,this.getPromotionByCustomerGroup())
            if (doc) {
                if (sp.happy_hour_promotion) {
                    sp.discount_type = ''
                    sp.discount = 0
                    sp.happy_hours_promotion_title = ''
                    sp.happy_hour_promotion = ''
                }
                doc.product_promotions.forEach(r => {
                    if (moment(sp.order_time).format('HH:mm:ss') == r.order_time && sp.is_free == false) {
                        sp.discount_type = 'Percent'
                        sp.discount = r.percentage_discount
                        sp.happy_hours_promotion_title = r.promotion_title
                        sp.happy_hour_promotion = r.promotion_name
                    }
                })
            }
        }
    }

    getPromotionProducts(product_checks, promotionGroups) {
        return new Promise((resolve, reject) => {
            createResource({
                url: 'epos_restaurant_2023.api.promotion.get_promotion_products',
                auto: true,
                params: {
                    products: product_checks,
                    promotions: promotionGroups
                },
                onSuccess(doc) {
                    resolve(doc)
                },
                onError(err) {
                    reject(err)
                }
            });
        });
    }

    getPromotionByCustomerGroup(){
    let promotions = []
    if(this.promotion && this.promotion.length > 0){
        this.promotion.forEach(r => {
            if(r.customer_groups.length > 0){
                r.customer_groups.forEach(g=>{
                    if(g.customer_group_name_en == this.sale.customer_group){
                        promotions.push(r)
                    }
                })
            }else{
                promotions.push(r)
            }
        });
        return promotions
    }
    return promotions
    }

    //on sale product apply tax setting
    onSaleProductApplyTax(tax_rule, sp) {
        sp.tax_rule = tax_rule.name || "";
        sp.rate_include_tax = tax_rule.rate_include_tax||0;
        sp.tax_1_rate = tax_rule.tax_1_rate || 0;
        sp.percentage_of_price_to_calculate_tax_1 = tax_rule.percentage_of_price_to_calculate_tax_1 || 100;
        sp.calculate_tax_1_after_discount = tax_rule.calculate_tax_1_after_discount || false;

        sp.tax_2_rate = tax_rule.tax_2_rate || 0;
        sp.percentage_of_price_to_calculate_tax_2 = tax_rule.percentage_of_price_to_calculate_tax_2 || 100;
        sp.calculate_tax_2_after_discount = tax_rule.calculate_tax_2_after_discount || false;
        sp.calculate_tax_2_after_adding_tax_1 = tax_rule.calculate_tax_2_after_adding_tax_1 || false;

        sp.tax_3_rate = tax_rule.tax_3_rate || 0;
        sp.percentage_of_price_to_calculate_tax_3 = tax_rule.percentage_of_price_to_calculate_tax_3 || 100;
        sp.calculate_tax_3_after_discount = tax_rule.calculate_tax_3_after_discount || false;
        sp.calculate_tax_3_after_adding_tax_1 = tax_rule.calculate_tax_3_after_adding_tax_1 || false;
        sp.calculate_tax_3_after_adding_tax_2 = tax_rule.calculate_tax_3_after_adding_tax_2 || false;
        this.updateSaleProduct(sp);
    }

    _priceForCalcTax(sp, cal_after_disc){
        let amount = sp.sub_total
        if (sp.rate_include_tax == 1) { 
            if(sp.tax_rule_data != undefined){ 
                let priceBefore = this.getRateBeforeTax( sp.sub_total - (cal_after_disc==0?0: sp.total_discount),JSON.parse(sp.tax_rule_data), sp.tax_1_rate, sp.tax_2_rate, sp.tax_3_rate)
                amount =  priceBefore +  (cal_after_disc==0?0: sp.total_discount)
            }
        } 
        return   amount;       
    }

    //on calculate tax
    onCalculateTax(sp) {
 
        let amount = this._priceForCalcTax(sp,1)
        // let amount = sp.sub_total
        // if (sp.rate_include_tax == 1) { 
        //     if(sp.tax_rule_data != undefined){
        //         // let priceBefore = this.getRateBeforeTax(sp.sub_total - sp.total_discount,JSON.parse(sp.tax_rule_data), sp.tax_1_rate, sp.tax_2_rate, sp.tax_3_rate)
        //         let priceBefore = this.getRateBeforeTax(sp.sub_total- sp.total_discount,JSON.parse(sp.tax_rule_data), sp.tax_1_rate, sp.tax_2_rate, sp.tax_3_rate)
        //         amount =  priceBefore   + sp.total_discount
        //     }
        // }   


        // //tax 1
        sp.taxable_amount_1 =   this._priceForCalcTax(sp,sp.calculate_tax_1_after_discount);
        // sp.taxable_amount_1 = amount;
        // //tax 1 taxable amount
        // //if cal tax1 taxable after disc.
        // if (sp.calculate_tax_1_after_discount) {
        //     sp.taxable_amount_1 = (amount - sp.total_discount);
        // }

        sp.taxable_amount_1 *= ((sp.percentage_of_price_to_calculate_tax_1 || 0) / 100);
        //cal tax 1 amount
        sp.tax_1_amount = sp.taxable_amount_1 * ((sp.tax_1_rate || 0) / 100);


        //tax 2
        // //tax 2 taxable amount
        sp.taxable_amount_2 =this._priceForCalcTax(sp,sp.calculate_tax_2_after_discount);
        // sp.taxable_amount_2 =amount;
        // //if cal tax2 taxable after disc.
        // if (sp.calculate_tax_2_after_discount) {
        //     sp.taxable_amount_2 = (amount - sp.total_discount);
        // }
        sp.taxable_amount_2 *= ((sp.percentage_of_price_to_calculate_tax_2 || 0) / 100);
        //if cal tax2 taxable after add tax1
        if (sp.calculate_tax_2_after_adding_tax_1) {
            sp.taxable_amount_2 += sp.tax_1_amount;
        }
        //cal tax2 amount
        sp.tax_2_amount = sp.taxable_amount_2 * ((sp.tax_2_rate || 0) / 100);
        
        //tax 3
        // //tax 3 taxable amount
        sp.taxable_amount_3 = this._priceForCalcTax(sp,sp.calculate_tax_3_after_discount);
        // sp.taxable_amount_3 = amount;
        // //if cal tax3 taxable after disc.
        // if (sp.calculate_tax_3_after_discount) {
        //     sp.taxable_amount_3 = (amount - sp.total_discount);
        // }
        sp.taxable_amount_3 *= ((sp.percentage_of_price_to_calculate_tax_3 || 0) / 100);
        //if cal tax3 taxable after add tax1
        if (sp.calculate_tax_3_after_adding_tax_1) {
            sp.taxable_amount_3 += sp.tax_1_amount;
        }
        //if cal tax3 taxable after add tax2
        if (sp.calculate_tax_3_after_adding_tax_2) {
            sp.taxable_amount_3 += sp.tax_2_amount;
        }
        //cal tax3 amount
        sp.tax_3_amount = sp.taxable_amount_3 * ((sp.tax_3_rate || 0) / 100);
        sp.total_tax = sp.tax_1_amount + sp.tax_2_amount + sp.tax_3_amount; 
        
        sp.selling_price = ((sp.sub_total - sp.total_tax) /sp.quantity) - (sp.modifiers_price||0) 
    }

    onRateIncludeOrNotIncludeTaxClick(){ 
        if (!this.isBillRequested()) {
            this.sale.rate_include_tax = ((this.sale.rate_include_tax||0)==1?0:1) 
            this.sale.sale_products.forEach((sp)=>{
                sp.rate_include_tax = this.sale.rate_include_tax;
                this.onRateIncludeTax(sp, false,true,  false)
            })
            this.updateSaleSummary()  
        }
    }

    onRateIncludeTax(sp, update_rate = true, update_sale_product=true, update_sale=true){
        let _tax_rule = JSON.parse(JSON.stringify(this.setting.tax_rules)).filter((r)=>r.tax_rule == sp.tax_rule||this.sale.tax_rule )
        if(_tax_rule.length > 0){
            sp.tax_rule_data = _tax_rule[0].tax_rule_data;
            if(update_rate){
                sp.rate_include_tax = ((sp.rate_include_tax||0)==1?0:1)
            }
            if(update_sale_product){
                this.updateSaleProduct(sp)
            }
            if(update_sale){
                this.updateSaleSummary();
            }
        }
    }

    getRateBeforeTax(amount, tax_rule, tax_1_rate, tax_2_rate, tax_3_rate){
        amount= (amount || 0)

        const t1_r = (tax_1_rate || 0) / 100
        const t2_r = (tax_2_rate ||  0)  / 100
        const t3_r = (tax_3_rate || 0)  / 100
        
        let tax_1_amount = 0
        let tax_2_amount = 0
        let tax_3_amount = 0
        let price = 0

        let t1_af_disc = tax_rule.calculate_tax_1_after_discount
        let t2_af_disc = tax_rule.calculate_tax_2_after_discount

        let t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1
        
        let t3_af_disc	= tax_rule.calculate_tax_3_after_discount

        let t3_af_add_t1 =  tax_rule.calculate_tax_3_after_adding_tax_1
        let t3_af_add_t2 =   tax_rule.calculate_tax_3_after_adding_tax_2


        let tax_rate_con = 0
        tax_rate_con = (1 + t1_r + t2_r 
                            + (t1_r * t2_af_add_t1 * t2_r) 
                            + t3_r + (t1_r * t3_af_add_t1 * t3_r) 
                            + (t2_r * t3_af_add_t2 * t3_r)
                            + (t1_r * t2_af_add_t1 * t2_r * t3_af_add_t2 * t3_r))  
        tax_rate_con = tax_rate_con || 1
 
        price = amount /  (tax_rate_con ==0?1:tax_rate_con)
        
        return  price
    }

    //on sale apply  tax setting
    onSaleApplyTax(tax_rule, s) {
        if(tax_rule.rate_include_tax == undefined ){
            tax_rule.rate_include_tax = tax_rule.is_rate_include_tax||0;
        }
        s.rate_include_tax = tax_rule.rate_include_tax||0;
        s.tax_rule = tax_rule.name || "";
        s.tax_1_rate = tax_rule.tax_1_rate || 0;
        s.percentage_of_price_to_calculate_tax_1 = tax_rule.percentage_of_price_to_calculate_tax_1 || 100;
        s.tax_2_rate = tax_rule.tax_2_rate || 0;
        s.percentage_of_price_to_calculate_tax_2 = tax_rule.percentage_of_price_to_calculate_tax_2 || 100;
        s.tax_3_rate = tax_rule.tax_3_rate || 0;
        s.percentage_of_price_to_calculate_tax_3 = tax_rule.percentage_of_price_to_calculate_tax_3 || 100;
        //update tax setting of sale product
        (s.sale_products || []).forEach((sp) => {
            if ((sp.product_tax_rule || "") == "") {
                this.onSaleProductApplyTax(tax_rule, sp);
            }
        });
    }

    //update sale summary
    updateSaleSummary(sale_status = '') {
        const precision = (this.setting.pos_setting.main_currency_precision||2) //newline
        this.onUpdateSaleDiscount(this.sale.discount, this.sale.discount_type, this.sale.discount_note)
        const sp = Enumerable.from(this.sale.sale_products);
        this.sale.total_quantity = this.getNumber(sp.where("$.is_timer_product == 0").sum("$.quantity"));
        this.sale.sub_total = this.getNumber(sp.sum("$.sub_total"));        
        let total_tax_exclude = this.getNumber(sp.where("$.rate_include_tax == 1").sum("$.total_tax"))

        this.changed = 1
        //calculate sale discount
        this.sale.sale_discountable_amount = this.getNumber(sp.where("$.allow_discount==1 && $.discount==0").sum("$.sub_total"));
        this.sale.sale_discountable_amount =  Number((this.sale.sale_discountable_amount + Number.EPSILON).toFixed(precision)); //new
        this.sale.sale_discountable_amount = this.sale.sale_discountable_amount - total_tax_exclude; //new

        this.sale.discount = this.getNumber(this.sale.discount);
        this.sale.sale_discount = 0;
       
        if (this.sale.discount_type == "Percent") {
            this.sale.sale_discount = sp.sum("$.sale_discount_amount")
        } else {
            this.sale.sale_discount = this.sale.discount;
        } 

        this.sale.sale_discount = parseFloat((this.sale.sale_discount + Number.EPSILON).toFixed(precision)); //new 
        this.sale.product_discount = this.getNumber(sp.sum("$.discount_amount"));
        this.sale.product_discount = Number( (this.sale.product_discount +Number.EPSILON).toFixed(precision)) //new
        this.sale.total_discount = (Number(this.sale.sale_discount) || 0) + (Number(this.sale.product_discount) || 0); 


        //tax
        this.sale.tax_1_amount = this.getNumber(sp.sum("$.tax_1_amount"));
        this.sale.tax_2_amount = this.getNumber(sp.sum("$.tax_2_amount"));
        this.sale.tax_3_amount = this.getNumber(sp.sum("$.tax_3_amount"));
        this.sale.total_tax = this.getNumber(sp.sum("$.total_tax"));

        this.sale.sub_total -= total_tax_exclude;

        //grand_total
        this.sale.grand_total = ((this.sale.sub_total || 0) - (this.sale.total_discount || 0)) + ((this.sale.total_tax || 0));
        this.sale.grand_total =   parseFloat((this.sale.grand_total + Number.EPSILON).toFixed(precision)); //new
        // crypto able amount
        this.sale.crypto_able_amount = (this.sale.sale_discount > 0 ? 0 : this.getNumber(sp.sum("$.crypto_able_amount")));        
        //
        this.sale.balance = this.sale.grand_total - (this.sale.deposit || 0) - (this.sale.total_cash_coupon_claim||0);
        this.sale.balance =  parseFloat((this.sale.balance + Number.EPSILON).toFixed(precision)); //new
        // commission
        if (this.sale.commission_type == "Percent") {
            this.sale.commission_amount = (this.sale.grand_total * this.sale.commission / 100);
        } else {
            this.sale.commission_amount = this.sale.commission;
        }
        this.sale.commission_amount =  parseFloat((this.sale.commission_amount + Number.EPSILON).toFixed(precision)); //new
        this.orderChanged = true;
        socket.emit("ShowOrderInCustomerDisplay", this.sale, sale_status, this.customer_display_key);
        //add sale product to temp resend sale product to kitchen order
        let re_send_sale_product_kot = []
        this.reSendSaleProductKOT = []
        re_send_sale_product_kot = JSON.parse(JSON.stringify(this.sale.sale_products.filter((r) => (r.name ?? "") != "")));
        re_send_sale_product_kot.forEach((r)=>{
            if(this.setting.pos_setting.combo_menu_print_captain_by_items_printer && r.is_combo_menu){
                this.reSendSaleProductKOT.push(r);
            }else{
                if(((r.printers || "[]") != "[]")){
                     this.reSendSaleProductKOT.push(r);
                }
            } 
        });
        //add sale to move item
        this.moveItemSaleProduct = JSON.parse(JSON.stringify(this.sale.sale_products.filter((r) => (r.name ?? "") != "")));
    }

    updateQuantity(sp, n) {
        sp.quantity = n;
        this.updateSaleProduct(sp)
        this.updateSaleSummary();
    }

    async onRemoveItem(sp, gv, numberFormat, input = (-99999)) {
        if (!this.isBillRequested()) {
            if (sp.sale_product_status == 'Submitted') {
                let authorize_key = "delete_item_required_password"
                if (gv.setting.pos_setting['check_delete_item_require_passord_from_product'] == 1 && sp.delete_from_pos_require_password == 0) {
                    authorize_key = "delete_item_required_password_dont_check" //we change this authorize key is just for when delete item do not show popup password
                }
                gv.authorize(authorize_key, "delete_item", "delete_item_required_note", "Delete Item Note", sp.product_code, true).then(async (v) => {
                    if (v) {
                        let result = false;
                        if (input == (-99999)) {
                            let hide_keypad = input == (-99999) ? undefined : true
                            if (!hide_keypad && sp.is_timer_product) {
                                hide_keypad = true
                            }
                            result = await keypadWithNoteDialog({
                                data: {
                                    hide_keypad: hide_keypad,
                                    title: `${$t('Delete Item')} ${sp.product_name}`,
                                    label_input: $t('Enter Quantity'),
                                    note: "Delete Item Note",
                                    category_note_name: v.category_note_name,
                                    number: input == (-99999) ? sp.quantity : input,
                                    product_code: sp.product_code
                                }
                            });
                        }
                        else {
                            if (gv.setting.pos_setting['delete_item_required_note'] == 1) {
                                result = await keypadWithNoteDialog({
                                    data: {
                                        hide_keypad: true,
                                        title: `${$t('Delete Item')} ${sp.product_name}`,
                                        label_input: $t('Enter Quantity'),
                                        note: "Delete Item Note",
                                        category_note_name: v.category_note_name,
                                        number: input,
                                        product_code: sp.product_code
                                    }
                                });
                            } else {
                                result = {
                                    number: input,
                                    note: '',
                                }
                            }
                        }
                        if (result) {
                            if (sp.quantity < result.number) {
                                result.number = sp.quantity;
                            }
                            sp.deleted_item_note = result.note;
                            sp.deleted_quantity = (sp.deleted_quantity || 0) + result.number;
                            this.onRemoveSaleProduct(sp, result.number, v.user);

                            let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
                            let msg = `${v.user} delete item: ${item_description}`;
                            msg += `, Qty: ${result.number}`;
                            msg += `, Amount: ${numberFormat(gv.getCurrnecyFormat, sp.amount)}`;
                            msg += `${result.note == "" ? '' : ', Reason: ' + result.note}`;
                            this.auditTrailLogs.push({
                                doctype: "Comment",
                                subject: "Delete Sale Product",
                                comment_type: "Info",
                                reference_doctype: "Sale",
                                reference_name: "New",
                                comment_by: v.user,
                                content: msg,
                                custom_item_description: `${result.number} x ${item_description}`,
                                custom_note: result.note,
                                custom_amount: sp.amount
                            });

                        }
                    }
                });
            } else {
                const u = JSON.parse(localStorage.getItem('make_order_auth'));
                if ((sp.name || "") != "") {                  
                    this.onRemoveSaleProduct(sp, sp.quantity, u.name);
                    let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`
                    let msg = `${u.name} delete item: ${item_description}`;
                    msg += `, Qty: ${sp.quantity}`;
                    msg += `, Amount: ${numberFormat(gv.getCurrnecyFormat, sp.amount)}`;
                    this.auditTrailLogs.push({
                        doctype: "Comment",
                        subject: "Delete Not Submit Sale Product",
                        comment_type: "Info",
                        reference_doctype: "Sale",
                        reference_name: "New",
                        comment_by: u.name,
                        content: msg,
                        custom_item_description: `${sp.quantity} x ${item_description}`,
                        custom_note: '',
                        custom_amount: sp.amount
                    });
                } else {
                   if(input!= (-99999)){
                        if(sp.quantity <= input){
                            this.sale.sale_products.splice(this.sale.sale_products.indexOf(sp), 1);
                        }
                        else{
                            this.onRemoveSaleProduct(sp, input, u.name); 
                        }
                   }else{
                    this.sale.sale_products.splice(this.sale.sale_products.indexOf(sp), 1);
                   }
                    this.updateSaleSummary();
                }
            }
        }
    }

    async onChangePrice(sp, gv, numberFormat, input = (-99999)) {
        if (!this.isBillRequested()) {
            gv.authorize("change_item_price_required_password", "change_item_price", "change_item_price_required_note", "Change Item Price Note", sp.product_code).then(async (v) => {
                if (v) {
                    let result = false;
                    if (input == (-99999)) {
                        input = await keyboardDialog({ title: $t("Change Price"), type: 'number', value: sp.price });
                        result = input;
                    }
                    else {
                        result = input;
                    }
                    if (result != false || result == 0 ) {
                        const price = sp.price;
                        sp.change_price_note = v.note;
                        if (result == false) {
                            sp.price = parseFloat(this.getNumber(sp.price));
                        }else{
                            sp.price = parseFloat(this.getNumber(result));
                        }
                        this.updateSaleProduct(sp);
                        this.updateSaleSummary();
                        let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
                        let msg = `${v.user} change price on item: ${item_description}`;
                        msg += `, from: ${numberFormat(gv.getCurrnecyFormat, price)} to ${numberFormat(gv.getCurrnecyFormat, sp.price)}`;
                        msg += `${v.note == "" ? '' : ', Reason: ' + v.note}`;
                        this.auditTrailLogs.push({
                            doctype: "Comment",
                            subject: "Change Price",
                            comment_type: "Info",
                            reference_doctype: "Sale",
                            reference_name: "New",
                            comment_by: v.user,
                            content: msg,
                            custom_item_description: `${sp.quantity} x ${item_description} (from: ${numberFormat(gv.getCurrnecyFormat, price)} to ${numberFormat(gv.getCurrnecyFormat, sp.price)})`,
                            custom_note: v.note,
                            custom_amount: sp.amount,
                        });
                    }
                    this.dialogActiveState = false;
                }
            });
        }
    }

    async onChangeQuantity(sp, gv) {
        if (this.setting.pos_setting.allow_change_quantity_after_submit == 0 && sp.sale_product_status == 'Submitted') {
            return;
        }
        if (!this.isBillRequested()) {
            const result = await keyboardDialog({ title: $t("Change Quantity"), type: 'number', value: sp.quantity });
            if (result) {
                let quantity = this.getNumber(result);
                if (this.setting.pos_setting.allow_change_quantity_after_submit == 1 || sp.sale_product_status == "New") {
                    if (quantity == 0) {
                        quantity = 1
                    }
                    if (sp.is_return == 1){
                        quantity = quantity * -1
                    }
                    const u = JSON.parse(localStorage.getItem('make_order_auth'));
                    let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
                    let msg = `${u.name} change quantity on: ${item_description}`;
                    msg += `, from : ${sp.quantity} to ${quantity}`;
                    const curr_sp = JSON.parse(JSON.stringify(sp));
                    //update quantity and sale product data
                    this.updateQuantity(sp, quantity);
                    //add to audit log
                    this.auditTrailLogs.push({
                        doctype: "Comment",
                        subject: "Change Quantity",
                        comment_type: "Info",
                        reference_doctype: "Sale",
                        reference_name: "New",
                        comment_by: u.name,
                        content: msg,
                        custom_item_description: `${quantity} x ${item_description} (from : ${curr_sp.quantity} to ${quantity})`,
                        custom_note: "",
                        custom_amount: sp.amount
                    });
                } else {
                    sp.selected = false;
                    //do add record
                    if (quantity > sp.quantity) {
                        this.cloneSaleProduct(sp, quantity);
                    } else {
                        if (sp.quantity - quantity > 0) {
                            //do delete record
                            gv.authorize("delete_item_required_password", "delete_item", "delete_item_required_note", "Delete Item Note", "", false).then(async (v) => {
                                if (v) {
                                    sp.deleted_item_note = v.note;
                                    this.onRemoveSaleProduct(sp, sp.quantity - quantity, v.user);
                                    let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
                                    let msg = `${v.user} delete item: ${item_description}`;
                                    msg += `, Qty: ${quantity}`;
                                    msg += `, Amount: ${NumberFormat(gv.getCurrnecyFormat, sp.amount)}`;
                                    msg += `${(sp.deleted_item_note || "") == "" ? '' : ', Reason: ' + sp.deleted_item_note}`;
                                    this.auditTrailLogs.push({
                                        doctype: "Comment",
                                        subject: "Delete Sale Product",
                                        comment_type: "Info",
                                        reference_doctype: "Sale",
                                        reference_name: "New",
                                        comment_by: v.user,
                                        content: msg,
                                        custom_item_description: `${quantity} x ${item_description}`,
                                        custom_note: v.note,
                                        custom_amount: sp.amount
                                    });
                                }
                            });
                        }
                    }
                }
            }
            this.dialogActiveState = false;
        }
    }

    async onSaleProductNote(sp) {
        if (!this.isBillRequested()) {
            const result = await noteDialog({ title: $t("Note"), name: 'Items Note', data: sp });
            if (result != false) {
                sp.note = result
                socket.emit("ShowOrderInCustomerDisplay", this.sale,"", this.customer_display_key);
            }
        }
    }

    async onSaleNote(p) {
        if (!this.isBillRequested()) {
            const result = await noteDialog({ title: $t("Note"), name: 'Sale Note', data: p });
            if (result != false) {
                p.note = result
            }
        }
    }

    async onSplitSaleProduct( sp){
        if(!this.isBillRequested()){
            const currentQty = sp.quantity ;
            if(currentQty <=1){
                return;
            }
            const result =  await keyboardDialog({ title: `${$t("Split Item")}`, type: 'number', value: 1 });
            if(result){
                let splipQty = parseFloat(this.getNumber(result));
                if(splipQty >= currentQty){
                    toaster.warning($t("Item cannot split equal or over current quantity"))
                    return;
                }
                let splitItemProduct = JSON.parse(JSON.stringify(sp));
                splitItemProduct.name = "";
                splitItemProduct.quantity = splipQty;
                splitItemProduct.selected = false; 
                this.updateSaleProduct(splitItemProduct);
                this.sale.sale_products.push(splitItemProduct);
                //update old sale product  
                sp.quantity = sp.quantity - splipQty;
                this.updateSaleProduct(sp);
                this.updateSaleSummary();
            }
            this.dialogActiveState = false;
        }
    }

    async onSaleProductFree(sp) {
        let freeQty = 0;
        const result = sp.quantity == 1 ? 1 : await keyboardDialog({ title: $t("Change Free Quantity"), type: 'number', value: sp.quantity });
        if (result != false) {
            freeQty = parseFloat(this.getNumber(result));
            if (freeQty > sp.quantity) {
                freeQty = sp.quantity;
            }
            let free_by = sp.free_by || "";
            let free_note = sp.free_note;
            if (freeQty == sp.quantity) {
                sp.is_free = true;
                sp.backup_modifier_price = sp.modifiers_price
                sp.backup_product_price = sp.price
                sp.price = 0;
                sp.modifiers_price = 0;
                this.updateSaleProduct(sp);
                this.updateSaleSummary();
            }
            else {
                let freeSaleProduct = JSON.parse(JSON.stringify(sp));
                freeSaleProduct.name = "";
                freeSaleProduct.quantity = freeQty;
                freeSaleProduct.backup_product_price = sp.price
                freeSaleProduct.backup_modifier_price = sp.modifiers_price
                freeSaleProduct.price = 0;
                freeSaleProduct.modifiers_price = 0;
                freeSaleProduct.selected = false;
                freeSaleProduct.is_free = true;
                this.updateSaleProduct(freeSaleProduct);
                this.sale.sale_products.push(freeSaleProduct);
                //old record 
                sp.free_note = "";
                sp.quantity = sp.quantity - freeQty;
                this.updateSaleProduct(sp);
            }
            this.updateSaleSummary();
            //audit trail
            let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
            let msg = `${free_by} free on item: ${item_description}`;
            msg += `, Qty: ${freeQty}`;
            msg += `${(free_note || "") == "" ? '' : ', Reason: ' + free_note}`;
            this.auditTrailLogs.push({
                doctype: "Comment",
                subject: "Free Sale Product",
                comment_type: "Info",
                reference_doctype: "Sale",
                reference_name: "New",
                comment_by: free_by,
                content: msg,
                custom_item_description: `${freeQty} x ${item_description}`,
                custom_note: free_note
            });
        }
        this.dialogActiveState = false;

    }
    async onRemoveParkItem(sp) {
        sp.is_park = 0
        sp.expired_date = ''
    }
    async onSaleProductPark(sp) {
        let parkQty = 0;
        const result = sp.quantity == 1 ? 1 : await keyboardDialog({ title: $t("Change Park Quantity"), type: 'number', value: sp.quantity });
        if (result != false) {
            parkQty = parseFloat(this.getNumber(result));
            if (parkQty > sp.quantity) {
                parkQty = sp.quantity;
            }
            let park_by = sp.free_by || "";
            if (parkQty == sp.quantity) {
                sp.backup_product_price = sp.price
                sp.is_park = 1
                sp.expired_date = moment(window.current_working_date).add(this.setting.pos_setting.park_item_days_expiry, 'days').format('yyyy-MM-DD');
                this.updateSaleProduct(sp);
                this.updateSaleSummary();
            }
            else {
                let parkSaleProduct = JSON.parse(JSON.stringify(sp));
                parkSaleProduct.name = "";
                parkSaleProduct.quantity = parkQty;
                parkSaleProduct.backup_product_price = sp.price
                parkSaleProduct.backup_modifier_price = sp.modifiers_price
                parkSaleProduct.selected = false;
                parkSaleProduct.is_park = true;
                parkSaleProduct.expired_date = moment(window.current_working_date).add(this.setting.pos_setting.park_item_days_expiry, 'days').format('yyyy-MM-DD');
                this.updateSaleProduct(parkSaleProduct);
                this.sale.sale_products.push(parkSaleProduct);
                //old record 
                sp.quantity = sp.quantity - parkQty;
                this.updateSaleProduct(sp);
            }
            this.updateSaleSummary();
            //audit trail
            let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
            let msg = `${free_by} park on item: ${item_description}`;
            msg += `, Qty: ${park_by}`;
            this.auditTrailLogs.push({
                doctype: "Comment",
                subject: "Park Sale Product",
                comment_type: "Info",
                reference_doctype: "Sale",
                reference_name: "New",
                comment_by: park_by,
                content: msg,
                custom_item_description: `${park_by} x ${item_description}`,
                custom_note: free_note
            });
        }
        this.dialogActiveState = false;

    }

    // change tax setting
    async onChangeTaxSetting(title, _tax_rule_name, _change_tax_setting_note, gv, sale_product) {
        if (!this.isBillRequested()) {
            this.dialogActiveState = true
            // const tax_rule_name = tax_rule
            await gv.authorize("change_tax_setting_required_password", "change_tax_setting", "change_tax_setting_required_note", "Change Tax Setting", "", true).then(async (v) => {
                if (v) {
                    const resp = await changeTaxSettingModal({
                        title: title,
                        data: {
                            tax_rule: _tax_rule_name,
                            note: _change_tax_setting_note,
                            category_note_name: v.category_note_name
                        }
                    })
                    this.sale.dialogActiveState = false
                    if (resp != false) {
                        const _tax_rule = JSON.parse(resp.tax_rule.tax_rule_data);
                        if (sale_product) {
                            sale_product.product_tax_rule = _tax_rule.name;
                            this.onSaleProductApplyTax(_tax_rule, sale_product);
                            // this.onCalculateTax(sale_product);
                            this.updateSaleProduct(sale_product);
                        }
                        else {
                            this.onSaleApplyTax(_tax_rule, this.sale);
                        }
                        this.updateSaleSummary();
                    }
                }
            });
        }
    }

    async onSaleProductChangeTaxSetting(sp, gv) {
        await this.onChangeTaxSetting($t('Change Tax Setting'), sp.product_tax_rule, sp.change_tax_setting_note, gv, sp);
    }
    onUpdateSaleDiscount(discount,discount_type, discount_note){
        this.sale.discount = discount;
        this.sale.discount_type = discount_type;
        this.sale.discount_note = discount_note;
        const sale_discount = this.sale.discount;
        (this.sale.sale_products ?? []).forEach(_sp => {
            if (sale_discount > 0 && _sp.allow_discount && _sp.discount == 0) {
                _sp.sale_discount_percent = sale_discount;
                const temp_sale_discount_amount = (sale_discount / 100) * _sp.sub_total;
                const sale_discount_amount =  Number((temp_sale_discount_amount + Number.EPSILON).toFixed(this.setting.pos_setting.main_currency_precision))
                _sp.sale_discount_amount = sale_discount_amount
            }
            else {
                _sp.sale_discount_percent = 0;
                _sp.sale_discount_amount = 0;
            }
            _sp.total_discount = (_sp.sale_discount_amount || 0) + (_sp.discount_amount || 0);
            this.updateSaleProduct(_sp);
        });
    }

    async onDiscount(gv, title, amount, discount_value, discount_type, discount_codes, discount_note, sp, category_note_name) {
        const branch = this.setting?.business_branch
        const result = await saleProductDiscountDialog({
            title: title,
            value: amount,
            data: {
                discount_value: discount_value,
                discount_type: discount_type,
                discount_codes: discount_codes.filter(d=> (d.branch || branch) == branch),
                discount_note: discount_note,
                sale_product: sp,
                category_note_name: category_note_name
            }
        })
        this.dialogActiveState = false;
        if (result != false) {
            if (sp) {
                sp.discount = result.discount;
                sp.discount_type = result.discount_type;
                sp.discount_note = result.discount_note;
                this.updateSaleProduct(sp);
                //discount sale product audit
                this.onDiscountSaleProductAudit(sp, gv, result);
            } else {
                if (result.revenue_group.length > 0) {
                    this.sale.discount = 0;
                    this.sale.sale_products.forEach(sp => {
                        if (sp.allow_discount) {
                            if (result.revenue_group.includes(sp.revenue_group)) {
                                sp.discount = result.discount;
                                sp.discount_type = result.discount_type;
                                sp.discount_note = result.discount_note;
                                this.updateSaleProduct(sp);
                                //disoucnt sale product audit
                                this.onDiscountSaleProductAudit(sp, gv, result);
                            }
                        }
                    });
                }
                else {
                    this.onUpdateSaleDiscount(result.discount, result.discount_type,result.discount_note);
                    //sale discount audit
                    let discount = this.sale.discount_type == "Percent" ? `${this.sale.discount} %` : NumberFormat(gv.getCurrnecyFormat, this.sale.discount);                //audit trail
                    let msg = `${this.sale.temp_discount_by} discount (${discount}) on Bill`;
                    msg += `${(result.discount_note || "") == "" ? '' : ', Reason: ' + result.discount_note}`;
                    this.auditTrailLogs.push({
                        doctype: "Comment",
                        subject: "Sale Discount",
                        comment_type: "Info",
                        reference_doctype: "Sale",
                        reference_name: "New",
                        comment_by: this.sale.temp_discount_by,
                        content: msg,
                        custom_item_description: `Discount (${discount})`,
                        custom_note: result.discount_note,
                        custom_amount: (this.sale.grand_total || 0)
                    });
                }
            }
            this.updateSaleSummary();
        }
        this.dialogActiveState = false;

    }

    onDiscountSaleProductAudit(sp, gv, result) {
        let discount = sp.discount_type == "Percent" ? `${sp.discount} %` : NumberFormat(gv.getCurrnecyFormat, sp.discount);                //audit trail
        let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
        let msg = `${sp.temp_discount_by} discount (${discount}) on item: ${item_description} `;
        msg += `${(result.discount_note || "") == "" ? '' : ', Reason: ' + result.discount_note}`;
        this.auditTrailLogs.push({
            doctype: "Comment",
            subject: "Discount Sale Product",
            comment_type: "Info",
            reference_doctype: "Sale",
            reference_name: "New",
            comment_by: sp.temp_discount_by,
            content: msg,
            custom_item_description: `${sp.quantity} x ${item_description} (discount: ${discount})`,
            custom_note: result.discount_note,
            custom_amount: sp.amount
        });
    }

    async onSaleProductSetSeatNumber(sp) {
        if (!this.isBillRequested()) {
            const result = await keyboardDialog({ title: $t("Set Seat Number"), type: 'number', value: sp.seat_number })
            if (typeof result == 'number') {
                sp.seat_number = parseInt(result);
                if (sp.seat_number == undefined || isNaN(sp.seat_number)) {
                    sp.seat_number = 0;
                    socket.emit("ShowOrderInCustomerDisplay", this.sale,"", this.customer_display_key);
                }
            } else {
                return;
            }
        }
    }

    onSaleProductCancelFree(sp) {
        if (!this.isBillRequested()) {
            sp.is_free = 0
            sp.price = sp.backup_product_price
            sp.modifiers_price = sp.backup_modifier_price
            sp.free_note = ''
            this.updateSaleProduct(sp)
            this.updateSaleSummary();
            //audit trail
            const u = JSON.parse(localStorage.getItem('make_order_auth'));
            let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
            let msg = `${u.name} remove free on item: ${item_description} `;
            msg += `, Qty: ${sp.quantity}`;
            this.auditTrailLogs.push({
                doctype: "Comment",
                subject: "Remove Free Sale Product",
                comment_type: "Info",
                reference_doctype: "Sale",
                reference_name: "New",
                comment_by: u.name,
                content: msg,
                custom_item_description: `${sp.quantity} x ${item_description}`,
                custom_note: "",
                custom_amount: sp.amount
            });
        }
    }

    getNumber(val) {
        val = (val = val == null ? 0 : val)
        if (isNaN(val)) {
            return 0;
        }
        return parseFloat(val);
    }

    getString(val) {
        val = (val = val == null ? "" : val)
        return val;
    }

    onRemoveSaleProduct(sp, quantity, username) {
        if (sp.quantity == quantity) {
            if (sp.sale_product_status == 'Submitted') {
                sp.show_in_list = true;
                const sp_data = JSON.parse(JSON.stringify(sp));
                sp_data.created_by = username;
                this.deletedSaleProducts.push(sp_data);
                this.deletedSaleProductsDisplay.push(sp_data);
            }
            this.sale.sale_products.splice(this.sale.sale_products.indexOf(sp), 1);

        } else {
            sp.show_in_list = false;
            sp.quantity = sp.quantity - quantity;
            if (sp.sale_product_status == 'Submitted') {
                let deletedRecord = JSON.parse(JSON.stringify(sp))
                deletedRecord.quantity = quantity;
                deletedRecord.created_by = username;
                this.deletedSaleProducts.push(deletedRecord);
                this.deletedSaleProductsDisplay.push(deletedRecord);
            }
        }
        // check if product is timer peroduct then remove it child
        // child record will remove in  doctype event
        if (sp.is_timer_product && sp.name) {
            this.sale.sale_products.filter(r => r.reference_sale_product == sp.name).forEach(x => {
                this.sale.sale_products.splice(this.sale.sale_products.indexOf(x), 1);
            })
        }
        this.updateSaleProduct(sp);
        this.updateSaleSummary();
    }

    async OnEditSaleProduct(sp) {
        if (sp.is_combo_menu && sp.use_combo_group) {
            const result = await SaleProductComboMenuGroupModal();
            if (result) {
                if (result.combo_groups.length > 0) {
                    let combo_menu_items = ''
                    if (result.combo_groups.length > 0) {
                        result.combo_groups.forEach(r => {
                            combo_menu_items = combo_menu_items + r.product_name + ' x' + r.quantity + ', '
                        });
                        sp.combo_menu = combo_menu_items.slice(0, combo_menu_items.length - 2)
                        sp.combo_menu_data = JSON.stringify(result.combo_groups)
                    } else {
                        sp.combo_menu = ''
                        sp.combo_group_data = '[]'
                    }
                } else {
                    sp.combo_menu = ''
                    sp.combo_group_data = "[]"
                }
                this.updateSaleProduct(sp);
                this.updateSaleSummary();
                toaster.success($t("msg.Update successfully"))
            }
        }
        else {
            const result = await addModifierDialog();
            if (result) {
                if (result.portion != undefined) {
                    sp.portion = this.getString(result.portion.portion);
                    sp.price = this.getNumber(result.portion.price);
                    sp.unit = this.getString(result.portion.unit);
                }

                if (result.modifiers != undefined) {
                    sp.modifiers = this.getString(result.modifiers.modifiers);
                    sp.modifiers_price = this.getNumber(result.modifiers.price);
                    sp.modifiers_data = result.modifiers.modifiers_data;
                } else {
                    sp.modifiers = "";
                    sp.modifiers_price = 0;
                    sp.modifiers_data = "[]";
                }
                this.updateSaleProduct(sp);
                this.updateSaleSummary();
                toaster.success($t("msg.Update successfully"))
            }
        }
    }

    onCheckPriceSmallerThanZero() {
        if (this.sale.sale_products.filter(r => r.amount < 0 && r.is_return == 0).length > 0) {
            toaster.warning($t('msg.Product price cannot smaller than zero'));
            return true
        }
        else if (this.sale.grand_total < 0 && this.sale.sale_products.filter(r => r.amount < 0 && r.is_return == 1).length <= 0) {
            toaster.warning($t('msg.Sale price cannot smaller than zero'));
            return true
        }
        else {
            return false
        }
    }
    
    async onSubmit() {
        this.loading = true;
        let is_new = this.sale.creation == this.sale.modified
        let allow_overwrite_max_order_per_guest = JSON.parse(localStorage.getItem("current_user")).permission["allow_overwrite_max_order_per_guest"]
        let allow_overwrite_waiting_time = JSON.parse(localStorage.getItem("current_user")).permission["allow_overwrite_waiting_time"]
        if(this.setting.maximum_order_per_guest>0 && this.setting.use_retail_ui == 0){
            if(this.sale.guest_cover == 0){
                toaster.error($t('Please add guest cover.'));
                this.loading = false;
                return
            }

            let maximum_order_per_guest = this.setting.maximum_order_per_guest
            let new_orders_qty = this.sale?.sale_products?.filter(r=>r.is_newly_added == 1)?.reduce((sum, a) => sum + (a.quantity || 0), 0);
            let guest_cover = this.sale.guest_cover
            let average_orders_per_guest = new_orders_qty/guest_cover
            if(maximum_order_per_guest<average_orders_per_guest && has_changes(this.sale) == 1 && allow_overwrite_max_order_per_guest == 0){
                this.loading = false;
                ComOrderLimitDialog({ business_branch:this.setting?.business_branch,order_limit:1 });
                return
            }
        }
        if(this.setting.menu_waiting_time > 0 && !is_new && this.setting.use_retail_ui == 0){
            const top = this.sale.sale_products.filter(r=>(r.is_newly_added || 0) == 0).reduce((maxObj, obj) => 
                obj.order_time > maxObj.order_time ? obj : maxObj
            );
            const start = new Date(top.order_time);
            const end = new Date();
            let diff = ((end-start)/60000)
            let minimum = this.setting.menu_waiting_time
            if(diff < minimum && has_changes(this.sale) == 1 && allow_overwrite_waiting_time == 0){
                this.loading = false;
                ComOrderLimitDialog({ business_branch:this.setting?.business_branch,time_limit:1 });
                return
            }
        }
        const resp = await Ping(this.setting)
        if(resp == 0){
            toaster.error($t('Please check your network connection'));
            this.loading = false;
            return
        }

        return new Promise(async (resolve) => {
            if (this.sale.sale_products.length == 0 && this.sale.name == undefined && (this.sale.from_reservation || "") == "") {
                toaster.warning($t('msg.Please select a menu item to submit order'));
                resolve(false);
            }
            else if (this.onCheckPriceSmallerThanZero()) {
                resolve(false);
            }
            else {
                let doc = JSON.parse(JSON.stringify(this.sale));
                let _sale = undefined;
                this.generateProductPrinters();
                if (this.sale.sale_status != "Hold Order") {
                    doc.sale_products.filter(r => r.sale_product_status == "New").forEach(x => {
                        x.sale_product_status = "Submitted";
                    })
                }
                if (this.getString(this.sale.name) == "") {
                    if (this.newSaleResource == null) {
                        this.createNewSaleResource();
                    }
                    try{
                         _sale = await this.newSaleResource.submit({ doc: doc });
                    }
                    catch(error){
                        if(this.sale.sale_status == "Bill Requested"){
                            this.sale.sale_status = "Submitted";
                        }
                        this.loading = false;
                   
                        return;
                    }
                }
                else {
                    try{
                        _sale = await this.saleResource.setValue.submit(doc);   
                        if (_sale.name && _sale.grand_total !=  this.__backup_sale.grand_total && (_sale.aba_transaction_id||"") != ""){
                            call.post("epos_restaurant_2023.api.payway.aba_close_transaction", { 
                                "property_code": this.setting.property_code,
                                "pos_config": this.setting.pos_config,
                                "invoice_id": _sale.name
                            }); 
                        }
                    }
                    catch(error){
                        if(this.sale.sale_status == "Bill Requested"){
                            this.sale.sale_status = "Submitted";
                        }
                        this.loading = false;
                     
                        return;
                    }
                }
                this.submitToAuditTrail(doc);
                //refresh tabl 
                resolve(_sale);
            }
             this.loading = false;
        })

    }



    async onSubmitQuickPay() {
        if (this.sale.sale_products.filter(r => !r.time_out_price && r.is_timer_product).length > 0) {
            toaster.warning($t('msg.Please stop timer on timer product'));
            return;
        }
        return new Promise(async (resolve) => {
            if (this.sale.sale_products.length == 0) {
                toaster.warning($t('msg.Please select a menu item to process payment'));
                resolve(false);
            } else {
                const check_employee = this.sale.sale_products.filter((sp) => sp.is_require_employee && (JSON.parse(sp.employees || "[]")).length <= 0)
                if (check_employee.length > 0) {
                    toaster.warning($t('msg.Please assign employee to items'));
                    resolve(false);
                }
                else {
                    if (await confirmDialog({ title: $t("Quick Pay"), text: $t('msg.are you sure to process quick pay and close order') })) {
                        this.loading = true;
                        const resp = await Ping(this.setting)
                        if(resp == 0){
                            toaster.error($t('Please check your network connection'));
                            this.loading = false;
                            resolve(false);
                            return
                        }
                        this.sale.payment = [];
                        this.sale.payment.push({
                            payment_type: this.setting?.default_payment_type,
                            input_amount: this.sale.grand_total,
                            amount: this.sale.grand_total
                        });
                        socket.emit("ShowOrderInCustomerDisplay", this.sale, "paid", this.customer_display_key);
                        const now = new Date();
                        const u = JSON.parse(localStorage.getItem('make_order_auth'));
                        this.sale.paid_by = u.name;
                        this.sale.paid_date = moment(now).format('yyyy-MM-DD HH:mm:ss.SSS');
                        if ((this.sale.printed_by || "") == "") {
                            this.sale.printed_by = u.name;
                            this.sale.printed_date = moment(now).format('yyyy-MM-DD HH:mm:ss.SSS');
                        }
                        this.sale.sale_status = "Submitted";
                        this.sale.docstatus = 1;
                        this.sale.sale_status = "Closed";
                        this.sale.cashier_shift = this.cashier_shift;
                        this.sale.working_day = this.working_day;
                        this.sale.pos_profile = this.setting?.pos_profile;
                        this.sale.outlet = this.setting?.outlet;
                        this.action = "quick_pay";
                        let doc = JSON.parse(JSON.stringify(this.sale));
                        this.generateProductPrinters();
                        let msg = `${u.name} quick pay`;
                        this.auditTrailLogs.push({
                            doctype: "Comment",
                            subject: "Quick Payment",
                            comment_type: "Info",
                            reference_doctype: "Sale",
                            reference_name: "New",
                            comment_by: u.name,
                            content: msg,
                            custom_item_description: "",
                            custom_note: "",
                            custom_amount: ((this.sale.total_paid || 0) - (this.sale.changed_amount || 0))
                        });
                        if (this.getString(this.sale.name) == "") {
                            if (this.newSaleResource == null) {
                                this.createNewSaleResource();
                            }
                            await this.newSaleResource.submit({ doc: doc });
                        }
                        else {
                            await this.saleResource.setValue.submit(doc);
                        }
                        this.submitToAuditTrail(doc);
                        resolve(true);
                    }
                }
            }
            this.loading = false;
        })
    }

    async onSubmitPayment(isPrint = true, ignore = false) {
        this.isPrintReceipt = isPrint;
        return new Promise(async (resolve) => {
            let balance = Number((this.sale.balance + Number.EPSILON).toFixed(this.setting.pos_setting.main_currency_precision));
            if (balance > 0 && ignore == false) {
                toaster.error($t('Please enter all payment amount'));
                resolve(false);
            } else { 
                let conf = true;
                if(ignore == false ){
                    conf = await confirmDialog({ title: $t("Payment"), text: $t("msg.are you sure to process payment and close order") });
                }
                if (conf) {
                    this.loading = true;
                    const resp = await Ping(this.setting)
                    if(resp == 0){
                        toaster.warning($t('msg.Please check your network connection'));
                        this.loading = false;
                        resolve(false);
                        return
                    }
                    socket.emit("ShowOrderInCustomerDisplay", this.sale, "paid", this.customer_display_key);
                    this.generateProductPrinters();
                    const now = new Date();
                    const u = JSON.parse(localStorage.getItem('make_order_auth'));
                    this.sale.paid_by = u.name;
                    this.sale.paid_date = moment(now).format('yyyy-MM-DD HH:mm:ss.SSS');
                    if ((this.sale.printed_by || "") == "") {
                        this.sale.printed_by = u.name;
                        this.sale.printed_date = moment(now).format('yyyy-MM-DD HH:mm:ss.SSS');
                    }
                    this.sale.sale_status = "Closed";
                    this.sale.docstatus = 1;
                    this.sale.cashier_shift = this.cashier_shift;
                    this.sale.working_day = this.working_day;
                    this.sale.pos_profile = this.setting?.pos_profile;
                    this.sale.outlet = this.setting?.outlet;
                    this.action = "payment";
                    if (this.getString(this.sale.name) == "") {
                        if (this.newSaleResource == null) {
                            this.createNewSaleResource();
                        }
                        this.printWaitingOrderAfterPayment = true;
                        try{
                             await this.newSaleResource.submit({ doc: this.sale });
                        }
                        catch(error){
                            this.loading = false;
                            return;
                        }
                    } else {
                        try{
                            await this.saleResource.setValue.submit(this.sale);
                        }
                        catch(error){
                            this.loading = false;
                            return;
                        }
                    }
                    this.submitToAuditTrail(this.sale);

                    if(ignore==true){
                        socket.emit("ABAPayWaySuccess", {}, this.customer_display_key);
                    }

                    resolve(true);
                }
            }
            this.loading = false;
        });
    }

    async onProcessTaskAfterSubmit(doc) { 
        if (this.action == "submit_order") {
            this.onPrintToKitchen(doc); 
            if(this.setting?.device_setting?.print_invoice_on_submit == 1 && this.changed == 1){
                if (this.pos_receipt == undefined || this.pos_receipt == null) {
                    this.pos_receipt = this.setting?.default_pos_receipt;
                }
                this.onPrintReceipt(this.pos_receipt, "print_invoice", doc);
                this.changed = 0
            }
            //print waiting doc
            if (this.setting.pos_setting.print_waiting_order_after_submit_order) {
                this.onPrintWaitingOrder(doc);
            }
        }
        else if (this.action == "print_bill" || this.action =="print_invoice_by_seat") {
            if (this.pos_receipt == undefined || this.pos_receipt == null) {
                this.pos_receipt = this.setting?.default_pos_receipt;
            }
            this.onPrintToKitchen(doc);
            this.onPrintReceipt(this.pos_receipt, `${this.action == "print_invoice_by_seat"? "print_invoice_by_seat": "print_invoice" }`, doc);
        }
        else if (this.action == "quick_pay") {
            
            this.onPrintToKitchen(doc);
            if (this.printWaitingOrderAfterPayment) {
                this.onPrintWaitingOrder(doc);
            }
            this.onPrintReceipt(this.setting?.default_pos_receipt, "print_receipt", doc);
        }
        else if (this.action == "payment") {  
            //open cashdrawer
            if (localStorage.getItem("is_window") == "1") {
                window.chrome.webview.postMessage(JSON.stringify({ action: "open_cashdrawer" }));
            }
            this.onPrintToKitchen(doc); 
            if (this.printWaitingOrderAfterPayment) {
                    this.onPrintWaitingOrder(doc);
            }  
            if (this.isPrintReceipt == true) {
                await  this.onPrintReceipt(this.pos_receipt, "print_receipt", doc);
            }
        }
        //create deleted sale product to database;
        this.deletedSaleProducts.forEach((r) => {
            this.onCreateDeletedSaleProduct(r);
        });

        this.submitToAuditTrail(doc);
        this.sale = {};
        this.orderTime = "";
        socket.emit("RefreshTable");

        
    }

    submitToAuditTrail(d) {
        this.auditTrailLogs.forEach((r) => {
            r.reference_name = d.name;
            this.auditTrailResource.submit({ doc: r })
        });
        this.auditTrailLogs = [];
    }

    onPrintToKitchen(doc, products = null) {
        var _productPrinters = products ?? this.productPrinters; 
        const data = {
            action: "print_to_kitchen",
            setting: this.setting?.pos_setting,
            sale: doc,
            product_printers: _productPrinters,
            station_device_printing: (this.setting?.device_setting?.station_device_printing) || "",
            printers: []
        }
        var groupKeys = "{printer:$.printer,group_item_type:$.group_item_type,ip_address:$.ip_address,port:$.port}"
        var groupFields = "$.printer+','+$.group_item_type+','+$.ip_address+','+$.port";
        var printers = Enumerable.from(data.product_printers).groupBy(groupKeys, "", groupKeys, groupFields).toArray();
        printers.forEach((p) => {
            var _printer = data.product_printers.filter((x) => x.printer == p.printer)
            if (_printer.length > 0) {
                data.printers.push({
                    "printer_name": _printer[0].printer,
                    "group_item_type": _printer[0].group_item_type,
                    "ip_address": _printer[0].ip_address,
                    "port": _printer[0].port,
                    "is_label_printer": (_printer[0].is_label_printer ?? false) ? 1 : 0,
                    "usb_printing": _printer[0].usb_printing ?? 0,
                    "products": _printer
                });
            }
            // We send this to refresh kitchen order display
            socket.emit("SubmitKOD", { "screen_name": _printer[0].printer })
        });
        let kotProducts = {
            action: "print_to_kitchen",
            setting: this.setting?.pos_setting,
            sale: doc,
            product_printers: _productPrinters,
            station_device_printing: (this.setting?.device_setting?.station_device_printing) || "",
            printers: [],
        }
        let productUSBPrinter = JSON.parse(JSON.stringify(kotProducts));
        kotProducts.printers = [];
        productUSBPrinter.printers = []
        let station_printers = (this.setting?.device_setting?.station_printers);
        if (station_printers.length <= 0) {
        } else {
            station_printers.forEach((p) => {
                let temp_sale_products = data.product_printers.filter((x) => x.printer == p.printer_name)
                if (temp_sale_products.length > 0) {
                    if (p.usb_printing == 1) {
                        productUSBPrinter.printers.push({
                            "printer_name": p.printer_name,
                            "group_item_type": p.group_item_type,
                            "ip_address": p.ip_address,
                            "port": p.port,
                            "cashier_printer": p.cashier_printer,
                            "is_label_printer": p.is_label_printer,
                            "usb_printing": p.usb_printing,
                            "products": temp_sale_products
                        });


                    } else {
                        kotProducts.printers.push({
                            "station": this.setting?.device_setting?.name ?? "",
                            "printer": {
                                "printer_name": p.printer_name,
                                "group_item_type": p.group_item_type,
                                "ip_address": p.ip_address,
                                "port": p.port,
                                "cashier_printer": p.cashier_printer,
                                "is_label_printer": p.is_label_printer,
                                "usb_printing": p.usb_printing,
                            },
                            "products": temp_sale_products
                        });
                    }
                }
            });
        }

        if ((this.setting?.device_setting?.use_server_network_printing || 0) == 1) {
            //printer network
            if (kotProducts.printers.length > 0) {
                call.post("epos_restaurant_2023.api.network_printing_api.print_kot_to_network_printer", { "data": kotProducts })
            }
            //trigger print usb print
            if (productUSBPrinter.printers.length > 0) {
                socket.emit("PrintReceipt", JSON.stringify(productUSBPrinter))
            }
        } else {
            if (localStorage.getItem("is_window") == 1) {
                if ((data.product_printers ?? []).length > 0) {
                    window.chrome.webview.postMessage(JSON.stringify(data));
                }
            }
            else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
                if (_productPrinters.length > 0) {
                    //trigger printer network
                    if (kotProducts.printers.length > 0) {
                        flutterChannel.postMessage(JSON.stringify(kotProducts));
                    }
                    //trigger print usb print
                    if (productUSBPrinter.printers.length > 0) {
                        socket.emit("PrintReceipt", JSON.stringify(productUSBPrinter))
                    }
                }
            }
            else {
                socket.emit("PrintReceipt", JSON.stringify(data))

            }
        }
        //reset product printer
        if (products == null) {
            this.productPrinters = [];
        } 
    }

    //p = printer, r = sale product
    onAddToProductPrinters(p, r){
        this.productPrinters.push({
            sale_product_name: (r.name || "New"),
            printer: p.printer,
            group_item_type: p.group_item_type,
            is_label_printer: p.is_label_printer == 1,
            ip_address: p.ip_address,
            port: p.port,
            usb_printing: p.usb_printing,
            product_code: r.product_code,
            product_name_en: r.product_name,
            product_name_kh: r.product_name_kh,
            kitchen_group:r.kitchen_group||"",
            kitchen_group_sort_order: r.kitchen_group_sort_order || 0,
            seat_number: r.seat_number||"",
            portion: r.portion,
            unit: r.unit,
            modifiers: r.modifiers,
            note: r.note,
            quantity: r.quantity,
            is_deleted: false,
            is_free: r.is_free == 1,
            combo_menu: r.combo_menu,
            combo_menu_data: r.combo_menu_data,
            order_by: r.order_by,
            creation: r.creation,
            modified: r.modified,
            is_timer_product: (r.is_timer_product || 0),
            reference_sale_product: r.reference_sale_product,
            duration: r.duration,
            time_stop: (r.time_stop || 0),
            time_in: r.time_in,
            time_out_price: r.time_out_price,
            time_out: r.time_out,
            amount: r.amount
        })
    }

    //get combo print KOT by combo items
    async getProductPrinterOfComboItem(saleProduct, isDeleted = false,moveFromTable=undefined, moveFromSale=undefined){
        let saleProductPrinters = []
        const r = saleProduct;
        if(this.setting.pos_setting.combo_menu_print_captain_by_items_printer && r.is_combo_menu){

            const combo_data = JSON.parse(r.combo_menu_data)
                let productCodes = combo_data.map(i => i.product_code);
                const res = await call.post("epos_restaurant_2023.api.api.get_product_printer_by_products", {
                     "product_codes":productCodes
                });    
                // const printers = JSON.parse(r.printers); 
                const combo_product_printers = res["message"]     
                let product_printers = [];     
                for(const pro of combo_data ){
                    const p_printers = combo_product_printers.filter(r=>r.product_code == pro.product_code)
                    for(const p of p_printers){                    
                            product_printers.push({
                                sale_product_name: (r.name || "New"),
                                move_from_table: moveFromTable,
                                move_from_sale: moveFromSale,
                                printer: p.printer_name,
                                group_item_type: p.group_item_type,
                                is_label_printer: p.is_label_printer == 1,
                                ip_address: p.ip_address,
                                port: p.port,
                                usb_printing: p.usb_printing,
                                product_code: pro.product_code,
                                product_name_en: pro.product_name,
                                product_name_kh: pro.product_name_kh || pro.product_name,
                                kitchen_group:pro.kitchen_group||"",
                                kitchen_group_sort_order: pro.kitchen_group_sort_order || 0,
                                seat_number: r.seat_number||"",
                                portion: r.portion,
                                unit: r.unit,
                                modifiers: r.modifiers,
                                note: r.note,
                                quantity: r.quantity ,
                                combo_quantity : (pro.quantity||1),
                                combo_id : pro.menu_name,
                                is_deleted: isDeleted,
                                is_free: r.is_free == 1,
                                combo_menu: r.product_name,
                                combo_menu_data: null,
                                order_by: r.order_by,
                                creation: r.creation,
                                modified: r.modified,
                                is_timer_product: (r.is_timer_product || 0),
                                reference_sale_product: r.reference_sale_product,
                                duration: r.duration,
                                time_stop: (r.time_stop || 0),
                                time_in: r.time_in,
                                time_out_price: r.time_out_price,
                                time_out: r.time_out,
                                amount: r.amount
                            })
                    }
                }   
                
                // Group by combo_menu, printer, quantity, is_deleted, is_free
                let merged = Object.values(
                    product_printers.reduce((acc, item) => {
                        // key based on fields you want to merge by
                        let key = `${item.combo_menu}|${item.printer}`;
                        if(item.group_item_type != "Printer cut by order"){
                            key += `|${item.product_code}|${item.combo_id}`
                        }

                        if(item.is_label_printer == 1){
                            item.quantity = item.quantity * item.combo_quantity
                        }
                        // const key = `${item.combo_menu}|${item.printer}|${item.quantity}|${item.is_deleted}|${item.is_free}`;
                        const item_display = item.product_name_en 
                      
                        if (!acc[key]) {
                            // copy first item
                            acc[key] = { ...item };
                            // initialize array to store product names for combo_menu field
                           
                            acc[key].combo_menu_list = [item_display];
                            acc[key].combo_menu_code_list = [item.product_code]; 
                        } else {
                            // collect product names
                            acc[key].combo_menu_list.push(item_display);
                            acc[key].combo_menu_code_list.push(item.product_code);
                        }

                        return acc;
                    }, {})
                );
 
                // Map merged array to final structure
                let finalList = merged.map(item => ({
                    sale_product_name: item.sale_product_name,
                    printer: item.printer,
                    group_item_type: item.group_item_type,
                    is_label_printer: item.is_label_printer,
                    ip_address: item.ip_address,
                    port: item.port,
                    usb_printing: item.usb_printing,
                    product_code: r.product_code,
                    product_name_en: r.product_name,
                    product_name_kh: r.product_name_kh,
                    kitchen_group: item.kitchen_group,
                    kitchen_group_sort_order: item.kitchen_group_sort_order,
                    seat_number: item.seat_number,
                    portion: item.portion,
                    unit: item.unit,
                    modifiers: item.modifiers,
                    note: item.note,
                    quantity: item.quantity,
                    is_deleted: item.is_deleted,
                    is_free: item.is_free,
                    combo_menu: item.combo_menu_list.join("^ "), // merged product names
                    combo_menu_data: JSON.stringify(combo_data.filter((x)=> item.combo_menu_code_list.includes(x.product_code) )),
                    order_by: item.order_by,
                    creation: item.creation,
                    modified: item.modified,
                    is_timer_product: item.is_timer_product,
                    reference_sale_product: r.reference_sale_product,
                    duration: item.duration,
                    time_stop: item.time_stop,
                    time_in: item.time_in,
                    time_out_price: item.time_out_price,
                    time_out: item.time_out,
                    amount: item.amount
                })); 

                 finalList.forEach((p)=>{ 
                    saleProductPrinters.push(p)
                 });

                return saleProductPrinters


        }else{
            return false
        }
    }

    generateProductPrinters() {
        this.productPrinters = [];
        this.sale.sale_products.filter(r => r.sale_product_status == 'New').forEach(async (r) => {  
            let comboItemPrinters = await this.getProductPrinterOfComboItem(r);
            ///check if combo print KOT by combo items
            if(!comboItemPrinters){
                const printers = JSON.parse(r.printers);
                if(printers.length > 0){
                    printers.forEach((p) => { 
                        this.productPrinters.push({
                            sale_product_name: (r.name || "New"),
                            printer: p.printer,
                            group_item_type: p.group_item_type,
                            is_label_printer: p.is_label_printer == 1,
                            ip_address: p.ip_address,
                            port: p.port,
                            usb_printing: p.usb_printing,
                            product_code: r.product_code,
                            product_name_en: r.product_name,
                            product_name_kh: r.product_name_kh,
                            kitchen_group:r.kitchen_group||"",
                            kitchen_group_sort_order: r.kitchen_group_sort_order || 0,
                            seat_number: r.seat_number||"",
                            portion: r.portion,
                            unit: r.unit,
                            modifiers: r.modifiers,
                            note: r.note,
                            quantity: r.quantity,
                            is_deleted: false,
                            is_free: r.is_free == 1,
                            combo_menu: r.combo_menu,
                            combo_menu_data: r.combo_menu_data,
                            order_by: r.order_by,
                            creation: r.creation,
                            modified: r.modified,
                            is_timer_product: (r.is_timer_product || 0),
                            reference_sale_product: r.reference_sale_product,
                            duration: r.duration,
                            time_stop: (r.time_stop || 0),
                            time_in: r.time_in,
                            time_out_price: r.time_out_price,
                            time_out: r.time_out,
                            amount: r.amount
                        })
                    });
                }

            }
            else{
                comboItemPrinters.forEach((p)=>{
                    this.productPrinters.push(p);
                });
            } 
        });


        //generate sale product print when change table
        if ((this.changeTableSaleProducts?.length || 0) > 0) {
            this.changeTableSaleProducts.forEach(x => {
                this.productPrinters.push(x);
            })
        }
        if ((this.moveItemSaleProducts?.length || 0) > 0) {
            this.moveItemSaleProducts.forEach(x => {
                this.productPrinters.push(x);
            })
        }


        if (this.setting.pos_setting.print_new_deleted_sale_product) {
            //generate deleted product to product printer list
            this.deletedSaleProducts.forEach(async (r) => {
                let comboItemPrinters = await this.getProductPrinterOfComboItem(r, true);
                 if(!comboItemPrinters){
                    const printers = JSON.parse(r.printers);
                    printers.forEach((p) => {
                        this.productPrinters.push({
                            printer: p.printer,
                            group_item_type: p.group_item_type,
                            is_label_printer: p.is_label_printer == 1,
                            ip_address: p.ip_address,
                            port: p.port,
                            usb_printing: p.usb_printing,
                            product_code: r.product_code,
                            product_name_en: r.product_name,
                            product_name_kh: r.product_name_kh,
                            kitchen_group: r.kitchen_group||"",
                            kitchen_group_sort_order: r.kitchen_group_sort_order || 0,
                            seat_number: r.seat_number||"",
                            portion: r.portion,
                            unit: r.unit,
                            modifiers: r.modifiers,
                            note: r.note,
                            quantity: r.quantity,
                            is_deleted: true,
                            is_free: r.is_free == 1,
                            combo_menu: r.combo_menu,
                            combo_menu_data: r.combo_menu_data,
                            deleted_note: r.deleted_item_note,
                            order_by: r.order_by,
                            creation: r.creation,
                            modified: r.modified,
                            reference_sale_product: r.reference_sale_product,
                            duration: r.duration,
                            time_stop: (r.time_stop || 0),
                            time_in: r.time_in,
                            time_out_price: r.time_out_price,
                            time_out: r.time_out
                        })
                    });
                }else{
                    comboItemPrinters.forEach((p)=>{
                        this.productPrinters.push(p);
                    });
                }
            }); 
        } 
    }


    getPrintReportPath(doctype, name, reportName, isPrint = 0) {
        let url = "";
        // const serverUrl = window.location.protocol + "//" + "//" + window.location.hostname + (window.location.protocol == "https:" ? "" : (":" + this.setting?.pos_setting?.backend_port));
        let port = this.setting?.pos_setting?.use_backend_port == 0 ? `:${window.location.port}` : (window.location.protocol == "https:" ? "" : `:${this.setting?.pos_setting?.backend_port}`)
        const serverUrl = `${window.location.protocol}//${window.location.hostname}${port}`;
        url = serverUrl + "/printview?doctype=" + doctype + "&name=" + name + "&format=" + reportName + "&no_letterhead=0&letterhead=Defualt%20Letter%20Head&settings=%7B%7D&_lang=en&d=" + new Date()
        if (isPrint) {
            url = url + "&trigger_print=" + isPrint
        }
        return url;
    }

    async  onPrintPressed(r, action = "print_bill") {
        if(this.sale.sale_products.filter(r=>!r.time_out_price && r.is_timer_product).length>0){
                toaster.warning($t('msg.Please stop timer on timer product'));
                return false;
        }
        if (this.sale.sale_products?.length == 0) {
            toaster.warning($t("msg.Please select a menu item to submit order"));
            return false
        } else {
            const now = new Date();     
            const u = JSON.parse(localStorage.getItem('make_order_auth'));    
            this.sale.printed_by = u.name;
            this.sale.printed_date = moment(now).format('yyyy-MM-DD HH:mm:ss.SSS');
            this.sale.sale_status = "Bill Requested";
            this.action = action;
            this.pos_receipt = r; 
            let msg = `${u.name} was ${action=="print_bill"?"Printed Bill":"Printed Bill by Seat"}`; 
            this.auditTrailLogs.push({
                doctype:"Comment",
                subject:"Print Bill",
                comment_type:"Info",
                reference_doctype:"Sale",
                reference_name:"New",
                comment_by:u.name,
                content:msg,
                custom_item_description: "",
                custom_note:"",
                custom_amount: (this.sale.grand_total ||0) 
            })  ; 
            return true; 
        }
    }

    async onPrintReceipt(receipt, action, doc) {
        let seat_numbers = []
        // if(action == "print_invoice_by_seat"){
            var groupKeys = "{seat_number:$.seat_number}"
            var groupFields = "$.seat_number";
            var _seat_numbers = Enumerable.from(doc.sale_products).groupBy(groupKeys, "", groupKeys, groupFields).toArray();
            seat_numbers = []
            _seat_numbers.forEach((sn)=>{
                seat_numbers.push(sn.seat_number||"")
            })
        // }  
        let data = {
            action: action,
            print_setting: receipt,
            setting: this.setting?.pos_setting,
            sale: doc,
            seat_numbers:seat_numbers,
            station_device_printing: (this.setting?.device_setting?.station_device_printing) || "",
            station: (this.setting?.device_setting?.name) || "",
        }
        let printer = (this.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
        let _printer = undefined
        if(printer.length>0){
            _printer = {
                "printer_name": printer[0].printer_name,
                "ip_address": printer[0].ip_address,
                "port": printer[0].port,
                "cashier_printer": printer[0].cashier_printer,
                "is_label_printer": printer[0].is_label_printer,
                "usb_printing": printer[0].usb_printing,
            }
        }
        if ((this.setting?.device_setting?.use_server_network_printing || 0) == 1) {            
            if (printer.length <= 0) {
                toaster.warning($t("Printer not yet config for this device"))
                return // not printer
            }
            if (printer[0].usb_printing == 0) {
                const body = {
                    "data": {
                        "name": data["sale"]["name"],
                        "seat_numbers":data["seat_numbers"],
                        "reprint": 0,
                        "action": data["action"],
                        "print_setting": data["print_setting"],
                        "template_name": data["print_setting"]["pos_receipt_template"],
                        "printer": _printer
                    }
                }
                call.post("epos_restaurant_2023.api.network_printing_api.print_bill_to_network_printer", body)
                return // print network
            }else if((localStorage.getItem("flutterWrapper") || 0) == 1){
                data.printer = _printer;
                socket.emit('PrintReceipt', JSON.stringify(data));
                return
            }
        }
        if (receipt?.pos_receipt_file_name && localStorage.getItem("is_window")) {
            window.chrome.webview.postMessage(JSON.stringify(data));
        } else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
            if (printer.length <= 0) {
                toaster.warning($t("Printer not yet config for this device"))
            } else {
                data.printer = _printer;
                flutterChannel.postMessage(JSON.stringify(data));
            }
        } else {
            let print_from_android_preview = (this.setting?.device_setting?.print_from_android_preview || 0);
            if(print_from_android_preview == 1){
                this.onOpenBrowserPrint("Sale", doc.name, receipt.name)
            }
            else{
                if (receipt?.pos_receipt_file_name) {
                    data.printer = _printer;
                    socket.emit('PrintReceipt', JSON.stringify(data));
                }
                else {
                    this.onOpenBrowserPrint("Sale", doc.name, receipt.name)
                }
            }
        }
    }

    onPrintWaitingOrder(doc) {
        if (this.setting.pos_setting.print_waiting_order_after_submit_order) {
            if (this.orderChanged) {
                const data = {
                    action: "print_waiting_order",
                    setting: this.setting?.pos_setting,
                    sale: doc,
                    station_device_printing: (this.setting?.device_setting?.station_device_printing) || "",
                    station: (this.setting?.device_setting?.name) || "",
                }
                let printer = (this.setting?.device_setting?.station_printers).filter((e) => e.cashier_printer == 1);
                let _printer = undefined;
                if(printer.length>0){
                    _printer = {
                        "printer_name": printer[0].printer_name,
                        "ip_address": printer[0].ip_address,
                        "port": printer[0].port,
                        "cashier_printer": printer[0].cashier_printer,
                        "is_label_printer": printer[0].is_label_printer,
                        "usb_printing": printer[0].usb_printing,
                    }
                }
                if ((this.setting?.device_setting?.use_server_network_printing || 0) == 1) {                    
                    if (printer.length <= 0) {
                        return // not printer
                    }
                    if (printer[0].usb_printing == 0) {
                        const body = {
                            "data": {
                                "name": this.sale.name,
                                "printer": _printer
                            }
                        }
                        call.post("epos_restaurant_2023.api.network_printing_api.print_waiting_number_to_network_printer", body)
                        return // print network
                    }else if ((localStorage.getItem("flutterWrapper") || 0) == 1){
                        data.printer = _printer;
                        socket.emit('PrintReceipt', JSON.stringify(data)); 
                    }
                }
                if (localStorage.getItem("is_window") == "1") {
                    window.chrome.webview.postMessage(JSON.stringify(data));
                }
                else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
                    if (printer.length <= 0) {
                        //pass
                    } else {
                        data.printer = _printer;
                        flutterChannel.postMessage(JSON.stringify(data));
                    }
                }
                else {
                    data.printer = _printer;
                    socket.emit('PrintReceipt', JSON.stringify(data));
                }
                this.printWaitingOrderAfterPayment = false;
                this.orderChanged = false;
            }
        }
    }

    onOpenBrowserPrint(doctype, docname, filename) {
        const url = this.getPrintReportPath(doctype, docname, filename, 1)
        window.open(url).print();
        window.close();
    }

    isBillRequested() {
        if (this.sale.sale_status == 'Bill Requested') {
            toaster.warning($t('msg.this sale order is already print bill please cancel print bill first'));
            return true;
        } else {
            return false;
        }
    }



   async handlePayWayPaymentCallback(paywaysocket, data) {
    // Process payment data
        const resp = data.response;
        if(resp.invoice_id == this.sale.name && 
            this.setting.pos_config == resp.pos_config &&
            this.setting.property_code == resp.property_code        
        ){    
            const check = await this.onPayWayCallbackReCheckTransaction(data);
            if(check == true){
                return;
            } 
            this.sale.payment = (data.sale_payment || this.sale.payment);
            this.sale.payment.forEach((p)=>{
                if(p._temp_payway_tran_id == resp.temp_tran_id && p.is_generate_qr == 1){
                    p.aba_pay_transaction = data.tran_id
                }
            });

            this.payway_complete_payment = true; //trigger to close dialog scan qr            
            this.sale.show_aba_khqr = undefined;
            this.sale.aba_khqr_data = undefined;
            this.sale.payment_transaction = data;

            await setTimeout(()=>{
                socket.emit("ShowOrderInCustomerDisplay", this.sale,"", this.customer_display_key);   
            }, 500)


            if(this.__open_payment_form ==true){
                this.close_payment_form = true;
            }else{

                const is_apk_ipa = localStorage.getItem("apkipa");                
                this.pos_receipt = undefined;
                let is_print = false;
                if(!is_apk_ipa){
                    this.pos_receipt = this.setting.default_pos_receipt;
                    is_print = true;
                }
                   
                this.onSubmitPayment(is_print,true ).then((v) => {
                    if (v) {
                        this.message = $t("msg.Payment successfully");  
                        this.onPayWaySuccessPayment();
                    }
                });
            }

            try{
              call.post("epos_restaurant_2023.helpers.payway_helper.update_payway_tranaction_id_on_callback_success_enqueue", {
                "tran": data
              });
            } catch (err){}
         
           
        }
    }

    onPayWaySuccessPayment(){
        if (this.setting.table_groups.length > 0) {
            this.router.push({ name: "TableLayout" });
        } else {
            this.newSale();
            this.tableSaleListResource.fetch();
            
            let template = (this.setting.device_setting?.main_sale_screen??"Default");
            if(template == "Default"){
                this.router.push({  name: "AddSale"});
            }else {
                const result = template.toLowerCase().replace(/\s+/g, '-');
                let _template = result;
                this.router.push({ 
                    name: "SaleOrder",
                    query: { menu: _template }
                });
            }


            call.get('epos_restaurant_2023.api.api.get_current_shift_information', {
                business_branch: this.setting?.business_branch,
                pos_profile: localStorage.getItem("pos_profile")
            }).then((data) => {
                if (this.message.cashier_shift == null) {
                    toaster.warning($t("msg.Please start shift first"));
                    this.router.push({ name: "OpenShift" });
                } else if (data.message.working_day == null) {
                    toaster.warning($t('msg.Please start working day first'));
                    this.router.push({ name: "StartWorkingDay" });
                } else {
                    this.sale.working_day = data.message.working_day.name;
                    this.sale.posting_date = data.working_day.posting_date;
                    this.posting_date = data.working_day.posting_date;

                    this.sale.cashier_shift = data.message.cashier_shift.name;
                    this.sale.shift_name = data.message.cashier_shift.shift_name;
                    // gv.confirm_close_working_day(data.message.working_day.posting_date);
                    // onCheckExpireHappyHoursPromotion();
                }
            });
        }
    }


    async onPayWayCallbackReCheckTransaction(param){
        if((param.type || "") == "Check Transaction"){
            return false;
        }
        const p = param;

        const request_params = { 
            "tran_id": p.tran_id,//required
            "property_code":p.response.property_code, //required
            "pos_config":p.response.pos_config, //required
            "response":{ //required
                "pos_profile": p.response.pos_profile,
                "station_name":p.response.station_name,
                "invoice_id": p.response.invoice_id,
                "temp_tran_id":p.response.temp_tran_id
            }
        }
        try{
            const resp = await call.post("epos_restaurant_2023.api.payway.aba_check_transaction", request_params)
            if(resp){
                if((resp.message ||"") != "" && (resp.message ||"").toLowerCase() != "pending"){                       
                    return true;
                }
            } 
            return false;           
        }
        catch (err) {
            console.log({"aba_check_transaction": err})
            return false;
        }
    }

    async   onRemovePayment(p) { 
        this.sale.payment.splice(this.sale.payment.indexOf(p), 1);
        this.updatePaymentAmount();
        this.paymentInputNumber = this.sale.balance.toFixed(this.setting.pos_setting.main_currency_precision);  
        if( this.sale.payment.length<=0){
            this.is_payment_first_load = true;
        }             
    }


    async onAddPayment(data) {
        // data {paymentType: , amount:,fee_amount:0,room:null, folio = null, folio_transaction_type=null,folio_transaction_number}     
        const single_payment_type = this.sale.payment.find(r => r.is_single_payment_type == 1);
        if (single_payment_type) {
            toaster.warning($t('msg.You cannot add other payment type with', [single_payment_type.payment_type]));
            return false
        } else {
            const precision = this.setting.pos_setting.main_currency_precision;
            if (data.paymentType.is_single_payment_type == 1) {
                this.sale.payment = [];
                data.amount = parseFloat((parseFloat(this.sale.grand_total * data.paymentType.exchange_rate) + Number.EPSILON).toFixed(precision)); 
            }
            else if( data.paymentType.allow_aba_pay_with_qr_scan == 1){
                let current_precision = data.paymentType.exchange_rate == 1? precision : this.setting.pos_setting.second_currency_precision
                 data.amount = parseFloat((parseFloat((this.sale.balance + Number.EPSILON).toFixed(current_precision) * data.paymentType.exchange_rate) + Number.EPSILON).toFixed(current_precision)); 
            }


            if (!this.getNumber(data.amount) == 0) {

                if ((data.fee_amount || 0) == 0) {
                    data.fee_amount = parseFloat((parseFloat(data.amount / data.paymentType.exchange_rate) +  Number.EPSILON).toFixed(precision)) * (data.paymentType.fee_percentage / 100);
                }

                let payment = {
                    payment_type: data.paymentType.payment_method,
                    payment_type_group:data.paymentType.payment_type_group,
                    input_amount: parseFloat(data.amount),
                    amount: parseFloat((parseFloat(data.amount / data.paymentType.exchange_rate) + Number.EPSILON ).toFixed(precision)),
                    exchange_rate: data.paymentType.exchange_rate,
                    change_exchange_rate: data.paymentType.change_exchange_rate,
                    currency: data.paymentType.currency,
                    is_single_payment_type: data.paymentType.is_single_payment_type,
                    required_customer: data.paymentType.required_customer,
                    use_room_offline: data.paymentType.use_room_offline,
                    room_number: data.room,
                    folio_number: data.folio,
                    account_code: data.paymentType.account_code,
                    cancel_order_adjustment_account_code: data.paymentType.cancel_order_adjustment_account_code,
                    fee_percentage: data.paymentType.fee_percentage,
                    fee_amount: data.fee_amount,
                    folio_transaction_type: data.folio_transaction_type,
                    folio_transaction_number: data.folio_transaction_number,
                    city_ledger_name: data.city_ledger_name,
                    reservation_stay:data.reservation_stay,
                    issue_gift_voucher:data.voucher_name,
                    is_generate_qr: data.paymentType.allow_aba_pay_with_qr_scan,
                    _temp_payway_tran_id : data.temp_payway_tran_id,
                    coupon_code: data.coupon_code
                }

                this.sale.payment.push(payment);
                
                this.updatePaymentAmount();
                this.paymentInputNumber = (this.sale.balance + Number.EPSILON).toFixed(precision);



                //generate payway qr
                if(data.paymentType.allow_aba_pay_with_qr_scan ==  1){                       
                    let payway_payment_amount = data.amount;                    
                    payway_payment_amount += (data.fee_amount ||0) * data.paymentType.exchange_rate ;
                    const result = await scanqrDialog({
                        "temp_tran_id": data.temp_payway_tran_id,
                        "sale_id":this.sale.name,
                        "payment_amount": data.paymentType.currency == "KHR" ?  Math.round(parseFloat(payway_payment_amount).toFixed(0) / 100) * 100  : payway_payment_amount ,
                        "currency":data.paymentType.currency,
                    });
                    if(!result){
                        this.onRemovePayment(payment)
                    }
                }

                return true
            } else {
                toaster.warning($t("msg.Please enter payment amount"));
                return false
            }
        }
    }

    updatePaymentAmount() {
        const claim_amount = (this.sale.total_cash_coupon_claim||0);
        const payments = Enumerable.from(this.sale.payment);
        const total_payment = payments.sum("$.amount") + (this.sale.deposit || 0);
        const total_fee = payments.sum("$.fee_amount");
        this.sale.total_paid = total_payment;
        this.sale.total_fee = total_fee;
        this.sale.balance = (this.sale.grand_total || 0) - this.sale.total_paid -claim_amount;
        if (this.sale.balance < 0) {
            this.sale.balance = 0;
        }
        let change_amount =( total_payment + claim_amount) - this.sale.grand_total;
        this.sale.changed_amount = change_amount;
        this.sale.second_changed_amount = change_amount * this.sale.change_exchange_rate;
        this.sale.second_changed_amount = Number((this.sale.second_changed_amount + Number.EPSILON).toFixed(this.setting.pos_setting.second_currency_precision));
        this.sale.changed_amount = Number((this.sale.changed_amount + Number.EPSILON).toFixed(this.setting.pos_setting.main_currency_precision));
        if (this.sale.changed_amount <= 0) {
            this.sale.changed_amount = 0;
        }
        this.action
    }

    isOrdered(message = $t('msg.please save or submit your current order first', [$t('Submit') + " " + $t('or') + " " + $t('Save')])) {
        if ((this.sale.sale_products || []).length > 0) {
            const sp = Enumerable.from(this.sale.sale_products);
            if (sp.where("$.name==undefined").toArray().length > 0) {
                toaster.warning(message);
                return true
            }
        }
        return false
    }

    getShortCutKey(name) {
        let key = this.setting.shortcut_key.filter(item => item.name == name).map(item => item.key)
        return key[0];
    }

    //
    async onLoadDeleteSaleProducts(sale_id) {
        //frappe db
        const db = frappe.db();
        await db.getDocList('Sale Product Deleted', {
            fields: ['*'],
            filters: [['sale_doc', '=', sale_id]],
            limit: 100
        }).then((docs) => {
            this.deletedSaleProductsDisplay = [];
            if ((this.sale.sale_products || []).length > 0) {
                (this.sale.sale_products || []).forEach((sp) => {
                    const doc = docs.filter((d) => d.sale_product_id == sp.name);
                    if (doc.length > 0) {
                        sp.deleted_quantity = doc.reduce((a, i) => a + i.quantity, 0);
                        doc[0].removed = true;
                    }
                });
            }
            docs.forEach((d) => {
                if (d.removed == undefined) {
                    const _sp = JSON.parse(d.sale_product);
                    _sp.show_in_list = true;
                    this.deletedSaleProductsDisplay.push(_sp);
                }
            });
        }).catch((error) => { });
    }

    onCreateDeletedSaleProduct(data) {
        if ((this.sale.name || "") != "") {
            const db = frappe.db();
            data.deleted_quantity = data.quantity;
            this.updateSaleProduct(data)
            db.createDoc('Sale Product Deleted', {
                sale_product_id: data.name,
                product_name: `${data.product_name}${data.portion ? '.' + data.portion : ''}${data.modifiers ? ' ' + data.modifiers : ''}`,
                sale_doc: this.sale.name,
                sale_product: data,
                quantity: data.quantity,
                amount: data.total_revenue,
                deleted_by: data.created_by,
                order_time: data.order_time,
                kod_status: data.kod_status,
                printers: data.printers,
                deleted_note: data.deleted_item_note,
                portion: data.portion,
                modifiers: data.modifiers,
                combo_menu_data: data.combo_menu_data,
                combo_menu: data.combo_menu,
                product_name_kh: data.product_name_kh,
                note: data.note,
                order_by: data.order_by,
                is_free: data.is_free
            })
            .then((doc) => { })
            .catch((error) => {

            });
        }
    }

    onChangeMenuLanguage() {
        this.load_menu_lang = true;
        const mlang = localStorage.getItem('mLang');
        if (mlang != null) {
            if (mlang == "en") {
                localStorage.setItem('mLang', "km");
            } else {
                localStorage.setItem('mLang', "en");
            }
        } else {
            localStorage.setItem('mLang', "en");
        }
    }

    async onAssignEmployee(sp) {
        if (!this.isBillRequested()) {
            const res = await selectEmployeeDialog({ "data": sp })
            if (res) {
                sp.employees = JSON.stringify(res);
                sp.employee_names = "";
                res.forEach(e => {
                    sp.employee_names += `${e.employee_name}(${e.duration_title}), `;
                })
                if (sp.employee_names != "") {
                    sp.employee_names = sp.employee_names.substring(0, sp.employee_names.length - 2);
                }
            }
        }
    }


    getScreenNames(sale_products) {
        let printers = []
        sale_products?.forEach((r) => {
            printers = printers.concat(JSON.parse(r.printers).map(r => r.printer));
        });
        return [...new Set(printers)]
    }

    async onRequestCouponCode(code)  { 
        let data =  await call.get("epos_restaurant_2023.api.api.scan_coupon_number",{"code":code})
        return data["message"]
    }

    getUniqueKey(prefix) {
        const d = new Date()
        const pad = (n, l = 2) => String(n).padStart(l, '0')
        return (
            (prefix||"") +
            d.getFullYear() +
            pad(d.getMonth() + 1) +
            pad(d.getDate()) +
            pad(d.getHours()) +
            pad(d.getMinutes()) +
            pad(d.getSeconds()) +
            pad(d.getMilliseconds(), 2)
        )
    }
}

function has_changes(sale){
  let has_value_changes = 0
  let sale_products = (sale.sale_products || [])
  if(sale_products.length > 0){
      let news = sale_products.filter(r => r.is_newly_added == 1).length
      if (news>0){
          has_value_changes = 1
      }
  }
  return has_value_changes
}

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function Ping(setting) {
    await delay(500)
    let port =  setting?.pos_setting?.use_backend_port == 0 ? `:${window.location.port}` : (window.location.protocol == "https:" ? "" : `:${setting?.pos_setting?.backend_port}`)
    const url = `${window.location.protocol}//${window.location.hostname}${port}/api/method/epos_restaurant_2023.api.utils.ping`;
    const controller = new AbortController();
    const timer = setTimeout(() => {
        controller.abort();
    }, 3000)
    try {
        const start = performance.now();
        let status = 0
        const resp = await fetch(url, {signal: controller.signal});
        const end = performance.now();
        if(resp.status != 200){
            status = 0
        }
        else{
            const responseTime = end - start;
            if(responseTime>2000){
                status = 0
            }
            else{
                status = 1
            }
        }
        clearTimeout(timer);
        return status
    } catch (error) {
        clearTimeout(timer);
        return 0
    }
}