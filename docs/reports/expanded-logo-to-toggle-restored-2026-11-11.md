# Expanded Logo-to-Toggle restored — 2026-11-11

## Changes
- `templates/base.html`: expanded Fold + Flowspace is again a native collapse button. Fold displays normally; the existing collapse icon occupies the same logo area on hover/keyboard focus. Removed the redundant separate collapse control.
- `static/css/app.css`: expanded-control-only opacity swap, visible focus outline and token-based transitions. Existing reduced-motion support applies. Mobile retains its original logo link and drawer controls.
- Collapsed Fold button/behavior and JavaScript remain unchanged, including persistence, tooltips, ARIA synchronization and focus handoff. No navigation, footer, backend or other component changes; prior uncommitted work retained.

## Actual checks
- **PASS:** VI/EN header rendering; expanded logo/wordmark and collapse icon, no redundant button, collapsed Fold-only control and existing mobile controls.
- **PASS:** Node VM checks against unchanged handler code from both initial states: two-way toggle, persistence, tooltips, ARIA state and focus handoff. JavaScript syntax check also passed.
- **PASS:** Django system check (0 issues; process-only settings, in-memory SQLite) and `git diff --check` (LF→CRLF advisories only).
- No new screenshot attachment was visible in this request; implemented the described previous logo-to-toggle treatment. No browser automation or visual screenshot comparison performed. No Git writes or database changes.
