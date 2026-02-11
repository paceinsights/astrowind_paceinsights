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

- [x] **Fix ESLint errors (40 errors → 0)** *(2026-02-11)*
  - Added test runner globals (`describe`, `it`, `expect`, etc.) to ESLint config for `tests/` directory
  - Removed unused `metadata` variable from `community.astro` (redirect-only page)
  - Replaced `arguments` with rest params (`...args`) in `Analytics.astro` Plausible script + added `is:inline`

## Discovered During Work

- [ ] **Review wider homepage messaging** — Owner noted the homepage may need further copy updates as the business evolves.
