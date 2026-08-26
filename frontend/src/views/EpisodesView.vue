<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { RouterLink } from "vue-router";
import { api } from "@/api/client";
import FilterBar from "@/components/FilterBar.vue";
import type {
  Episode,
  EpisodeFilters,
  Medicine,
  Paginated,
  Trigger,
} from "@/types";

const { t } = useI18n();
const episodes = ref<Episode[]>([]);
const medicines = ref<Medicine[]>([]);
const triggers = ref<Trigger[]>([]);
const loading = ref(true);
const loadingMore = ref(false);
const nextPage = ref<number | null>(null);
const sentinel = ref<HTMLElement | null>(null);
const filters = ref<EpisodeFilters>({});

let observer: IntersectionObserver | null = null;

function clean(params: EpisodeFilters) {
  const out: Record<string, string | number> = {};
  for (const [k, v] of Object.entries(params)) {
    if (v !== "" && v !== undefined && v !== null) out[k] = v;
  }
  return out;
}

async function loadCatalogs() {
  const [m, tr] = await Promise.all([
    api.get<Paginated<Medicine>>("/medicines/", { params: { page_size: 200 } }),
    api.get<Paginated<Trigger>>("/triggers/", { params: { page_size: 200 } }),
  ]);
  medicines.value = m.data.results;
  triggers.value = tr.data.results;
}

async function fetchPage(page: number, append: boolean) {
  const { data } = await api.get<Paginated<Episode>>("/episodes/", {
    params: { ...clean(filters.value), page, page_size: 100 },
  });
  episodes.value = append ? [...episodes.value, ...data.results] : data.results;
  nextPage.value = data.next ? page + 1 : null;
}

async function load() {
  loading.value = true;
  episodes.value = [];
  nextPage.value = null;
  try {
    await fetchPage(1, false);
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  const page = nextPage.value;
  if (page == null || loading.value || loadingMore.value) return;
  loadingMore.value = true;
  try {
    await fetchPage(page, true);
  } finally {
    loadingMore.value = false;
  }
}

function reset() {
  filters.value = {};
  load();
}

async function setupObserver() {
  await nextTick();
  const el = sentinel.value;
  if (!el || typeof IntersectionObserver === "undefined") return;
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) loadMore();
    },
    { rootMargin: "300px" },
  );
  observer.observe(el);
}

function painLabel(value: number | null) {
  return value == null ? t("common.unknown") : `${value}/10`;
}

onMounted(async () => {
  await loadCatalogs();
  await load();
  setupObserver();
});

onBeforeUnmount(() => {
  observer?.disconnect();
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold">{{ t("episode.title") }}</h1>
      <RouterLink
        to="/episodes/new"
        class="rounded-xl bg-[var(--accent)] px-3 py-2 text-sm text-white"
      >
        {{ t("common.add") }}
      </RouterLink>
    </div>
    <FilterBar
      v-model="filters"
      :medicines="medicines"
      :triggers="triggers"
      @apply="load"
      @reset="reset"
    />
    <p v-if="loading">{{ t("common.loading") }}</p>
    <ul v-else class="grid gap-2">
      <li v-for="ep in episodes" :key="ep.id">
        <RouterLink
          :to="`/episodes/${ep.id}/edit`"
          class="block rounded-2xl border border-[var(--line)] bg-[var(--card)] px-3 py-3"
        >
          <div class="flex items-center justify-between">
            <p class="font-medium">{{ ep.occurred_on }}</p>
            <p class="text-sm">{{ painLabel(ep.pain_level) }}</p>
          </div>
          <p class="mt-1 text-sm text-[var(--muted)]">
            {{
              ep.doses
                .map((d) => `${d.medicine_name} ×${d.quantity}`)
                .join(" · ")
            }}
          </p>
          <p v-if="ep.triggers.length" class="mt-1 text-xs text-[var(--muted)]">
            {{ ep.triggers.map((x) => x.name).join(", ") }}
          </p>
          <p v-if="ep.notes" class="mt-1 text-sm">{{ ep.notes }}</p>
        </RouterLink>
      </li>
      <li v-if="!episodes.length" class="text-sm text-[var(--muted)]">
        {{ t("common.empty") }}
      </li>
    </ul>
    <div
      ref="sentinel"
      class="flex justify-center py-3 text-sm text-[var(--muted)]"
    >
      <p v-if="loadingMore">{{ t("common.loading") }}</p>
    </div>
  </div>
</template>
