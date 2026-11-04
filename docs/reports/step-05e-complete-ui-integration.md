# Task 05E — Complete UI integration

**Date:** 2026-11-04 (Asia/Bangkok)
**Workspace:** `/workspace/cloud-task-manager`, branch `work`
**Status:** Implemented and browser verified; existing suite has four text assertion failures.

## Scope and environment

Integrated the approved light/dark dashboard, task list and settings direction into Django templates and vanilla CSS/JavaScript. The existing PostgreSQL Docker stack, authentication, sessions, ownership rules, forms, CSRF protection, stored task statuses and URLs remain in use. No schema, dependency, archived Node, WebI or deployment changes were made. The existing cloud checkout and local Start Skill were reused; named volumes and development configuration were preserved. No secrets were read or printed.

The Figma design-context tool was attempted once for file `yet2aySuPAwhOU1fCc2JSE` and returned “nothing selected; select a layer first.” The five supplied design exports and `step-05d-b-figma-design.md` were used as the visual source. The outdated HTML prototype was read for context, not copied as the UI.

## Files changed and reasons

| Files | Reason |
| --- | --- |
| `templates/base.html`, `static/css/app.css`, `static/js/app.js` | Shared accessible navigation, compact header, responsive mobile drawer, SVG icon system, light/dark palette, persisted theme and sidebar preference, focus styles and reduced-motion support. |
| `templates/dashboard.html`, `templates/includes/task_row.html` | Compact live statistics, owned priority queue, due-soon list, status controls and empty state. |
| `templates/task_list.html`, `tasks/views.py`, `tasks/urls.py` | Dedicated task list with owned search, status filters and pagination; owner-checked POST status toggle; legacy dashboard filter URLs still render the filtered list. |
| `templates/settings.html` | VI/EN language choice plus functional local browser theme and sidebar choices; authenticated account card and logout. |
| `templates/home.html`, `templates/task_detail.html` | Simplified public entry and task detail navigation in the new visual system. Existing create, edit, delete, login, registration and logged-out templates inherit the shared shell and form styles. |
| `locale/vi/LC_MESSAGES/django.po`, `.mo` | Added and compiled 56 new Vietnamese strings; template key scan found zero missing translations. |
| `Dockerfile` | Packages `locale/` in the application image. The existing environment-only Dockerfile override received the same `COPY` so the cloud rebuild exercised it. |
| `tasks/models.py` | Keeps developer-facing `__str__` stable across UI languages after the catalog is packaged; translated display labels remain unchanged. |
| `tasks/test_task_crud.py` | Three focused tests for owned dashboard counts, task list search/filtering and POST-only owner-checked status toggling. Existing assertions were preserved. |

## Behavior

Dashboard counts pending, completed and due-within-seven-calendar-days tasks from the current user only. The priority list shows up to five pending tasks ordered by due date, followed by recently completed tasks when space remains. Task list search checks titles, combines with the existing status values and paginates at seven rows. Task checkboxes submit POST with CSRF; the toggle endpoint checks task ownership. Existing create/edit/delete routes and validation remain intact.

Theme and sidebar preferences use browser `localStorage`; language continues to use Django's language cookie. Mobile navigation has an explicit menu button, `aria-expanded`, a dismissal overlay and Escape handling. Page copy defaults to Vietnamese and switches to English through the existing Django endpoint.

## Verification and evidence

| Check | Result | Actual command or evidence |
| --- | --- | --- |
| Docker image rebuild | **PASS**, exit 0 | `/workspace/cloud-task-manager-local/compose build app` (final build). |
| Start Skill, system check, health | **PASS**, exit 0 | `/workspace/cloud-task-manager-local/start.sh`; `manage.py check`: no issues; HTTP `/health/`: `ok`. |
| Migration check | **PASS**, exit 0 | `manage.py makemigrations --check --dry-run`: no changes detected. |
| Vietnamese catalog in rebuilt container | **PASS**, exit 0 | `manage.py shell` checked Vietnamese `Workspace` and `Use English for the interface`, then English `Workspace`. |
| Browser smoke | **PASS**, exit 0 | Headless Chromium/Playwright, 19 checks: registration, login/logout, dashboard, task create/edit/delete, search, completed filter, status toggle, VI/EN, theme and sidebar persistence, settings choices, 390 px mobile drawer/labels and no horizontal overflow. Temporary screenshots of light, dark/collapsed and mobile states were inspected. Disposable 05E accounts were deleted afterward. |
| Django suite | **FAIL**, exit 1 | `manage.py test --verbosity 0`: **55 run, 51 pass, 4 fail, 0 errors**. The three new UI flow tests pass. |
| Diff whitespace | **PASS**, exit 0 | `git diff --check`. |
| Figma design-context fetch | **BLOCKED** | Tool required an active Figma layer selection; supplied frames and design notes were used instead. |
| Azure/VPS deployment, merge | **NOT RUN** | Outside scope. |

### Test failures

Reported baseline failures still present, with assertions unchanged:

1. `LoginTests.test_login_failure_shows_error_and_no_session` expects English Django error text under Vietnamese default.
2. `RegistrationTests.test_duplicate_registration_shows_form_error` expects English Django error text under Vietnamese default.
3. `TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks` expects the old `No tasks found` empty-state copy.

One additional existing text assertion fails: `ProtectedAreaTests.test_authenticated_user_can_access_dashboard` looks for the literal English `Dashboard` in a Vietnamese page. The authenticated dashboard renders correctly in both languages and passed browser smoke; the assertion does not switch language before checking. No existing test assertion was changed. The initial 52-test onboarding baseline reported 49 pass / 3 fail; this final 55-test run is 51 pass / 4 fail after adding three passing tests and changing the visible dashboard copy.

## Remaining risks

- The four stale text assertions keep the full suite red until their language/copy expectations are explicitly reviewed. The product UI and existing assertions were left intact.
- Theme and sidebar choices are local to each browser, matching the no-schema-change boundary; they do not sync between devices.
- Browser checks were run in Chromium at desktop and 390 px mobile widths; other browsers and assistive technology were not tested.
- No automated pixel comparison to the Figma file was possible after the design-context selection error. The supplied light/dark/collapsed screenshots were used for visual inspection.

## Git status and next step

The work remains an uncommitted reviewable diff on branch `work`. Changed tracked files: `Dockerfile`, the two Vietnamese catalog files, `static/css/app.css`, `tasks/models.py`, `tasks/test_task_crud.py`, `tasks/urls.py`, `tasks/views.py`, and the base, dashboard, home, settings and task-detail templates. New files: `static/js/app.js`, `templates/includes/task_row.html`, `templates/task_list.html` and this report. The pre-existing untracked `docs/reports/cloud-environment-onboarding.md` was not changed. No pull request was created, no merge or deployment was performed.

Next allowed step: review the diff and the four language/copy assertions, then create a pull request if the team wants one. Deployment remains a separate decision.
