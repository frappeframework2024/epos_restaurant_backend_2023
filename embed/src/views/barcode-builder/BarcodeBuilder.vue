<template>
  <div class="p-4">
    <label for="cmInput" class="block mb-2">Enter value in centimeters:</label>
    <InputText
      id="cmInput"
      type="number"
      v-model="centimeters"
      class="border rounded p-2 mb-4 w-full"
      placeholder="Enter centimeters"
    />
    <p>{{ centimeters }} cm is approximately {{ pixels.toFixed(2) }} pixels</p>
  </div>
  <!-- Barcode Generator -->
  <h2 class="flex justify-content-center align-items-center">
    Barcode Generator
  </h2>

  <div class="grid p-3">
    <div
      class="flex-1 w-full flex align-items-center justify-content-center m-3"
    >
      <Fieldset class="w-full" legend="Barcode">
        <div class="grid formgrid p-fluid">
          <div class="field col-12 md:col-6">
            <label for="barcodeType">Barcode Type :</label>
            <Dropdown
              v-model="setting.barcodeType"
              :options="barcodeTypes"
              optionLabel="label"
              inputId="barcodeType"
              class="input-dropdown mx-2 w-8"
              placeholder="Select a barcode type"
            />
          </div>

          <div class="field col-12 md:col-6">
            <label for="price">Price($USD) :</label>
            <InputNumber
              v-model="setting.price"
              inputId="price"
              :min="0"
              :max="100"
              class="input-dropdown mx-2 w-8"
            />
          </div>

          <div class="field col-12 md:col-6">
            <label for="barcode">Barcode:</label>
            <InputText
              v-model="setting.code"
              inputId="barcode"
              placeholder="Enter barcode"
              class="input-dropdown mx-2 w-auto"
            />
          </div>

          <div class="field col-12 md:col-6">
            <label for="fontFamily">Font Type:</label>
            <Dropdown
              v-model="setting.fontFamily"
              :options="fontFamily"
              optionLabel="label"
              placeholder="Select a Font"
              class="input-dropdown mx-2 w-auto"
            />
          </div>

          <div class="field col-12 md:col-6">
            <label for="rotate">Rotate:</label>
            <Dropdown
              v-model="setting.rotate"
              :options="rotate"
              optionLabel="label"
              class="input-dropdown mx-2 w-auto"
            />
          </div>

          <div class="field col-12 md:col-6">
            <label for="fontSize">Font Size:</label>
            <InputNumber
              disabled
              v-model="setting.fontSize"
              inputId="fontSize"
              class="input-dropdown mx-2 w-8"
            />
            <Slider v-model="setting.fontSize" :max="36" class="my-2 w-full" />
          </div>

          <div class="preview-controls">
            <label>
              <input type="checkbox" v-model="setting.include_text" />
              Include Text
            </label>

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
              <InputNumber v-model="setting.width" :max="400" fluid />
              <label>Width: {{ setting.width }} px</label>
              <!-- <InputText disabled v-model.number="setting.width" class="w-3" /> -->
              <Slider
                v-model="setting.width"
                :min="200"
                :max="400"
                class="w-3"
              />
            </div>
          </div>
        </div>
      </Fieldset>
    </div>

    <div class="flex-1 w-full flex justify-content-center m-3">
      <Fieldset class="w-full" legend="Previews">
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

        <label for="text_align_x">Text Alignment X:</label>
        <Dropdown
          v-model="setting.text_align_x"
          :options="text_align_x"
          optionLabel="label"
          inputId="text_align_x"
          class="input-dropdown mx-2 w-8"
          placeholder="Select a align"
        />

        <label for="text_align_y">Text Alignment Y :</label>
        <Dropdown
          v-model="setting.text_align_y"
          :options="text_align_y"
          optionLabel="label"
          inputId="text_align_y"
          class="input-dropdown mx-2 w-8"
          placeholder="Select a align"
        />
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

const centimeters = ref(0);

function cmToPx(centimeters, ppi = 96) {
  return (centimeters / 2.54) * ppi;
}
const pixels = computed(() => cmToPx(centimeters.value));

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
  { label: "Code 128", value: "code128" },
  { label: "Code 39", value: "39" },
  { label: "QR Code", value: "qrcode" },
]);

const fontFamily = ref([
  { label: "Arial", value: "Arial, sans-serif" },
  { label: "Courier New", value: "'Courier New', monospace" },
  { label: "Lucida Sans", value: "'Lucida Sans', sans-serif" },
  { label: "Verdana", value: "Verdana, sans-serif" },
]);

const rotate = ref([
  { label: "0°", value: 0 },
  { label: "90°", value: 90 },
  { label: "180°", value: 180 },
  { label: "270°", value: 270 },
]);

const text_align_x = ref([
  { label: "Left", value: "left" },
  { label: "Right", value: "right" },
  { label: "Center", value: "center" },
  { label: "Off-Right", value: "offright" },
  { label: "Off-Left", value: "offleft" },
  { label: "Justify", value: "justify" },
]);

const text_align_y = ref([
  { label: "Center", value: "center" },
  { label: "Below", value: "below" },
  { label: "Above", value: "above" },
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
  include_text: false,
  text_align_x: text_align_x.value[2],
  text_align_y: text_align_y.value[0],
});

const url = computed(() => {
  const encodedCode = encodeURIComponent(setting.value.code);
  const includeTextParam = setting.value.include_text ? "&includetext" : "";
  return `http://bwipjs-api.metafloor.com/?bcid=${setting.value.barcodeType.value}&text=${encodedCode}&rotate${includeTextParam}&textxalign=${setting.value.text_align_x.value}&textyalign=${setting.value.text_align_y.value}`;
});

function onPrint() {
  const divContents = document.querySelector(".bar_code_content").outerHTML;
  const a = window.open("", "", `height=1000px, width=1000px`);
  a.document.write("<html>");
  a.document.write(
    "<body style='display:flex; justify-content:center; align-items:center'>"
  );
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
