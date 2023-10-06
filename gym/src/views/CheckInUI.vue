
<template >
<ComIsLoadingPanel :isLoading="is_busy"/>
  <div style="height: 100vh;">
    <div class="inner h-full">
      <div class="grid m-0 h-full">
        <div class="col-12 p-0 md:col-12 lg:col-6 h-item">
          <div class="h-full">
            <div class="bg-white p-4 h-full flex flex-column"
              style="background-image: linear-gradient(to top, #a8edea 0%, #fed6e3 100%);">
              <div v-if="1==0" class="card flex justify-content-center">
                <Calendar v-model="date" showIcon inputStyle="border-radius: 50px 0 0 50px;text-align:center"
                  class="date-pick" dateFormat="yy/mm/dd" />
              </div>
              <!-- ===== -->
              <div class="mt-3">
                <div class="wrapper">
                  <div class="tab-wrapper">
                    <ul class="tabs">
                      <li class="tab-link" v-for="(item, index) in tap" :key="index" @click="currentTab(index)" :class="curTap === index ? 'active' : ''" :data-tab="index">{{ item }}</li>
                    </ul>
                  </div>
                  <div class="content-wrapper">
                    <div id="tab-1" class="tab-content" :class="curTap == 0 ? 'active' : ''">
                      <div id="phone" class="mt-5">
                        <div id="wrapper">
                          <h1 class="text-center mb-3 text-white">Check In</h1>
                          <form action="" method="GET" @submit.prevent="onCheckInClick" v-focustrap>
                            <div class="card flex justify-content-center" > 
                              <InputText type="text" class="dial-up-input key mb-5" v-model="checkInCode" autofocus 
                                placeholder="Enter check-in code..." />
                            </div>
                            <div class="flex justify-content-center w-full">
                              <div>
                                <div class="key dial" rel="1" @click="onKeyDialClick('1')">1</div>
                                <div class="key dial" rel="2" @click="onKeyDialClick('2')">2</div>
                                <div class="key dial" rel="3" @click="onKeyDialClick('3')">3</div>
                                <div class="clear"></div>
                                <div class="key dial" rel="4" @click="onKeyDialClick('4')">4</div>
                                <div class="key dial" rel="5" @click="onKeyDialClick('5')">5</div>
                                <div class="key dial" rel="6" @click="onKeyDialClick('6')">6</div>
                                <div class="clear"></div>
                                <div class="key dial" rel="7" @click="onKeyDialClick('7')">7</div>
                                <div class="key dial" rel="8" @click="onKeyDialClick('8')">8</div>
                                <div class="key dial" rel="9" @click="onKeyDialClick('9')">9</div>
                                <div class="clear"></div>
                                <div class="key dial special" rel="*" @click="onKeyDialClick('backspace')"><i class="pi pi-times"></i></div>
                                <div class="key dial" rel="1" @click="onKeyDialClick('0')">0</div>
                                <div class="key dial special" rel="#" @click="onCheckInClick"><i class="pi pi-check"></i></div>
                              </div>
                            </div>
                            <div class="clear"></div>
                            <div class="flex mt-3 justify-content-center">
                              <button type="submit" class="px-3 btn" >Check In<i class="pi pi-sign-in ml-2"></i></button>
                            </div>
                            <div class="clear"></div>
                          </form>
                        </div>
                      </div>
                    </div>
                    <div id="tab-2" class="tab-content" :class="curTap == 1 ? 'active' : ''">
                      <div class="mt-5 flex justify-content-center">
                          <ComAutoComplete doctype="Customer" @onSelected="onSelectCustomer"  placeholder="Enter Name..." />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-12 p-0 md:col-12 lg:col-6 h-item">
          <div class="h-full">
            <div class="bg-white p-4 h-full">
              <h3 class="mb-3">Recent Check-In</h3>
              <div class="scroll-item-cart">
                  <ComRecentCheckIn v-if="is_load_recent_check_in"/> 
              </div>
              <div class="btn-view-all flex justify-content-end pt-3">
                <button  class="px-3 btn" @click="onViewAllMemberCheckInClick"><i class="pi pi-eye mr-2" ></i>View all Member Check In </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import moment from 'moment';
