---
name: browser-preview-screenshots
description: Use a browser preview to visually verify a running web app, handle login if needed, navigate to specific UI states, and capture screenshots for review.
---

## When to use this skill

Use this when you need to:

- Preview a local dev server visually (UI/layout verification)
- Capture screenshots to confirm changes
- Navigate the app to specific pages/sections/states
- Validate responsive layouts (mobile/tablet/desktop)
- Troubleshoot UI issues by checking console/network

## Inputs to ask the user for (if missing)

- The dev server URL (for example `http://localhost:3000`)
- The page/path to verify (for example `/dashboard`)
- Whether the app requires authentication
- If authentication is required:
  - Ask the user to log in manually in the preview window (preferred)
  - Ask for confirmation once they are logged in

## Procedure

### 1) Ensure a dev server is running

- If there is no server running, ask the user to start it.
- If the port is unknown, ask where the server is listening.

### 2) Create a browser preview

- Create a browser preview that points at the dev server origin (no path).
- Tell the user to open the preview in their browser.

### 3) Navigate to the target page

- Navigate to the full URL (origin + path).
- If the page is a SPA, wait for a stable UI cue (visible text) before capturing.

### 4) Handle authentication (if applicable)

- If you hit a login page, do NOT guess credentials.
- Ask the user to log in manually.
- If the login involves SSO, 2FA, CAPTCHA, or magic links:
  - Always ask the user to complete it.
  - Wait for user confirmation before continuing.

### 5) Move to the relevant UI state

Depending on the task:

- Scroll a section into view
- Click through UI to reveal dialogs/menus
- Fill form fields (only when the user explicitly provides safe test values)
- Wait for loading spinners to disappear or for a specific text to appear

### 6) Capture evidence

- Prefer a viewport screenshot after scrolling to the exact section.
- Use a full-page screenshot when the overall layout is being reviewed.
- Take multiple screenshots if comparing states (before/after, mobile/desktop, light/dark).

### 7) Optional: quick diagnostics

If the UI is broken or content is missing:

- List console warnings/errors
- Inspect recent network failures (4xx/5xx)
- Take a snapshot (UIDs) if you need to click/target specific elements

## Common snippets (adapt as needed)

### Scroll to a section by text

Run a script to find a section containing a unique text fragment and scroll it into view, then take a screenshot.

### Responsive checks

Resize to common sizes:

- 375x667 (mobile)
- 768x1024 (tablet)
- 1280x800 (desktop)

### Theme checks

If the app supports theme switching, capture both light and dark.

## Safety notes

- Never request or store real passwords.
- Prefer manual login for any real account.
- If sensitive information might be visible, warn the user before taking screenshots.
