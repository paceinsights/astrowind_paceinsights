# Pace Insights – Project Instructions

## Overview

Pace Insights is a marketing/sales website for an Applied AI consultancy run by Samir Abid. The site is built on the **AstroWind** template and is primarily a static site with blog posts added periodically.

## Tech Stack

- **Framework:** Astro 5.x
- **Styling:** Tailwind CSS 3.x
- **Icons:** Astro Icon (Tabler, Flat Color Icons)
- **Typography:** Inter (via Fontsource)
- **Deployment:** Netlify
- **Language:** TypeScript

## Project Structure

- `src/pages/index.astro` — Homepage (hero, testimonials, logo marquee, about section)
- `src/pages/` — All site pages and blog posts
- `src/components/widgets/` — Reusable page-level widgets (Hero2, Steps3, Testimonials, etc.)
- `src/components/ui/` — Low-level UI components (Button, Headline, etc.)
- `src/components/` — Standalone components (LogoMarquee, etc.)
- `src/assets/images/` — All images (people, logos, OG images, etc.)
- `src/navigation.ts` — Header/footer navigation config
- `src/types.d.ts` — Shared TypeScript type definitions
- `src/layouts/` — Page layouts

## Content Updates

- **Blog posts** are added periodically in the posts/articles section.
- **Homepage messaging** is updated occasionally as the business evolves.
- Content changes are typically text/copy updates, not structural.

## Conventions

- Use existing component patterns (Hero2, Steps3, etc.) rather than creating new ones.
- Images go in `src/assets/images/` with descriptive filenames.
- Follow the existing Tailwind class patterns for consistency.
- Keep the site lightweight and fast — avoid unnecessary dependencies.

## Pre-Commit Checks

**Before every commit**, run the full check suite to ensure CI will pass:

```bash
npm run check
```

This runs three checks in sequence:

1. `astro check` — TypeScript and Astro diagnostics
2. `eslint .` — Linting
3. `prettier --check .` — Formatting

A **Git pre-commit hook** is installed (`.git/hooks/pre-commit`) that runs these automatically on every `git commit`. If any check fails, the commit is blocked.

**In Windsurf**, use the `/pre-commit` workflow to have Cascade run the full suite, fix any issues, and confirm it's safe to commit.

**Tip:** If Prettier formatting fails, run `npx prettier --write .` first, then re-run `npm run check`.

## Key URLs

- **Discovery Call CTA:** `https://tidycal.com/yourdatadriven/discovery-call`
- **Deployment:** Netlify (see `netlify.toml`)
