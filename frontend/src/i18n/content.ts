import type { Locale } from './config';
import type { VersionContent, UiStrings } from '../content/types';

const versionAModules = import.meta.glob<{ versionA: VersionContent }>(
  '../content/locales/*/version-a.ts',
  { eager: true },
);

const versionBModules = import.meta.glob<{ versionB: VersionContent }>(
  '../content/locales/*/version-b.ts',
  { eager: true },
);

const uiModules = import.meta.glob<{ ui: UiStrings }>(
  '../content/locales/*/ui.ts',
  { eager: true },
);

function findModule<T>(
  modules: Record<string, T>,
  locale: Locale,
  file: string,
): T {
  const key = `../content/locales/${locale}/${file}`;
  const mod = modules[key];
  if (mod) return mod;
  // Fallback to English if translation not yet available
  const fallback = modules[`../content/locales/en/${file}`];
  if (!fallback) throw new Error(`Missing ${file} for locale "en" (fallback)`);
  return fallback;
}

export function getVersionA(locale: Locale): VersionContent {
  return findModule(versionAModules, locale, 'version-a.ts').versionA;
}

export function getVersionB(locale: Locale): VersionContent {
  return findModule(versionBModules, locale, 'version-b.ts').versionB;
}

export function getUi(locale: Locale): UiStrings {
  return findModule(uiModules, locale, 'ui.ts').ui;
}