import { ref, inject, onMounted } from 'vue'
import Calendar from 'primevue/calendar';
import InputText from 'primevue/inputtext';
import ComCheckInMembership from '@/views/components/ComCheckInMembership.vue';
import ComAutoComplete from '@/components/ComAutoComplete.vue';
import ComRecentCheckIn from '@/views/components/ComRecentCheckIn.vue';
import { useDialog } from 'primevue/usedialog';
import { useToast } from "primevue/usetoast";


const dialog = useDialog();
const toast = useToast();


const isFullscreen = ref(false)
 
const is_busy = ref(false)

const date = ref();
const curTap = ref(0);
const checkInCode = ref("");
const data = ref(null);
const tap = ref(['Enter Code', 'Name Search'])
const is_load_recent_check_in = ref(true)

const currentTab = (index) => {
  curTap.value = index
}


onMounted(()=>{ 
  window.parent.postMessage("full_screen","*")
})

function onKeyDialClick(n){
  if(n=="backspace"){
    if(checkInCode.value.length > 0){
      checkInCode.value = checkInCode.value.substring(0, checkInCode.value.length-1);
    }
  }else{
    checkInCode.value += n 
  }
}

function onCheckInClick(){
  
  const param = {
      'code':checkInCode.value, 
      check_in_date : moment().format('YYYY-MM-DD')
    }  
    is_busy.value = true; 
    window.call.get("epos_restaurant_2023.api.gym.membership_check_in",param)
    .then((res)=>{ 
      is_busy.value = false
      if(res.message){ 
        data.value = res.message;
        const dialogRef = dialog.open(ComCheckInMembership, {
              data: data.value,
              props: {
                      header: 'Check-In',
                      style: {
                          width: '80vw'
                      },
                      modal: true,
                      position:"top"
                  
                },
              onClose: (options) => { 
                  const data = options.data;
                  if (data) {
                    toast.add({ severity: 'success', summary: 'Check In', detail: 'Check In successfully.', life: 3000 });
                    checkInCode.value = "";
                    is_load_recent_check_in.value = false
                    setTimeout(() => {
                      is_load_recent_check_in.value = true;
                      console.log(data)
                    }, 50); 
                  
                  }
              }
          });

      }else{
        data.value = null
        checkInCode.value = "";
        toast.add({ severity: 'warn', summary: 'Member Code', detail: 'You input code is invalide member', life: 3000 });
   
      }     
    })
    .catch((error)=>{
      console.log(error);
      is_busy.value = false; 
    })
}

function onSelectCustomer(data){
  if(data.value == undefined){
    return
  } 
  checkInCode.value = data.value
  onCheckInClick();
  checkInCode.value = ""
}

function onViewAllMemberCheckInClick(){
  window.parent.postMessage("view_all_recent_membership_check_in","*")
}

window.addEventListener("message", receiveMessageFromIframe, false);

	function receiveMessageFromIframe(event) {		
		isFullscreen.value = true
	}

</script>

<style>
body,
html {
  margin: 0;
  padding: 0;
  background-color: var(--green-50);
  color: #444;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  color: #444;
  margin: 0;
}


#wrapper {
  margin: 0 auto 0 auto;
  position: relative;
  /* top: 50%;
  transform: translateY(-50%); */
}

.key {
  border-radius: 50px 50px 50px 50px;
  color: #444;
  width: 70px;
  height: 70px;
  text-align: center;
  font-size: 30px;
  float: left;
  box-sizing: border-box;
  margin: 0 7px 10px 7px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f8ff69;
  transition: all .4s ease;
}

