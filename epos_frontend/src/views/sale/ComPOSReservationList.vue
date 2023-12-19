<template>
    <ComModal :mobileFullscreen="true" @onClose="onClose()" width="1200px" :hideOkButton="true">
      <template #title>
        {{ $t('Reservation') }}
      </template>
      <template #content>
        <ComPlaceholder :loading="isLoading" :is-not-empty="reservationData.length > 0"
          :text="$t('Empty Data')" icon="mdi-note-outline">
          <div>
          <div class="grid gap-2 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
            <v-card v-for="(s, index) in reservationData" :key="index">
              <v-card-title class="!p-0">
                <v-toolbar height="48">
                  <v-toolbar-title class="text">
                    <span class="font-bold text-sm">{{ s.name }}</span>
                  </v-toolbar-title>
                  <template v-slot:append>
                    <v-chip size="small" class="ma-2" :color="s.reservation_status_background_color" :text-color="s.reservation_status_color">
                      {{ s.reservation_status }}
                    </v-chip>
                  </template>
                </v-toolbar>
              </v-card-title>
              <v-card-text class="!pt-0 !pr-0 !pb-14 !pl-0">
                <v-list :lines="false" density="compact" class="pa-0">

                  <v-list-item :title="`${$t('Arrival Date')}:`">
                    <template v-slot:append>
                      {{ moment(new Date(`${s.arrival_date} ${s.arrival_time}`)).format('yyyy-MM-DD hh:mm A')  }}
                    </template>
                  </v-list-item> 

                  <v-list-item :title="`${$t('Table')}#`" v-if="s.table_number">
                    <template v-slot:append>
                      {{ s.table_number }}
                    </template>
                  </v-list-item>

                  <v-list-item :title="`${$t('Guest Cover')}:`" v-if="s.total_guest">
                    <template v-slot:append>
                      {{ s.total_guest }}
                    </template>
                  </v-list-item>
                  <v-list-item :title="`${$t('Customer Code')}:`">
                    <template v-slot:append>
                      {{ s.guest }}
                    </template>
                  </v-list-item>

                  <v-list-item :title="`${$t('Customer Name')}:`">
                    <template v-slot:append>
                      {{ s.guest_name }}
                    </template>
                  </v-list-item>

                  <v-list-item :title="`${$t('Total Qty')}:`" v-if="s.total_quantity>0">
                    <template v-slot:append>
                      {{ s.total_quantity }}
                    </template>
                  </v-list-item>


                </v-list>
              </v-card-text>
              <v-card-actions class="pt-0 flex items-center justify-between absolute bottom-0 w-full">
             
                <v-btn variant="tonal" color="success" @click="onCheckIn(s.name)">
                 {{ $t('Checked In') }}
                </v-btn>
              </v-card-actions>
            </v-card>
          </div>
        </div>
        </ComPlaceholder>
      </template>
    </ComModal>
  </template>
  <script setup>
  import { useRouter, defineProps, createResource, defineEmits, ref, inject, createToaster,i18n,onMounted,smallViewSaleProductListModal } from "@/plugin"
  import ComModal from "../../components/ComModal.vue";
  import ComPlaceholder from "../../components/layout/components/ComPlaceholder.vue";
  import { useDisplay } from 'vuetify';  
  import moment from '@/utils/moment.js';


  const { t: $t } = i18n.global;  
  const { mobile } = useDisplay();

  const isLoading = ref(true);
  const reservationData = ref([]);


  const frappe = inject("$frappe");
  const router = useRouter();
  const emit = defineEmits(["resolve"])
  const gv = inject('$gv');
  const sale = inject("$sale");
  const tableLayout = inject("$tableLayout");
  const toaster = createToaster({ position: "top" });

  const db = frappe.db();
  const call = frappe.call();
  
  const props = defineProps({
    params: {
      type: Object,
      required: true,
    }
  }) 

  onMounted(()=>{ 
    const today =  moment(new Date()).format('yyyy-MM-DD')
    db.getDocList("POS Reservation",
    {
      fields:["name"],
      filters:[
        ["property","=",gv.setting.business_branch],
        ["arrival_date","=",today],
        ["status","in","Confirmed"]
      ],
      limit: 50,
      orderBy: {
        field: 'arrival_date',
        order: 'desc',
      },
    }).then(doc=>{
      reservationData.value = [];
      doc.forEach(d => {
        db.getDoc("POS Reservation",d.name).then(r=>{
          reservationData.value.push(r) ;
          
        })
       
      });
      
      isLoading.value = false;
      console.log(reservationData.value )
    }).catch(err=>{
      isLoading.value = false;
    });

  })
   
 
   function onCheckIn(reservation){
    alert(reservation)
   }
  
  
  function onClose() {
    emit('resolve', false);
  }
  </script>