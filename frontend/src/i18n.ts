import { createI18n } from "vue-i18n";
import en from "./locales/en.json";
import it from "./locales/it.json";

export const SUPPORTED_LOCALES = ["it", "en"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];

const STORAGE_KEY = "locale";

function isSupported(value: string | null | undefined): value is Locale {
  return value === "it" || value === "en";
}

function detectLocale(): Locale {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (isSupported(saved)) return saved;

  if (typeof navigator !== "undefined") {
    const candidates = Array.isArray(navigator.languages)
      ? navigator.languages
      : [navigator.language];
    for (const candidate of candidates) {
      const tag = String(candidate).toLowerCase();
      if (tag.startsWith("it")) return "it";
      if (tag.startsWith("en")) return "en";
    }
  }

  return "it";
}

export const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: "en",
  messages: { it, en },
});

export function setLocale(next: Locale) {
  i18n.global.locale.value = next;
  localStorage.setItem(STORAGE_KEY, next);
  document.documentElement.lang = next;
}

export function currentLocale(): Locale {
  return isSupported(i18n.global.locale.value) ? i18n.global.locale.value : "it";
}
