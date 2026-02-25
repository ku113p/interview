# Frontend

Landing pages for demand validation. Built with Astro 5, Tailwind CSS v4, and TypeScript.

## Pages

- `/` — Version A: CV/Career focus (primary landing page)
- `/developers` — Version B: MCP/Technical focus (developer audience)
- `/thanks` — Post-signup thank you page

## Development

```bash
pnpm install     # Install dependencies
pnpm dev         # Start dev server (localhost:4321)
pnpm build       # Build static site to dist/
pnpm preview     # Preview production build
pnpm check       # TypeScript type checking
pnpm format      # Format with Prettier
```

## Configuration

- **Formspree:** Update `formAction` in `src/content/version-a.ts` and `version-b.ts` with your Formspree form ID
- **Analytics:** Plausible script loads in production only. Update `data-domain` in `src/components/Analytics.astro`
- **Site URL:** Update `site` in `astro.config.mjs` for sitemap and canonical URLs
