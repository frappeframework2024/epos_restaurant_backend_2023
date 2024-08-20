import Enumerable from 'linq'
import { keyboardDialog, createResource } from "@/plugin"
import { createToaster } from "@meforma/vue-toaster";

const toaster = createToaster({ position: "top-right" });
import { FrappeApp } from 'frappe-js-sdk';
const frappe = new FrappeApp();
const db = frappe.db()
const call = frappe.call()

export default class Product {
    constructor() {
        this.setting = null;
        this.parentMenu = "";
        this.searchProductKeyword = "";
        this.searchProductKeywordStore = "";
        this.is_open_price = 0;
        this.selectedProduct = {};
        this.prices = [];
        this.modifiers = [];
        this.keyword = "";
        this.combo_group_temp = [];
        this.currentRootPOSMenu = null
        this.productCategory = "";
        this.menuProducts = []
        this.isLoadingProduct = false
        this.isGetAllProduct = false
        this.isSearchProduct = false
   
        this.canBack = false

        this.selectedProductCategory = "All Product Category"
        this.posSearchProductPager = {
            limit:10,
            page:1
        }

        this.posMenuResource = createResource({
            url: 'epos_restaurant_2023.api.product.get_product_by_menu',
            params: {
                root_menu: this.setting?.default_pos_menu
            },
            auto: true,
            cache: ["pos_menu"]
        })
    }

    onClearKeyword() {
        this.parentMenu = "";
        this.searchProductKeyword = "";
        this.searchProductKeywordStore = "";
        this.selectedProduct = {};
    }
    loadPOSMenu() {
        this.posMenuResource.update({
            params: {
                root_menu: this.currentRootPOSMenu ? this.currentRootPOSMenu : this.setting?.default_pos_menu
            }
        });
        this.posMenuResource.reload();
    }

    getPOSMenu() {
        if (this.getString(this.searchProductKeyword) == "") {
            if (this.parentMenu) {
                
                return this.posMenuResource.data?.filter(r => r.parent == this.parentMenu)
            }
            else {
                
                let defaultMenu = this.currentRootPOSMenu ? this.currentRootPOSMenu : this.setting?.default_pos_menu;
                if (localStorage.getItem('default_menu')) {
                    defaultMenu = localStorage.getItem('default_menu')
                }
                return   Enumerable.from(this.posMenuResource.data?.filter(r => r.parent == defaultMenu)).orderBy("$.type_index").orderBy("$.sort_order").thenBy("$.name_en");

            }
        } else {
            return this.posMenuResource.data?.filter((r) => {
                return String(r.name_en + ' ' + r.name_kh + ' ' + r.name).toLocaleLowerCase().includes(this.searchProductKeyword.toLocaleLowerCase()) && r.type == "product"
            }).sort((a, b)=>a.sort_order-b.sort_order)
        }
    }

    getProductMenuByProductCategory(product_category) {
        
        if((typeof product_category ) =="object"){
            product_category = product_category.name
        }
        if(!product_category){
            product_category = this.selectedProductCategory ?  this.selectedProductCategory: 'All Product Categories'
        }else {
            this.selectedProductCategory = product_category
        }
        
        this.posSearchProductPager.page = 0
        this.isGetAllProduct = false
        this.isSearchProduct = false
        window.location.hash = product_category;
        this.posSearchProductPager.limit =this.getItemLimit() || 20
        this.getProductFromDB({category:product_category,include_product_category:1})
  
    }

    getProductFromDB({keyword="",category='',include_product_category=0}={}){
       
        
        this.isLoadingProduct = true
 
        if(!this.isGetAllProduct){
           
            this.posSearchProductPager.page = this.posSearchProductPager.page + 1
            call.get("epos_restaurant_2023.api.product.get_products", {
                category:category==''? this.selectedProductCategory:category,
                limit:this.posSearchProductPager.limit,
                page:this.posSearchProductPager.page,
                keyword:keyword,
                include_product_category:include_product_category
            }).then((res) => {
               
               
               
                
                this.isLoadingProduct = false
                if(include_product_category==1){
                    this.menuProducts = res.message.categories
                }
                this.menuProducts = this.menuProducts.concat(res.message.products)
   
                this.isGetAllProduct = res.message.products.length < this.posSearchProductPager.limit
            }).catch((err) => {
                this.isLoadingProduct = false
            })
        }else {
            this.isLoadingProduct = false
        }
       
    }

