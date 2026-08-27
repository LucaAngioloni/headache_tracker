<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import type { Medicine, Paginated } from "@/types";

const { t } = useI18n();
const items = ref<Medicine[]>([]);
const loading = ref(true);
const error = ref("");
const form = ref({ name: "", active_ingredient: "", unit: "cpr" });
const editing = ref<Medicine | null>(null);

async function load() {
  loading.value = true;
  const { data } = await api.get<Paginated<Medicine>>("/medicines/", {
    params: { page_size: 200 },
  });
  items.value = data.results;
  loading.value = false;
}

async function save() {
  error.value = "";
  if (editing.value) {
    await api.patch(`/medicines/${editing.value.id}/`, form.value);
  } else {
    await api.post("/medicines/", form.value);
  }
  form.value = { name: "", active_ingredient: "", unit: "cpr" };
  editing.value = null;
  await load();
}

function startEdit(item: Medicine) {
  editing.value = item;
  form.value = {
    name: item.name,
    active_ingredient: item.active_ingredient,
    unit: item.unit,
  };
}

async function remove(item: Medicine) {
  if (!confirm(t("common.confirmDelete"))) return;
  try {
    await api.delete(`/medicines/${item.id}/`);
    await load();
  } catch {
    error.value = t("medicine.inUse");
  }
}

onMounted(load);
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ t("medicine.title") }}</h1>
    <form
      class="grid gap-2 rounded-2xl border border-[var(--line)] bg-[var(--card)] p-3"
      @submit.prevent="save"
    >
      <input
        v-model="form.name"
        required
        class="rounded-xl border border-[var(--line)] px-3 py-2"
        :placeholder="t('medicine.name')"
      />
      <input
        v-model="form.active_ingredient"
        class="rounded-xl border border-[var(--line)] px-3 py-2"
        :placeholder="t('medicine.ingredient')"
      />
      <input
        v-model="form.unit"
        class="rounded-xl border border-[var(--line)] px-3 py-2"
        :placeholder="t('medicine.unit')"
      />
      <div class="flex gap-2">
        <button class="rounded-xl bg-[var(--accent)] px-3 py-2 text-white">
          {{ t("common.save") }}
        </button>
        <button
          v-if="editing"
          type="button"
          class="rounded-xl border px-3 py-2"
          @click="
            editing = null;
            form = { name: '', active_ingredient: '', unit: 'cpr' };
          "
        >
          {{ t("common.cancel") }}
        </button>
      </div>
    </form>
    <p v-if="error" class="text-sm text-red-700">{{ error }}</p>
    <p v-if="loading">{{ t("common.loading") }}</p>
    <ul v-else class="grid gap-2">
      <li
        v-for="item in items"
        :key="item.id"
        class="flex items-center justify-between rounded-2xl border border-[var(--line)] bg-[var(--card)] px-3 py-2"
      >
        <div>
          <p class="font-medium">{{ item.name }}</p>
          <p class="text-xs text-[var(--muted)]">{{ item.active_ingredient }} · {{ item.unit }}</p>
        </div>
        <div class="flex gap-2 text-sm">
          <button @click="startEdit(item)">{{ t("common.edit") }}</button>
          <button class="text-red-700" @click="remove(item)">
            {{ t("common.delete") }}
          </button>
        </div>
      </li>
      <li v-if="!items.length" class="text-sm text-[var(--muted)]">
        {{ t("common.empty") }}
      </li>
    </ul>
  </div>
</template>
