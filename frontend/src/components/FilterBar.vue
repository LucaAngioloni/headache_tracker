<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import DateInput from "@/components/DateInput.vue";
import type { EpisodeFilters, Medicine, Trigger } from "@/types";

const props = defineProps<{
  modelValue: EpisodeFilters;
  medicines: Medicine[];
  triggers: Trigger[];
}>();

const emit = defineEmits<{
  "update:modelValue": [value: EpisodeFilters];
  apply: [];
  reset: [];
}>();

const { t } = useI18n();

const open = ref(false);

const local = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

function patch(partial: Partial<EpisodeFilters>) {
  emit("update:modelValue", { ...props.modelValue, ...partial });
}
</script>

<template>
  <form
    class="rounded-2xl border border-[var(--line)] bg-[var(--card)]"
    @submit.prevent="emit('apply')"
  >
    <button
      type="button"
      class="flex w-full items-center justify-between p-3 text-left"
      @click="open = !open"
    >
      <span class="text-sm font-medium">{{ t("common.filters") }}</span>
      <span
        class="text-sm text-[var(--muted)] transition-transform duration-200"
        :class="{ 'rotate-90': open }"
        aria-hidden="true"
        >›</span
      >
    </button>
    <div v-if="open" class="grid gap-3 px-3 pb-3">
      <div class="grid grid-cols-2 gap-2">
        <label class="grid gap-1 text-xs text-[var(--muted)]">
          {{ t("common.from") }}
          <DateInput
            class="rounded-lg border border-[var(--line)] px-2 py-2 text-sm text-[var(--ink)]"
            :model-value="local.date_after || ''"
            @update:model-value="patch({ date_after: $event })"
          />
        </label>
        <label class="grid gap-1 text-xs text-[var(--muted)]">
          {{ t("common.to") }}
          <DateInput
            class="rounded-lg border border-[var(--line)] px-2 py-2 text-sm text-[var(--ink)]"
            :model-value="local.date_before || ''"
            @update:model-value="patch({ date_before: $event })"
          />
        </label>
      </div>
      <div class="grid grid-cols-2 gap-2">
        <label class="grid gap-1 text-xs text-[var(--muted)]">
          {{ t("episode.medicine") }}
          <select
            class="rounded-lg border border-[var(--line)] px-2 py-2 text-sm text-[var(--ink)]"
            :value="local.medicine ?? ''"
            @change="
              patch({
                medicine: ($event.target as HTMLSelectElement).value
                  ? Number(($event.target as HTMLSelectElement).value)
                  : '',
              })
            "
          >
            <option value="">—</option>
            <option v-for="m in medicines" :key="m.id" :value="m.id">
              {{ m.name }}
            </option>
          </select>
        </label>
        <label class="grid gap-1 text-xs text-[var(--muted)]">
          {{ t("episode.triggers") }}
          <select
            class="rounded-lg border border-[var(--line)] px-2 py-2 text-sm text-[var(--ink)]"
            :value="local.trigger ?? ''"
            @change="
              patch({
                trigger: ($event.target as HTMLSelectElement).value
                  ? Number(($event.target as HTMLSelectElement).value)
                  : '',
              })
            "
          >
            <option value="">—</option>
            <option v-for="tr in triggers" :key="tr.id" :value="tr.id">
              {{ tr.name }}
            </option>
          </select>
        </label>
      </div>
      <div class="grid grid-cols-2 gap-2">
        <label class="grid gap-1 text-xs text-[var(--muted)]">
          {{ t("episode.pain") }} min
          <input
            type="number"
            min="1"
            max="10"
            class="rounded-lg border border-[var(--line)] px-2 py-2 text-sm"
            :value="local.pain_min ?? ''"
            @input="
              patch({
                pain_min: ($event.target as HTMLInputElement).value
                  ? Number(($event.target as HTMLInputElement).value)
                  : '',
              })
            "
          />
        </label>
        <label class="grid gap-1 text-xs text-[var(--muted)]">
          {{ t("episode.pain") }} max
          <input
            type="number"
            min="1"
            max="10"
            class="rounded-lg border border-[var(--line)] px-2 py-2 text-sm"
            :value="local.pain_max ?? ''"
            @input="
              patch({
                pain_max: ($event.target as HTMLInputElement).value
                  ? Number(($event.target as HTMLInputElement).value)
                  : '',
              })
            "
          />
        </label>
      </div>
      <label class="grid gap-1 text-xs text-[var(--muted)]">
        {{ t("common.search") }}
        <input
          type="search"
          class="rounded-lg border border-[var(--line)] px-2 py-2 text-sm"
          :value="local.search || ''"
          @input="patch({ search: ($event.target as HTMLInputElement).value })"
        />
      </label>
      <div class="flex gap-2">
        <button type="submit" class="rounded-xl bg-[var(--accent)] px-3 py-2 text-sm text-white">
          {{ t("common.apply") }}
        </button>
        <button
          type="button"
          class="rounded-xl border border-[var(--line)] px-3 py-2 text-sm"
          @click="emit('reset')"
        >
          {{ t("common.reset") }}
        </button>
      </div>
    </div>
  </form>
</template>
