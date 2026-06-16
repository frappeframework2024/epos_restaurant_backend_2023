
<script setup>
import {inject} from '@/plugin'
import { onMounted } from 'vue';
    const gv = inject('$gv')
    const sale = inject('$sale')
    const frappe = inject('$frappe')
    const emit = defineEmits(['onHandle']);
    const call = frappe.call();
    const props = defineProps({
        saleProduct: Object
    }) 
    async function onCheckPromotion(){
        const resp = await call.post("epos_restaurant_2023.api.promotion.check_promotion",{
            check_time: 1,
            business_branch: gv.setting.business_branch || ''
        });
        if(resp.message){
            return resp.message
        }else{
            return false;
        } 
    }


    
    async function checkProductPromotion(){

        const resp = await call.post("epos_restaurant_2023.api.promotion.check_promotion_product",{
            product_name: props.saleProduct.product_code,
            promotions: gv.getPromotionByCustomerGroup(sale.sale.customer_group) || []
        });
        if(resp.message){
            return resp.message
        }else{
            return false;
        }  
    }


    onMounted(async()=>{        
        const check_promotion = await onCheckPromotion(); 
        if(check_promotion){
            gv.promotion = check_promotion;
            sale.promotion = check_promotion;          
            const check_product_promotion = await checkProductPromotion();       
            if(check_product_promotion){ 
                onUpdateSaleProduct(check_product_promotion)                
            }          
            props.saleProduct.is_render = false;     
        }
        else{
            gv.promotion = null,
            sale.promotion = null
        }
        props.saleProduct.is_render = false;
    })

    function onUpdateSaleProduct(promotion){
        const sp = props.saleProduct;
        if(promotion && sp.allow_discount){
            sp.discount_type = 'Percent'
            sp.discount = (promotion.percentage_discount || 0)
            sp.happy_hour_promotion = promotion.name
            sp.happy_hours_promotion_title = promotion.promotion_name
            sale.updateSaleProduct(sp);
            sale.updateSaleSummary();            
        }
    }
</script>