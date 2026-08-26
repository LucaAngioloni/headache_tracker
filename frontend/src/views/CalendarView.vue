<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { api } from "@/api/client";
import type { Episode, Paginated } from "@/types";

const { t, locale } = useI18n();
const router = useRouter();

const cursor = ref(new Date());
const episodes = ref<Episode[]>([]);
const selected = ref<string | null>(null);

const year = computed(() => cursor.value.getFullYear());
const month = computed(() => cursor.value.getMonth());

const monthLabel = computed(() =>
  new Intl.DateTimeFormat(locale.value, { month: "long", year: "numeric" }).format(cursor.value),
);

const byDay = computed(() => {
  const map = new Map<string, Episode[]>();
  for (const ep of episodes.value) {
    const list = map.get(ep.occurred_on) || [];
    list.push(ep);
    map.set(ep.occurred_on, list);
  }
  return map;
});

const cells = computed(() => {
  const first = new Date(year.value, month.value, 1);
  const startPad = (first.getDay() + 6) % 7;
  const daysInMonth = new Date(year.value, month.value + 1, 0).getDate();
  const out: Array<{ date: string | null; day: number | null }> = [];
  for (let i = 0; i < startPad; i++) out.push({ date: null, day: null });
  for (let d = 1; d <= daysInMonth; d++) {
    const iso = `${year.value}-${String(month.value + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    out.push({ date: iso, day: d });
  }
  return out;
});

const selectedEpisodes = computed(() => (selected.value ? byDay.value.get(selected.value) || [] : []));

function shift(delta: number) {
  cursor.value = new Date(year.value, month.value + delta, 1);
  load();
}

async function load() {
  const start = `${year.value}-${String(month.value + 1).padStart(2, "0")}-01`;
  const endDate = new Date(year.value, month.value + 1, 0);
  const end = `${year.value}-${String(month.value + 1).padStart(2, "0")}-${String(endDate.getDate()).padStart(2, "0")}`;
  const { data } = await api.get<Paginated<Episode>>("/episodes/", {
    params: { date_after: start, date_before: end, page_size: 200 },
  });
  episodes.value = data.results;
}

function open(date: string) {
  selected.value = date;
}

function add() {
  router.push({ path: "/episodes/new", query: { date: selected.value || undefined } });
}

onMounted(load);
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <button class="rounded-full border px-3 py-1" @click="shift(-1)">‹</button>
      <h1 class="text-lg font-semibold capitalize">{{ monthLabel }}</h1>
      <button class="rounded-full border px-3 py-1" @click="shift(1)">›</button>
    </div>
    <div class="grid grid-cols-7 gap-1 text-center text-xs text-[var(--muted)]">
      <span v-for="d in 7" :key="d">{{ d }}</span>
    </div>
    <div class="grid grid-cols-7 gap-1">
      <button
        v-for="(cell, i) in cells"
        :key="i"
        class="aspect-square rounded-xl border border-transparent p-1 text-sm"
        :class="cell.date ? 'bg-[var(--card)] border-[var(--line)]' : ''"
        :disabled="!cell.date"
        @click="cell.date && open(cell.date)"
      >
        <span class="block">{{ cell.day }}</span>
        <span v-if="cell.date && byDay.get(cell.date)?.length" class="mx-auto mt-1 block h-1.5 w-1.5 rounded-full bg-[var(--accent)]" />
        <span v-if="cell.date && (byDay.get(cell.date)?.length || 0) > 1" class="text-[10px] text-[var(--accent)]">
          {{ byDay.get(cell.date)?.length }}
        </span>
      </button>
    </div>

    <div v-if="selected" class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3">
      <div class="mb-2 flex items-center justify-between">
        <p class="font-medium">{{ selected }}</p>
        <button class="text-sm" @click="selected = null">{{ t("common.close") }}</button>
      </div>
      <ul class="grid gap-2">
        <li v-for="ep in selectedEpisodes" :key="ep.id">
          <RouterLink :to="`/episodes/${ep.id}/edit`" class="block text-sm">
            {{ ep.pain_level ?? t("common.unknown") }}/10 ·
            {{ ep.doses.map((d) => d.medicine_name).join(", ") }}
          </RouterLink>
        </li>
        <li v-if="!selectedEpisodes.length" class="text-sm text-[var(--muted)]">{{ t("common.empty") }}</li>
      </ul>
      <button class="mt-3 w-full rounded-xl bg-[var(--accent)] py-2 text-sm text-white" @click="add">
        {{ t("calendar.addForDay") }}
      </button>
    </div>
  </div>
</template>
