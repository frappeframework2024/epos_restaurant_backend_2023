import { ref } from "vue"

const homeData = ref({
    coupon_info:{
        coupon_number:"",
        issue_date:"",
        expired_date:"",
        coupon_amount:0,
        use_amount:0,
        balance:0,
    }
})

function getHomeData(){
    alert("get home data")
}
export function useHome() {

    

    return {
        homeData,
        getHomeData
    }

}