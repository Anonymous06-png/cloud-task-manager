# TASK 05M — Sidebar Toggle and Public Home Layout

Date: 2026-11-04
Project: `C:\ProjectCloud\cloud-task-manager`
Branch: `main` (unchanged, no Git operations performed)
Result: **DONE — both fixes implemented and visually verified in the browser at 1440×830.**

## Scope followed

Only Django templates plus `static/css/app.css` was touched; existing components (`.btn`, panel/card, eyebrow, badge vocabulary, data attributes) were reused. No redesign, no backend/database/schema changes, no new dependencies, no full CSS rewrite.

## 1. Sidebar toggle (authenticated Dashboard header)

- `templates/base.html`: removed the redundant bottom `.sidebar-collapse` "Collapse sidebar" button from `.sidebar-bottom`. Exactly ONE toggle remains: the topbar `sidebar-top-toggle` (`data-sidebar-toggle`) next to the breadcrumb in the `utility-bar` header. Expand/collapse behavior, ARIA state, tooltips and `localStorage` persistence are untouched (`static/js/app.js` handles both buttons generically, so only the element was removed).
- `static/css/app.css`: removed all now-dead `.sidebar-collapse` rules (base rule, hover rule, `icon-expand/icon-collapse` swaps, collapsed-rail sizing reference, ≤760px `display:none` entry, mobile drawer behavior kept for `.mobile-menu`).

## 2. Public Home layout (unauthenticated `/`)

The page previously rendered only the hero copy and two orphan `section-heading` blocks (feature grid, tech badges, hero mark and footer were all `display:none`), which produced large empty space.

- `templates/base.html` (public header): "Create account" is now the primary CTA reusing the existing `.btn` component; "Log in" / "Settings" stay quiet links; nav gets `align-items: center`.
- `static/css/app.css` (Public Pages section only): added minimal styles reusing the existing 1Design token vocabulary for the already-present markup — `.feature-grid` (3-col), `.feature-card`, `.feature-number`, `.tech-stack` + `.tech-badge` (pill/badge pattern), `.footer` (border-top divider). `.hero-mark` stays hidden. Hero vertical rhythm now `space-7/space-6`; ≤760px stacks `.feature-grid` to 1 column and relaxes hero padding.

## Files changed

| File | Change |
|---|---|
| `templates/base.html` | Removed bottom collapse button; public header CTA hierarchy. |
| `static/css/app.css` | Removed dead `.sidebar-collapse` rules; public page component styles + hero/nav spacing; mobile stacking. |
| `staticfiles/css/app.*.css` | Regenerated via `manage.py collectstatic` (Whitenoise manifest storage) so the browser served the updated CSS. |
| `docs/reports/step-05m-sidebar-toggle-home-layout.md` | This report. |

## Checks

| Check | Result |
|---|---|
| `manage.py check` | PASS — `System check identified no issues (0 silenced).` |
| `manage.py collectstatic --noinput` | PASS — 1 updated file (app.css), 129 unmodified. |
| Verified the served CSS hash `app.584a64216901.css` in browser network log (fresh manifest, not stale) | PASS |
| Browser: unauthenticated `/` at 1440 viewport, full-page screenshot | PASS — balanced header (brand left; Log in, primary "Create account", Settings right), centered-rhythm hero with CTAs, 3 feature cards, tech badges, footer; no excessive empty space; zero console errors |
| Browser: `/dashboard/` authenticated at 1440 viewport | PASS — single topbar toggle aligned with breadcrumb; DOM check: `toggleCount: 1`, `.sidebar-collapse` element absent |
| Browser: toggle collapsed → clicked again → expanded | PASS — `state/aria-expanded/title` cycle correctly (`collapsed/false/“Expand sidebar”` → `expanded/true/“Collapse sidebar”`), rail renders 76px-centered icons, content margin settles 76px ↔ 232px, `localStorage['ctm-sidebar']` persists, no console errors |

## Verification setup (documented for transparency)

- Local PostgreSQL was down; started it the same way `start-web.ps1` does, plus a temporary current-source Django server on `127.0.0.1:8000` (DEBUG=False, process-only env/secret, no settings files or configuration changed). Both were stopped again afterwards.
- To authenticate the Dashboard in a real browser (no credentials were available), a temporary throwaway QA user `qa-05m-verify` was created in the existing **local dev database**, logged in via the real login form, and **deleted immediately after verification** (auth.User count 1 removed). This is transient dev-data cleanup usage of the existing local DB only — no schema, backend code or production data was touched. Existing users and their data were untouched.

## Blockers / notes

- None for this scope. Minor observation: sidebar header label measures show no overflow at settled width (scrollWidth 69 = clientWidth 69); truncation seen in screenshots occurs only mid-transition (180ms) while the rail animates.
- GNU gettext remains unavailable locally (as already reported in 05L); irrelevant here since no new translation strings were added.

## Git status at delivery

```text
 M static/css/app.css
 M templates/base.html
?? design-reference/
?? design-system/
?? docs/reports/step-05e-complete-ui-integration.md
?? start-web.bat
?? start-web.ps1
```

`design-reference/`, `design-system/`, `step-05e` report and start scripts are pre-existing untracked files, not from this task. No commit, push, reset or clean was performed. `staticfiles/` output is git-ignored.
