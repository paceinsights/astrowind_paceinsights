---
description: Run the full pre-commit check suite (astro check + eslint + prettier) before committing
---

# Pre-Commit Check Workflow

Run this workflow before every commit to ensure the build will pass in CI.

## Steps

1. **Format all files with Prettier**

// turbo

```bash
npx prettier --write .
```

2. **Run the full check suite** (astro check → eslint → prettier --check)

// turbo

```bash
npm run check
```

3. **Review the output**

- If **all three checks pass** (exit code 0), tell the user: "All checks pass — safe to commit and push."
- If **any check fails**, identify the specific errors, fix them, then re-run `npm run check` from step 2.
- Do NOT tell the user it's ready until you see exit code 0 from `npm run check`.

4. **Stage and summarise**

- List the files that were modified (by fixes or formatting).
- Suggest a commit message based on the changes.
