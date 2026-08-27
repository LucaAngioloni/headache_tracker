<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { api } from "@/api/client";
import LanguageSwitcher from "@/components/LanguageSwitcher.vue";
import { useAuthStore } from "@/stores/auth";
import type { AppVersion } from "@/types";

const { t } = useI18n();
const auth = useAuthStore();
const router = useRouter();

const frontendVersion = __APP_VERSION__;
const backendVersion = ref<string | null>(null);

onMounted(async () => {
  try {
    const { data } = await api.get<AppVersion>("/version/");
    backendVersion.value = data.version;
  } catch {
    backendVersion.value = null;
  }
});

function logout() {
  auth.logout();
  router.replace({ name: "login" });
}
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ t("nav.more") }}</h1>
    <p v-if="auth.user" class="text-sm text-[var(--muted)]">
      {{ auth.user.username }}
    </p>
    <LanguageSwitcher />
    <div class="grid gap-2">
      <router-link
        class="rounded-2xl border border-[var(--line)] bg-[var(--card)] px-4 py-3"
        to="/medicines"
      >
        {{ t("nav.medicines") }}
      </router-link>
      <router-link
        class="rounded-2xl border border-[var(--line)] bg-[var(--card)] px-4 py-3"
        to="/triggers"
      >
        {{ t("nav.triggers") }}
      </router-link>
      <button
        class="rounded-2xl border border-[var(--line)] bg-[var(--card)] px-4 py-3 text-left"
        @click="logout"
      >
        {{ t("nav.logout") }}
      </button>
    </div>
    <div class="grid gap-2 rounded-2xl border border-[var(--line)] bg-[var(--card)] p-4 text-sm">
      <p class="flex items-center justify-between gap-2">
        <span class="text-[var(--muted)]">{{ t("version.frontend") }}</span>
        <span class="font-medium">{{ frontendVersion }}</span>
      </p>
      <p class="flex items-center justify-between gap-2">
        <span class="text-[var(--muted)]">{{ t("version.backend") }}</span>
        <span class="font-medium">{{ backendVersion ?? t("version.unknown") }}</span>
      </p>
    </div>
  </div>
</template>
