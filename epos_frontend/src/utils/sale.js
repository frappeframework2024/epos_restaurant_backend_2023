import { computed, addModifierDialog, SelectDateTime, i18n, inject, keypadWithNoteDialog, SelectGoogleImageDialog, SaleProductComboMenuGroupModal, createToaster, EmptyStockProductDialog } from '@/plugin'

import ComEditSaleProduct from '@/views/sale/components/ComEditSaleProduct.vue'
import { FrappeApp } from 'frappe-js-sdk';
const frappe = new FrappeApp();
const call = frappe.call()

export async function onSelectProduct(product_data,sale,product,dialog,unit = ""){
   
    if (sale.setting.pos_menus.length>0 || sale.setting.use_menu_retail == 1){
        // sale is sale from inject 
        // product is product from inject 
        let p = JSON.parse(JSON.stringify( product_data))
        if (!sale.isBillRequested()) {
            product.is_open_price = p.is_open_price

            if (p.is_empty_stock_warning == 1) {
                    //message dialog confirmation   
                let emptyConfirm = await EmptyStockProductDialog();
                if (!emptyConfirm) {
                    return
                }
            }  
            
            if(p.has_variants==1){
                
                p  = await selectVariant(p,dialog);
                
                if(!p){
                    return
                }            
            }
        
            if (!p.is_timer_product) {
                if (p.is_open_product == 1) {

                    let productPrices = await keypadWithNoteDialog({
                        data: {
                            title: `${p.name_en}`,
                            label_input: 'Enter Price',
                            note: "Open Menu Note",
                            category_note_name: "Open Menu Note",
                            number: 0,
                            product_code: p.name
                        }
                    });

                    if (productPrices) {
                        p.name_en = productPrices.note;
                        p.name_kh = productPrices.note;
                        p.price = productPrices.number;
                        p.modifiers = '';
                        sale.addSaleProduct(p);
                        return
                    } else {
                        return
                    }

                }
                else if (p.is_combo_menu) {
                    await onComboMenu(p)
                    p.modifiers = "";
                    p.portion = "";
                    p.modifiers_data = "[]";
                }
                else {
                    const portions = JSON.parse(p.prices)?.filter(r => (r.branch == sale.sale.business_branch || r.branch == '') && r.price_rule == sale.sale.price_rule);
                    const check_modifiers = product.onCheckModifier(JSON.parse(p.modifiers || "[]"));

                    
                    if (portions?.length == 1) {
                        p.price = portions[0].price
                        p.unit = portions[0].unit
                        p.discount = portions[0].default_discount || 0


                    }
                    
                    if (check_modifiers || portions?.length > 1 || p.is_open_price) {
                        const pro_data = product_data

                        if (p.is_open_price && portions.length == 0) {
                            pro_data.prices = JSON.stringify([{ "price": p.price, "branch": "", "price_rule": sale.sale.price_rule, "portion": "Normal", "unit": p.unit, "default_discount": 0 }])
                        }
                    product.setSelectedProduct(pro_data,sale.sale.price_rule);
                    let productPrices = null
                    let base_unit = ""
                    if(sale.setting.use_menu_retail == 1){
                        await get_base_unit(p.name).then((res)=>{base_unit = res})
                        if(unit == "" || unit == null || unit == undefined){
                            unit = base_unit
                        }
                        if(unit != base_unit){
                            const portion = JSON.parse(p.prices)?.filter(r => (r.branch == sale.sale.business_branch || r.branch == '') && r.price_rule == sale.sale.price_rule && decodeURIComponent(r.unit) == unit);
                            const modifiers = JSON.parse((p.modifiers || ""))?.filter(r => (r.branch == sale.sale.business_branch || r.branch == ''));
                            productPrices = { "portion":(portion[0] || []),"modifiers":(modifiers[0] || [])}
                        }
                        else if(unit == base_unit && sale.setting.base_unit_popup == 1){
                            productPrices = await addModifierDialog();
                        }
                        else{
                            const portion = JSON.parse(p.prices)?.filter(r => (r.branch == sale.sale.business_branch || r.branch == '') && r.price_rule == sale.sale.price_rule && decodeURIComponent(r.unit) == unit);
                            const modifiers = JSON.parse((p.modifiers || ""))?.filter(r => (r.branch == sale.sale.business_branch || r.branch == ''));
                            productPrices = { "portion":(portion[0] || []),"modifiers":(modifiers[0] || [])}
                        }
                    }
                    else{
                        productPrices = await addModifierDialog();
                    }
                    if (productPrices) {
                    
                        if (productPrices.portion != undefined) {
                            p.price = productPrices.portion.price;
                            p.portion = productPrices.portion.portion;
                            p.unit = productPrices.portion.unit
                            p.discount = productPrices.portion.default_discount || 0
                        }
                        p.modifiers = (productPrices.modifiers.modifiers || "");
                        p.modifiers_data = (productPrices.modifiers.modifiers_data || "[]");
                        p.modifiers_price = (productPrices.modifiers.price || 0)

                    } else {
                        return;
                    }
                    } else {
                        p.modifiers = "";
                        p.modifiers_data = "[]";
                        p.portion = "";
                    }
                }

            } else {
                let selectdatetime = await SelectDateTime();
                if (selectdatetime) {
                    if (selectdatetime != 'Set Later') {
                        p.time_in = selectdatetime;
                    } else {
                        p.time_in = undefined;
                    }

                } else {
                    return
                }
            }
            
            sale.addSaleProduct(p);
        }
    } else {
        // for retail
        AddProductTotalSaleOrderForRetailPOS(product_data,sale,product,dialog)

    }


}

