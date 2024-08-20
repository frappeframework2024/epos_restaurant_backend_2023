<template>
    <div class="grid gap-1" :class="mobile ? 'grid-cols-3 text-sm' : 'grid-cols-2'">
        <div class="border rounded-sm px-2 py-4 text-center cursor-pointer bg-orange-100 hover:bg-orange-300 flex justify-center items-center"
            v-for="(pt, index) in gv.setting?.payment_types" :key="index"
            @click="onPaymentTypeClick(pt)">
            <div>
                {{ pt.payment_method }} 
            </div>
        </div>
    </div>
</template>
<script setup>
import { inject , payToRoomDialog,createToaster,payToCityLedgerDialog,payDeskfolioDialog,i18n ,computed,keyboardDialog,ref} from '@/plugin';
import { useDisplay } from 'vuetify'
const {mobile} = useDisplay()
const gv = inject("$gv")
const sale = inject("$sale")
const frappe = inject("$frappe")
const { t: $t } = i18n.global;  
const toaster = createToaster({ position: "top-right" });
const numberFormat = inject("$numberFormat")
const db = frappe.db()

const format = ref("#,###,##0.00##")

const currency_setting = gv.setting?.currencies.find(r => r.name == gv.setting?.default_currency)
if (currency_setting) {
    format.value = currency_setting.pos_currency_format
}

async function onPaymentTypeClick(pt) { 

    let room = null;
    let folio_transaction_number = null
    let folio_transaction_type=null
    let folio = null
    let city_ledger_name = null
    let desk_folio = null
    let reservation_stay = null

    if(pt.payment_type_group=="Pay to Room" ){ 
        if(sale.paymentInputNumber<=0){
            toaster.warning($t("msg.Please enter payment amount"));
            return
        }

        const result = await payToRoomDialog({
            data : pt
        });

        //
        if(result == false){
            return
        }
        room = result.room;
        if (pt.use_room_offline == 0){
            
            folio = result.folio;
            folio_transaction_number =result.folio;
            folio_transaction_type="Reservation Folio";
            reservation_stay=result.reservation_stay;        
            sale.sale.customer = result.guest;
            sale.sale.customer_name = result.guest_name;
        }
        
    }
    else if(pt.payment_type_group == "City Ledger"){
        const result = await payToCityLedgerDialog({
            data : pt
        });
        //if close
        if(result == false){
            return
        }
         
        folio_transaction_number =result.folio_transaction_number;
        folio_transaction_type="City Ledger";
        city_ledger_name = result.city_ledger_name;
    }
    else if(pt.payment_type_group == "Desk Folio"){
        const result = await payDeskfolioDialog({
            data : pt
        });
        //if close
        if(result == false){
            return
        }
         
        folio_transaction_number =result.folio_transaction_number;
        folio_transaction_type="Desk Folio"
        desk_folio = result.desk_folio
    }else if(pt.payment_type_group == "Crypto"){   
        
        let crypto_able_amount = sale.sale.crypto_able_amount * ((gv.setting.pos_setting.percentage_of_bill_amount_to_claim_crypto || 0)/100)
        let total_crypto_able_amount =crypto_able_amount;
        let total_crypto_settle_amount = 0;

        if(total_crypto_able_amount <=0){
            toaster.warning(`${$t("Bill not accept with payment type")}`);
            return
        }
        

        if (sale.sale.payment != undefined ){
            let sum = sale.sale.payment.filter((r)=>r.payment_type_group =="Crypto" ).reduce((value, item) => value + item.amount, 0);
            crypto_able_amount -= sum;
            total_crypto_settle_amount = parseFloat(sum) 
        }
        total_crypto_settle_amount += parseFloat( parseFloat(sale.paymentInputNumber )/pt.exchange_rate);
        
        const res = await db.getDoc("Customer", sale.sale.customer);           
        if(res.total_crypto_balance <=0 || res.total_crypto_balance < total_crypto_settle_amount){
            toaster.warning(`${res.customer_code_name} ${$t(" don't hvae enough saving crypto amount")}`);
            return;
        }else if(total_crypto_settle_amount > total_crypto_able_amount){
            let amount =  numberFormat(format.value,   isNaN(crypto_able_amount)?0:crypto_able_amount) 
            toaster.warning(`${$t("Payment accept with amount")} ${amount}`);
            return;
        }        

    }

    //check if payment exist manual fee
    let fee_amount = 0;
    if(pt.is_manual_fee==1){
        const fee = await keyboardDialog({ title:$t("Enter Fee Amount"), type: 'number', value: 0 });
        if(!fee){
            return;
        }      
        fee_amount = fee;
    }

    if(mobile.value){
        sale.is_payment_first_load = false;
    }  

    if(pt.allow_change==0 &&  parseFloat(sale.paymentInputNumber) > parseFloat(balance.value * pt.exchange_rate)){
        sale.paymentInputNumber = balance.value *  pt.exchange_rate;        
    }
    else  if(sale.is_payment_first_load){       
        sale.paymentInputNumber = sale.paymentInputNumber * pt.exchange_rate;       
    }  
    const payment_obj={paymentType: pt, amount:sale.paymentInputNumber,fee_amount:fee_amount,room:room, folio : folio, folio_transaction_type:folio_transaction_type,folio_transaction_number:folio_transaction_number,city_ledger_name:city_ledger_name,reservation_stay:reservation_stay}
     
    sale.onAddPayment(payment_obj);
}

const balance = computed(()=>{
    if(sale.sale?.balance>0){ 
        return Number(sale.sale.balance.toFixed(gv.setting.pos_setting.main_currency_precision));
    }else {
        return 0;
    }
})

 


</script>