# Desktop sidebar toggle regression fix — 2026-11-11

## Changes
- `templates/base.html`: restored Fold + Flowspace as the left-side dashboard link, with a separate native collapse button on the far right. Collapsed Fold-only expand button and mobile controls unchanged.
- `static/css/app.css`: removed expanded logo-swap rules; collapse button uses existing icon-button styling, cannot shrink, and aligns right with `margin-left: auto`. Sidebar dimensions, branding and transition rules unchanged.
- JavaScript unchanged: existing toggle, persistence, translated tooltips/ARIA and focus handoff reused. No navigation/footer, backend or unrelated UI changes. Pre-existing work preserved.

## Actual verification
- **PASS:** VI/EN shared-header renders: correct logo/link/control order, separate collapse icon, Fold-only expand control and existing mobile controls.
- **PASS:** source checks for right alignment, absence of logo-swap rules and unchanged collapsed/mobile visibility rules.
- **PASS:** Node VM checks from both initial states: two-way toggling, persistence, ARIA/tooltips and focus handoff; JavaScript syntax check passed.
- **PASS:** Django system check (0 issues; process-only settings/in-memory SQLite); `git diff --check` (LF→CRLF advisories only).
- No browser automation, screenshot pixel comparison, database changes or Git writes. Visual layout/mobile behavior reviewed in source only.

## Git status
`main...origin/main`; no staged changes. Existing 18 modified tracked paths and prior untracked work retained. This task changes only the two already-modified implementation files and adds this report:
```text
 M templates/base.html
 M static/css/app.css
?? docs/reports/desktop-sidebar-toggle-regression-fix-2026-11-11.md
```
`static/js/app.js` remains pre-existing modified work, not written by this task.
