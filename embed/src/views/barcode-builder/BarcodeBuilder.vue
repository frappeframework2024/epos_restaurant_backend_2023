<template>
  <div class="flex align-items-center justify-content-center p-3">
    <div
      style="border: 1px solid red"
      class="flex-1 flex align-items-center justify-content-center m-3"
    >
      Lorem ipsum dolor sit amet
    </div>
    <div
      style="border: 1px solid red"
      class="flex-1 flex align-items-center justify-content-center m-3"
    >
      Lorem ipsum dolor sit amet
    </div>
  </div>

  <!-- Barcode Generator -->

  <div class="flex align-items-center justify-content-center p-3">
    <div class="flex-1 flex align-items-center justify-content-center m-3">
      <Fieldset legend="Barcode">
        <label for="barcodeType">Barcode Type : </label>
        <Dropdown
          v-model="setting.barcodeType"
          :options="barcodeTypes"
          optionLabel="label"
          inputId="barcodeType"
          class="input-dropdown mb-2"
          placeholder="Select a barcode type"
        />

        <div class="control-group">
          <label for="price">Price($USD):</label>
          <InputNumber
            v-model="setting.price"
            inputId="price"
            :min="0"
            :max="100"
            class="w-2"
          />

          <label for="barcode">Barcode:</label>
          <InputText
            v-model="setting.code"
            inputId="barcode"
            placeholder="Enter barcode"
            class="w-2"
          />

          <label>Font Type:</label>
          <Dropdown
            v-model="setting.fontFamily"
            :options="fontFamily"
            optionLabel="label"
            placeholder="Select a Font"
            class="input-dropdown w-2"
          />

          <label> Rotate: </label>
          <Dropdown
            v-model="setting.rotate"
            :options="rotate"
            optionLabel="label"
            class="input-dropdown w-2"
          />

          <label>FontSize:</label>
          <InputNumber disabled v-model="setting.fontSize" class="w-2" />
          <Slider v-model="setting.fontSize" :max="36" class="my-2, w-2" />
        </div>
      </Fieldset>
    </div>

    <div class="flex-1 flex align-items-center justify-content-center m-3">
      <Fieldset legend="Previews">
        <div class="preview-controls">
          <div>
            Bold:
            <input type="checkbox" v-model="isBold" />
          </div>
          <div>
            Italic
            <input type="checkbox" v-model="isItalic" />
          </div>

          <div class="control-group">
            <label>Height:</label>
            <InputText disabled v-model.number="setting.height" class="w-3" />
            <Slider v-model="setting.height" :max="250" class="w-3" />
          </div>
          <div class="control-group">
            <label>Width: {{ setting.width }} px</label>
            <!-- <InputText disabled v-model.number="setting.width" class="w-3" /> -->
            <Slider v-model="setting.width" :max="500" class="w-3" />
          </div>
        </div>

        <div class="card">
          <div
            class="barcode-container"
            :style="{
              height: setting.height + 'px',
              width: setting.width + 'px',
              backgroundColor: setting.backgroundColor,
              fontSize: setting.fontSize + 'px',
              fontFamily: setting.fontFamily.value,
              transform: 'rotate(' + setting.rotate.value + 'deg)',
            }"
            style="
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              position: relative;
              overflow: hidden;
              padding: 1rem;
            "
          >
            <div :style="boxStyle" @mousedown="startDrag">
              <span :style="textStyle">
                {{ setting.name }}
              </span>
            </div>

            <img
              style="max-width: 100%; max-height: 100%"
              :src="url"
              alt="Barcode"
            />
          </div>
        </div>
        <Button label="Print" icon="pi pi-print" @click="onPrint" />
      </Fieldset>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import Fieldset from "primevue/fieldset";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Slider from "primevue/slider";
import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import RadioButton from "primevue/radiobutton";

const isBold = ref(false);
const isItalic = ref(false);

const textStyle = computed(() => ({
  fontWeight: isBold.value ? "bold" : "normal",
  fontStyle: isItalic.value ? "italic" : "normal",
}));

const boxStyle = ref({
  position: "absolute",
  top: "100px",
  left: "100px",
  cursor: "grab",
});

let startX = 0;
let startY = 0;
let offsetX = 0;
let offsetY = 0;

function startDrag(event) {
  boxStyle.value.cursor = "grabbing";
  startX = event.clientX;
  startY = event.clientY;
  offsetX = parseInt(boxStyle.value.left, 10);
  offsetY = parseInt(boxStyle.value.top, 10);

  document.addEventListener("mousemove", onDrag);
  document.addEventListener("mouseup", stopDrag);
}

function onDrag(event) {
  const dx = event.clientX - startX;
  const dy = event.clientY - startY;

  boxStyle.value.left = `${offsetX + dx}px`;
  boxStyle.value.top = `${offsetY + dy}px`;
}

function stopDrag() {
  boxStyle.value.cursor = "grab";
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", stopDrag);
}

const barcodeTypes = ref([
  { label: "Code 128", code: "128" },
  { label: "Code 39", code: "39" },
  { label: "QR Code", code: "qr" },
]);

const fontFamily = ref([
  { label: "Arial", value: "Arial, sans-serif" },
  { label: "Courier New", value: "'Courier New', monospace" },
  { label: "Georgia", value: "Georgia, serif" },
  { label: "Verdana", value: "Verdana, sans-serif" },
]);

const rotate = ref([
  { label: "0°", value: 0 },
  { label: "90°", value: 90 },
  { label: "180°", value: 180 },
  { label: "270°", value: 270 },
]);

const setting = ref({
  height: 100,
  width: 200,
  backgroundColor: "white",
  name: "Product",
  code: "IVC12235",
  price: 22.5,
  fontSize: 16,
  barcodeType: barcodeTypes.value[0],
  fontFamily: fontFamily.value[0],
  rotate: rotate.value[0],
});

const url = computed(() => {
  return `https://barcodeapi.org/api/${setting.value.barcodeType.code}/${setting.value.code}`;
});

function onPrint() {
  const divContents = document.querySelector(".barcode-container").outerHTML;
  const a = window.open(
    "",
    "",
    `height=${setting.value.height}px, width=${setting.value.width}px`
  );
  a.document.write("<html>");
  a.document.write("<body>");
  a.document.write(divContents);
  a.document.write("</body></html>");
  setTimeout(function () {
    a.document.close();
    a.print();
  }, 1000);
}
</script>

<style scoped>
.preview-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.control-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.barcode-container {
  border: 2px dashed #7ea0c4;
  padding: 1rem;
  background-color: #ffffff;
  border-radius: 0.5rem;
  transition: box-shadow 0.3s ease;
}

.barcode-container:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>