    getItemLimit(){
        const setting = JSON.parse( localStorage.getItem("item_menu_setting"))
        
        const scrollContainer = document.querySelector("#wrap_menu")
        let height  = 768
        if (scrollContainer){
            height = scrollContainer.offsetHeight; 
        }
        

        return  Math.ceil( (setting?.show_column_item || 1) * (height/ (setting?.item_height || 140))) 
    }

    getProductFromDbByKeyword(keyword) {
        if(keyword.length<3){
            return
        }

        this.isGetAllProduct = false
        this.isSearchProduct = true
        this.menuProducts = []
        this.posSearchProductPager.page = 0 
        
        this.getProductFromDB({limit:20,keyword:keyword, category:"All Product Categories"})
    }



    setSelectedProduct(p,price_rule='') {
        
        this.selectedProduct = p;
        
        this.prices = [];
        this.modifiers = [];
        this.combo_group_temp = [];
        let prices = []
        if (p.prices) {
            prices = JSON.parse(p.prices)
        }
       
        prices.filter(r => r.branch == this.setting?.business_branch || r.branch == "").forEach((p) => {
            p.selected = false;
            this.prices.push(p)
        });
        if (this.prices.length > 0) {
            this.prices.forEach((p)=>{
                if (p.price_rule == price_rule){
                    p.selected = true;
                }
            })
        }

        let modifiers = JSON.parse(p.modifiers);

        modifiers.forEach((r) => {
            r.selected = false
        });
        this.modifiers = modifiers;

        if (p.is_combo_menu && p.use_combo_group) {

            let combo_groups = JSON.parse(p.combo_group_data)
            combo_groups.forEach((r) => {
                r.selected = false
                r.menus.forEach((m) => {
                    m.group = r.combo_group
                    m.group_title = r.pos_title
                })
            })
            this.combo_group_temp = combo_groups
        }

    }
    setSelectedProductByMenuID(id) {
        let p = Enumerable.from(this.posMenuResource.data ?? []).where(`$.menu_product_name=='${id}'`).firstOrDefault();      
   
        if (p) {
            this.setSelectedProduct(p);
            return true;
        }
        else {
            p = Enumerable.from(this.posMenuResource.data ?? []).where(`$.name=='${id}'`).firstOrDefault();
            if(p){
                this.setSelectedProduct(p);
                return true;
            }
            return false;
        }

    }
    setModifierSelection(sp) {
        
        Enumerable.from(this.prices).where("$.selected==true").forEach("$.selected = false");
        const portion = Enumerable.from(this.prices).where(`$.portion=='${sp.portion}'`).firstOrDefault();
        if (portion != undefined) {
            portion.selected = true;
        }
        const selectedModifiers = JSON.parse(sp.modifiers_data)
        const modfierItems = Enumerable.from(this.modifiers).selectMany("$.items");
        if (selectedModifiers != undefined) {
            selectedModifiers.forEach((r) => {
                const modifierItem = modfierItems.where(`$.name=='${r.name}'`).firstOrDefault();
                if (modifierItem != undefined) {
                    modifierItem.selected = true;
                }
            })
        }
    }

    getModifierItem(category) {
        if (this.keyword == "") {
            return category.items.filter((r) => {
                return (r.branch == this.setting?.business_branch || r.branch == '')
            });
        } else {

            return category.items.filter((r) => {
                return (r.branch == this.setting?.business_branch || r.branch == '') && String(r.modifier).toLocaleLowerCase().includes(this.keyword.toLocaleLowerCase());
            });
        }
    }

    onCheckModifier(modifiers) {
        if (modifiers) {
            const data = modifiers.filter((r) => {
                return r.items.some(x => x.branch == this.setting?.business_branch || x.branch == '')
            })
            return data.length > 0;
        }
        return false
    }

    onSelectPortion(p) {

        Enumerable.from(this.prices).where("$.selected==true").forEach("$.selected=false");
        p.selected = true;
    }
    onSelectModifier(category, modifier) {
        if (category.is_multiple == 0) {
            Enumerable.from(category.items).where(`$.selected==true`).forEach("$.selected=false");
        }
        modifier.selected = !modifier.selected;

    }