.key span {
  display: block;
  color: #444;
  text-align: center;
  font-size: 12px;
  text-transform: uppercase;
}

.key.special {
  line-height: 60px;
}

.key.nb {
  border: none;
}

.key.phone {
  background: #5CDB74;
  border: none;
  color: #FFF;
  line-height: 60px;
  font-size: 1rem;
  height: 45px !important;
  margin: 0 auto !important;
  width: 50%;
  transition: all .4s ease;
}

.clear {
  clear: both;
}

.dial-up-input {
  border: none;
  line-height: 60px;
  font-size: 1rem;
  height: 60px;
  width: 50%;
}

.dial-up-input::placeholder {
  color: rgb(185, 185, 185);
  opacity: 1;
  /* Firefox */
}

.dial-up-input::-ms-input-placeholder {
  /* Edge 12-18 */
  color: rgb(185, 185, 185);
}

.dial-up-input:focus-visible {
  outline: 0;
}

.key.dial:hover {
  background-color: #a8a8a8a1;
  transition: all .4s ease;
}

.key.phone:hover {
  background-color: #109429c7;
  transition: all .4s ease;
}

.profile {
  width: 60px;
  height: 60px;
  /* border-radius: 50%; */
  overflow: hidden;
}

.profile img {
  object-fit: cover;
}

.profile-info .date {
  color: #ccc;
  font-size: 13px;
}

.cart-item {
  /* box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px; */
  border-bottom: 1px solid #cccccc40;
}

.scroll-item-cart {
  overflow: auto;
  height: calc(100vh - 147px);
}

button.btn {
  background: #5CDB74;
  border: none;
  color: #FFF;
  line-height: 2.5;
  transition: all .4s ease;
  border-radius: 50px 50px 50px 50px;
  font-size: 1rem;
}

/*tab active */
.tab-wrapper {
  text-align: center;
  display: block;
  margin: auto;
  max-width: 500px;
}

.tabs {
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
}

.tab-link {
  margin: 0 1%;
  list-style: none;
  padding: 10px 15px;
  color: #aaa;
  cursor: pointer;
  font-weight: 700;
  transition: all ease 0.5s;
  border-bottom: solid 3px rgba(255, 255, 255, 0);
  letter-spacing: 1px;
}

.tab-link:hover {
  color: #999;
  border-color: #999;
}

.tab-link.active {
  color: #333;
  border-color: #333;
}

.tab-link:nth-of-type(1).active {
  color: #EE6534;
  border-color: #EE6534;
}

.tab-link:nth-of-type(2).active {
  color: #1790D2;
  border-color: #1790D2;
}

.tab-link:nth-of-type(3).active {
  color: #EEC63B;
  border-color: #EEC63B;
}

.tab-content {
  display: none;
  text-align: center;
  color: #888;
  font-weight: 300;
  font-size: 15px;
  opacity: 0;
  transform: translateY(15px);
  animation: fadeIn 0.5s ease 1 forwards;
}

.tab-content.active {
  display: block;
}

.date-pick button {
  border-radius: 0 50px 50px 0;
  background-color: #5CDB74;
  border: 0;
}

.date-pick input {
  color: #444;
  height: 40px;
  text-align: center;
  font-size: 16px;
  float: left;
  box-sizing: border-box;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f8ff69;
  transition: all .4s ease;
  border: 0;
}

@keyframes fadeIn {
  100% {
    opacity: 1;
    transform: none;
  }
}

button.btn {
  cursor: pointer;
}

button.btn:hover {
  background: #3f814b;
}

@media (max-width: 992.98px) {
  #phone {
    height: 655px !important;
  }

  .dial-up-input {
    width: 80%
  }

  .h-item {
    height: unset !important;
  }

  .scroll-item-cart {
    height: calc(100vh - 1px);
  }
}

.p-calendar:not(.p-calendar-disabled).p-focus>.p-inputtext {
  box-shadow: unset !important;
}</style>
