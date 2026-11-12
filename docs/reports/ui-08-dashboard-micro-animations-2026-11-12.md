# UI-08 — Dashboard micro-animations — 2026-11-12

## Outcome and scope

Implemented restrained CSS-only motion on the existing Flowspace Direction C Dashboard. No dependencies, JavaScript, colors, spacing, typography, breakpoints, task behavior or translation strings changed.

- NEW `static/css/dashboard-motion.css`: three summary cards enter once per page render using opacity and a 6px vertical transform over 260ms; delays are 0/35/70ms (330ms total). No looping, scrolling triggers, retained forwards fill or hidden default state.
- Fine-pointer hover: 2px summary-card lift and 1px action-button lift; active states return to rest. Card hover uses independent `translate` so entrance `transform` does not block feedback.
- Existing task-row background feedback transitions in 140ms without moving rows or their menus. Existing card borders, links, task actions and checkbox feedback receive bounded 140–180ms transitions. Existing hover colors remain authoritative.
- Motion is enabled only under `prefers-reduced-motion: no-preference`. An explicit reduced-motion rule removes animation, transitions and movement from the targeted Dashboard elements while preserving immediate feedback and focus styling.
- `templates/dashboard.html`: only added the `static` tag import and Dashboard stylesheet link. The link lives at the start of the existing content block because the shared template has no head extension block; no shared template edit was needed. Content remains visible if the stylesheet or animations are unavailable.
- All element selectors are scoped to `.flowspace-dashboard`; keyframe name is Dashboard-specific. No layout-driving properties, new color values, shadows, permanent `will-change` or new dependencies.
- Latest relevant report read: `docs/reports/dashboard-upcoming-timeline-2026-11-11.md`. Preserved the current Dashboard template, task-row include and directly related incumbent styles. Existing uncommitted work was not reverted or overwritten.

This task changed only the Dashboard template, new isolated stylesheet and this new report. No Settings, Profile, sidebar, backend, forms, live database or other-page edits. Tests used a process-only in-memory SQLite database; no application records or database files were touched. No browser automation or Git write commands.

## Verification environment

Working directory for every command below: `C:\ProjectCloud\cloud-task-manager`. Python: repository `.venv\Scripts\python.exe`. Verification settings were process-only; repository configuration and environment files were not edited.

Temporary verification artifacts outside the repository:

- `C:\Users\Ky\AppData\Local\Temp\opencode\ui-08-dashboard-baseline.json`: pre-edit Dashboard template and SHA-256 hashes of shared `app.css` / `design-tokens.css`.
- `C:\Users\Ky\AppData\Local\Temp\opencode\ui-08-dashboard-verification.py`: source guards, staticfiles discovery, four baseline/current server-template render comparisons, and optional pre-edit stale-test reproduction. CRLF/LF normalized for template comparison only.

## Exact verification commands, exit codes and results

### Django check — PASS, exit 0

```powershell
.\.venv\Scripts\python.exe -c "import os; os.environ.update(SECRET_KEY='ui-08-isolated-verification-only', DATABASE_URL='sqlite:///:memory:', DEBUG='True', DJANGO_SETTINGS_MODULE='config.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'check'])"
```

Result: `System check identified no issues (0 silenced).`

### Focused Dashboard tests — 8 passed, 1 pre-existing failure, exit 1

```powershell
.\.venv\Scripts\python.exe -c "import os; os.environ.update(SECRET_KEY='ui-08-isolated-verification-only', DATABASE_URL='sqlite:///:memory:', DEBUG='True', DJANGO_SETTINGS_MODULE='config.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'test', 'tasks.test_task_crud.TaskCrudTests.test_dashboard_shows_only_current_users_tasks', 'tasks.test_task_crud.TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks', 'tasks.test_task_crud.TaskStatusFilterTests', 'tasks.test_task_crud.TaskAnonymousAccessTests.test_anonymous_cannot_access_dashboard', 'tasks.test_authentication.ProtectedAreaTests', '--verbosity', '2'])"
```

Nine tests ran. Ownership isolation, all four existing status-filter tests, anonymous access protection and authenticated Dashboard access passed. The sole failure is `test_dashboard_shows_empty_state_when_no_tasks`, which expects translated `Your list is clear.` instead of the incumbent approved Dashboard's `Start with one clear next step.` No copy, tests or behavior were changed to mask this mismatch.

### Pre-edit failure reproduction — same existing failure, exit 1

```powershell
.\.venv\Scripts\python.exe C:\Users\Ky\AppData\Local\Temp\opencode\ui-08-dashboard-verification.py --baseline
```

Result: the same single empty-state test fails on its stale assertion with the pre-edit Dashboard supplied via a process-only in-memory template loader. This confirms the focused-suite failure predates UI-08. One test, one failure; output was captured to avoid dumping an entire unrelated shared-page render.

### Dashboard source and VI/EN render checks — PASS, final exit 0

```powershell
.\.venv\Scripts\python.exe C:\Users\Ky\AppData\Local\Temp\opencode\ui-08-dashboard-verification.py
```

Results:

