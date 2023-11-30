<template>
  <template v-if="data != null">
     
    <div class="grid">
      <div class="col-5 bg-cyan-900 border-round-left-sm overflow-auto" style="height: calc(100vh - 12em);">
        <div class="flex flex-column">
          <div>
            <p class="text-white text-center m-3 text-3xl">Welcome back!</p>
            <div class="flex w-full justify-content-center">
              <div class="profile popup">
                <img class="w-full h-full" :src="data?.member?.photo ? data?.member?.photo : '/src/assets/images/d-profile.jpeg'">
              </div>
            </div>
            <h3 class="text-center text-white my-3">{{ `${data.member.customer_name_en== data.member.customer_name_kh?data.member.customer_name_en: data.member.customer_name_en + ' ('+data.member.customer_name_kh+')'}` }}</h3>
            <h5 class="text-center text-white my-3">{{ `${data.member.name}` }}</h5>
         
            <div style="width:50%;border-color: #e9ecef33 !important;" class="border-1 m-auto"></div>
            <h3 class="text-center my-3"><strong class="text-white">Membership</strong></h3>
          </div>
   
          <div>

            <h4 class="text-center my-3" v-if="data.membership.length<=0"><i><strong class="text-white">Not Available</strong></i></h4>

            <div class="member-checkin inner-items p-2 mb-2 border-round-sm" v-for="(d, index) in data.membership" :key="index"
            :style="`background: ${d.locked ? 'rgb(255 255 255 / 7%)' : '#ffffff2b'};border: 1px solid ${d.selected ? 'green' : 'transparent'};`"
            >

              <div :disabled="d.locked"  @click="onMembershipSelected(d)" :style="!d.locked?'cursor: pointer':'cursor: hand'" >
                <div class="item-inner-text pb-2 mb-2">
                  <div class="grid">
                    <div class="col">
                      <div class="mb-2">
                        
                        <span class="text-base">{{ d.name }} - {{ d.membership_type }}</span> 
                      </div>
                      
                      <p class="text-400 text-xs">Register on: {{ d.posting_date }}</p> 
                      <p class="m-0 text-400 text-xs">{{ d.membership }}</p>
                      <template v-if="d.duration_type == 'Limited Duration'">
                        <p class="text-400 text-xs">{{ `${d.duration_type} : ${d.membership_duration} ${d.duration_base_on}` }}</p>
                        <p class="text-400 text-xs">From: {{ d.start_date }} - {{ d.end_date }}</p>
                      </template>
                      <template v-else>
                        <p class="text-400 text-xs">{{ `Duration: ${d.duration_type}` }}</p>
                      </template>
                      
                      <p class="mt-1" v-if="d.locked">
                        <label class="text-xs text-white bg-green-200 border-round-3xl pl-2 pr-2 pt-1 pb-1" style="background-color: rgba(247, 162, 5, 0.863) !important;">Not Available</label>
                      </p>
                    </div>
                    <div class="col-4 flex justify-content-end" >
                      <div class="flex flex-column justify-content-between"> 
                        <div class="flex justify-content-end">
                          <Checkbox v-if="!d.locked" v-model="d.selected" :binary="true" :disabled="d.locked"  @click="onMembershipSelected(d)" />
                        </div>
                        <div>
                          <span>
                            <label class="text-xs text-white bg-green-200 border-round-3xl p-2 " style="background-color: #033d2299 !important;">Checked-In <span class="bg-green-500 px-1 border-round-xs">{{ d.total_checked_in }}</span></label>
                            <span class=""></span>
                          </span>
                          
                        </div>
                      </div>
                    </div>
                    
                  </div>
                </div>
              </div>
              <div class="access-dropdown">
                <Accordion :activeIndex="1">
                  <AccordionTab header="Access Details">
                    <div class="card">
                      <p>
                        <template v-if="d.tracking_limited == 1">
                          <span v-if="d.duration_type == 'Limited Duration'">
                            Max Accessable:  {{`${d.max_access} time(s) in ${d.membership_duration} ${d.duration_base_on}`}}
                          </span>
                          <span v-else>
                            Max Accessable: {{`${d.max_access} time(s)  ${d.duration_type}`}}
                          </span>
                        </template>
                        <template v-else>
                          <template v-if="d.access_type == 'Unlimited'"> 
                            <span>{{ d.access_type }}</span>
                          </template>
                          <template v-else>
                            <span>Access {{ `${d.duration} ${d.access_type.toLowerCase()} / ${d.per_duration.toLowerCase()}` }}</span>
                          </template>
                        </template>  
                      </p>
                    </div>
                  </AccordionTab>
                </Accordion>                               
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col border-round-right-sm" style="background-color: var(--green-50);height: calc(100vh - 12em);">
        <div class="flex flex-column justify-content-between h-full p-3">
          <div>
            <div class="mb-6">
              <h3>Check-In Items</h3>
              <p class="text-500 m-0 text-sm">Choose the items you are checking into:</p>
            </div>
            <div class="overflow-auto pr-4" style="height: calc(100vh - 23em);margin-right: -1.5rem;">
              <div v-for="(d, index) in dataSelected" :key="index"> 
               <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">{{ d.name }} - {{ d.membership_type }}</strong>
                      <p class="text-500 text-xs mb-0">{{ d.membership }}</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">
                      <template v-if="d.tracking_limited == 1">
                        <span v-if="d.duration_type == 'Limited Duration'">
                            Max Accessable:  {{`${d.max_access} time(s) in ${d.membership_duration} ${d.duration_base_on}`}}
                          </span>
                          <span v-else>
                            Max Accessable: {{`${d.max_access} time(s)  ${d.duration_type}`}}
                          </span>
                      </template>
                      <template v-else>
                        <template v-if="d.access_type == 'Unlimited'">
                          <span>Access: {{ d.access_type }}</span>
                        </template>
                        <template v-else>
                          <span>Access: {{ `${d.duration} ${d.access_type.toLowerCase()} /
                                      ${d.per_duration.toLowerCase()}` }}</span>
                        </template>
                      </template>                     
                    </p>
                  </div>
                </div>
               </div> 
              </div>             
            </div>
          </div>
          <div class="flex justify-content-end mt-2">
            <Button class="btn" label="Confirm Check-In"  :loading="is_processing" style="line-height: 1.5;" :disabled="dataSelected.length<=0 || is_processing" @click="onCheckInClick"/>
          </div>
        </div>
      </div>
    </div>
 
  </template>
