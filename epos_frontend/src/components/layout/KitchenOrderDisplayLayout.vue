<template>
    <v-app>
        <v-app-bar :elevation="2" color="error">
            <template #prepend>
                <!-- <v-app-bar-nav-icon size="small" variant="text" @click.stop="onDrawer()"></v-app-bar-nav-icon> -->
                
                    
                <v-btn icon @click="onBack('Home')">
                    <v-icon>mdi-home-outline</v-icon>
                </v-btn>
              
                <v-app-bar-title>
                    <div :class="mobile ? 'text-xs' : ''">
                        Kitchen Order Display(KOD) - {{ screen_name }}
                    </div>
                </v-app-bar-title>
            </template>


            <template #append>
                <ComKodSetting/>
       
                <v-btn :loading="kod.loading" @click="kod.getKODData(setting.pos_setting.business_branch, screen_name)"> <v-icon>mdi-refresh</v-icon></v-btn>
                <ComTimeUpdate />
                <template v-if="isWindow">
                   
                    <v-btn :icon="(!gv.isFullscreen ? 'mdi-fullscreen' : 'mdi-fullscreen-exit')"
                        @click="onFullScreen()"></v-btn>
                </template>
                

                <v-menu :location="location">

                    <template v-slot:activator="{ props }">
                        <v-avatar v-if="currentUser?.photo" :image="currentUser.photo" v-bind="props"></v-avatar>
                        <avatar v-else :name="currentUser?.full_name || 'No Name'" v-bind="props" class="cursor-pointer"
                            size="40"></avatar>
                    </template>
                    <v-card min-width="300">
                        <ComCurrentUserAvatar />
                        <v-divider></v-divider>
                        <v-list density="compact">
                            <v-list-item @click="onReload()">

                                <template v-slot:prepend class="w-12">
                                    <v-icon icon="mdi-reload"></v-icon>
                                </template>
                                <v-list-item-title>{{ $t('Reload') }}</v-list-item-title>
                            </v-list-item>
                            <v-divider></v-divider>
                            <v-list-item @click="onLogout">

                                <template v-slot:prepend class="w-12">
                                    <v-icon icon="mdi-logout"></v-icon>
                                </template>
                                <v-list-item-title>{{ $t('Logout') }}</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-card>

                </v-menu>
            </template>
        </v-app-bar>
        <v-navigation-drawer v-model="drawer" temporary>
            <MainLayoutDrawer />

            <template v-slot:append>
                <v-btn variant="tonal" prepend-icon="mdi-arrow-left" class="w-full" @click="onDrawer">
                    {{ $t('Close') }}
                </v-btn>
            </template>
        </v-navigation-drawer>
        <v-main>
            <router-view />
        </v-main>
    </v-app>
</template>

<script setup>
import ComProductSearch from '../../views/sale/components/ComProductSearch.vue'
import MainLayoutDrawer from './MainLayoutDrawer.vue';
import ComTimeUpdate from './components/ComTimeUpdate.vue';
import ComCurrentUserAvatar from './components/ComCurrentUserAvatar.vue';
import ComKodSetting from '@/views/kitchen_order_display/components/ComKodSetting.vue';

import { useDisplay } from 'vuetify';
import { useRouter, ref, inject, confirmBackToTableLayout, SearchProductDialog } from '@/plugin';

import { computed } from 'vue';
import Enumerable from 'linq';
const kod = inject("$kod")
const setting = JSON.parse(localStorage.getItem("setting"))
const screen_name = JSON.parse(localStorage.getItem("device_setting")).default_kod
const emit = defineEmits('closeModel')

const auth = inject("$auth")
const gv = inject("$gv")

const { mobile } = useDisplay();
const router = useRouter();


const currentUser = computed(() => {
    return JSON.parse(localStorage.getItem('current_user'))
});

const isWindow = computed(() => {
    return localStorage.getItem('is_window') == '1';
})

let drawer = ref(false);


function onDrawer() {
    drawer.value = !drawer.value;
}
function onReload() {
    location.reload();
    const apkipa = localStorage.getItem('apkipa');
    const flutterChannel = localStorage.getItem('flutterChannel');
    if ((apkipa || 0) == 1) {
        if ((flutterChannel || 0) == 1) {
            flutterChannel.postMessage("mobile_reload");
        }
        else {
            window.ReactNativeWebView.postMessage("mobile_reload");
        }

    }
}

async function onAdvanceSearch() {
    const result = await SearchProductDialog({ title: "Search Product" })
}
function onLogout() {
    const isOrdered = sale.isOrdered()
    if (isOrdered == false) {
        auth.logout().then((r) => {
            router.push({ name: 'Login' })
        })
    }
}

function onFullScreen() {
    window.chrome.webview.postMessage(JSON.stringify({ action: "toggle_fullscreen", "is_full": gv.isFullscreen ? "0" : "1" }));
    gv.isFullscreen = gv.isFullscreen ? false : true;
}



async function onBack(_router) {

    const sp = Enumerable.from(sale.sale.sale_products);
    if (sp.where("$.name==undefined").toArray().length > 0) {
        let result = await confirmBackToTableLayout({});
        if (result) {
            if (result == "hold" || result == "submit") {
                if (result == "hold") {
                    sale.sale.sale_status = "Hold Order";
                    sale.action = "hold_order";
                } else {
                    sale.sale.sale_status = "Submitted";
                    sale.action = "submit_order";
                }
                await sale.onSubmit().then(async (value) => {
                    if (value) {
                        router.push({ name: _router })
                    }
                });
            } else {
                //continue
                sale.sale = {};
                router.push({ name: _router })
            }
        }
    } else {
        sale.sale = {};
        router.push({ name: _router })
    }
}


</script>

<style>
.advanced-btn {
    border: 1px solid #adadad !important;
    background: #2196f3 !important;

}

.sale-search-cs .v-field__input {
    width: 155px;
}
</style>