    getSelectedPortion() {
        if (this.prices.length == 1) {
            return this.prices[0];
        }
        let selected = Enumerable.from(this.prices).where("$.selected==true").firstOrDefault();
        if (selected == undefined) {
            selected = this.prices[0]
        }
        return selected;
    }
    getSelectedModifierList() {
        const data = (Enumerable.from(this.modifiers).selectMany("$.items").where("$.selected==true").orderBy("$.modifier")).toArray();
        return data;
    }

    

    getSelectedModifier() {

        const selected = (Enumerable.from(this.modifiers).selectMany("$.items").where("$.selected==true").orderBy("$.modifier"));
        let modifiers = selected.select("r=>(r.prefix || '') + ' ' + r.modifier").toJoinedString(", ");
        if (modifiers == "[]" || modifiers == undefined) {
            modifiers = "";
        }

        return {
            modifiers_data: selected.select("x => {name:x['name'], modifier: x['modifier'], price: x['price'] }").toJSONString(),
            modifiers: modifiers,
            price: selected.sum("$.price")
        }
    }
    validateModifier() {
        return new Promise((resolve) => {
            this.modifiers.forEach((c) => {
                const countItem = c.items.filter(r => r.branch == this.setting.business_branch || r.branch == '').length
                if (countItem > 0) {
                    if (c.is_required == 1) {
                        if (c.items.filter(r => r.selected == true).length == 0) {
                            toaster.warning("Please select a modifier of " + c.category);
                            resolve(false)
                        }
                    }
                }
            })
            resolve(true)
        })
    }

    setSelectedComboMenu(p) {
        this.selectedProduct = p;
        let combo_group_data = JSON.parse(p.combo_group_data);
        combo_group_data.forEach((r) => {
            r.menus.forEach((x) => {
                x.selected = r.menus.length === r.item_selection,
                    x.group = r.combo_group,
                    x.group_title = r.pos_title
            })
        });
        this.combo_group_temp = combo_group_data;
    }
    getSelectedComboGroup() {
        let selected = Enumerable.from(this.combo_group_temp).selectMany("$.menus").where("$.selected==true").toArray();
        if (selected == undefined) {
            selected = []
        }

        return selected;
    }
    validateComboGroup() {
        return new Promise((resolve) => {
            this.combo_group_temp.forEach((c) => {

                const countSelected = c.menus.filter(r => r.selected == true).length
                if (countSelected === 0) {
                    toaster.warning(`Please select products of ${c.pos_title}`)
                    resolve(false)
                }
                else if (countSelected != c.item_selection) {
                    toaster.warning(`Must select all ${c.item_selection} of ${c.pos_title}`);
                    resolve(false)
                }
            })
            resolve(true)
        })
    }
    getComboMenu(group) {
        if (this.keyword == "") {
            return group.menus
        } else {

            return group.menus.filter((r) => {
                return String(r.product_name).toLocaleLowerCase().includes(this.keyword.toLocaleLowerCase());
            });
        }
    }

    onSelectComboMenu(item, group) {
        if (group.item_selection != group.menus.length) {
            if (group.item_selection == 1) {
                const selectedFilter = Enumerable.from(this.combo_group_temp).where(`$.combo_group == '${group.combo_group}'`)
                selectedFilter.selectMany("$.menus").where('$.selected==true').forEach("$.selected=false");
            }
            item.group = group.combo_group
            item.selected = !item.selected;
        }
    }

    setComboGroupSelection(sp) {
        const selectedComboGroups = JSON.parse(sp.combo_menu_data)
        const comboGroupItems = Enumerable.from(this.combo_group_temp).selectMany("$.menus");
        if (selectedComboGroups != undefined) {
            selectedComboGroups.forEach((r) => {
                const item = comboGroupItems.where(`$.menu_name=='${r.menu_name}'`).firstOrDefault();
                if (item != undefined) {
                    item.selected = true;
                }
            })
        }
    }

    getString(val) {
        val = (val = val == null ? "" : val)
        return val;
    }
}