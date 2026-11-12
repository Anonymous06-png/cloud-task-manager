# Combined sidebar toggle controls — 2026-11-11

## Changes
- `templates/base.html`: expanded header now has BOTH the Fold/Flowspace collapse control and the existing separate far-right collapse button. Collapsed header has only the Fold expand control. Each logo control contains its appropriate state-specific toggle icon.
- `static/css/app.css`: logo icon swaps on hover/keyboard focus using existing motion/color tokens; returns to Fold when hover/focus ends. Only the icon changes, not the wordmark. Expanded right-side button and its alignment remain unchanged. Desktop state visibility and mobile logo/drawer controls preserved.
- Existing JavaScript reused without modification: all controls use `data-sidebar-toggle`, persistence, translated tooltips/ARIA and focus handoff. Dimensions, navigation, footer and other components unchanged; prior uncommitted work retained.

## Actual verification
- **PASS:** VI/EN shared-header renders confirm both expanded controls, the single collapsed control, correct Fold/open/close icons and existing mobile controls.
- **PASS:** Node VM checks separately activate the expanded logo, expanded right button and collapsed logo. All toggle correctly, persist state, update ARIA/tooltips and transfer focus correctly.
- **PASS:** source guards for logo hover/focus swap, far-right button alignment and desktop/mobile visibility.
- **PASS:** JavaScript syntax check; Django system check (0 issues, process-only settings/in-memory SQLite); `git diff --check` (LF→CRLF advisories only).
- No browser automation, visual screenshot comparison, backend/database changes or Git writes. Hover/blur appearance and responsive behavior were reviewed in source, not browser-tested.
