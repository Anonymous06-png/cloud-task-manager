# Cloud Task Manager — Task Dashboard Design Specification

**Task:** 05D — Modern Task Dashboard Design Prototype  
**Status:** Design-only prototype; implementation requires user approval  
**Prototype:** [`task-dashboard-prototype.html`](./task-dashboard-prototype.html)

## 1. Product intent

A focused, calm productivity workspace for a person managing their own tasks. The screen prioritizes the next action rather than turning the dashboard into a marketing page:

1. orient the user with date, greeting and current workspace;
2. show progress at a glance through four compact statistics;
3. let the user filter, complete, edit or delete a task directly from the list;
4. keep language and settings access visible without competing with task work;
5. retain the same task concepts already present in the application: all, incomplete, completed, due dates and CRUD actions.

Vietnamese is the default visible language. The prototype includes an intentionally small English toggle to prove that labels can expand without breaking the layout. Demo content is static and has no database or Django connection.

## 2. Selected skills and influences

The WebIOT skills directory was checked read-only at the readily available project path. No immediately accessible WebIOT skill files were found, so no WebIOT skill was copied or imported.

| Selected source | How it influenced this prototype |
| --- | --- |
| `frontend-design` skill | Used its emphasis on a clear visual direction, deliberate typography, tokenized color, responsive composition, distinctive details and production-grade states. The result uses a dark evergreen navigation rail, a lime action accent and a soft editorial canvas rather than a generic white SaaS screen. |
| Animate UI repository (read-only reference) | Used only as motion/design inspiration: reusable motion patterns, consistent transitions, progressive enhancement and animation that does not change the meaning of controls. Translated to small CSS transitions, a restrained page reveal and a toast; no React, Motion, Tailwind, shadcn or source code was copied. |
| Existing 05C application direction | Preserved the existing product vocabulary and workflow: Vietnamese default, VI/EN choice, dashboard/settings access, incomplete/completed states, due dates and task CRUD actions. The prototype is a visual proposal and does not alter Django templates or runtime styles. |

## 3. Visual system

### Color tokens

| Token | Value | Use |
| --- | --- | --- |
| `--navy` | `#18372F` | Sidebar, high-contrast utility panel, primary dark text foundation |
| `--navy-2` | `#234C40` | Supporting dark evergreen |
| `--lime` | `#C9EE75` | Primary create action, active navigation state |
| `--canvas` | `#F4F6F3` | Page background |
| `--surface` | `#FFFFFF` | Cards and controls |
| `--surface-alt` | `#F8FBF8` | Filter rail, hover surfaces |
| `--ink` | `#16251F` | Main text |
| `--ink-soft` | `#486057` | Secondary headings and breadcrumbs |
| `--muted` | `#7B8D86` | Supporting text, metadata |
| `--line` | `#DFE8E2` | Default borders and dividers |
| `--mint` | `#D9F2DF` | Completed states and positive support |
| `--mint-strong` | `#2C8A60` | Completed status text and progress |
| `--coral` | `#F06B55` | Due-soon emphasis, avatar and destructive hover |
| `--amber-soft` | `#FFF5DF` | Pending status background |
| `--blue` | `#4C79D8` | Keyboard focus ring |

Color is not the only status signal: status chips include text and a dot; completion also uses a checkmark and strikethrough.

### Typography

- **Body:** `Trebuchet MS`, then `Segoe UI`, then a sans-serif fallback. The slightly humanist shape supports a personal productivity tool and remains broadly available without a font request.
- **Display/heading treatment:** same family with heavier weight and tight negative tracking, keeping the prototype easy to reproduce in Django templates without a font dependency.
- **Hierarchy:** page title `clamp(2rem, 4vw, 3.45rem)`, section title `1.25rem`, task title `.88rem`, metadata `.70rem`, eyebrow `.69rem` uppercase.
- Vietnamese diacritics must remain intact; do not force uppercase on user-generated task titles.

### Spacing and shape

- Base rhythm: 4px increments, with common values 8 / 12 / 16 / 20 / 24 / 28 / 38.
- Sidebar width: 252px on desktop, collapsing into a horizontal navigation strip below 760px.
- Main content is fluid with a maximum comfortable reading density created by the two-column content grid.
- Radii: 10px control, 16px card, 24px primary panel, 99px status pill.
- Shadows are soft and low-opacity; borders carry most of the structure.

## 4. Component specification

### App shell and sidebar

