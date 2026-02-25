/**
 * Translation script — uses OpenRouter API to translate content files.
 *
 * Usage:
 *   pnpm translate              # translate all locales
 *   pnpm translate -- --locale es   # translate single locale
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
if (!OPENROUTER_API_KEY) {
  console.error('Error: OPENROUTER_API_KEY environment variable is required');
  process.exit(1);
}

const MODEL = 'openai/gpt-4.1-mini';
const TEMPERATURE = 0.3;
const API_URL = 'https://openrouter.ai/api/v1/chat/completions';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LOCALES_DIR = path.resolve(__dirname, '../src/content/locales');

const LOCALE_NAMES: Record<string, string> = {
  es: 'Spanish',
  fr: 'French',
  de: 'German',
  'pt-BR': 'Brazilian Portuguese',
  ru: 'Russian',
  'zh-CN': 'Simplified Chinese',
  ja: 'Japanese',
  ko: 'Korean',
  ar: 'Arabic',
};

const NON_DEFAULT_LOCALES = Object.keys(LOCALE_NAMES);

const FILES_TO_TRANSLATE = ['version-a.ts', 'version-b.ts', 'ui.ts'];

const SYSTEM_PROMPT = `You are a professional translator for a SaaS marketing website.
Translate the TypeScript content file from English to {LANGUAGE}.

RULES:
1. Output ONLY the complete TypeScript file — no explanations, no markdown fences.
2. Preserve ALL TypeScript structure: imports, exports, types, "as const", semicolons, quotes.
3. Keep the import paths EXACTLY as they are (e.g., "../../constants", "../../types").
4. Keep the exported variable name EXACTLY as-is (versionA, versionB, ui).
5. DO NOT translate:
   - Brand names: Interview Assistant, Claude, ChatGPT, Cursor, Windsurf, Mem0, Zep, Telegram, Formspree
   - Technical terms: MCP, ATS, PDF, JSON, Docker, USDC, BTC, API, Bearer token, SSE
   - URLs, email addresses, icon keys (brain, sparkles, clock, layers, grid, repeat)
   - HTML tags like <br>
   - Number values, price values, currency symbols ($)
6. Use natural, compelling marketing language — not literal word-for-word translation.
7. Match the tone: confident, conversational, professional.
8. For pricing labels like "$79 one-time" or "$29/month", keep the dollar amounts but translate the descriptive part.
9. Keep the TypeScript "as const" assertion at the end if present.`;

async function translate(
  englishSource: string,
  language: string,
): Promise<string> {
  const prompt = SYSTEM_PROMPT.replace('{LANGUAGE}', language);

  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: MODEL,
      temperature: TEMPERATURE,
      messages: [
        { role: 'system', content: prompt },
        {
          role: 'user',
          content: `Translate this TypeScript file to ${language}:\n\n${englishSource}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  const data = await response.json();
  let content: string = data.choices[0].message.content;

  // Strip markdown code fences if the model wraps them
  content = content
    .replace(/^```(?:typescript|ts)?\s*\n/m, '')
    .replace(/\n```\s*$/m, '');

  return content;
}

async function translateFile(
  locale: string,
  fileName: string,
): Promise<void> {
  const englishPath = path.join(LOCALES_DIR, 'en', fileName);
  const targetDir = path.join(LOCALES_DIR, locale);
  const targetPath = path.join(targetDir, fileName);

  const englishSource = fs.readFileSync(englishPath, 'utf-8');

  fs.mkdirSync(targetDir, { recursive: true });

  const language = LOCALE_NAMES[locale];
  console.log(`  Translating ${fileName} → ${language}...`);

  const translated = await translate(englishSource, language);
  fs.writeFileSync(targetPath, translated, 'utf-8');

  console.log(`  ✓ ${locale}/${fileName}`);
}

async function translateLocale(locale: string): Promise<void> {
  console.log(`\n[${locale}] ${LOCALE_NAMES[locale]}`);
  for (const file of FILES_TO_TRANSLATE) {
    await translateFile(locale, file);
  }
}

// CLI
const args = process.argv.slice(2);
const localeIdx = args.indexOf('--locale');
const targetLocale = localeIdx >= 0 ? args[localeIdx + 1] : undefined;

const localesToTranslate = targetLocale
  ? [targetLocale]
  : NON_DEFAULT_LOCALES;

console.log(
  `Translating ${localesToTranslate.length} locale(s): ${localesToTranslate.join(', ')}`,
);

for (const locale of localesToTranslate) {
  await translateLocale(locale);
}

console.log('\nDone! Run `pnpm format && pnpm check` to verify.');
