// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Business Branch", {
	refresh(frm, ) {
        if(!frm.is_new()){
            frm.add_custom_button(__('Update Business Name Transaction'), function () {
                frm.call("update_to_transaction").then(r=>{
                    
                })
            },"Actions")
        }
        frm.set_query("default_temporary_opening_account", function() {
            return {
                filters: [
                     ["is_group","=",0],
                    ["account_type","=","Temporary"]
                ]
            }
        });
        frm.set_query("default_cash_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_change_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_bank_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_pos_difference_amount_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_cash_transaction_expense_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_income_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_receivable_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_sale_discount_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_sale_cash_coupon_claim_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_tip_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_credit_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_purchase_discount_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("income_head_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("expense_head_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_inventory_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("stock_adjustment_account", function() {
            return {
                filters: [
                     ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_cost_of_good_sold_account", function() {
            return {
                filters: [
                    ["is_group","=",0]
                ]
            }
        });
        frm.set_query("default_bank_fee_account", function() {
            return {
                filters: [
                    ["is_group","=",0]
                ]
            }
        });
	},
});
