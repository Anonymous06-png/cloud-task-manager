# Task 10A — Product-Grade Home Redesign

Date: 2026-11-07

Scope: public Home page only (shared public navigation, Home hero, sample preview include, Home-scoped CSS). Login, Register, Dashboard, backend, routes, and dependencies unchanged.

## Changes

| File | Changes |
|---|---|
| `templates/base.html` | Public pages: one `public-header` row now carries brand + VI/EN switch + theme toggle + Log in + Create account. The separate unauthenticated utility bar (breadcrumb "Workspace / Home" and duplicated controls) was removed for public pages; the authenticated utility bar is unchanged. |
| `templates/home.html` | Hero rebuilt: brand eyebrow, large translated headline, one lead paragraph, two CTAs. No marketing filler. |
| `templates/includes/workspace_preview.html` | Replaced the marketing panel with a mini-dashboard: compact sidebar (brand, Overview / Tasks 3 / Completed 2), "Your tasks" header, 2/5 · 40% progress (accurately derived from the sample list), 5 sample tasks with pending/completed states and due chips, sample-data caption. Decorative-only (`role="img"`, `aria-hidden` inner content, no fake controls). |
| `static/css/app.css` | Rewrote the Home/public-header section; auth-page rules preserved. Stronger hierarchy: h1 `clamp(34px, 4vw, 54px)`, 5fr/6fr hero split (preview larger), layered app card with `--shadow-2`, tighter spacing. Responsive: hero stacks ≤760px; mini-dashboard sidebar becomes a horizontal strip ≤440px; equal-width CTAs on small screens. |

All copy uses existing translated strings from `locale/vi/LC_MESSAGES/django.po` (VI renders natively; a few sample-task titles remain English in the VI catalog — see issues). No fake metrics, gradients, dead controls, or heavy animation; only existing design tokens used. No JS changes.

## Verification

| Check | Result |
|---|---|
| `manage.py check` (process-only env, no config written) | PASS — exit 0, 0 issues |
| `git diff --check` | PASS — exit 0 (informational CRLF warnings only) |
| Desktop 1280px DOM audit (dev server, DEBUG=True live reload) | PASS — header single row; breadcrumb/utility bar absent; no horizontal overflow; preview app 563×418, sidebar 172px, nav counts 3/2; progress fill exactly 40% with 2/5 completed; CTAs 44px min-height |
| Mobile 390px DOM audit | PASS — no overflow; sidebar switches to row; CTAs equal width; header fits |
| Dark theme computed colors | PASS — tokens resolve correctly (surface #19211C, sidebar #151D18, track #344B39, readable text) |
| VI/EN rendering | PASS — EN session renders 5/5 hero+preview strings; VI session renders translated headline; VI/EN + theme controls present in header |
| Login page regression | PASS — `/login/` renders form + preview include, auth CSS intact |
| Visual comparison vs attached reference image | NOT RUN — image content cannot be read in this session (known tooling limit); compensated with measured DOM/computed-style audit |
| Screenshot viewing | NOT RUN — captured for the record only; image review unavailable |

## Remaining issues

1. Six sample strings ("Send the weekly update", "Tomorrow", "Draft the meeting agenda", "Review the launch checklist", "Prepare the project brief", "Plan the week ahead") are not yet in the VI catalog and fall back to English. `msgfmt` remains unavailable — compile via the standard Django/gettext workflow later.
2. No git operations performed; all pre-existing uncommitted changes preserved.

## Commands

`manage.py check` (exit 0) · `git diff --check` (exit 0) · browser DOM audits at 1280/390px · `set_language` POST EN→VI (302/302) · curl `/login/` render check.
