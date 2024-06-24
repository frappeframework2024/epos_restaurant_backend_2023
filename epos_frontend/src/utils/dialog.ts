import { createPromiseDialog } from "vue-promise-dialogs"
import ComPopup from '@/views/ComPopup.vue';
import ComPopup2 from '@/views/ComPopup2.vue';
import ComPrintPreview from '@/components/ComPrintPreview.vue'
import ComSaleDetail from '@/views/receipt_list/components/ComSaleDetail.vue';
import CustomerDetail from '@/views/customer/CustomerDetail.vue';
import ComConfirm from '@/components/ComConfirm.vue';
import ComAuthorize from '@/components/ComAuthorize.vue';
import ComNote from '@/components/ComNote.vue';
import ComModelKeyboard from '@/components/form/ComModalKeyboard.vue';
import ComSelectSaleOrder from '@/views/sale/components/ComSelectSaleOrder.vue';
import ComSaleProductNoteModal from '@/views/sale/components/ComSaleProductNoteModal.vue';
import ComAddModifier from '@/views/sale/components/ComAddModifier.vue';
import ComSaleProductComboMenuGroupModal from '@/views/sale/components/combo_menu/ComSaleProductComboMenuGroupModal.vue';
import ComAddCustomer from '@/views/customer/ComAddCustomer.vue';
import ComConfirmBackToTableLayout from '@/views/sale/components/ComConfirmBackToTableLayout.vue';
import ComSearchCustomer from '@/views/sale/components/ComSearchCustomer.vue';
import ComScanCustomerCode from '@/views/sale/components/ComScanCustomerCode.vue';
import ComSaleProductDiscountModal from '@/views/sale/components/ComSaleProductDiscountModal.vue';
import ComPayment from '@/views/sale/components/ComPayment.vue';
import ComPayToRoomModal from '@/views/sale/components/ComPayToRoomModal.vue';
import ComPayToCityLedgerModal from '@/views/sale/components/ComPayToCityLedgerModal.vue';
import ComPayToDeskFolioModal from '@/views/sale/components/ComPayToDeskFolioModal.vue';
import ComKeypadWithNote from '@/components/form/ComKeypadWithNote.vue';
import ComViewBillModal from '@/views/sale/components/ComViewBillModal.vue';
import ComSmallViewSaleProductListModal from '@/views/sale/components/mobile_screen/ComSmallViewSaleProductListModal.vue';
import ComSmallCurrencyPrefineModel from '@/views/sale/components/mobile_screen/ComSmallCurrencyPrefineModel.vue';
import ComChangeTable from '@/views/sale/components/ComChangeTable.vue';
import ComChangePriceRuleModal from '@/views/sale/components/ComChangePriceRuleModal.vue';
import ComChangePOSMenuModal from '@/views/sale/components/ComChangePOSMenuModal.vue';
import ComSearchSaleModal from '@/views/sale/components/ComSearchSaleModal.vue'
import ComChangeSaleTypeModal from '@/views/sale/components/ComChangeSaleTypeModal.vue'
import ComAddCashDrawerModal from '@/views/cash_drawer/components/ComAddCashDrawerModal.vue'
import ComChangeTableSelectSaleOrder from '@/views/sale/components/ComChangeTableSelectSaleOrder.vue'
import ComPendingSaleList from '@/views/sale/ComPendingSaleList.vue'
import ComPOSReservationList from '@/views/sale/ComPOSReservationList.vue'
import ComPOSReservationCalendarDialog from '@/views/sale/ComPOSReservationDetailDialog.vue'
import ComInputNumber from '@/components/ComInputNumber.vue'
import ComShortcutKeyHelp from '@/components/ComShortcutKeyHelp.vue'
import ComAddCommission from '@/views/sale/components/ComAddCommissionModal.vue'
import ComSaleReferenceNumberModal from '@/views/sale/components/ComSaleReferenceNumberModal.vue'
import ComPrintWifiPassword from '@/components/ComPrintWifiPasswordModal.vue'
import ComSwitchPosProfile from '@/components/ComSwitchPosProfile.vue'
import ComViewHappyHourPromotionModal from '@/views/sale/components/happy_hour_promotion/ComViewHappyHourPromotionModal.vue'
import ComSelectDateTime from '@/views/sale/components/ComSelectDateTime.vue'
import ComSetStopTimerModal from '@/views/sale/components/ComSetStopTimerModal.vue'

