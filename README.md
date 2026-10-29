# HORSE STARS

Static Astro website with Tailwind CSS v4, TypeScript, and small scripts for HorseDex filters, card previews, collection scrolling, stat comparison, and an opt-in video player. No framework hydration.

## Local development

Use Node.js 22 LTS or newer.

```sh
npm install
npm run dev
```

`npm run check` validates Astro and TypeScript. `npm run build` checks and generates the static site in `dist/`. `npm run preview` serves that build.

## Structure

- `src/components/`: one small component per homepage section, shared navigation, stat icons, card previews, and footer. `HomePage.astro` controls the scrolling sequence.
- `src/layouts/SiteLayout.astro`: shared document, metadata, global styles, and navigation.
- `src/pages/`: English `/`, `/horses/`, `/horses/[slug]/`, and equivalent Czech routes under `/cs/`. Language routes share all components.
- `src/data/horses.json`: accurate supplied sample records, with stable IDs, slugs, edition keys, image paths, and numeric statistics.
- `src/data/collection.ts`: typed records, total collection size, and featured selection.
- `src/data/horse-types.ts` and `horses.schema.json`: TypeScript contract and import/editor JSON schema.
- `src/data/assets.ts`: build-time asset resolution for Astro image optimization.
- `src/data/site.ts`: verified contact details, pending social destinations, featured video configuration, retailer records, and Champion teaser artwork.
- `src/i18n/`: interface copy in English and Czech. Add a dictionary and locale entry for future languages.
- `src/styles/global.css`: Tailwind, brand tokens, responsive component styles, and reduced-motion rules.
- `src/styles/home-sections.css`: styles for the homepage continuation, keeping approved Hero and Collection styling separate.
- `src/components/horsedex/`, `src/scripts/horsedex.ts`, and `src/styles/horsedex.css`: collection browser, shared tiles, generated detail layout, and progressively enhanced filtering.
- `public/images/`: supplied brand, hero, card, and product assets. Images imported into components are resized and converted to WebP by Astro at build time.

## Homepage scope

The approved Hero and Collection are followed by How to Play, Special Horses, a separate Champion Edition teaser, the Collector’s Book, News, availability, retailer enquiries, a final brand moment, and the complete footer. English and Czech share all components. The collection contains the **three provided original-edition cards**, not invented records for the full 102-horse collection. Clicking or tapping a card opens an accessible native dialog; Escape closes it and focus returns to the trigger. On mobile, swipe the collection or use the arrow buttons.

The homepage's HorseDex CTAs now open `/horses/` (or `/cs/horses/`). Its visual layout remains unchanged. The play demonstration calculates values from `horses.json`. The guide follows the supplied five-round rules, with a clearly stated house-rule suggestion if both the round stat and Total tie; confirm that edge case before printing official rules.

The Collector’s Book showcase uses a high-resolution raster of the real supplied Czech PDF cover. The news artwork is an explicitly named placeholder crop of the supplied hero, not a fabricated episode. See `VISUAL_ASSETS.md` for recommended replacement assets.

## Content configuration

- Add exact official YouTube/Instagram URLs to `site` in `src/data/site.ts`. Until provided, both are visibly marked coming soon, without guessed links.
- Add an 11-character video ID to `featuredVideo.youtubeId`. The player stays disabled until configured. Once configured, a click replaces the poster with a `youtube-nocookie.com` iframe; there are no YouTube requests before that click. Set `featuredVideo.poster` to the final thumbnail path. The default poster is optimized through a local Astro import.
- Add real `Retailer` records to `retailers` using stable IDs, ISO country codes, city, and an optional URL. The section renders them automatically. No map API or location permission is needed.
- Retailer enquiries and availability questions use `info@playhorsestars.com`.
- The book CTA and legal copy are explicit placeholders pending product information and approved legal documents.

## Next steps

The HorseDex intentionally stops at six verified sample records. Follow `HORSEDEX_DATA.md` to populate the other 96. New image paths are picked up automatically by `assets.ts`; no component edits or individual page files are needed. Use each record's `edition` and globally unique `slug` when extending the collection. Champion Edition can use a distinct edition key, globally unique IDs/slugs, and optional `bonus` metadata without changing the data model. It is not exposed as a HorseDex edition until real records are added.

The default production origin is `https://playhorsestars.com`, as specified in the brief. Override `PUBLIC_SITE_URL` when needed; canonical links, language alternates, and social images use this origin. English is the master dictionary; Czech interface copy is provided, while printed card artwork retains its original language. Have final translations reviewed before launch.

Configure hosting to serve `dist/`, run `npm run build`, and use HTTPS. Supply final legal documents and social destinations before launch.
