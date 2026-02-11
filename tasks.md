# Pace Insights – Task Tracker

## Completed

- [x] **Update hero eyebrow label** — Changed "AI Agency" → "Applied AI Partner" *(2026-02-11)*
- [x] **Update hero headline and body copy** — New messaging about reimagining business constraints *(2026-02-11)*
- [x] **Fix all TypeScript errors (astro check: 0 errors)** *(2026-02-11)*
  - Deleted rogue `src/types.ts` (duplicate of `types.d.ts` from a previous fix attempt)
  - Cleaned up `content/config.ts` — removed invalid `@types` import and unrelated site constants
  - Fixed `navigation.ts` — added `as const` to variant literal to prevent type widening
  - Fixed `community.astro` — replaced non-existent `MetaSEO` type with `MetaData`
  - Fixed `index.astro` — removed invalid `openGraph.image` field, used `satisfies` for heroActions
  - Fixed `Steps.astro` — spread image object instead of accessing `.src`/`.alt` on `unknown`
  - Widened `Steps.image` type in `types.d.ts` to accept `ImageMetadata`
  - Added `position` prop to `Header.astro` Props interface
  - Added `window.plausible` type declaration in `env.d.ts`
  - Fixed `ClickableImage.astro` — `.substr()` → `.substring()`, added missing `ImageMetadata` import

## Discovered During Work

- [ ] **Review wider homepage messaging** — Owner noted the homepage may need further copy updates as the business evolves.
- [ ] **community.astro metadata unused** — The `metadata` variable is declared but never consumed (page is just a redirect). Low priority hint.
