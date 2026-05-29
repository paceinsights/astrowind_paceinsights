# Pace Insights – Task Tracker

## In Progress

- [ ] **Change Learn More CTA target** — Redirect the "Learn More" CTA on the homepage hero to anchor link down to the Founder Spotlight section (`#founder`) _(2026-05-29)_

## Completed

- [x] **Update hero image to sailboat** — Cropped `sail-boat-into-sunset1.jpg` to a 1:1 aspect ratio with a precise custom crop placing the horizon exactly 3/4 from the top and 1/4 from the bottom, saved as `sail-boat-into-sunset-horizon-bottom.jpg` (bypassing any local build/browser caching), imported and set it as the hero image in `src/pages/index.astro`, and verified all quality and formatting checks. _(2026-05-29)_
- [x] **Change image in founder section** — Updated the Founder Spotlight section in `src/pages/index.astro` to use the same desk image (`Samir Abid - desk1.png`) used in the hero, and removed the unused standing image import. _(2026-05-29)_
- [x] **Update hero eyebrow label** — Changed "AI Agency" → "Applied AI Partner" _(2026-02-11)_
- [x] **Update hero headline and body copy** — New messaging about reimagining business constraints _(2026-02-11)_
- [x] **Fix all TypeScript errors (astro check: 0 errors)** _(2026-02-11)_
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

- [x] **Fix ESLint errors (40 errors → 0)** _(2026-02-11)_
  - Added test runner globals (`describe`, `it`, `expect`, etc.) to ESLint config for `tests/` directory
  - Removed unused `metadata` variable from `community.astro` (redirect-only page)
  - Replaced `arguments` with rest params (`...args`) in `Analytics.astro` Plausible script + added `is:inline`

- [x] **Replace About Samir section with Founder Spotlight** — Built custom `FounderSpotlight.astro` component replacing Steps3. Narrative copy targeting non-technical business leaders, with bolding on business-relevant signals (credentials, leadership teams, concrete AI proof point, philosophy). _(2026-02-11)_
- [x] **Create reusable Samir blog voice and SEO skill** — Added `.windsurf/skills/samir-blog-voice-seo/SKILL.md` covering Samir Abid voice rules, blog SEO checks, internal linking, validation, and pre-commit expectations. _(2026-05-28)_
- [x] **Add CHP logo to homepage carousel** — Copied CHP logo from raw assets, imported and integrated it into `LogoMarquee.astro` in alphabetical order, and ran full check suite with success. _(2026-05-28)_
- [x] **Update homepage hero image** — Copied `Samir Abid - desk1.png` to production assets, replaced the AI strategy illustration in `src/pages/index.astro` Hero section with this new image of Samir Abid, and verified formatting and project build. _(2026-05-28)_
- [x] **Update homepage hero copy** — Revised tagline to "AI Product Partner" and updated the title and subtitle in `src/pages/index.astro` to focus on productizing expertise and knowledge assets. _(2026-05-28)_
- [x] **Remove Jeff Braun testimonial** — Removed the Jeff Braun testimonial block from `src/pages/index.astro` and cleaned up its unused image import to prevent lint warnings. _(2026-05-28)_
- [x] **Center homepage testimonials** — Updated `Testimonials.astro` to dynamically apply centered, beautifully-sized, literal grid column classes using Astro's `class:list` when there are fewer than 3 testimonials on the page. _(2026-05-28)_

## Discovered During Work

- [ ] **Review wider homepage messaging** — Owner noted the homepage may need further copy updates as the business evolves.
