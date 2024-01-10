import Enumerable from 'linq'
import { keyboardDialog, createResource } from "@/plugin"
import { createToaster } from "@meforma/vue-toaster";
import moment from '@/utils/moment.js';

const toaster = createToaster({ position: "top" });

export default class POSLicense {
    constructor() { 
        this.invalid_license = false;
        this.is_unlimit_license = false;
        this.is_trail_license = false;
        this.export_date = moment(new Date()).format('yyyy-MM-DD HH:mm:ss')
    }
}