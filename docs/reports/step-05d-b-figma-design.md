# Task 05D-B — Figma dashboard refinement

**Date:** 2026-11-04  
**Status:** Design complete; ready for review

## Scope

Design-only refinement of the Cloud Task Manager dashboard, task list, settings, light/dark themes, and expanded/collapsed navigation. The existing bilingual UI report, dashboard design report, HTML prototype, and supplied screenshot were used as references. The deliverable is an editable Figma prototype; this Markdown handoff is the only new repository file.

## Figma deliverable

- **File:** [Cloud Task Manager — Dashboard UI refinement](https://www.figma.com/design/yet2aySuPAwhOU1fCc2JSE)
- **Page:** `Product screens`
- **Required frames:** `Dashboard Light`, `Dashboard Dark`, `Sidebar Expanded`, `Sidebar Collapsed`, `Settings Light`, `Settings Dark`
- **Additional frames:** `Task List Light`, `Task List Dark`, `Dashboard Collapsed Light`, `Dashboard Collapsed Dark`, `UI System & Interaction Notes`
- **Reusable components:** `Component / Primary button`, `Component / Navigation item`, `Component / Task row`
- **Foundations:** `UI / Theme` color variables with Light and Dark modes; `UI / Spacing` variables at 4, 8, 12, 16, 20, 24, 32, and 40 px; eight text styles; eight reference paint styles.

## Design decisions

- Removed the prominent product-name label from the interface. The sidebar uses the neutral label **Không gian làm việc**; screen headings describe the current task area.
- Put the task list and due work ahead of ornamental metrics. The dashboard has a compact three-value summary, a practical task queue, and a short due list. The previous large greeting, circular card ornament, weekly chart, and shortcuts panel are absent.
- Used Vietnamese copy by default, with room for English labels and the existing VI/EN control. Task status and due dates have text labels so meaning does not depend on color.
- Designed the sidebar at **236 px expanded** and **76 px collapsed**. Full dashboard frames show both widths in light and dark themes. The Figma prototype links the sidebar toggles between these frames with 180 ms Smart Animate. Navigation and theme controls link the corresponding screens.
- Kept a calm neutral canvas, restrained green action color, clear card boundaries, and a compact Inter type scale. Inter is available in Figma; the source HTML's Trebuchet MS/Segoe UI stack was not available in the Figma font list.
- Settings shows the existing language choice and proposed appearance/sidebar preferences. Appearance and sidebar preferences are design proposals, not claims about current Django functionality.
- The UI system frame documents sidebar behavior, theme and language handling, task controls, and reduced-motion guidance. Spacing rules are captured in the `UI / Spacing` variables. The Figma controls and notes are intended as a straightforward template/CSS handoff.

## Intentionally not done

No Django template, stylesheet, JavaScript, Python, backend, database, Docker, Azure, or deployment file was modified. No implementation code or browser test was run. Task checkbox, search, filters, and settings choices are visual interaction specifications; they do not operate on live application data in Figma. No Animate UI source code was copied.

## Verification

**PASS — Figma structure and visual review.** The file contains eight editable 1440 × 900 full screens plus the standalone sidebar and UI system frames. An Figma structural audit found editable text in every screen, no image-filled or flattened full-UI nodes, the three named components, both color modes, eight text styles, eight paint styles, and **30 linked prototype controls**. All audited text uses Inter. Screenshots of the dashboard in both themes, task list in light mode, settings in both themes, collapsed sidebar, full collapsed dashboard in light mode, and UI system were inspected; clipping found in the first task-list and settings passes was fixed and checked again.

**Repository boundary:** the only intended repository change from this task is this new report. Browser behavior, production accessibility, and Django integration remain unverified because implementation was out of scope.

## Blockers

None for the Figma design. Figma does not verify how the proposed appearance and sidebar preferences will be persisted in the existing app; that is an implementation decision for a later task.

## Next allowed step

Review and approve or revise the Figma prototype. A separate implementation task may then adapt the approved frames into Django templates and CSS while preserving existing language handling, task actions, URLs, CSRF protection, and stored status values.
