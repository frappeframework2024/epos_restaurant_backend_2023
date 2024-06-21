<iframe id="iframe-page-container" src="/app/business-source" />
<script>
import { onMounted } from "@/plugin"
onMounted(() => {
    var iframe = root_element.querySelector('#iframe-page-container');
    alert( window.screen.height)
    iframe.addEventListener('load', function () {
        var observer = new MutationObserver(function (mutationsList) {
            iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';

        });

        // Observe changes to the body of the document inside the iframe
        observer.observe(iframe.contentWindow.document.body, { attributes: true, childList: true, subtree: true });
    });
})
</script>
