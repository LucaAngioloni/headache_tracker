<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import FilterBar from "@/components/FilterBar.vue";
import type {
  EpisodeFilters,
  Medicine,
  Paginated,
  Stats,
  Trigger,
} from "@/types";

const { t } = useI18n();
const stats = ref<Stats | null>(null);
const medicines = ref<Medicine[]>([]);
const triggers = ref<Trigger[]>([]);
const filters = ref<EpisodeFilters>({});
const loading = ref(true);

function clean(params: EpisodeFilters) {
  const out: Record<string, string | number> = {};
  for (const [k, v] of Object.entries(params)) {
    if (v !== "" && v !== undefined && v !== null) out[k] = v;
  }
  return out;
}

function pct(n: number) {
  return `${Math.round(n * 100)}%`;
}

function maxCount(rows: Array<{ count: number }>) {
  return Math.max(1, ...rows.map((r) => r.count));
}

async function loadCatalogs() {
  const [m, tr] = await Promise.all([
    api.get<Paginated<Medicine>>("/medicines/", { params: { page_size: 200 } }),
    api.get<Paginated<Trigger>>("/triggers/", { params: { page_size: 200 } }),
  ]);
  medicines.value = m.data.results;
  triggers.value = tr.data.results;
}

async function load() {
  loading.value = true;
  const { data } = await api.get<Stats>("/stats/", {
    params: clean(filters.value),
  });
  stats.value = data;
  loading.value = false;
}

function reset() {
  filters.value = {};
  load();
}

onMounted(async () => {
  await loadCatalogs();
  await load();
});
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ t("stats.title") }}</h1>
    <FilterBar
      v-model="filters"
      :medicines="medicines"
      :triggers="triggers"
      @apply="load"
      @reset="reset"
    />
    <p v-if="loading">{{ t("common.loading") }}</p>
    <template v-else-if="stats">
      <div class="grid grid-cols-2 gap-2">
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">{{ t("stats.episodes") }}</p>
          <p class="text-2xl font-semibold">{{ stats.episode_count }}</p>
        </div>
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">{{ t("stats.avgPain") }}</p>
          <p class="text-2xl font-semibold">{{ stats.avg_pain ?? "—" }}</p>
        </div>
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">{{ t("stats.medianPain") }}</p>
          <p class="text-2xl font-semibold">{{ stats.median_pain ?? "—" }}</p>
        </div>
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">{{ t("stats.avgGap") }}</p>
          <p class="text-2xl font-semibold">
            {{ stats.avg_days_between ?? "—" }}
          </p>
        </div>
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">
            {{ t("stats.currentStreak") }}
          </p>
          <p class="text-2xl font-semibold">
            {{ stats.current_headache_free_streak_days }}
          </p>
        </div>
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">
            {{ t("stats.longestStreak") }}
          </p>
          <p class="text-2xl font-semibold">
            {{ stats.longest_headache_free_streak_days }}
          </p>
        </div>
        <div
          class="col-span-2 rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">{{ t("stats.secondDose") }}</p>
          <p class="text-2xl font-semibold">
            {{ pct(stats.second_dose_rate) }}
          </p>
        </div>
      </div>

      <section class="space-y-2">
        <h2 class="font-medium">{{ t("stats.byMonth") }}</h2>
        <div v-if="stats.episodes_by_month.length" class="grid gap-1">
          <div
            v-for="row in stats.episodes_by_month"
            :key="row.month"
            class="grid grid-cols-[5rem_1fr_2rem] items-center gap-2 text-sm"
          >
            <span>{{ row.month }}</span>
            <div class="h-3 rounded bg-[var(--line)]">
              <div
                class="h-3 rounded bg-[var(--accent)]"
                :style="{
                  width: `${(row.count / maxCount(stats.episodes_by_month)) * 100}%`,
                }"
              />
            </div>
            <span>{{ row.count }}</span>
          </div>
        </div>
        <p v-else class="text-sm text-[var(--muted)]">
          {{ t("common.empty") }}
        </p>
      </section>

      <section class="space-y-2">
        <h2 class="font-medium">{{ t("stats.byWeek") }}</h2>
        <div v-if="stats.episodes_by_week.length" class="grid gap-1">
          <div
            v-for="row in stats.episodes_by_week"
            :key="row.week"
            class="grid grid-cols-[5.5rem_1fr_2rem] items-center gap-2 text-sm"
          >
            <span>{{ row.week }}</span>
            <div class="h-3 rounded bg-[var(--line)]">
              <div
                class="h-3 rounded bg-[var(--accent)]"
                :style="{
                  width: `${(row.count / maxCount(stats.episodes_by_week)) * 100}%`,
                }"
              />
            </div>
            <span>{{ row.count }}</span>
          </div>
        </div>
        <p v-else class="text-sm text-[var(--muted)]">
          {{ t("common.empty") }}
        </p>
      </section>

      <section class="space-y-2">
        <h2 class="font-medium">{{ t("stats.medicines") }}</h2>
        <ul class="grid gap-1 text-sm">
          <li v-for="row in stats.medicines" :key="row.id">
            {{ row.name }} · {{ row.episode_count }} ({{ pct(row.pct) }})
          </li>
          <li v-if="!stats.medicines.length" class="text-[var(--muted)]">
            {{ t("common.empty") }}
          </li>
        </ul>
      </section>

      <section class="space-y-2">
        <h2 class="font-medium">{{ t("stats.triggers") }}</h2>
        <ul class="grid gap-1 text-sm">
          <li v-for="row in stats.triggers" :key="row.id">
            {{ row.name }} · {{ row.episode_count }} ({{ pct(row.pct) }})
          </li>
          <li v-if="!stats.triggers.length" class="text-[var(--muted)]">
            {{ t("common.empty") }}
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
