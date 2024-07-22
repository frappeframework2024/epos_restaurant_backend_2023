<template>
    <div>
        Coupon Number
        <InputText v-model="saleCoupon.coupon_number"/>

        {{ saleCoupon }}
        <AutoComplete v-model="selectedMember" @focus="memberFocus" inputId="ac" optionLabel="label"  :suggestions="items" @complete="search">
            <template #option="slotProps">
                {{ slotProps.option.label }}
                <br/>
                {{ slotProps.option.description }}
            </template>
        </AutoComplete>
        <label for="ac">Membership Type</label>
        
        <InputText type="text"/>
        Price
        <InputNumber v-model="saleCoupon.price"/>
        <InputText type="text"/>
        <InputText type="text"/>
        <InputText type="text"/>
        <InputText type="text"/>
    </div>
</template>

<script setup>
    import InputText from "primevue/inputtext"
    import InputNumber from "primevue/inputnumber";
    import AutoComplete from 'primevue/autocomplete';
    import {ref,inject,watch } from 'vue'
    const frappe = inject("$frappe")
    const db = frappe.db();
    const call = frappe.call();
    const items = ref([]);
    const saleCoupon = ref({})
    const selectedMember = ref("")

    const search = (event) => {
        
        call.get("frappe.desk.search.search_link",{ 
            txt: event.query,
            doctype: "Membership",
            ignore_user_permissions: 0,
            reference_doctype: "Sale Coupon"
         }).then((res)=>{
            items.value = res.message
         })
    }
    function memberFocus(event){
        call.get("frappe.desk.search.search_link",{ 
            txt: "",
            doctype: "Membership",
            ignore_user_permissions: 0,
            reference_doctype: "Sale Coupon"
         }).then((res)=>{
            items.value = res.message
         })
    }
    watch(selectedMember, async (member) =>{
        saleCoupon.value.membership=member.value
    })
</script>

<style lang="css" scoped>

</style>