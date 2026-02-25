export const locales = [
  'en',
  'es',
  'fr',
  'de',
  'pt-BR',
  'ru',
  'zh-CN',
  'ja',
  'ko',
  'ar',
  'hi',
  'id',
  'tr',
  'vi',
  'pl',
] as const;

export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'en';

export const nonDefaultLocales = locales.filter(
  (l) => l !== defaultLocale,
) as unknown as Exclude<Locale, 'en'>[];

export const localeNames: Record<Locale, string> = {
  en: 'English',
  es: 'Español',
  fr: 'Français',
  de: 'Deutsch',
  'pt-BR': 'Português',
  ru: 'Русский',
  'zh-CN': '中文',
  ja: '日本語',
  ko: '한국어',
  ar: 'العربية',
  hi: 'हिन्दी',
  id: 'Bahasa Indonesia',
  tr: 'Türkçe',
  vi: 'Tiếng Việt',
  pl: 'Polski',
};

const rtlLocales = new Set<Locale>(['ar']);

export function isRtl(locale: Locale): boolean {
  return rtlLocales.has(locale);
}

export function localePath(locale: Locale, path: string): string {
  const clean = path.replace(/^\/|\/$/g, '');
  if (locale === defaultLocale) return clean ? `/${clean}` : '/';
  return clean ? `/${locale}/${clean}` : `/${locale}`;
}

export function getLocaleFromUrl(url: URL): Locale {
  const [, segment] = url.pathname.split('/');
  if (segment && (locales as readonly string[]).includes(segment)) {
    return segment as Locale;
  }
  return defaultLocale;
}