</template>
<script setup>
import { inject, onMounted, ref } from 'vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Checkbox from 'primevue/checkbox';
const frappe = inject("$frappe")
 
const call = frappe.call();

const dialogRef = inject("dialogRef");
const data = ref(null)

const dataSelected = ref([]);
const is_processing = ref(false)


onMounted(() => {
  is_processing.value = false;
  data.value = dialogRef.value.data
})

function onMembershipSelected(m) {
  if (!m.locked)
    m.selected = !m.selected


  dataSelected.value = data.value.membership.filter((r) => r.selected)
}

function onCheckInClick() {



  const check = data.value.membership.filter((r) => r.selected);
  if (check.length <= 0) {
    return
  } 
  is_processing.value = true;

  const submit_data = ref([]);

  check.forEach((c) => {
    submit_data.value.push({
    "doctype": "Membership Check In",
    "member": data.value.member.name,
    "check_in_date": data.value.check_in_date,    
    "membership_check_in_item": [{
      "membership": c.name,
      "member":data.value.member.name 
    }]}) 
  });

 

  call.get('epos_restaurant_2023.api.gym.check_in_submit_data',{"data":JSON.stringify(submit_data.value) }).then((res)=>{
      data.value = null;
      dialogRef.value.close(res.message);
      is_processing.value = false;
  }).catch((error) => {
    is_processing.value = false;
 
  });
 
}
</script>
<style>
.profile.popup {
  width: 100px !important;
  height: 100px !important;
}
.text-500{
  color: #4b535b !important;
}

.member-checkin * {
  color: #fff;
}

.member-checkin .inner-items {
  background-color: #ffffff2b;
}

.inner-items .item-inner-text {
  border-bottom: 1px solid #ffffff59;
}

.inner-items .item-inner-text * {
  font-size: 14px;
  margin: 0;
}

.access-dropdown * {
  font-size: 14px;
}

.access-dropdown .p-accordion .p-accordion-header .p-accordion-header-link {
  background: transparent !important;
  padding: 7px 0 !important;
  border: 0 !important;
}

.access-dropdown .p-accordion .p-accordion-header .p-accordion-header-link svg {
  width: 13px;
  fill: #ffffff69 !important;
}

.access-dropdown .p-accordion .p-accordion-header:not(.p-disabled).p-highlight .p-accordion-header-link {
  background: transparent;
}

.access-dropdown .p-accordion .p-accordion-content {
  background: transparent;
  border: 0;
  padding: 0 1.25rem;
}

.access-dropdown .p-accordion .p-accordion-header:not(.p-disabled) .p-accordion-header-link:focus-visible {
  box-shadow: unset;
}

.access-dropdown .p-accordion-header-text{
  color: #ffffff69 !important;
  font-size: 12px !important;
}
::-webkit-scrollbar-track
{
	-webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
	background-color: #F5F5F5;
}

::-webkit-scrollbar
{
	width: 5px;
	background-color: #F5F5F5;
}

::-webkit-scrollbar-thumb
{
	background-color: var(--blue-500);	
}
</style>