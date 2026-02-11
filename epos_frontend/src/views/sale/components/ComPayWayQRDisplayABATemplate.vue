<template lang="">   
  <div class="card">
      <div class="top"> 
          <!-- small QR icon (top-right) -->
          <div class="mini-qr" aria-hidden="true" style="position: absolute; top:-10px; left:-10px ">
              <svg  xmlns="http://www.w3.org/2000/svg"  viewBox="0 0 24 24"  width="24"  height="24"  fill="none">
                <path
                  d="M3 3h7v7H3V3Zm2 2v3h3V5H5Zm9-2h7v7h-7V3Zm2 2v3h3V5h-3ZM3 14h7v7H3v-7Zm2 2v3h3v-3H5Zm11 0h2v2h-2v-2Zm-2-2h2v2h-2v-2Zm6 0h1v3h-1v-3Zm-2 3h3v1h-3v-1Zm-4 2h2v2h-2v-2Zm3 0h4v2h-1v-1h-3v-1Z"
                  fill="#ffffff"
                />
              </svg>
          </div> 
          <v-btn v-if="showClose" icon @click="onClose()" style="position: absolute; top: -10px; right: -10px;">
              <v-icon>mdi-close</v-icon>
          </v-btn> 
      </div>  
      <div class="screen"> 
        <div class="page-sub-card"> 
            <div class="sub-card">
              <img  v-if="qrData.qr_image" :src="qrData.qr_image" alt="QR Code"/>
            </div>
        </div> 
      </div>
  </div>
</template>
<script setup>
    import { i18n } from '@/plugin'; 
     const { t: $t } = i18n.global; 
    const emit = defineEmits(["onClose"])
    const props = defineProps({
        qrData:Object,
        showClose:false
    });

    function onClose() { 
        emit('onClose',false);
    }


</script>
<style scoped>
    .card{
      width:100%;
      height:100% !important;
      padding:18px 18px 16px;
      color:#ffffff;
      border-radius:18px;
      /* background: linear-gradient(135deg, #2d69af 0%, #3c5fd1 55%, #b8c2f6 140%); */
      background: #e8e9ec;
      /* background: linear-gradient(135deg, #10dfff 0%, #00475f 55%, #000000ba 140%); */
      
      box-shadow:0 18px 40px rgba(20,30,70,.18);
      position:relative;
      overflow:hidden;
      font-family: "Khmer OS Siemreap";
    }

    .card::before{
      content:"";
      position:absolute;
      inset:-40px -40px auto auto;
      width:220px;
      height:220px;
      background:radial-gradient(circle at 30% 30%, rgba(255,255,255,.20), rgba(255,255,255,0) 60%);
      transform:rotate(10deg);
      pointer-events:none;
    }

    .top{
      display:flex;
      align-items:flex-start;
      justify-content:space-between;
      gap:12px;
      margin-bottom:10px;
      position:relative;
      z-index:1;
    }

    .top-left .kh{
      font-size:14px;
      opacity:.9;
      letter-spacing:.2px;
      margin:0 0 2px 0;
      line-height:1.15;
    }
    .top-left .name{
      font-size:16px;
      font-weight:600;
      margin:0;
      line-height:1.15;
    }

    .mini-qr{
      width:34px;
      height:34px;
      border-radius:6px;
      background:rgba(255,255,255,.15);
      display:grid;
      place-items:center;
      flex:0 0 auto;
      backdrop-filter: blur(2px);
    }
    .mini-qr svg{ width:22px; height:22px; opacity:.95; }

    .page-sub-card { 
      display: flex;
      align-items: center;
      justify-content: center;
    }
      
    .sub-card{ 
      width: 230px !important; 
    }



    .screen { 
     
      padding: 18px 14px 22px;
      background: transparent;
      /* background: #ffffff; */
    }

    /* ===== Header Logo ===== */
    .brand {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
      margin-bottom: 14px;
    }

    .aba {
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 0.28em;
      color: #0b5874;
    }

    .pay {
      font-size: 22px;
      font-weight: 800;
      color: #00a9d4;
      display: flex;
      align-items: flex-end;
      gap: 6px;
    }

    .pay .dot {
      width: 7px;
      height: 7px;
      background: #e5161f;
      border-radius: 50%;
      transform: translateY(-9px);
    }
 

    .card-header {
      height: 50px;
      background: #e5161f;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      border-top-right-radius: 25px;
    border-top-left-radius: 25px;
    }

    .card-header::after {
        content: "";
        position: absolute;
        top: 50px;
        right: 0;
        width: 0;
        height: 0;
        border-right: 27px solid transparent;
        border-bottom: 18px solid rgb(255 255 255);
        background: #e5161f;
    }

    .khqr {
      color: #ffffff;
      font-weight: 900;
      letter-spacing: 0.14em;
      font-size: 18px;
    }

    .card-body {
      padding: 14px 16px 10px;
    }

    .merchant {
      font-size: 13px;
      color: #6b7485;
    }

    .amount {
      margin-top: 6px;
      font-size: 20px;
      font-weight: 800;
      display: flex;
      align-items: baseline;
      gap: 6px;
      color: #1e2430;
    }

    .currency {
      font-size: 14px;
      font-weight: 700;
      color: #3a4252;
    }

    .divider {
      height: 2px;
      border-top: 2px dashed #e8ebf0;
      margin: 12px 0 14px;
    }

    /* ===== QR ===== */
    .qr-wrap {
      display: flex;
      justify-content: center;
    }

    .qr {
      width: 180px;
      height: 180px;
      border-radius: 10px;
      border: 1px solid #eef1f6;
      overflow: hidden;
      background: #ffffff;
    }

    .qr img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .page-hint { 
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .hint {
      text-align: center;
      font-size: 11px;
      color: #ffffff;
      padding: 10px 12px 14px;
      width: 230px;
    }
</style>