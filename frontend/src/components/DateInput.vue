<script setup lang="ts">
import { ref, watch } from "vue";
import { fromDisplay, toDisplay } from "@/utils/date";

const props = withDefaults(
  defineProps<{
    modelValue: string;
    required?: boolean;
  }>(),
  { required: false },
);

const emit = defineEmits<{ "update:modelValue": [value: string] }>();

const display = ref(toDisplay(props.modelValue));
const picker = ref<HTMLInputElement | null>(null);

watch(
  () => props.modelValue,
  (v) => {
    display.value = toDisplay(v);
  },
);

function formatTyping(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 8);
  const parts: string[] = [];
  if (digits.length > 0) parts.push(digits.slice(0, 2));
  if (digits.length > 2) parts.push(digits.slice(2, 4));
  if (digits.length > 4) parts.push(digits.slice(4, 8));
  return parts.join("/");
}

function onDisplayInput(e: Event) {
  const el = e.target as HTMLInputElement;
  const caret = el.selectionStart ?? el.value.length;
  const digitsBefore = el.value.slice(0, caret).replace(/\D/g, "").length;
  el.value = formatTyping(el.value);
  const newCaret = Math.min(digitsBefore + Math.floor((digitsBefore - 1) / 2) + 1, el.value.length);
  el.setSelectionRange(newCaret, newCaret);
  display.value = el.value;
}

function onDisplayBlur(e: Event) {
  const el = e.target as HTMLInputElement;
  const iso = fromDisplay(el.value);
  if (iso) {
    display.value = toDisplay(iso);
    el.value = display.value;
    emit("update:modelValue", iso);
  } else if (el.value.trim() === "") {
    emit("update:modelValue", "");
  } else {
    display.value = toDisplay(props.modelValue);
    el.value = display.value;
  }
}

function onNativeInput(e: Event) {
  const el = e.target as HTMLInputElement;
  const iso = el.value;
  emit("update:modelValue", iso);
  display.value = toDisplay(iso);
  if (picker.value) picker.value.value = "";
}

function openPicker() {
  const el = picker.value;
  if (!el) return;
  if (typeof el.showPicker === "function") {
    el.showPicker();
  } else {
    el.focus();
    el.click();
  }
}
</script>
<template>
  <div class="relative">
    <input
      type="text"
      inputmode="numeric"
      placeholder="dd/mm/yyyy"
      class="w-full rounded-xl border border-[var(--line)] px-3 py-2 text-sm"
      :value="display"
      :required="required"
      @input="onDisplayInput"
      @blur="onDisplayBlur"
    />
    <button
      type="button"
      tabindex="-1"
      aria-label="Open calendar"
      class="absolute inset-y-0 right-0 flex w-9 cursor-pointer items-center justify-center text-[var(--muted)] focus:outline-none"
      @click="openPicker"
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <rect x="3" y="4" width="18" height="18" rx="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    </button>
    <input
      ref="picker"
      type="date"
      class="pointer-events-none absolute bottom-0 right-1 h-0 w-0 overflow-hidden opacity-0"
      tabindex="-1"
      :value="modelValue"
      @input="onNativeInput"
    />
  </div>
</template>
