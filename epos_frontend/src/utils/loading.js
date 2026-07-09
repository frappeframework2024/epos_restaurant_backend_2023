import { ref } from 'vue'

export const loadingVisible = ref(false)
export const loadingMessage = ref('Loading...')

let counter = 0

export function showLoading(message = 'Loading...') {
    counter++

    loadingMessage.value = message
    loadingVisible.value = true

    let closed = false

    return {
        close() {
            if (closed) return

            closed = true
            counter--

            if (counter <= 0) {
                counter = 0
                loadingVisible.value = false
            }
        }
    }
}