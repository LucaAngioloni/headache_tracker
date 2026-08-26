<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { setLocale } from "@/i18n";

defineProps<{ compact?: boolean }>();

const { locale, t } = useI18n();

function change(value: string) {
  if (value === "it" || value === "en") setLocale(value);
}
</script>

<template>
  <label
    class="flex items-center gap-2 text-sm text-[var(--muted)]"
    :title="t('common.language')"
  >
    <span v-if="!compact">{{ t("common.language") }}</span>
    <select
      class="rounded-lg border border-[var(--line)] bg-white px-2 py-1 text-[var(--ink)]"
      :aria-label="t('common.language')"
      :value="locale"
      @change="change(($event.target as HTMLSelectElement).value)"
    >
      <option value="it">IT</option>
      <option value="en">EN</option>
    </select>
  </label>
</template>
