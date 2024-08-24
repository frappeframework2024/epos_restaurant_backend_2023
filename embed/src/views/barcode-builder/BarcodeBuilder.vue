<template>
  <!-- Barcode Generator -->

  <div class="grid p-3">
    <div
      class="flex-1 w-full flex align-items-center justify-content-center m-3"
    >
      <Fieldset class="w-full" legend="Barcode">
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

    <div class="flex-1 w-full flex justify-content-center m-3">
      <Fieldset class="w-full" legend="Previews">
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
            <Slider
              v-model="setting.height"
              :min="100"
              :max="400"
              class="w-3"
            />
          </div>
          <div class="control-group">
            <label>Width: {{ setting.width }} px</label>
            <!-- <InputText disabled v-model.number="setting.width" class="w-3" /> -->
            <Slider v-model="setting.width" :min="200" :max="400" class="w-3" />
          </div>
        </div>

        <div class="card">
          <div
            class="barcode-container flex justify-content-center align-items-center"
          >
            <div
              class="bar_code_content"
              :style="{
                backgroundColor: setting.backgroundColor,
                fontSize: setting.fontSize + 'px',
                fontFamily: setting.fontFamily.value,
                transform: 'rotate(' + setting.rotate.value + 'deg)',
                height: setting.height + 50 + 'px',
                width: setting.width + 50 + 'px',
              }"
              style="
                position: relative;
                padding-top: 2rem !important;
                display: flex;
                justify-content: center;
              "
            >
              <div
                :style="boxStyle"
                @mousedown="(event) => startDrag(event, 'box')"
              >
                <span :style="textStyle">
                  {{ setting.name }}
                </span>
              </div>
              <div
                :style="boxPriceStyle"
                @mousedown="(event) => startDrag(event, 'boxPrice')"
              >
                <span :style="textStyle">
                  {{ setting.price }}
                </span>
              </div>
              <img
                :style="{
                  height: setting.height + 'px',
                  width: setting.width + 'px',
                }"
                :src="url"
                alt="Barcode"
              />
            </div>
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
  top: "10px",
  left: "10px",
  cursor: "grab",
});

const boxPriceStyle = ref({
  position: "absolute",
  top: "10px",
  right: "10px",
  cursor: "grab",
});

let startX = 0;
let startY = 0;
let offsetX = 0;
let offsetY = 0;

let draggingBox = null;

function startDrag(event, box) {
  draggingBox = box;

  if (box === "box") {
    boxStyle.value.cursor = "grabbing";
    offsetX = parseInt(boxStyle.value.left, 10);
    offsetY = parseInt(boxStyle.value.top, 10);
  } else if (box === "boxPrice") {
    boxPriceStyle.value.cursor = "grabbing";
    offsetX = parseInt(boxPriceStyle.value.right, 10); // Use correct right offset
    offsetY = parseInt(boxPriceStyle.value.top, 10); // Use correct top offset
  }

  startX = event.clientX;
  startY = event.clientY;

  document.addEventListener("mousemove", onDrag);
  document.addEventListener("mouseup", stopDrag);
}

function onDrag(event) {
  const dx = event.clientX - startX;
  const dy = event.clientY - startY;

  if (draggingBox === "box") {
    boxStyle.value.left = `${offsetX + dx}px`;
    boxStyle.value.top = `${offsetY + dy}px`;
  } else if (draggingBox === "boxPrice") {
    boxPriceStyle.value.right = `${offsetX - dx}px`; // Correct calculation for right positioning
    boxPriceStyle.value.top = `${offsetY + dy}px`;
  }
}

function stopDrag() {
  if (draggingBox === "box") {
    boxStyle.value.cursor = "grab";
  } else if (draggingBox === "boxPrice") {
    boxPriceStyle.value.cursor = "grab";
  }

  draggingBox = null;

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
  const divContents = document.querySelector(".bar_code_content").outerHTML;
  const a = window.open("", "", `height=500px, width=500px`);
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
  padding: 1rem;
  background-color: #ffffff;
  border-radius: 0.5rem;
  transition: box-shadow 0.3s ease;
  width: 500px;
  overflow: hidden;
  height: 500px;
}

.barcode-container:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
.bar_code_content {
  height: 100%;
  width: 100%;
  border: 2px dashed #7ea0c4;
}
</style>
