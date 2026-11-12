# Desktop sidebar header correction — 2026-11-11

## Changes
- `templates/base.html`: collapsed desktop header contains only the approved Fold, as a native expand button. Expanded header restores Screenshot 2's arrangement: Fold + Flowspace dashboard link at left, separate collapse button at right. No icon replacement on the expanded logo and no external expand icon.
- `static/css/app.css`: removed obsolete icon-swap/side-by-side expand styles. Collapsed Fold uses the existing centered 44px target. Existing header dimensions, branding, focus styles, sidebar transitions and mobile controls retained.
- `static/js/app.js`: updated focus handoff between collapsed Fold and expanded collapse button; existing persistence and state synchronization unchanged.

## Actual results
- **PASS:** VI/EN shared-template rendering: Fold-only expand control, separate translated collapse button, non-toggle logo/wordmark link, correct header order and existing mobile controls.
- **PASS:** Node VM checks from expanded and collapsed initial states: two-way toggling, persisted `ctm-sidebar`, ARIA labels/expanded state and focus handoff.
- **PASS:** JavaScript syntax check; Django system check (0 issues, process-only settings/in-memory SQLite); `git diff --check` (LF→CRLF advisories only).
- No browser automation or screenshot pixel comparison performed. CSS visibility/layout reviewed in source; no backend/database or unrelated UI changes. Existing uncommitted work preserved; no Git writes.

## Git status
`main...origin/main`, no staged changes. Existing modified/untracked work remains; task-specific paths:
```text
 M templates/base.html
 M static/css/app.css
 M static/js/app.js
?? docs/reports/desktop-sidebar-header-correction-2026-11-11.md
```
All three implementation files were already modified before this task.
