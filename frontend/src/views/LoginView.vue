<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import LanguageSwitcher from "@/components/LanguageSwitcher.vue";
import { useAuthStore } from "@/stores/auth";

const { t } = useI18n();
const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const error = ref(false);
const loading = ref(false);

async function submit() {
  error.value = false;
  loading.value = true;
  try {
    await auth.login(username.value, password.value);
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/episodes";
    await router.replace(redirect);
  } catch {
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="mx-auto mt-10 max-w-sm space-y-6">
    <div class="flex items-start justify-between">
      <div>
        <h1 class="text-2xl font-semibold">{{ t("app.name") }}</h1>
        <p class="text-sm text-[var(--muted)]">{{ t("auth.login") }}</p>
      </div>
      <LanguageSwitcher />
    </div>
    <form class="grid gap-3 rounded-2xl border border-[var(--line)] bg-[var(--card)] p-4" @submit.prevent="submit">
      <label class="grid gap-1 text-sm">
        {{ t("auth.username") }}
        <input v-model="username" class="rounded-xl border border-[var(--line)] px-3 py-2" required autocomplete="username" />
      </label>
      <label class="grid gap-1 text-sm">
        {{ t("auth.password") }}
        <input
          v-model="password"
          type="password"
          class="rounded-xl border border-[var(--line)] px-3 py-2"
          required
          autocomplete="current-password"
        />
      </label>
      <p v-if="error" class="text-sm text-red-700">{{ t("auth.error") }}</p>
      <button class="rounded-xl bg-[var(--accent)] py-2 text-white disabled:opacity-60" :disabled="loading">
        {{ t("auth.submit") }}
      </button>
    </form>
  </div>
</template>
