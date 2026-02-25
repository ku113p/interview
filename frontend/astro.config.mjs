import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

const locales = [
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
];

export default defineConfig({
  site: 'https://interviewassistant.ai',
  i18n: {
    defaultLocale: 'en',
    locales,
    routing: {
      prefixDefaultLocale: false,
    },
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/thanks'),
      i18n: {
        defaultLocale: 'en',
        locales: Object.fromEntries(locales.map((l) => [l, l])),
      },
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