import ComChangeShiftName from "@/views/shift/components/ComSelectShiftName.vue"
import ComSplitBill from "@/views/sale/components/ComSplitBill.vue"
import ComChangeTaxSettingModal from "@/views/sale/components/ComChangeTaxSettingModal.vue"
import ComSelectEmployeeModal from "@/views/sale/employee/ComSelectEmployeeModal.vue"
import ComAddVoucherTopUp from "@/views/voucher_top_up/ComAddTopUp.vue"
import ComVoucherTopUpDetail from "@/views/voucher_top_up/ComVoucherTopUpDetail.vue"
import ComVoucherTopUpAddPayment from "@/views/voucher_top_up/ComVoucherTopUpAddPayment.vue"
import ComSearchProduct from "@/views/sale/components/retail_ui/ComSearchProduct.vue"
import ComResendDialog from "@/views/sale/components/ComResendDialog.vue";
import ComSelectGoogleImageDialog from "@/views/sale/components/ComSelectGoogleImageModal.vue";
import ComRedeemParkItemDialog from "@/views/sale/components/ComRedeemParkItemDialog.vue";
import ComEmptyStockProductDialog from "@/views/sale/components/ComEmptyStockProductDialog.vue";
import ComMoveItemModal from "@/views/sale/components/ComMoveItemModal.vue";
import ComMoveItemChangeTable from "@/views/sale/components/ComMoveItemChangeTable.vue";
import ComEditPOSMenu from "@/views/setting/ComEditPOSMenu.vue";
import ComMoveItemSelectOrder from "@/views/sale/components/ComMoveItemSelectOrder.vue";
import ComUnpaidBillList from "@/views/credit_balance/UnpaidBillDialog.vue";

interface params {
    doctype?: String,
    name?: String,
    text?: String,
    title?: String,
    type?: String,
    report?: String,
    value?: String,
    print: {
        type: Boolean,
        default: 0
    },
    data: Object,//use in comSelectSaleOrder
    table: Object, //use in comSelectSaleOrder
    permissionCode: String
}

