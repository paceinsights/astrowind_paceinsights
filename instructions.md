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

## Key URLs

- **Discovery Call CTA:** `https://tidycal.com/yourdatadriven/discovery-call`
- **Deployment:** Netlify (see `netlify.toml`)
