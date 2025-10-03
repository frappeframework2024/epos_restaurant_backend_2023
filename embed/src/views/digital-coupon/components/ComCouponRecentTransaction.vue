<template>
    <h1 class="font-bold mb-2">Recent transaction</h1>
    <div class="flex flex-column gap-2 transaction-list">
        <template v-for="(item, index) in data">
            <div class="transaction-item flex justify-content-between border-round-xl p-3 align-items-center">
                <div class="flex gap-3 align-items-center">
                    <div class="transaction-icon">
                        <svg width="30px" height="30px" viewBox="0 0 24 24" fill="none"
                            xmlns="http://www.w3.org/2000/svg">
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                            <g id="SVGRepo_iconCarrier">
                                <path d="M18 18H9M18 18V9M18 18L11.5 11.5M6 6L8.5 8.5" stroke="#ff0000" stroke-width="1.5"
                                    stroke-linecap="round" stroke-linejoin="round"></path>
                            </g>
                        </svg>
                    </div>
                    <div>
                        <p><strong>{{item.store_name}}</strong></p>
                        <p><small>Coupon Code: {{item.coupon_code}}</small></p>
                        <p><small>{{item.issue_date}}</small></p>
                    </div>
                </div>
                
                <div class="text-right">
                    <p class="text-2xl tran-price"><strong>{{item.remain_balance}}</strong></p>
                    <small>Bal: {{item.remain_balance}}</small>
                </div>
            </div>
        </template>
    </div>
</template>
<script setup>
import {ref} from '@/plugin'

const data = ref({})

data.value = [
    {
        "transaction_id": "CUP001",
        "store_name": "តូបចិន",
        "coupon_code": "10500",
        "issue_date": "9/30/2025 6:20 PM",
        "remain_balance": "10000 ៛",
        "balance": "6000 ៛"
    },
    {
        "transaction_id": "CUP002",
        "store_name": "តូបគៀវ",
        "coupon_code": "20890",
        "issue_date": "10/01/2025 10:15 AM",
        "remain_balance": "12000 ៛",
        "balance": "8000 ៛"
    },
    {
        "transaction_id": "CUP003",
        "store_name": "Western",
        "coupon_code": "30955",
        "issue_date": "10/01/2025 3:40 PM",
        "remain_balance": "15000 ៛",
        "balance": "5000 ៛"
    },
    {
        "transaction_id": "CUP004",
        "store_name": "ផ្សារចាស់",
        "coupon_code": "41200",
        "issue_date": "10/02/2025 9:00 AM",
        "remain_balance": "7000 ៛",
        "balance": "4000 ៛"
    },
    {
        "transaction_id": "CUP005",
        "store_name": "Bar",
        "coupon_code": "57820",
        "issue_date": "10/02/2025 7:25 PM",
        "remain_balance": "20000 ៛",
        "balance": "15000 ៛"
    },
    {
        "transaction_id": "CUP006",
        "store_name": "តូបខ្មែរ",
        "coupon_code": "68910",
        "issue_date": "10/03/2025 8:45 AM",
        "remain_balance": "18000 ៛",
        "balance": "9000 ៛"
    },
    {
        "transaction_id": "CUP007",
        "store_name": "តូបខ្មែរ",
        "coupon_code": "75500",
        "issue_date": "10/03/2025 2:10 PM",
        "remain_balance": "25000 ៛",
        "balance": "12000 ៛"
    },
    {
        "transaction_id": "CUP008",
        "store_name": "ផ្សារថ្មី",
        "coupon_code": "82450",
        "issue_date": "10/04/2025 6:55 PM",
        "remain_balance": "6000 ៛",
        "balance": "3000 ៛"
    },
    {
        "transaction_id": "CUP009",
        "store_name": "តូបខ្មែរ ១",
        "coupon_code": "90210",
        "issue_date": "10/05/2025 11:30 AM",
        "remain_balance": "14000 ៛",
        "balance": "7000 ៛"
    },
    {
        "transaction_id": "CUP010",
        "store_name": "តូបចិន ១",
        "coupon_code": "99999",
        "issue_date": "10/05/2025 8:15 PM",
        "remain_balance": "3000 ៛",
        "balance": "2000 ៛"
    }
]

</script>