<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import LanguageSwitcher from "@/components/LanguageSwitcher.vue";
import { useAuthStore } from "@/stores/auth";

const { t } = useI18n();
const auth = useAuthStore();
const router = useRouter();

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
  </div>
</template>
