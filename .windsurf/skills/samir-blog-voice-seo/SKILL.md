---
name: samir-blog-voice-seo
description: Rewrite and optimise Pace Insights blog articles in Samir Abid's voice, preserving SEO, internal links, content structure, and running project checks before completion.
---

## When to use this skill

Use this skill when the user asks to:

- Rewrite, polish, or review a Pace Insights blog article
- Make an article sound more like Samir Abid
- Improve SEO for a blog post or MDX/Markdown article
- Cross-link related articles
- Convert rough article notes into publishable blog content
- Check whether a blog post is ready to publish

This skill is designed for the Pace Insights AstroWind project. It follows the same pattern a `skill-builder` skill should enforce: clear trigger conditions, required context gathering, repeatable procedure, quality gates, safety checks, and final validation.

## Required context before editing

Always gather this context before making changes:

1. **Project instructions**
   - Read `instructions.md`.
   - Read `tasks.md`.
   - If the task is not listed, add a short task entry with today's date before editing, then mark it complete at the end.

2. **Target article**
   - Read the full target `.md` or `.mdx` file under `src/content/post/`.
   - Identify whether it uses Markdown or MDX imports/components.
   - Preserve imports, images, components, canonical URLs, and working links unless the user asks to change them.

3. **Related articles**
   - Search `src/content/post/` for likely related posts.
   - Identify 1-3 internal link opportunities.
   - Prefer links that genuinely help the reader, not generic SEO linking.

4. **URL/permalink shape**
   - Check `src/config.yaml`, `src/utils/blog.ts`, or existing live/local URLs if unsure.
   - Do not invent URLs. If the user provides a working localhost URL, preserve that slug shape.

5. **Existing voice examples**
   - Use recently edited posts as voice references when relevant:
     - `how-to-create-a-simple-app-with-ai-may-2026.md`
     - `what-ai-can-do-for-your-business.mdx`
     - `what-i-learned-building-rag-system.mdx`

## Samir Abid voice rules

The target voice is:

- Plain English
- Considered
- Quietly confident
- Commercially grounded
- Useful rather than performative
- Credible without sounding like a consultancy deck
- Human, not AI-generated

### Structure the argument like this

Build from:

1. **Situation** - what is happening in the reader's world
2. **Implication** - why it matters and where the limit sits
3. **Possibility** - what this makes possible now
4. **Action** - what to do about it

Do not lead with the recommendation before the reader understands the situation.

### Respect the reader

Never imply the reader is behind, naive, or missing something obvious.

Good framing:

- `Most businesses already have useful knowledge. It is just spread across PDFs, folders, slide decks, SOPs, emails and people.`
- `That structure is fine for a first sketch. Its natural limit appears when you want the thing to keep improving.`
- `The question is not simply X. The better question is Y.`

Avoid:

- `Stop wondering...`
- `AI is coming whether you are ready or not`
- `Businesses winning with AI...`
- `If you are not doing this, you are falling behind`

### Preferred phrases

Use these patterns when appropriate:

- `The important point is...`
- `The useful question is...`
- `A useful way to think about this is...`
- `What this makes possible...`
- `The condition is worth naming...`
- `The practical point is...`
- `Its natural limit appears when...`
- `This works best when...`

### Avoid AI voice and consultancy language

Avoid these words and phrases unless they appear in a title, quote, or required technical term:

- dive into
- delve
- leverage
- unlock
- robust
- seamless
- transformational
- game-changing
- massive opportunity
- exciting
- clearly
- obviously
- definitely
- at the end of the day
- strategic initiative
- synergy
- alignment
- ecosystem
- digital transformation

Replace with the concrete thing being made possible.

### Hype control

Replace overclaims with grounded language:

- `game-changing` → `important`, `material`, or the specific changed condition
- `completely flips the risk calculation` → `changes the risk calculation`
- `10x faster` → only use if literal; otherwise `much faster` or quantify from the article
- `for pennies` → remove or name actual cost
- `AI replaces staff` → `AI can carry out defined tasks with review`

