# Flowspace Dashboard polish (UI-01) — 2026-11-11

Scope: `templates/dashboard.html` and the dashboard-related rules in `static/css/app.css` only. Login, Register, Settings, task CRUD, backend logic, dependencies and locale files untouched.

## Changes

`templates/dashboard.html`
- Summary statistics restructured: each stat is now a big tabular number (`<strong>`) followed by a `.stat-label` span holding the existing icon and translated label. Same three counts (`pending_count`, `due_soon_count`, `completed_count`), same routes (`?status=incomplete`, `#due-heading`, `?status=completed`), same `aria-label`, same i18n msgids.
- The "View all" link in "Tasks to focus on" is now rendered only when `priority_tasks` is non-empty, so an empty dashboard no longer links to an empty filtered list.
- Empty-state CTA "Create a task" promoted from `btn secondary` to primary `btn` — it is the page's key action in that state. All other markup, includes and translated strings unchanged.

`static/css/app.css` (dashboard-scoped rules only)
- `.task-summary`: baseline-aligned stat band — numbers at `--step-2` in the heading font (weight 700, tabular-nums), muted labels with 15px icons, `min-height: 44px` touch targets, roomier `12px 48px` gaps, `24px` bottom padding and `28px` margin. Hover keeps the accent-green treatment on number and label.
- `.deadline-date` tiles switched from near-invisible `--color-shell` to `--color-accent-soft` with `--color-accent-text` month text (Flowspace green tint; dark-mode tokens resolve automatically). Day number stays `--color-text`.
- `.dashboard-tasks .empty-state` padding tightened to `44px 20px 56px` (scoped — task_list's shared `.empty-state` untouched).
- `.deadline-section h2 { scroll-margin-top: 32px; }` so the "Due soon" stat anchor does not land flush at the viewport top.
- Responsive bands: ≤760px stat gap `8px 24px`; ≤440px gap `8px 16px` and stat numbers down to `--step-1`.

Deliberately avoided (premium-frontend-product-designer): KPI cards, extra borders/shadows, new animation, new colors or fake data — hierarchy comes from type scale, spacing and the existing green tokens only.

## Actual verification

- **Django system check: PASS** — `System check identified no issues (0 silenced).` Run with the project `.venv` interpreter and temporary process-only environment values (`SECRET_KEY`, `DATABASE_URL` sqlite, `DEBUG=True`); no configuration files or database data touched.
- **Template compile: PASS** — `dashboard.html` and `includes/task_row.html` compile via `get_template` under the same throwaway env.
- **Render smoke test (both states): PASS** — with `LANGUAGE_CODE` forced to `en`: empty context renders the `empty-state` and no "View all"; populated context renders `priority-list`, "View all" and `recent-section`. (First attempt "failed" only because the project default language is `vi` — assertions were made translation-agnostic, not the template changed.)
- **`git diff --check`: PASS** — no whitespace errors; Git emitted the pre-existing LF→CRLF warnings on unrelated files (`.env.example`, `config/urls.py`, `requirements.txt`, `templates/registration/signup.html`).

No browser automation, no server restart, no translation compilation, no Git writes. Live VI/EN rendering, Light/Dark and responsive behavior remain for manual Brave verification; the running dev server picks up template/CSS edits on reload.

## Changed files

- `templates/dashboard.html` (modified — stats markup, conditional View all, empty-state CTA class)
- `static/css/app.css` (modified — `.task-summary` block, `.deadline-date`, `.deadline-section h2`, `.dashboard-tasks .empty-state`, two responsive-band lines)

## Git status (at report time)

HEAD `9e97879` on `main`. Pre-existing uncommitted work from earlier tasks remains (config/, locale/, start-web.ps1, home/auth templates, static assets, OAuth files, `frontend/`, earlier reports). This task adds no commits and only modifies the two files above; the new report file itself is untracked under `docs/reports/`.
