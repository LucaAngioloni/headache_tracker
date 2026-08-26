<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/api/client";
import DateInput from "@/components/DateInput.vue";
import type { Episode, EpisodeWrite, Medicine, Paginated, Trigger } from "@/types";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const medicines = ref<Medicine[]>([]);
const triggers = ref<Trigger[]>([]);
const occurredOn = ref(new Date().toISOString().slice(0, 10));
const pain = ref<number | null>(null);
const notes = ref("");
const selectedTriggers = ref<number[]>([]);
const triggerQuery = ref("");
const showTriggerSuggestions = ref(false);
const doses = ref<EpisodeWrite["doses"]>([{ medicine: 0, quantity: 1, note: "" }]);
const error = ref("");
const loading = ref(false);
const editId = computed(() => (route.params.id ? Number(route.params.id) : null));

async function loadCatalogs() {
  const [m, tr] = await Promise.all([
    api.get<Paginated<Medicine>>("/medicines/", { params: { page_size: 200 } }),
    api.get<Paginated<Trigger>>("/triggers/", { params: { page_size: 200 } }),
  ]);
  medicines.value = m.data.results;
  triggers.value = tr.data.results;
  if (doses.value[0] && !doses.value[0].medicine && medicines.value[0]) {
    doses.value[0].medicine = medicines.value[0].id;
  }
}

async function loadEpisode() {
  if (!editId.value) {
    if (typeof route.query.date === "string") occurredOn.value = route.query.date;
    return;
  }
  const { data } = await api.get<Episode>(`/episodes/${editId.value}/`);
  occurredOn.value = data.occurred_on;
  pain.value = data.pain_level;
  notes.value = data.notes;
  selectedTriggers.value = data.triggers.map((x) => x.id);
  doses.value = data.doses.map((d) => ({
    medicine: d.medicine,
    quantity: d.quantity,
    note: d.note,
    sort_order: d.sort_order,
  }));
}

function addDose() {
  doses.value.push({
    medicine: medicines.value[0]?.id || 0,
    quantity: 1,
    note: "",
  });
}

function removeDose(index: number) {
  doses.value.splice(index, 1);
}

const triggerSuggestions = computed(() => {
  const q = triggerQuery.value.trim().toLowerCase();
  return triggers.value.filter(
    (t) => !selectedTriggers.value.includes(t.id) && (!q || t.name.toLowerCase().includes(q)),
  );
});

const selectedTriggerObjects = computed(() =>
  triggers.value.filter((t) => selectedTriggers.value.includes(t.id)),
);

function removeTrigger(id: number) {
  const i = selectedTriggers.value.indexOf(id);
  if (i >= 0) selectedTriggers.value.splice(i, 1);
}

function selectTrigger(id: number) {
  if (!selectedTriggers.value.includes(id)) selectedTriggers.value.push(id);
  triggerQuery.value = "";
}

async function addTriggerFromQuery() {
  const name = triggerQuery.value.trim();
  if (!name) return;
  const existing = triggers.value.find((t) => t.name.toLowerCase() === name.toLowerCase());
  if (existing) {
    selectTrigger(existing.id);
    return;
  }
  const { data } = await api.post<Trigger>("/triggers/", { name });
  triggers.value.push(data);
  selectTrigger(data.id);
}

function onTriggerKeydown(e: KeyboardEvent) {
  if (e.key === "Enter") {
    e.preventDefault();
    void addTriggerFromQuery();
  } else if (e.key === "Backspace" && !triggerQuery.value && selectedTriggers.value.length) {
    selectedTriggers.value.pop();
  }
}

function bumpPain(delta: number) {
  const next = (pain.value ?? 0) + delta;
  if (next < 1) pain.value = null;
  else pain.value = Math.min(10, next);
}

