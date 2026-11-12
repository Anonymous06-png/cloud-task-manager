# Fold logo sidebar toggle — 2026-11-11

## Changes
- `templates/base.html`: desktop logo area is now a native button using the existing `data-sidebar-toggle` handler, translated action labels, `aria-controls` and synchronized `aria-expanded`. Separate desktop toggle removed. Mobile retains the dashboard logo link and existing drawer controls.
- `static/css/app.css`: approved Fold visible at rest; appropriate open/close icon replaces it on hover or keyboard focus. Visible focus outline, existing 44px target and short opacity transitions retained. Coarse-pointer devices show a small action indicator beside the Fold; hybrid mouse hover still swaps icons. Existing reduced-motion rule applies.
- This new report. JavaScript, navigation/footer, tokens, backend and other layouts unchanged. Prior uncommitted work retained.

## Actual verification
- **PASS:** shared template renders in VI and EN with exactly one desktop toggle, native button semantics, translated labels, approved Fold/open/close icons and existing mobile controls.
- **PASS:** Node VM checks against the existing toggle-handler code, from both expanded and collapsed initial states: two-way click behavior, `ctm-sidebar` persistence, ARIA/action-label synchronization and theme preservation.
- **PASS:** `node --check static/js/app.js`.
- **PASS:** Django system check — no issues (0 silenced), using process-only check settings and in-memory SQLite; no database writes.
- **PASS:** `git diff --check`; LF→CRLF advisory warnings only.
- Scoped Web Interface Guidelines review: native action button (Enter/Space provided by browser), decorative icons hidden from assistive technology, visible focus, touch target/discoverability, explicit opacity transitions and reduced-motion support. No outstanding findings in the changed header rules.
- No browser automation or Git writes. Visual hover/focus/touch behavior and mobile drawer operation were not browser-tested; mobile handlers and persistence code are unchanged.

## Git status
Branch `main...origin/main`; no staged changes. The existing 18 modified tracked paths and prior untracked work remain. Task-specific status:
```text
 M templates/base.html
 M static/css/app.css
?? docs/reports/fold-logo-sidebar-toggle-2026-11-11.md
```
Both tracked files were already modified before this task. `static/js/app.js` remains a pre-existing modification and was not written by this task.
