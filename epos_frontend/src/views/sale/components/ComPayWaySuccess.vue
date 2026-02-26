<template lang="">   
  <div class="card">
      <div class="top">   
          <v-btn icon @click="onClose()" style="position: absolute; top: -10px; right: -10px;">
              <v-icon>mdi-close</v-icon>
          </v-btn> 
      </div>      
      <div class="screen" :class="[isMobile?'screen-mobile-aba':'']"> 
        <div class="page-sub-card"> 
          <div class="success-container">
            <div class="success-icon">
              <svg viewBox="0 0 24 24">
                <path d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div class="success-title">{{$t("Payment Successful")}}</div>
            <div class="success-text">{{$t("Thank you! Your transaction has been completed.")}}</div>

             <div class="countdown">
              {{$t('Returning in')}} <span>{{timerCount}}</span> {{$t('seconds')}}
            </div>

          </div>
        </div> 
      </div> 
  </div>
</template>
<script setup> 
    import { i18n,ref,onBeforeUnmount ,onMounted } from '@/plugin'; 
    const totalSecond = 10;
    const timerCount = ref(totalSecond);

    const { t: $t } = i18n.global; 
    const isMobile = ref(false);
    const checkMobile = () => {
      isMobile.value = window.matchMedia("(max-width: 500px)").matches;
    }

    let mediaQuery;
    onMounted(() => {
      mediaQuery = window.matchMedia("(max-width: 500px)");
      isMobile.value = mediaQuery.matches;
      mediaQuery.addEventListener("change", checkMobile);

      const countdown = setInterval(()=>{
        timerCount.value--;
        if(timerCount.value <= 0){
          clearInterval(countdown)   ;
          onClose();     
        }
        
      },1000);

    });

    onBeforeUnmount(() => {
      mediaQuery.removeEventListener("change", checkMobile);
    });
    
    const emit = defineEmits(["onClose"]) ;
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
        /* 📱 Mobile */
    @media (max-width: 500px) {
      .card{
        background:  #e8e9ec;
        border: #ffffff solid 6px;
        border-radius: 18px;
        margin: 10px;
        width: 95%;
        /* or solid color */
        /* background: #00475f; */
      }
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

    .page-sub-card { 
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .screen { 
     
      padding: 18px 14px 22px;
      background: transparent;
      /* background: #ffffff; */
    }
  .success-container {
    background: #ffffff;
    padding: 40px 32px;
    border-radius: 16px;
    text-align: center;
    width: 320px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  }

  .success-icon {
    width: 90px;
    height: 90px;
    background: #22c55e;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px;
  }

  .success-icon svg {
    width: 48px;
    height: 48px;
    stroke: #ffffff;
    stroke-width: 3;
    fill: none;
  }

  .success-title {
    font-size: 20px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 8px;
  }

  .success-text {
    font-size: 14px;
    color: #6b7280;
  }

  .screen-mobile-aba {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  } 


  .countdown {
    font-size: 14px;
    color: #374151;
  }

  .countdown span {
    font-weight: 600;
    color: #ff0000;
  }

</style>