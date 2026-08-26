<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { RouterLink, useRoute } from "vue-router";
import LanguageSwitcher from "@/components/LanguageSwitcher.vue";

const { t } = useI18n();
const route = useRoute();

const items = computed(() => [
  { to: "/episodes", label: t("nav.episodes"), match: "episode" },
  { to: "/calendar", label: t("nav.calendar"), match: "calendar" },
  { to: "/stats", label: t("nav.stats"), match: "stats" },
  { to: "/more", label: t("nav.more"), match: "more" },
]);

function active(match: string) {
  const name = String(route.name || "");
  if (match === "episode") return name.startsWith("episode");
  if (match === "more") return ["more", "medicines", "triggers"].includes(name);
  return name === match;
}
</script>

<template>
  <header
    class="sticky top-0 z-20 hidden border-b border-[var(--line)] bg-[var(--card)] md:block"
  >
    <div class="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
      <span class="font-semibold">{{ t("app.name") }}</span>
      <nav class="flex items-center gap-4 text-sm">
        <RouterLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          class="rounded-full px-3 py-1"
          :class="
            active(item.match)
              ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
              : 'text-[var(--muted)]'
          "
        >
          {{ item.label }}
        </RouterLink>
        <LanguageSwitcher compact />
      </nav>
    </div>
  </header>

  <nav
    class="fixed inset-x-0 bottom-0 z-20 grid grid-cols-4 border-t border-[var(--line)] bg-[var(--card)] md:hidden"
  >
    <RouterLink
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="flex flex-col items-center py-2 text-xs"
      :class="
        active(item.match) ? 'text-[var(--accent)]' : 'text-[var(--muted)]'
      "
    >
      {{ item.label }}
    </RouterLink>
  </nav>
</template>
