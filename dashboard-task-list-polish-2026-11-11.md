# Dashboard task-list polish — 2026-11-11

## Files changed
- `static/css/app.css` — only Dashboard-scoped task/status/upcoming rules.
- This report.

## Refinements
- Compact status pills: reduced vertical padding, rounded ends, subtle slate-blue tint and regular-weight text. Completed pills retain a distinct, restrained success tint. Same treatment on mobile.
- Upcoming items: lighter, borderless date markers, softer separators, tighter consistent spacing, and clearer day-label/task-title hierarchy.
- Completed titles: explicit muted color and thin line-through, retained on hover. Row controls and text stay fully readable; no whole-row opacity.
- Existing Light/Dark tokens reused. No template, data, routing, JavaScript, page-layout or backend changes. Pre-existing uncommitted work retained.

## Verification
- **PASS:** six authenticated Dashboard server renders (three existing accounts × VI/EN), using actual stored tasks in a PostgreSQL read-only transaction. Included pending and completed rows; checked status labels, completed classes, task action URLs, CSRF fields and language output. No records created or changed; no task-toggle POST performed.
- **PASS:** Django system check — no issues (0 silenced), using process-only check settings and in-memory SQLite.
- **PASS:** `git diff --check` — no whitespace errors; existing LF→CRLF advisory warnings emitted.
- **Limit:** checked accounts had no upcoming tasks. Populated Upcoming rendering and browser/computed-style verification (including visual Light/Dark and responsive appearance) were not performed. Upcoming changes are CSS-only; no fake data introduced.

No Git writes or browser automation performed.
