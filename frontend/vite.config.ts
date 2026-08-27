import { fileURLToPath, URL } from "node:url";
import { readFileSync } from "node:fs";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

const pkg = JSON.parse(
  readFileSync(fileURLToPath(new URL("./package.json", import.meta.url)), "utf-8"),
);

export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
  plugins: [
    vue(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["icons/headache_tracker_icon_192.png"],
      manifest: {
        name: "Headache Tracker",
        short_name: "Headache",
        description: "Track you headaches, medications and symptoms.",
        lang: "it",
        start_url: "/",
        scope: "/",
        display: "standalone",
        orientation: "portrait",
        theme_color: "#f4f1ec",
        background_color: "#f4f1ec",
        icons: [
          {
            src: "icons/headache_tracker_icon_64.png",
            sizes: "64x64",
            type: "image/png",
          },
          {
            src: "icons/headache_tracker_icon_192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "icons/headache_tracker_icon_512.png",
            sizes: "512x512",
            type: "image/png",
          },
          {
            src: "icons/headache_tracker_icon_512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
        navigateFallbackDenylist: [/^\/api/],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    allowedHosts: true,
    hmr: {
      clientPort: 80,
      protocol: "ws",
    },
    watch: {
      usePolling: true,
    },
  },
});
