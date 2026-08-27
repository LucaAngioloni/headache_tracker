<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { useI18n } from "vue-i18n";
import {
  Bar,
  Line,
  Pie,
} from "vue-chartjs";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  type ChartOptions,
} from "chart.js";
import { api } from "@/api/client";
import FilterBar from "@/components/FilterBar.vue";
import type {
  EpisodeFilters,
  Medicine,
  Paginated,
  Stats,
  Trigger,
} from "@/types";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
);

const { t } = useI18n();
const stats = ref<Stats | null>(null);
const medicines = ref<Medicine[]>([]);
const triggers = ref<Trigger[]>([]);
const filters = ref<EpisodeFilters>({});
const loading = ref(true);

const theme = computed(() => {
  const s = getComputedStyle(document.documentElement);
  return {
    ink: s.getPropertyValue("--ink").trim() || "#1c1917",
    muted: s.getPropertyValue("--muted").trim() || "#78716c",
    card: s.getPropertyValue("--card").trim() || "#fffdf9",
    line: s.getPropertyValue("--line").trim() || "#e7e0d6",
    accent: s.getPropertyValue("--accent").trim() || "#c2410c",
    accentSoft: s.getPropertyValue("--accent-soft").trim() || "#ffedd5",
  };
});

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

const palette = [
  "#c2410c",
  "#78716c",
  "#b45309",
  "#3f6212",
  "#0e7490",
  "#7c3aed",
  "#be185d",
  "#475569",
];

const scatterColors = (n: number) => Array.from({ length: n }, (_, i) => palette[i % palette.length]);

const monthChart = computed(() => ({
  labels: stats.value?.episodes_by_month.map((r) => r.month) ?? [],
  datasets: [
    {
      label: t("stats.episodes"),
      data: stats.value?.episodes_by_month.map((r) => r.count) ?? [],
      backgroundColor: theme.value.accent,
      borderRadius: 6,
    },
  ],
}));

const monthOptions = computed<ChartOptions<"bar">>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { ticks: { color: theme.value.muted }, grid: { display: false } },
    y: { beginAtZero: true, ticks: { color: theme.value.muted } },
  },
}));

const weekChart = computed(() => ({
  labels: stats.value?.episodes_by_week.map((r) => r.week) ?? [],
  datasets: [
    {
      label: t("stats.episodes"),
      data: stats.value?.episodes_by_week.map((r) => r.count) ?? [],
      borderColor: theme.value.accent,
      backgroundColor: theme.value.accentSoft,
      fill: true,
      tension: 0.3,
      pointBackgroundColor: theme.value.accent,
      pointRadius: 3,
    },
  ],
}));

const weekOptions = computed<ChartOptions<"line">>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { ticks: { color: theme.value.muted, maxRotation: 45, minRotation: 0 }, grid: { display: false } },
    y: { beginAtZero: true, ticks: { color: theme.value.muted } },
  },
}));

const medicineChart = computed(() => ({
  labels: stats.value?.medicines.map((r) => r.name) ?? [],
  datasets: [
    {
      data: stats.value?.medicines.map((r) => r.episode_count) ?? [],
      backgroundColor: scatterColors(stats.value?.medicines.length ?? 0),
      borderColor: theme.value.card,
      borderWidth: 2,
    },
  ],
}));

const triggerChart = computed(() => ({
  labels: stats.value?.triggers.map((r) => r.name) ?? [],
  datasets: [
    {
      data: stats.value?.triggers.map((r) => r.episode_count) ?? [],
      backgroundColor: scatterColors(stats.value?.triggers.length ?? 0),
      borderColor: theme.value.card,
      borderWidth: 2,
    },
  ],
}));

const pieOptions = computed<ChartOptions<"pie">>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
      labels: { color: theme.value.ink },
    },
    tooltip: {
      callbacks: {
        label: (item) => {
          const list = item.dataset.data as number[];
          const total = list.reduce((a, b) => a + b, 0);
          const raw = item.parsed;
          const p = total ? Math.round((raw / total) * 100) : 0;
          return ` ${item.label}: ${raw} (${p}%)`;
        },
      },
    },
  },
}));

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
            {{ t("stats.avgEpisodesMonth") }}
          </p>
          <p class="text-2xl font-semibold">{{ stats.avg_episodes_per_month }}</p>
        </div>
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">
            {{ t("stats.avgEpisodesWeek") }}
          </p>
          <p class="text-2xl font-semibold">{{ stats.avg_episodes_per_week }}</p>
        </div>
        <div
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <p class="text-xs text-[var(--muted)]">
            {{ t("stats.currentStreak") }}
          </p>
          <p class="text-2xl font-semibold">{{ stats.current_headache_free_streak_days }}</p>
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
        <div
          v-if="stats.episodes_by_month.length"
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <div class="h-56">
            <Bar :data="monthChart" :options="monthOptions" />
          </div>
        </div>
        <p v-else class="text-sm text-[var(--muted)]">
          {{ t("common.empty") }}
        </p>
      </section>

      <section class="space-y-2">
        <h2 class="font-medium">{{ t("stats.byWeek") }}</h2>
        <div
          v-if="stats.episodes_by_week.length"
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <div class="h-56">
            <Line :data="weekChart" :options="weekOptions" />
          </div>
        </div>
        <p v-else class="text-sm text-[var(--muted)]">
          {{ t("common.empty") }}
        </p>
      </section>

      <section class="space-y-2">
        <h2 class="font-medium">{{ t("stats.medicines") }}</h2>
        <div
          v-if="stats.medicines.length"
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <div class="h-56">
            <Pie :data="medicineChart" :options="pieOptions" />
          </div>
          <p class="mt-2 text-sm text-[var(--muted)]">
            {{ stats.medicines.map((r) => `${r.name} · ${r.episode_count} (${pct(r.pct)})`).join(" · ") }}
          </p>
        </div>
        <p v-else class="text-sm text-[var(--muted)]">
          {{ t("common.empty") }}
        </p>
      </section>

      <section class="space-y-2">
        <h2 class="font-medium">{{ t("stats.triggers") }}</h2>
        <div
          v-if="stats.triggers.length"
          class="rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
        >
          <div class="h-56">
            <Pie :data="triggerChart" :options="pieOptions" />
          </div>
          <p class="mt-2 text-sm text-[var(--muted)]">
            {{ stats.triggers.map((r) => `${r.name} · ${r.episode_count} (${pct(r.pct)})`).join(" · ") }}
          </p>
        </div>
        <p v-else class="text-sm text-[var(--muted)]">
          {{ t("common.empty") }}
        </p>
      </section>
    </template>
  </div>
</template>
