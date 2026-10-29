# HorseDex sample and completion guide

The first implementation contains exactly six horses. All printed identities, breeds and statistics were checked against supplied artwork. Standard card images were rendered from the existing print PDF, cropped to its trim marks, and exported as WebP; no trading-card artwork was recreated.

| ID | Horse | Breed | Rarity | Source |
| --- | --- | --- | --- | --- |
| HS001 | Ezora | Arabian | Standard | Regular-card PDF, page 1 |
| HS009 | Byzantis | Arabian | Elite | Supplied Elite artwork |
| HS011 | Flits | Friesian | Standard | Regular-card PDF, page 10 |
| HS051 | Exon | Mustang | Legend | Supplied Legend artwork |
| HS052 | Ash | Mustang | Standard | Regular-card PDF, page 46 |
| HS085 | Queen | Thoroughbred | Epic | Supplied Epic artwork |

## Architecture

- `src/data/horses.json` is the only source of individual horse content. Statistics live under `stats`; artwork under `images`.
- `src/data/horses.schema.json` documents the import format. Editor association is in `.vscode/settings.json`. Build-time checks reject conflicting IDs/slugs, malformed slugs, unsupported rarities, missing card assets, and invalid statistics.
- Each JSON record automatically generates English and Czech detail pages, with canonical and language-alternate links and a card-specific Open Graph image.
- `featured` preserves the three approved homepage cards. `battleDemo` selects the two real cards used by the homepage game demonstration.
- Images anywhere under `public/images/` are discovered at build time and resized by Astro. Card files must exist; a missing file fails the build.
- Future editions use a distinct `edition` string, unique ID, and globally unique slug. For example, use `champion-flits` rather than reusing `flits`. Collection numbers need only be unique within their edition. Previous/next navigation remains within the same edition.
- Optional `bonus: { "stat": "speed", "amount": 10 }` is supported. Store the actual printed effective values in `stats` and `total`; the bonus is descriptive metadata, not added again by the website.
- The edition dropdown derives from records. No Champion option is shown for this six-record base-only sample.

## What is needed for all 102

1. **96 remaining verified records:** printed ID and number, final name and slug, canonical breed, rarity, edition (`base`), four statistics, and total. Reconcile the full catalog against the regular and special print PDFs; PDF page number is not the collection number.
2. **96 web-ready card exports:** use the existing PDFs wherever they contain final artwork. Export clean, upright, trimmed cards in WebP (approximately 800–1200 px high). Use stable names such as `hs052-ash.webp` and set `images.card` to the real public path. Do not include crop marks or bleed.
3. **Optional final titles/taglines:** include only authoritative wording. Regular samples intentionally omit these fields because their printed cards have no story text.
4. **Optional standalone horse artwork:** set `images.hero` only when a genuine separate image is available. No fabricated or nonexistent hero-image paths are included in the samples. Landscape art around 1600 × 1000 px is suitable; the printed card remains the principal visual.

The supplied source PDFs may already contain all required card artwork. A separate new photoshoot is not required to complete the catalog. Standalone horse imagery is an optional enhancement.

## Behavior and limits

The catalog shows a transparent six-horse sample notice, alongside the eventual collection size of 102. Previous/next links visit only published samples, in number order; the first and last entries have disabled boundary controls. The HS number is the printed number, not the sample's position.

Search is immediate, case-insensitive, accent-insensitive and name-only. Breed, rarity, and edition filters combine. Number sorts ascending; score sorts are descending, with number as the stable tiebreaker. Selections are reflected in the URL and restored on reload/back. Reset clears them. All six records remain usable as static links without JavaScript.

Related rails contain only other records of the same breed and exclude the current ID. Exon and Ash demonstrate Mustang relationships; Ezora and Byzantis demonstrate Arabian relationships. A breed with no second published horse displays an honest empty message instead of unrelated results.

Horse stories and printed card artwork remain in their original language; interface copy uses the shared English/Czech dictionaries.