- Evergreen rail with brand mark, active `Tổng quan`, `Công việc` count and `Đã hoàn thành`.
- The weekly focus card is supporting context, not a new feature: it visually summarizes the same task completion concept.
- Settings and help remain at the bottom on desktop.
- On mobile, the rail becomes a compact top strip; secondary focus/help card content is hidden to preserve task priority.

### Header

- Breadcrumb anchors the current location.
- VI/EN segmented control mirrors the existing 05C compact language switcher concept.
- Search, notification and profile controls are visible as familiar affordances, but are prototype-only and do not invent a new backend workflow.

### Welcome block

- Date, Vietnamese-first greeting, one-sentence focus copy and primary `Tạo công việc mới` action.
- The action is lime on evergreen-adjacent surfaces so it is easy to find without competing with the full task list.

### Statistics

Four cards map to the current task workflow: `Tổng công việc`, `Đang thực hiện`, `Đã hoàn thành`, `Sắp đến hạn`. Numbers are intentionally prominent; supporting trend text is secondary. The cards collapse to two columns on mobile.

### Task list

- Filter rail: `Tất cả`, `Chưa hoàn thành`, `Đã xong`; the active option has a raised surface treatment.
- Each row has a keyboard-accessible completion button, task title, status, due date and edit/delete actions.
- Pending, completed and due-today chips use separate text labels, color and dot indicators.
- Empty feedback is prepared for filter states.
- Demo interactions change only local prototype state and show a small status toast; no data is persisted.

### Supporting panels

- `Nhịp tuần này` provides a low-detail completion rhythm view, not a new analytics feature.
- `Lối tắt` groups the existing task/settings destinations and shows how a future implementation could keep frequent actions discoverable.

## 5. Interaction states

| State | Treatment |
| --- | --- |
| Default | Surface card, quiet border, readable metadata |
| Hover | Small lift or background shift, never color-only feedback |
| Press/activation | Existing browser press behavior plus short transition; do not move layout |
| Keyboard focus | 3px blue visible outline with 3px offset on links, buttons and controls |
| Active navigation | Lime fill, evergreen text, heavier weight |
| Active filter | White raised pill on soft rail with subtle shadow |
| Completed task | Green check, completed chip and strikethrough title; row remains available for reopening |
| Destructive action | Coral text/soft background on hover; future implementation must add confirmation before deletion |
| Empty filter | Centered message with enough padding; preserve filter context |
| Language change | `aria-pressed` changes on VI/EN controls; visible copy updates; toast confirms choice |
| Narrow viewport | Sidebar becomes horizontal navigation; task action labels become visible text in addition to icons |

## 6. Motion guidelines

- Motion is an enhancement layer. Content, hierarchy and controls remain understandable with all animation removed.
- Use short `150–200ms` ease transitions for hover/focus surfaces and a `480ms` one-time page reveal for the main content groups.
- Use transform only for small feedback (`translateY(-1/-2px)` or `translateX(2px)`); do not animate layout dimensions or cause content reflow.
- Use toast motion for confirmation, not as the only evidence of an action.
- Keep animation modular: future Django implementation should be able to remove `.page-reveal` or the transition tokens without changing markup semantics.
- `@media (prefers-reduced-motion: reduce)` disables meaningful movement and reduces transition/animation duration to near-zero.
- Avoid looping motion, parallax, auto-advancing panels and decorative animation behind task content.

## 7. Accessibility and responsive rules

- Use landmarks (`aside`, `nav`, `main`, `header`, `section`) and labels on navigation, filters and task lists.
- Use real buttons for state-changing actions and links for navigation.
- Preserve a visible `:focus-visible` ring.
- Provide `aria-label` text for icon-only controls and `aria-live="polite"` for the demo toast.
- Do not rely on status color alone; pair color with text, dot, icon or decoration.
- Maintain a minimum 44px target for primary controls and comfortable targets for mobile task actions.
- Desktop: fixed navigation rail + two-column content area. Tablet: sidebar narrows and supporting panels move below tasks. Mobile: horizontal nav, stacked content, two-column stats, full-width create action, and explicit text on task actions.
- Vietnamese labels should be allowed to wrap in future implementation; avoid fixed-width buttons and truncation for translated controls.

## 8. Implementation handoff boundary

This deliverable intentionally stops at the design prototype. The next allowed step is user approval followed by a separate implementation task. That task may adapt the proposal into Django templates and `static/css/app.css`, but must preserve existing URLs, form actions, CSRF behavior, translation tags, task ownership and status values. No application files were changed in 05D.
