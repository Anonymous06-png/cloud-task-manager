# Sidebar header adjustment — 2026-11-11

## Changes
- `templates/base.html`: expanded logo retains its collapse interaction. Collapsed mode shows the original Fold dashboard link beside a separate, labeled expand button; the logo no longer swaps to an expand icon.
- `static/css/app.css`: collapsed header stays horizontal. A 30px logo, 26×44px button and 2px gap fit inside the existing sidebar (58px controls within 59px header content). State-specific controls are hidden appropriately; existing focus outlines and transitions retained. Mobile logo/drawer behavior unchanged.
- `static/js/app.js`: transfers focus to the newly visible toggle after activation. Existing persistence and ARIA synchronization reused.

## Actual checks
- **PASS:** VI/EN shared-header renders; correct Fold/collapse markup, separate native expand button, translated label and existing mobile link/close controls.
- **PASS:** Node VM checks from expanded and collapsed initial states: two-way toggling, persisted state, ARIA updates and focus handoff.
- **PASS:** `node --check static/js/app.js`; Django check (no issues, process-only settings/in-memory SQLite); `git diff --check` (LF→CRLF advisory warnings only).
- Scoped senior-frontend/Web Interface Guidelines review: native keyboard controls, translated accessible labels, visible focus and minimum 26px-wide expand target. Width fit checked from CSS dimensions, not browser measurements.

No browser automation, database changes or Git writes. Visual/touch/mobile behavior was not browser-tested. Navigation/footer, backend and page layouts untouched; existing uncommitted work preserved.