async function get_base_unit(product_code){
    return new Promise((resolve) => {call.get("epos_restaurant_2023.api.product.get_product_detail_information", {
            product_code: product_code
        }).then((res) => {
            resolve(res.message.product.unit)
        })
    })
}

async function AddProductTotalSaleOrderForRetailPOS(product_data,sale,product,dialog){

    if (product_data.has_variants){
        product_data = await selectVariant(product_data.name,dialog)
       
    }
    sale.addSaleProduct(product_data);
}


function selectVariant(product_code,dialog){
    return new Promise((resolve) => {
        dialog.open(ComEditSaleProduct, {
            data:{product_code:product_code},
            props: {
                header: 'Product Option',
                style: {
                    width: '900px',
                    background: 'white',
                    color: 'black'
                },
                breakpoints:{ 
                    '960px': '90vw',
                    '640px': '90vw'
                },
                modal: true
            },
            onClose: (options) => {
                const data = options.data;
                
                if (data != undefined) {
                    resolve(data.product)
                }else {
                    resolve(false)
                }
            }
        });
      
    })
}

async function onComboMenu(p) {
    if (p.is_combo_menu && p.use_combo_group) {
        product.setSelectedComboMenu(p)
        const result = await SaleProductComboMenuGroupModal();
        if (result) {

            if (result.combo_groups.length > 0) {
                p.combo_menu = getSeperateNameComboGroup(p, result.combo_groups)

                p.combo_group_data = JSON.stringify(result.combo_groups)

            } else {
                p.combo_menu = ''
                p.combo_group_data = "[]"
            }
        }
    } else {
        if (p.is_combo_menu && p.combo_menu_data) {
            const combo_menu_data = JSON.parse(p.combo_menu_data)
            p.combo_menu = getSeperateName(combo_menu_data)

        }
    }
}


function getSeperateNameComboGroup(p, list) {
    let combo_groups = JSON.parse(p.combo_group_data)
    let combo_menu_items = []
    combo_groups.forEach((x) => {
        combo_menu_items.push('***' + x.pos_title + '***')
        let combo_menus = []
        list.forEach(r => {

            if (r.group == x.combo_group) {
                combo_menus.push(r.product_name + ' x' + r.quantity)
            }
        })

        combo_menu_items.push(combo_menus.join(", "))
    })
    return combo_menu_items.join("|")
}

function getSeperateName(list) {
    let combo_menus = []
    list.forEach(r => {
        combo_menus.push(r.product_name + ' x' + r.quantity)
    })
    return combo_menus.join(", ")
}