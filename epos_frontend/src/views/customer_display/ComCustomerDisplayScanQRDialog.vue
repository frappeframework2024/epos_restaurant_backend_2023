<template lang="">
    <v-dialog v-model="open" width="40rem" persistent>
   
            <div class="card">
                <div class="top"> 
                    <!-- small QR icon (top-right) -->
                    <div class="mini-qr" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="none">
                        <path d="M3 3h7v7H3V3Zm2 2v3h3V5H5Zm9-2h7v7h-7V3Zm2 2v3h3V5h-3ZM3 14h7v7H3v-7Zm2 2v3h3v-3H5Zm11 0h2v2h-2v-2Zm-2-2h2v2h-2v-2Zm6 0h1v3h-1v-3Zm-2 3h3v1h-3v-1Zm-4 2h2v2h-2v-2Zm3 0h4v2h-1v-1h-3v-1Z" fill="rgba(255,255,255,.95)"/>
                        </svg>
                    </div>
                </div>

                <div class="title">{{$t('Scan to Pay')}}</div>

                <div class="qr-wrap">
                    <div class="qr-frame">
                        <span class="corner c-tl"></span>
                        <span class="corner c-tr"></span>
                        <span class="corner c-bl"></span>
                        <span class="corner c-br"></span>

                        <div class="qr-box"> 
                        <!-- Put your real QR image here -->
                        <img width="250px"  v-if="qrImage" :src="qrImage" alt="QR Code"/>
                        </div>
                    </div>
                </div>

                <div class="code">{{$t('Account Name')}}: <b>Long Saroth</b></div>
                
                <div class="bottom">
                    <div class="col left">
                        <p class="label">{{$t('Transaction Date')}}</p>
                        <p class="value">15-10-2025</p>
                    </div>
 
                    <div class="col right flex justify-end gap-3">
                        <div>
                            <p class="label">{{$t('Balance')  }} ({{sale.setting.pos_setting.main_currency_name}})</p>
                            <p class="value white"><CurrencyFormat :value="props.data.balance" /></p>
                        </div>
                        <div>
                            <p class="label">{{ $t('Balance') }} ({{sale.setting.pos_setting.second_currency_name}})</p>
                            <p class="value white"><CurrencyFormat :value="props.data.balance * props.data.exchange_rate" :currency="sale.setting.pos_setting.second_currency_name"/></p>
                        </div>
                    </div>
                </div>
            </div>
             
    </v-dialog>
</template>
<script setup>
  import { inject, ref,onMounted,i18n } from '@/plugin';
  const { t: $t } = i18n.global; 
  const sale = inject('$sale')
  const frappe = inject('$frappe')
  const call = frappe.call()
  const open = ref(true)
  const props = defineProps({
      data: Object,
      aba_data: Object
  })

  const qrImage = ref(null)
  onMounted(()=>{
    qrImage.value = props.aba_data.qr_image_custom
  })
 


</script>
<style scoped>
    .card{
      width:100%;
      height:514px;
      padding:18px 18px 16px;
      color:#ffffff;
      border-radius:18px;
      background: linear-gradient(135deg, #2d69af 0%, #3c5fd1 55%, #b8c2f6 140%);
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

    .title{
      text-align:center;
      font-size:24px;
      font-weight:700;
      margin:8px 0 14px;
      letter-spacing:.3px;
      position:relative;
      z-index:1;
    }

    .qr-wrap{
      display:flex;
      justify-content:center;
      position:relative;
      z-index:1;
      margin-bottom:10px;
    }

    .qr-frame{
      position:relative;
      width:220px;
      height:220px;
      display:grid;
      place-items:center;
    }

    .qr-box{
      width:170px;
      height:170px;
      background:#ffffff;
      border-radius:10px;
      box-shadow:0 10px 22px rgba(10,20,60,.22);
      display:grid;
      place-items:center;
      overflow:hidden;
    }

    .qr-box img{
      width:90%;
      object-fit:contain;
      image-rendering:pixelated;
    }

    .corner{
      position:absolute;
      width:28px;
      height:28px;
      border:4px solid #2fe3ff;
      opacity:.95;
    }
    .c-tl{ top:6px; left:6px; border-right:none; border-bottom:none; }
    .c-tr{ top:6px; right:6px; border-left:none; border-bottom:none; }
    .c-bl{ bottom:6px; left:6px; border-right:none; border-top:none; }
    .c-br{ bottom:6px; right:6px; border-left:none; border-top:none; }

    .code{
      text-align:center;
      margin:6px 0 14px;
      font-size:16px;
      font-weight:600;
      color:rgba(255,255,255,.85);
      position:relative;
      z-index:1;
    }
    .code b{
      color:#ffffff;
      letter-spacing:1px;
      margin-left:6px;
      font-weight:700;
    }

    .bottom{
      position:absolute;
      left:18px;
      right:18px;
      bottom:14px;
      display:flex;
      justify-content:space-between;
      gap:10px;
      z-index:1;
    }

    .col{ min-width:0; }

    .label{
      font-size:12.5px;
      opacity:.9;
      margin:0 0 6px 0;
      line-height:1.2;
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
    }

    .value{
      font-size:18px;
      font-weight:700;
      margin:0;
      line-height:1.2;
      white-space:nowrap;
    }

    .value.red{ color:#ff3b30; }
    .value.white{ color:#ffffff; }

    .col.mid{
      text-align:center;
      flex:1;
    }
    .col.left{ text-align:left; width:110px; }
    .col.right{ text-align:right; width:140px; }

    .footer-glow{
      position:absolute;
      left:0; right:0; bottom:-40px;
      height:120px;
      background:radial-gradient(circle at 50% 0%, rgba(255,255,255,.18), rgba(255,255,255,0) 60%);
      pointer-events:none;
    }
</style>