<template>
    
	  <router-view />
	  <DynamicDialog />
	  <Toast>
        <template #message="slotProps">
            <div class="flex flex-column" style="flex: 1">
                <strong class="mb-1" v-if="slotProps.message.summary" v-html="slotProps.message.summary"></strong>
                <p v-if="slotProps.message.detail" v-html="slotProps.message.detail"></p>
            </div>
        </template>
    </Toast>
	
</template>
 