## SEO checklist

Before editing, identify the likely search intent:

- Informational: reader wants to understand a topic
- Practical: reader wants a step-by-step route
- Commercial: reader wants to know where AI fits in their business
- Technical: reader wants implementation lessons

Then optimise the article without keyword stuffing.

### Frontmatter checklist

For each article, review and improve if needed:

- `title`
  - Keep if already strong and human.
  - Make sure the main keyword/search phrase is present.
- `excerpt`
  - Plain English.
  - Keyword near the front.
  - Useful on listing pages.
- `category`
  - Keep consistent with existing taxonomy.
- `tags`
  - Use specific tags, not generic ones.
  - Prefer `ai strategy`, `rag systems`, `ai agents`, `workflow automation`, `internal tools`, `knowledge systems`, etc.
- `image`
  - Preserve unless a better article image exists.
- `author`
  - Ensure `Samir Abid` is present.
- `metadata.title`
  - Add if missing.
- `metadata.description`
  - Add if missing.
  - Keep concise and search-friendly.
- `metadata.canonical`
  - Preserve existing canonical.
  - Do not invent production URLs.

### Body SEO checklist

- Ensure the H1/title target phrase appears naturally.
- Use descriptive section headings.
- Add one or two internal links to genuinely related articles.
- Add reciprocal links where useful.
- Improve image alt text so it describes the image and supports the topic.
- Preserve captions/components unless improving clarity.
- Add a practical section if it improves search usefulness, for example:
  - `What this means for RAG projects`
  - `Where this fits in a business`
  - `What to do next`
- Keep CTAs calm and relevant.

## Editorial procedure

### 1. Analyse first

Before editing, tell the user:

- What is already working
- What feels off-tone
- What SEO opportunities exist
- Whether you recommend a surgical edit, moderate edit, or full rewrite

Default recommendation:

- **Surgical edit** for already strong articles
- **Moderate edit** for articles with good structure but weak voice/SEO
- **Full rewrite** only for rough notes, pasted HTML, or badly structured drafts

### 2. Preserve what matters

Do not casually remove:

- Personal anecdotes
- Concrete technical details
- Working URLs
- Canonical URLs
- Images/imports/components
- Existing commercial CTA
- User edits made after previous assistant changes

### 3. Apply voice edits

Work section by section:

- Start with situation
- Name the natural limit of the current approach
- Explain what becomes possible
- Add conditions for success
- End with practical next step

Use `What this makes possible:` where the article previously used hype phrases like `Real impact:`.

### 4. Apply SEO edits

- Update frontmatter.
- Tighten headings.
- Improve alt text.
- Add internal links.
- Add or refine the CTA.

### 5. Check links

For every internal link:

- Confirm the related article file exists.
- Confirm the slug shape from config or the user-provided URL.
- Prefer the known working article URL when provided by the user.

### 6. Run checks

Before saying the work is complete, run:

```bash
npx prettier --write <touched files>
npm run check
```

If preparing for commit or if multiple files were changed, use the `/pre-commit` workflow or run:

```bash
npx prettier --write .
npm run check
```

Only say `safe to commit` when `npm run check` exits with code 0.

## Quality gate

Before final response, verify:

1. Does it sound like a real person with judgement, not a consultant trying to impress?
2. Does it respect the reader's expertise?
3. Does it explain the situation before proposing action?
4. Does every section answer the `so what?`
5. Does it avoid hype, blame, and vague transformation language?
6. Are SEO fields present and useful?
7. Are internal links working and relevant?
8. Did formatting and project checks pass?

## Final response format

Summarise:

- Files changed
- Voice edits made
- SEO edits made
- Internal links added or fixed
- Check results
- Whether it is safe to commit

Keep the final answer concise and practical.