- Template equals the pre-edit snapshot after removing exactly the new static import/link (normalized line endings).
- Shared `static/css/app.css` and `static/css/design-tokens.css` SHA-256 hashes match their pre-edit values.
- Django staticfiles finds the new stylesheet at the expected source path.
- Source checks confirm Dashboard-only selectors and motion-only property allowlist, finite entrance, stagger, reduced-motion guards and no forwards fill / infinite loop / `transition: all`.
- EN empty, EN populated, VI empty and VI populated template renders are identical to pre-edit output except the stylesheet link. Each still has three summary cards; populated examples retain escaped titles and task-detail links. These are server-template checks with temporary in-memory context objects, not browser or live-data checks.
- First invocation exited 1 due to the temporary harness comparing mixed CRLF/LF text without normalization. Corrected only the external verification harness, reran the same command, and all checks passed. No application fix was needed.

### Scoped static motion/design detector — exit 0, limited result

```powershell
& 'C:\Users\Ky\.agents\skills\impeccable\scripts\impeccable.cmd' detect --json templates/dashboard.html static/css/dashboard-motion.css
```

Result: `[]` findings. Warning: the detector cannot resolve the Django `{% static ... %}` stylesheet URL while parsing the template, so linked color/custom-property analysis is incomplete. The stylesheet was also supplied directly; Django staticfiles discovery was checked independently above. This is not a rendered UI, accessibility or performance certification.

### Whitespace check — PASS, exit 0

```powershell
git diff --check
```

Run after implementation and again after this report was added. No whitespace errors; Git emitted existing LF-to-CRLF advisory warnings. Ordinary `git diff --check` does not include untracked files.

### Git status — exit 0

```powershell
git status --short
```

Final status is listed below. `templates/dashboard.html` was already modified before UI-08; the two UI-08 additions are `static/css/dashboard-motion.css` and this report. All other listed work predates this task.

```text
 M .env.example
 M config/settings.py
 M config/urls.py
 M locale/vi/LC_MESSAGES/django.mo
 M locale/vi/LC_MESSAGES/django.po
 M requirements.txt
 M start-web.ps1
 M static/css/app.css
 M static/css/design-tokens.css
 M static/js/app.js
 M tasks/test_authentication.py
 M tasks/views.py
 M templates/base.html
 M templates/dashboard.html
 M templates/home.html
 M templates/includes/workspace_preview.html
 M templates/registration/login.html
 M templates/registration/signup.html
 M templates/settings.html
 M templates/task_form.html
 M templates/task_list.html
?? dashboard-task-list-polish-2026-11-11.md
?? docs/database-design.md
?? docs/google-oauth-setup.md
?? docs/reports/dashboard-upcoming-timeline-2026-11-11.md
?? docs/reports/database-design-verification-2026-11-09.md
?? docs/reports/desktop-sidebar-header-correction-2026-11-11.md
?? docs/reports/desktop-sidebar-toggle-regression-fix-2026-11-11.md
?? docs/reports/expanded-logo-to-toggle-restored-2026-11-11.md
?? docs/reports/flowspace-auth-layout-fix-2026-11-10-989780a6.md
?? docs/reports/flowspace-dashboard-polish-2026-11-11.md
?? docs/reports/flowspace-direction-c-brand-unification-2026-11-11.md
?? docs/reports/flowspace-home-free-start-cta-2026-11-10-989780a6.md
?? docs/reports/flowspace-home-preview-cta-2026-11-10-989780a6.md
?? docs/reports/flowspace-home-ui-regressions-2026-11-10-989780a6.md
?? docs/reports/fold-logo-sidebar-toggle-2026-11-11.md
?? docs/reports/google-signin-allauth-2026-11-10.md
?? docs/reports/oauth-env-autoload-startweb-2026-11-11.md
?? docs/reports/sidebar-collapsed-fold-expand-2026-11-11.md
?? docs/reports/sidebar-combined-toggle-controls-2026-11-11.md
?? docs/reports/ui-03-flowspace-dashboard-integration-2026-11-11.md
?? docs/reports/ui-04-stitch-task-list-integration-2026-11-11.md
?? docs/reports/ui-04-task-list-search-i18n-regressions-2026-11-11.md
?? docs/reports/ui-05-stitch-create-edit-integration-2026-11-11.md
?? docs/reports/ui-05-task-date-presets-2026-11-11.md
?? docs/reports/ui-06-flowspace-settings-integration-2026-11-12.md
?? docs/reports/ui-08-dashboard-micro-animations-2026-11-12.md
?? docs/reports/workspace-preview-assertion-fix-2026-11-10.md
?? frontend/
?? static/css/dashboard-motion.css
?? static/flowspace/
?? static/fonts/
?? static/js/task-form.js
?? tasks/context_processors.py
?? tasks/test_google_oauth.py
?? tasks/test_task_list.py
?? templates/includes/google_button.html
?? templates/socialaccount/
```

## NOT RUN / limits

- NOT RUN: browser automation, screenshots or browser-based Light/Dark, responsive, hover, touch, keyboard and runtime reduced-motion checks, per task constraint. Existing layout/color/focus definitions are unchanged; actual computed/browser behavior was not observed.
- NOT RUN: runtime animation-disabled/stylesheet-failure simulation. Visible fallback is established by source: no base opacity/visibility hiding; all animated rules opt in to no-preference.
- NOT RUN: frame-rate, compositing, layout-shift or low-end-device measurements. Only opacity/transform entrance and lightweight bounded feedback were implemented; performance was not measured.
- NOT RUN: full test suite, unrelated audits, external inspiration-site scraping, dependency installation, production collectstatic/deployment or live PostgreSQL checks. Outside scope.
- NOT RUN: Git add, commit, checkout, reset, stash, push or any other Git writes. Existing user/agent changes preserved.

Stopped after the requested Dashboard implementation, verification and new report.
