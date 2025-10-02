<template>
    <p class="font-bold mb-2">Recent Transaction</p>
    <div class="flex flex-column gap-2 transaction-list">
        <div class="transaction-item flex justify-content-between border-round-xl p-3 align-items-center">
            <div class="transaction-icon"><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none"
                    xmlns="http://www.w3.org/2000/svg">
                    <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                    <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                    <g id="SVGRepo_iconCarrier">
                        <path d="M18 18H9M18 18V9M18 18L11.5 11.5M6 6L8.5 8.5" stroke="#ff0000" stroke-width="1.5"
                            stroke-linecap="round" stroke-linejoin="round"></path>
                    </g>
                </svg></div>
            <div>
                <p><strong>តូបចិន</strong></p>
                <p><small>Coupon Code: 10500</small></p>
                <p><small>9/30/2025 6:20 PM</small></p>
            </div>
            <div class="text-right">
                <p class="text-2xl tran-price"><strong>1000 ៛</strong></p>
                <small>Bal: 10000 ៛</small>
            </div>
        </div>
    </div>
</template>
<script setup>
</script>