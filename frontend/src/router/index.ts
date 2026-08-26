import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { public: true },
    },
    { path: "/", redirect: "/episodes" },
    {
      path: "/episodes",
      name: "episodes",
      component: () => import("@/views/EpisodesView.vue"),
    },
    {
      path: "/episodes/new",
      name: "episode-new",
      component: () => import("@/views/EpisodeFormView.vue"),
    },
    {
      path: "/episodes/:id/edit",
      name: "episode-edit",
      component: () => import("@/views/EpisodeFormView.vue"),
    },
    {
      path: "/calendar",
      name: "calendar",
      component: () => import("@/views/CalendarView.vue"),
    },
    {
      path: "/medicines",
      name: "medicines",
      component: () => import("@/views/MedicinesView.vue"),
    },
    {
      path: "/triggers",
      name: "triggers",
      component: () => import("@/views/TriggersView.vue"),
    },
    {
      path: "/stats",
      name: "stats",
      component: () => import("@/views/StatsView.vue"),
    },
    {
      path: "/more",
      name: "more",
      component: () => import("@/views/MoreView.vue"),
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.ready) {
    await auth.bootstrap();
  }
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && auth.isAuthenticated) {
    return { name: "episodes" };
  }
  return true;
});

export default router;
