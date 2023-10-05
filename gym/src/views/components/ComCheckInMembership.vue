<template>
  <template v-if="data != null">
    <div class="grid">
      <div class="col-5 bg-cyan-900 border-round-left-sm overflow-auto" style="height: calc(100vh - 12em);">
        <div class="flex flex-column">
          <div>
            <p class="text-white text-center m-3 text-4xl">Welcome back!</p>
            <div class="flex w-full justify-content-center">
              <div class="profile popup">
                <img class="w-full h-full" :src="data?.member?.photo ? data?.member?.photo : '/src/assets/images/d-profile.jpeg'">
              </div>
            </div>
            <h2 class="text-center text-white my-3">{{ data.member.customer_name_en }}</h2>
            <div style="width:50%;border-color: #e9ecef33 !important;" class="border-1 m-auto"></div>
            <p class="text-center my-3"><strong class="text-white">Membership</strong></p>
          </div>
          <div>
            <div class="member-checkin inner-items p-2 mb-2 border-round-sm" v-for="(d, index) in data.membership" :key="index"
            :style="`background: ${d.locked ? 'rgb(255 255 255 / 7%)' : '#ffffff2b'};border: 1px solid ${d.selected ? 'green' : 'transparent'};`"
            >
              <div :disabled="d.locked"  @click="onMembershipSelected(d)" :style="!d.locked?'cursor: pointer':'cursor: hand'" >
                <div class="item-inner-text pb-2 mb-2">
                  <div class="grid">
                    <div class="col">
                      <div class="mb-2">
                        <span class="text-base">{{ d.membership_type }}</span> <span v-if="d.locked">| <label class="text-xs text-white bg-green-200 border-round-3xl px-2 white-space-nowrap" style="background-color: #033d2299 !important;">Checked-In</label></span>
                      </div>
                      <p class="m-0 text-400 text-xs">{{ d.membership }}</p>
                      <template v-if="d.duration_type == 'Limited Duration'">
                        <p class="text-400 text-xs">{{ `${d.duration_type} : ${d.membership_duration} ${d.duration_base_on}` }}</p>
                        <p class="text-400 text-xs">From: {{ d.start_date }} - {{ d.end_date }}</p>
                      </template>
                      <template v-else>
                        <p class="text-400 text-xs">{{ `Duration: ${d.duration_type}` }}</p>
                      </template>
                    </div>
                    <div class="col-3 flex justify-content-end" >
                      <div class="flex flex-column justify-content-between"> 
                        <Checkbox v-if="!d.locked" v-model="d.selected" :binary="true" :disabled="d.locked"  @click="onMembershipSelected(d)" />
                        <div>
                          <p class="text-3xl flex align-items-center h-full">2</p>
                        </div>
                      </div>
                    </div>
                    
                  </div>
                </div>
              </div>
              <div class="access-dropdown">
                <template v-if="d.access_type == 'Unlimited'">
                  <div class="card">
                    <Accordion :activeIndex="1">
                      <AccordionTab header="Access Details">
                        <p>
                          <span>{{ d.access_type }}</span>
                        </p>
                      </AccordionTab>
                    </Accordion>
                  </div>
                </template>
                <template v-else>
                  <div class="card">
                    <Accordion :activeIndex="1">
                      <AccordionTab header="Access Details">
                        <p>
                          <span>Access {{ `${d.duration} ${d.access_type.toLowerCase()} /
                                    ${d.per_duration.toLowerCase()}` }}</span>
                        </p>
                      </AccordionTab>
                    </Accordion>
                  </div>
                </template>
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
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
            
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
             
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
              <div class="items-gym border-bottom-1 border-300 pb-3 mb-3">
                <div class="flex w-full justify-content-between">
                  <div class="flex">
                    <div class="flex h-full align-items-center mr-3">
                      <i class="pi pi-check-circle text-500"></i>
                    </div>
                    <div>
                      <strong class="text-500">Time4 Training</strong>
                      <p class="text-500 text-xs mb-0">90 Minutes</p>
                    </div>
                  </div>
                  <div class="flex align-items-end">
                    <p class="text-end text-500 text-xs m-0">Strength & Conditioning</p>
                  </div>
                </div>
              </div>
              
            </div>
          </div>
          <div class="flex justify-content-end mt-3">
            <Button @click="onCheckInClick">Confirm Check-In</Button>
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


onMounted(() => {
  data.value = dialogRef.value.data
})

function onMembershipSelected(m) {
  if (!m.locked)
    m.selected = !m.selected
}

function onCheckInClick() {
  const check = data.value.membership.filter((r) => r.selected);
  if (check.length <= 0) {
    return
  } 

  const submite_data = ref(
    {
    "doctype": "Membership Check In",
    "member": data.value.member.name,
    "check_in_date": data.value.check_in_date,    
    "membership_check_in_item": []
  })

  check.forEach((c) => {
    submite_data.value.membership_check_in_item.push({ "membership": c.name })
  }) 
  call.get('epos_restaurant_2023.api.gym.check_in_submit_data',{"data":submite_data.value}).then((res)=>{
      data.value = null;
      dialogRef.value.close(res.message);
  }).catch((error) => {
    console.log({'submit_data_bug':error})
  });
 
}
</script>
<style>
.profile.popup {
  width: 100px !important;
  height: 100px !important;
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