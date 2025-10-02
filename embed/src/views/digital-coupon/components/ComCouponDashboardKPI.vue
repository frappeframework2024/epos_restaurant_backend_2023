<template>
        <div>
            <p>Available Balance</p>
            <h1 class="font-bold">$2500.00</h1>
        </div>
        <div>
            <p class="font-bold">Used: $1250</p>
            <ProgressBar :value="50"></ProgressBar>
        </div>
        <div class="info-list">
            <div class="grid">
                <div class="col-6">
                    <div class="flex gap-2">
                        <div><svg width="20px" height="20px" viewBox="0 0 24 24" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                <g id="SVGRepo_iconCarrier">
                                    <path d="M13 21L17 3" stroke="#fff" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round"></path>
                                    <path d="M7 21L11 3" stroke="#fff" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round"></path>
                                    <path d="M20 9L4 9" stroke="#fff" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round"></path>
                                    <path d="M4 15L20 15" stroke="#fff" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round"></path>
                                </g>
                            </svg></div>
                        <div>
                            <p>Coupon</p>
                            <p class="list-value">10500</p>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="flex gap-2">
                        <div><svg width="20px" height="20px" viewBox="0 0 24 24" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                <g id="SVGRepo_iconCarrier">
                                    <path
                                        d="M3 9H21M7 3V5M17 3V5M6 12H8M11 12H13M16 12H18M6 15H8M11 15H13M16 15H18M6 18H8M11 18H13M16 18H18M6.2 21H17.8C18.9201 21 19.4802 21 19.908 20.782C20.2843 20.5903 20.5903 20.2843 20.782 19.908C21 19.4802 21 18.9201 21 17.8V8.2C21 7.07989 21 6.51984 20.782 6.09202C20.5903 5.71569 20.2843 5.40973 19.908 5.21799C19.4802 5 18.9201 5 17.8 5H6.2C5.0799 5 4.51984 5 4.09202 5.21799C3.71569 5.40973 3.40973 5.71569 3.21799 6.09202C3 6.51984 3 7.07989 3 8.2V17.8C3 18.9201 3 19.4802 3.21799 19.908C3.40973 20.2843 3.71569 20.5903 4.09202 20.782C4.51984 21 5.07989 21 6.2 21Z"
                                        stroke="#ffffff" stroke-width="2" stroke-linecap="round"></path>
                                </g>
                            </svg></div>
                        <div>
                            <p>Issue Date</p>
                            <p class="list-value">1/1/2025</p>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="flex gap-2">
                        <div><svg width="20px" height="20px" viewBox="0 0 24 24" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                <g id="SVGRepo_iconCarrier">
                                    <path
                                        d="M3 9H21M7 3V5M17 3V5M6 12H8M11 12H13M16 12H18M6 15H8M11 15H13M16 15H18M6 18H8M11 18H13M16 18H18M6.2 21H17.8C18.9201 21 19.4802 21 19.908 20.782C20.2843 20.5903 20.5903 20.2843 20.782 19.908C21 19.4802 21 18.9201 21 17.8V8.2C21 7.07989 21 6.51984 20.782 6.09202C20.5903 5.71569 20.2843 5.40973 19.908 5.21799C19.4802 5 18.9201 5 17.8 5H6.2C5.0799 5 4.51984 5 4.09202 5.21799C3.71569 5.40973 3.40973 5.71569 3.21799 6.09202C3 6.51984 3 7.07989 3 8.2V17.8C3 18.9201 3 19.4802 3.21799 19.908C3.40973 20.2843 3.71569 20.5903 4.09202 20.782C4.51984 21 5.07989 21 6.2 21Z"
                                        stroke="#ffffff" stroke-width="2" stroke-linecap="round"></path>
                                </g>
                            </svg></div>
                        <div>
                            <p>Expire Date</p>
                            <p class="list-value">1/1/2025</p>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="flex gap-2">
                        <div><svg fill="#ffffff" width="20px" height="20px" viewBox="0 0 32 32" version="1.1"
                                xmlns="http://www.w3.org/2000/svg" stroke="#ffffff">
                                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                <g id="SVGRepo_iconCarrier">
                                    <path
                                        d="M29.5 7c-1.381 0-2.5 1.12-2.5 2.5 0 0.284 0.058 0.551 0.144 0.805l-6.094 5.247c-0.427-0.341-0.961-0.553-1.55-0.553-0.68 0-1.294 0.273-1.744 0.713l-4.774-2.39c-0.093-1.296-1.162-2.323-2.482-2.323-1.38 0-2.5 1.12-2.5 2.5 0 0.378 0.090 0.732 0.24 1.053l-4.867 5.612c-0.273-0.102-0.564-0.166-0.873-0.166-1.381 0-2.5 1.119-2.5 2.5s1.119 2.5 2.5 2.5c1.381 0 2.5-1.119 2.5-2.5 0-0.332-0.068-0.649-0.186-0.939l4.946-5.685c0.236 0.073 0.48 0.124 0.74 0.124 0.727 0 1.377-0.316 1.834-0.813l4.669 2.341c0.017 1.367 1.127 2.471 2.497 2.471 1.381 0 2.5-1.119 2.5-2.5 0-0.044-0.011-0.086-0.013-0.13l6.503-5.587c0.309 0.137 0.649 0.216 1.010 0.216 1.381 0 2.5-1.119 2.5-2.5s-1.119-2.5-2.5-2.5z">
                                    </path>
                                </g>
                            </svg></div>
                        <div>
                            <p>Usage</p>
                            <p class="list-value">47%</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
</template>
<script setup>
import ProgressBar from 'primevue/progressbar';
</script>