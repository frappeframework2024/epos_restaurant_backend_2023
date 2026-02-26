import { ref } from "vue"
import { getApi,getDocList } from "@/plugin";
import dayjs from "dayjs";

const homeData = ref({
    coupon_info:{
        coupon:"",
        coupon_number:"0000",
        issue_date:dayjs(),
        expired_date:dayjs(),
        coupon_amount:0,
        use_amount:0,
        balance:0,
    },
    
})

const couponTransactionData = ref([])

async function getHomeData(){
    // alert("get home data")
    await getApi("management_coupon.get_home_page_data").then(result=>{
        homeData.value = result.message
        console.log(homeData.value)
    }).catch(err=>{
        
    })
}

async function getCouponTransaction(){
    
    await getApi("management_coupon.get_coupon_use_transaction",{
        coupon_code:homeData.value.coupon_info.coupon 
    }).then(x=>{
        couponTransactionData.value = x.message
    }).catch(err=>{

    })

}


export function useHome() {
    return {
        homeData,
        couponTransactionData,
        getHomeData,     
        getCouponTransaction
    }
}