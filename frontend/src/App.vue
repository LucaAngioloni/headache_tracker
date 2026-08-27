<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import AppNav from "@/components/AppNav.vue";

const route = useRoute();
const { locale } = useI18n();
const showNav = computed(() => route.name !== "login");
document.documentElement.lang = locale.value;
</script>

<template>
  <div class="min-h-dvh pb-[calc(6rem+env(safe-area-inset-bottom))] md:pb-0">
    <AppNav v-if="showNav" />
    <main class="mx-auto w-full max-w-3xl px-4 py-4 md:py-8">
      <router-view />
    </main>
  </div>
</template>