export const comPopupDialog = createPromiseDialog<params, object>(ComPopup);
export const comPopup2Dialog = createPromiseDialog<params, object>(ComPopup2);
export const saleDetailDialog = createPromiseDialog<params, object>(ComSaleDetail);
export const printPreviewDialog = createPromiseDialog<params, object>(ComPrintPreview);
export const confirm = createPromiseDialog<params, object>(ComConfirm);
export const confirmDialog = createPromiseDialog<params, object>(ComConfirm);
export const keyboardDialog = createPromiseDialog<params, object>(ComModelKeyboard);
export const selectSaleOrderDialog = createPromiseDialog<params, object>(ComSelectSaleOrder);
export const addModifierDialog = createPromiseDialog<params, object>(ComAddModifier);
export const customerDetailDialog = createPromiseDialog<params, object>(CustomerDetail);
export const addCustomerDialog = createPromiseDialog<params, object>(ComAddCustomer);
export const confirmBackToTableLayout = createPromiseDialog<params, object>(ComConfirmBackToTableLayout);
export const searchCustomerDialog = createPromiseDialog<params, object>(ComSearchCustomer);
export const saleProductNoteModalDialog = createPromiseDialog<params, object>(ComSaleProductNoteModal);
export const scanCustomerCodeDialog = createPromiseDialog<params, object>(ComScanCustomerCode);
export const authorizeDialog = createPromiseDialog<params, object>(ComAuthorize);
export const noteDialog = createPromiseDialog<params, object>(ComNote);
export const saleProductDiscountDialog = createPromiseDialog<params, object>(ComSaleProductDiscountModal);
export const paymentDialog = createPromiseDialog<params, object>(ComPayment);
export const payToRoomDialog = createPromiseDialog<params, object>(ComPayToRoomModal);
export const payToCityLedgerDialog = createPromiseDialog<params, object>(ComPayToCityLedgerModal);
export const payDeskfolioDialog = createPromiseDialog<params, object>(ComPayToDeskFolioModal);
export const keypadWithNoteDialog = createPromiseDialog<params, object>(ComKeypadWithNote);
export const viewBillModelModel = createPromiseDialog<params, object>(ComViewBillModal);
export const smallViewSaleProductListModal = createPromiseDialog<params, object>(ComSmallViewSaleProductListModal);
export const smallCurrencyPrefineModel = createPromiseDialog<params, object>(ComSmallCurrencyPrefineModel);
export const changeTableDialog = createPromiseDialog<params, object>(ComChangeTable);
export const changePriceRuleDialog = createPromiseDialog<params, object>(ComChangePriceRuleModal);
export const searchSaleDialog = createPromiseDialog<params, object>(ComSearchSaleModal);
export const changeSaleTypeModalDialog = createPromiseDialog<params, object>(ComChangeSaleTypeModal);
export const addCashDrawerModalDialog = createPromiseDialog<params, object>(ComAddCashDrawerModal);
export const changeTableSelectSaleOrderDialog = createPromiseDialog<params, object>(ComChangeTableSelectSaleOrder);
export const changePOSMenuDialog = createPromiseDialog<params, object>(ComChangePOSMenuModal);
export const pendingSaleListDialog = createPromiseDialog<params, object>(ComPendingSaleList);
export const posReservationDialog = createPromiseDialog<params, object>(ComPOSReservationList);
export const inputNumberDialog = createPromiseDialog<params, object>(ComInputNumber);
export const addCommissionDialog = createPromiseDialog<params, object>(ComAddCommission);
export const printWifiPasswordModal = createPromiseDialog<params, object>(ComPrintWifiPassword);
export const SwitchPosProfileModal = createPromiseDialog<params, object>(ComSwitchPosProfile);
export const splitBillDialog = createPromiseDialog<params, object>(ComSplitBill);
export const SaleProductComboMenuGroupModal = createPromiseDialog<params, object>(ComSaleProductComboMenuGroupModal);
export const changeTaxSettingModal = createPromiseDialog<params, object>(ComChangeTaxSettingModal);
export const ComSaleReferenceNumberDialog = createPromiseDialog<params, object>(ComSaleReferenceNumberModal);
export const posReservationCalendarDialog = createPromiseDialog<params, object>(ComPOSReservationCalendarDialog);
export const viewHappyHourPromotionModal = createPromiseDialog<params, object>(ComViewHappyHourPromotionModal);
export const ShortCutKeyHelpDialog = createPromiseDialog<params, object>(ComShortcutKeyHelp);
export const selectEmployeeDialog = createPromiseDialog<params, object>(ComSelectEmployeeModal);
export const SelectDateTime = createPromiseDialog<params, object>(ComSelectDateTime);
export const stopTimerModal = createPromiseDialog<params, object>(ComSetStopTimerModal);
export const ChangeShiftNameModal = createPromiseDialog<params, object>(ComChangeShiftName);
export const AddVoucherTopUpDialog = createPromiseDialog<params, object>(ComAddVoucherTopUp);
export const VoucherTopUpDetailDialog = createPromiseDialog<params, object>(ComVoucherTopUpDetail);
export const VoucherTopUpAddPaymentDialog = createPromiseDialog<params, object>(ComVoucherTopUpAddPayment);
export const SearchProductDialog = createPromiseDialog<params, object>(ComSearchProduct);
export const ResendDialog = createPromiseDialog<params, object>(ComResendDialog);
export const SelectGoogleImageDialog = createPromiseDialog<params, object>(ComSelectGoogleImageDialog);
export const RedeemParkItemDialog = createPromiseDialog<params, object>(ComRedeemParkItemDialog);
export const EmptyStockProductDialog = createPromiseDialog<params, object>(ComEmptyStockProductDialog);
export const MoveItemModal = createPromiseDialog<params, object>(ComMoveItemModal);
export const MoveItemChangeTable = createPromiseDialog<params, object>(ComMoveItemChangeTable);
export const EditPOSMenuDialog = createPromiseDialog<params, object>(ComEditPOSMenu);
export const MoveItemSelectOrderDialog = createPromiseDialog<params, object>(ComMoveItemSelectOrder);
export const UnpaidBillListDialog = createPromiseDialog<params, object>(ComUnpaidBillList);
