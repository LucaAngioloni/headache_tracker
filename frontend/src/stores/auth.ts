import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api, clearTokens, getRefreshToken, setTokens } from "@/api/client";
import type { Me } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<Me | null>(null);
  const ready = ref(false);

  const isAuthenticated = computed(() => Boolean(user.value));

  async function fetchMe() {
    const { data } = await api.get<Me>("/me/");
    user.value = data;
  }

  async function login(username: string, password: string) {
    const { data } = await api.post("/auth/token/", { username, password });
    setTokens(data.access, data.refresh);
    await fetchMe();
  }

  function logout() {
    clearTokens();
    user.value = null;
  }

  async function bootstrap() {
    if (!getRefreshToken()) {
      ready.value = true;
      return;
    }
    try {
      const { data } = await api.post("/auth/token/refresh/", {
        refresh: getRefreshToken(),
      });
      setTokens(data.access, getRefreshToken() || "");
      await fetchMe();
    } catch {
      logout();
    } finally {
      ready.value = true;
    }
  }

  return { user, ready, isAuthenticated, login, logout, bootstrap, fetchMe };
});