async function submit(stay = false) {
  error.value = "";
  if (!medicines.value.length) {
    error.value = t("episode.needMedicine");
    return;
  }
  const payload: EpisodeWrite = {
    occurred_on: occurredOn.value,
    pain_level: pain.value,
    notes: notes.value,
    trigger_ids: selectedTriggers.value,
    doses: doses.value.filter((d) => d.medicine),
  };
  if (!payload.doses.length) {
    error.value = t("episode.needDose");
    return;
  }
  loading.value = true;
  try {
    if (editId.value) {
      await api.put(`/episodes/${editId.value}/`, payload);
    } else {
      await api.post("/episodes/", payload);
    }
    if (stay) {
      resetForm();
      return;
    }
    await router.push("/episodes");
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  occurredOn.value = new Date().toISOString().slice(0, 10);
  pain.value = null;
  notes.value = "";
  selectedTriggers.value = [];
  triggerQuery.value = "";
  doses.value = [{ medicine: medicines.value[0]?.id || 0, quantity: 1, note: "" }];
  error.value = "";
}

onMounted(async () => {
  await loadCatalogs();
  await loadEpisode();
});
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ editId ? t("episode.edit") : t("episode.new") }}</h1>
    <form class="grid gap-4" @submit.prevent="submit()">
      <label class="grid gap-1 text-sm">
        {{ t("episode.date") }}
        <DateInput v-model="occurredOn" required class="rounded-xl border border-[var(--line)] px-3 py-2" />
      </label>
      <div class="grid gap-1 text-sm">
        <span>{{ t("episode.pain") }}</span>
        <div class="flex items-center gap-3">
          <button type="button" class="h-10 w-10 rounded-full border" @click="bumpPain(-1)">−</button>
          <span class="min-w-10 text-center text-lg font-semibold">{{ pain ?? t("episode.painUnknown") }}</span>
          <button type="button" class="h-10 w-10 rounded-full border" @click="bumpPain(1)">+</button>
        </div>
      </div>
      <div class="grid gap-2">
        <p class="text-sm font-medium">{{ t("episode.triggers") }}</p>
        <div v-if="selectedTriggerObjects.length" class="flex flex-wrap gap-2">
          <span
            v-for="tr in selectedTriggerObjects"
            :key="tr.id"
            class="inline-flex items-center gap-2 rounded-full border border-[var(--accent)] bg-[var(--accent-soft)] px-3 py-1 text-sm"
          >
            {{ tr.name }}
            <button type="button" class="text-[var(--muted)]" :aria-label="`${t('common.delete')} ${tr.name}`" @click="removeTrigger(tr.id)">×</button>
          </span>
        </div>
        <div class="relative">
          <input
            v-model="triggerQuery"
            type="text"
            class="w-full rounded-xl border border-[var(--line)] px-3 py-2 text-sm"
            :placeholder="t('trigger.name')"
            @focus="showTriggerSuggestions = true"
            @blur="showTriggerSuggestions = false"
            @keydown="onTriggerKeydown"
          />
          <ul
            v-if="showTriggerSuggestions && triggerSuggestions.length"
            class="absolute z-10 mt-1 max-h-48 w-full overflow-auto rounded-xl border border-[var(--line)] bg-[var(--card)] py-1 text-sm shadow"
          >
            <li v-for="tr in triggerSuggestions" :key="tr.id">
              <button type="button" class="block w-full px-3 py-1.5 text-left hover:bg-[var(--line)]" @mousedown.prevent @click="selectTrigger(tr.id)">
                {{ tr.name }}
              </button>
            </li>
          </ul>
        </div>
      </div>
      <div class="grid gap-2">
        <p class="text-sm font-medium">{{ t("episode.doses") }}</p>
        <div v-for="(dose, i) in doses" :key="i" class="grid gap-2 rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3">
          <select v-model.number="dose.medicine" class="rounded-xl border border-[var(--line)] px-3 py-2">
            <option v-for="m in medicines" :key="m.id" :value="m.id">{{ m.name }} ({{ m.unit }})</option>
          </select>
          <input v-model="dose.quantity" type="number" step="0.25" min="0.25" class="rounded-xl border border-[var(--line)] px-3 py-2" :placeholder="t('episode.quantity')" />
          <input v-model="dose.note" class="rounded-xl border border-[var(--line)] px-3 py-2" :placeholder="t('episode.doseNote')" />
          <button v-if="doses.length > 1" type="button" class="text-left text-sm text-red-700" @click="removeDose(i)">
            {{ t("common.delete") }}
          </button>
        </div>
        <button type="button" class="rounded-xl border px-3 py-2 text-sm" @click="addDose">{{ t("episode.addDose") }}</button>
      </div>
      <label class="grid gap-1 text-sm">
        {{ t("episode.notes") }}
        <textarea v-model="notes" rows="3" class="rounded-xl border border-[var(--line)] px-3 py-2" />
      </label>
      <p v-if="error" class="text-sm text-red-700">{{ error }}</p>
      <div class="grid gap-3 sm:grid-cols-2">
        <button class="rounded-xl bg-[var(--accent)] py-3 text-lg font-semibold text-white disabled:opacity-60" :disabled="loading">
          {{ t("common.save") }}
        </button>
        <button v-if="!editId" type="button" class="rounded-xl bg-emerald-600 py-3 text-lg font-semibold text-white disabled:opacity-60" :disabled="loading" @click="submit(true)">
          {{ t("episode.saveAndAdd") }}
        </button>
      </div>
    </form>
  </div>
</template>
