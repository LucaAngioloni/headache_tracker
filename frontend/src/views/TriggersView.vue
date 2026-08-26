<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import type { Paginated, Trigger } from "@/types";

const { t } = useI18n();
const items = ref<Trigger[]>([]);
const name = ref("");
const editing = ref<Trigger | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  const { data } = await api.get<Paginated<Trigger>>("/triggers/", { params: { page_size: 200 } });
  items.value = data.results;
  loading.value = false;
}

async function save() {
  if (editing.value) {
    await api.patch(`/triggers/${editing.value.id}/`, { name: name.value });
  } else {
    await api.post("/triggers/", { name: name.value });
  }
  name.value = "";
  editing.value = null;
  await load();
}

function startEdit(item: Trigger) {
  editing.value = item;
  name.value = item.name;
}

async function remove(item: Trigger) {
  if (!confirm(t("common.confirmDelete"))) return;
  await api.delete(`/triggers/${item.id}/`);
  await load();
}

onMounted(load);
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ t("trigger.title") }}</h1>
    <form class="flex gap-2" @submit.prevent="save">
      <input v-model="name" required class="flex-1 rounded-xl border border-[var(--line)] px-3 py-2" :placeholder="t('trigger.name')" />
      <button class="rounded-xl bg-[var(--accent)] px-3 py-2 text-white">{{ t("common.save") }}</button>
    </form>
    <p v-if="loading">{{ t("common.loading") }}</p>
    <ul v-else class="grid gap-2">
      <li v-for="item in items" :key="item.id" class="flex items-center justify-between rounded-2xl border border-[var(--line)] bg-[var(--card)] px-3 py-2">
        <span>{{ item.name }}</span>
        <div class="flex gap-2 text-sm">
          <button @click="startEdit(item)">{{ t("common.edit") }}</button>
          <button class="text-red-700" @click="remove(item)">{{ t("common.delete") }}</button>
        </div>
      </li>
      <li v-if="!items.length" class="text-sm text-[var(--muted)]">{{ t("common.empty") }}</li>
    </ul>
  </div>
</template>
