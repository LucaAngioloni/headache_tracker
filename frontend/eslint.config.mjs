import pluginVue from "eslint-plugin-vue";
import { defineConfigWithVueTs, vueTsConfigs } from "@vue/eslint-config-typescript";
import pluginPrettier from "@vue/eslint-config-prettier";

export default defineConfigWithVueTs(
  {
    name: "app/files-to-lint",
    files: ["**/*.{ts,mts,tsx,vue}"],
  },
  {
    name: "app/files-to-ignore",
    ignores: ["**/dist/**", "**/coverage/**", "**/node_modules/**"],
  },
  pluginVue.configs["flat/essential"],
  pluginVue.configs["flat/recommended"],
  vueTsConfigs.recommended,
  pluginPrettier,
);
