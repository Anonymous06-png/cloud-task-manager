# UI-09 — Task List micro-interactions — 2026-11-12

## Delivered

- `static/css/task-list-motion.css` (new): isolated `.flowspace-task-list` motion rules. Rows enter with opacity and 6px translateY over 260ms, using UI-08's `cubic-bezier(0.16, 1, 0.3, 1)`. Global stagger is 0/35/70ms, capped at 70ms regardless of row/group count (330ms maximum sequence).
- Existing row hover backgrounds transition in 140ms without row movement. Action buttons and filters receive 160ms feedback: fine-pointer hover lifts 1px, press moves 1px down; filter keyboard focus also lifts 1px while retaining the existing focus ring. Links, task menus and checkbox feedback transition in 140ms. No existing hover color rules duplicated.
- Search focus-within ring fades via outline-color over 160ms; its existing color, 2px width and 2px offset remain unchanged. The unfocused outline is transparent and consumes no layout space. No input movement or delayed typing/search behavior.
- `static/js/task-list-motion.js` (new): dependency-free, page-local entrance markers only. Marks initially open groups' rows once per page render, skips closed groups, clears markers on animation completion/cancellation, group collapse or first keyboard focus. Reopening groups does not intentionally replay an entrance. Does not intercept navigation, forms, clicks, filters or CRUD; no timers, scroll listeners or persistent storage.
- `templates/task_list.html`: only adds the static tag import, isolated stylesheet and deferred script. Assets are imported at the existing content block, avoiding edits to the shared base template.

No layout, spacing, typography, content, translations, existing colors, search/filter/pagination URLs, shared row markup, CSRF fields, focus outlines or responsive breakpoints changed. Existing Light/Dark styles remain authoritative. Animation is opt-in under `prefers-reduced-motion: no-preference`; reduced motion explicitly disables targeted animation/transitions/transforms. No hidden default state, forwards fill, loops or permanent compositing hints. Without JS or CSS, all content remains visible and functional; without JS, only the CSS feedback enhancements apply, not entrance motion.

Read the two requested reports, current Task List template, directly related styles and Dashboard motion reference. No shared CSS, Dashboard, sidebar, Settings, Profile, backend, live database or dependency edits. Pre-existing user/agent changes preserved. No Git writes.

## Verification — exact commands and actual results

All commands ran from `C:\ProjectCloud\cloud-task-manager`. Django verification used process-only settings and an isolated in-memory SQLite test database, not the application's PostgreSQL database. Repository configuration was not edited.

### Django check — PASS, exit 0

```powershell
.\.venv\Scripts\python.exe -c "import os; os.environ.update(SECRET_KEY='ui-09-isolated-verification-only', DATABASE_URL='sqlite:///:memory:', DEBUG='True', DJANGO_SETTINGS_MODULE='config.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'check'])"
```

`System check identified no issues (0 silenced).`

### Focused Task List / action regressions — PASS, exit 0

```powershell
.\.venv\Scripts\python.exe -c "import os; os.environ.update(SECRET_KEY='ui-09-isolated-verification-only', DATABASE_URL='sqlite:///:memory:', DEBUG='True', DJANGO_SETTINGS_MODULE='config.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'test', 'tasks.test_task_list', 'tasks.test_task_crud.TaskFormRenderingTests.test_task_list_search_status_and_pagination_are_owner_scoped', 'tasks.test_task_crud.TaskFormRenderingTests.test_toggle_is_post_only_and_owner_scoped', 'tasks.test_task_crud.TaskCrudTests.test_create_task', 'tasks.test_task_crud.TaskCrudTests.test_update_own_task', 'tasks.test_task_crud.TaskCrudTests.test_delete_own_task', '--verbosity', '2'])"
```

15 discovered: **14 passed, 1 skipped**, no failures. Covered Vietnamese exact/partial searches, blank/nonmatching/literal queries, owner isolation, status combinations, seven-row pagination/order, invalid parameters, VI/EN labels, CSRF/return path, owner-scoped toggle and create/update/delete. Skip: `test_postgresql_unicode_case_variants`, explicitly PostgreSQL/ICU-only; not exercised by SQLite.

### Source/isolation guards — PASS, exit 0

```powershell
.\.venv\Scripts\python.exe C:\Users\Ky\AppData\Local\Temp\opencode\ui-09-source-check.py
```

External temporary script compares against `ui-09-baseline.json` in the same temporary directory. Confirmed the Task List template differs only by the intended static import and two asset tags (LF/CRLF normalized); SHA-256 hashes of shared app CSS, tokens, Dashboard template and Dashboard motion CSS are unchanged. Verified scoped selectors, motion/focus-only property allowlist, timing/reduced-motion guards and new CSS/JS trailing whitespace/newlines. No application records used.

### Entrance lifecycle logic — PASS, exit 0

```powershell
node --version
node C:\Users\Ky\AppData\Local\Temp\opencode\ui-09-motion-check.cjs
```

Both commands exit 0. Node version: `v24.14.1` (already installed; no packages installed). External script executes the shipped JS using Node VM and a mock DOM. Verified capped global stagger, exclusion of closed rows, unrelated animation-event guard, end/cancel cleanup, collapse/reopen without replay, first-focus interruption, reduced-motion early return and absent-page guard. These are logic tests, not actual browser animation tests.

### Scoped static detector — exit 0, limited result

```powershell
& 'C:\Users\Ky\.agents\skills\impeccable\scripts\impeccable.cmd' detect --json templates/task_list.html static/css/task-list-motion.css
```

Returned `[]`. Warned that the Django static template URL cannot be resolved by its HTML parser, so linked color/custom-property analysis is incomplete. CSS supplied directly as a target. Not a visual, runtime or accessibility certification.

### Whitespace — PASS, exit 0

```powershell
git diff --check
```

No whitespace errors; existing LF-to-CRLF advisory warnings only. Repeated after report creation. Untracked files are not included by this command; the separate source guard checks new CSS/JS whitespace.

## Git status

```powershell
git status --short
```

Exit 0. Repository already had extensive unstaged modifications and untracked files, including Dashboard motion and the newer QA-01 test fix, before UI-09. This task's paths only:

```text
 M templates/task_list.html
?? static/css/task-list-motion.css
?? static/js/task-list-motion.js
?? docs/reports/ui-09-task-list-micro-interactions-2026-11-12.md
```

The template was already modified; only the import and two tags were added to its working-tree version. No staged changes or Git writes introduced. All unrelated status entries were left intact.

## NOT RUN / limitations

- NOT RUN: browser automation, visual screenshots, computed Light/Dark/responsive checks, actual keyboard/touch/hover interaction, disclosure interruption rendering, runtime reduced-motion preference switching or disabled-animation simulation. Source and mocked logic checks do not establish pixel-level or cross-browser approval.
- NOT RUN: frame-rate/compositing/layout-shift measurements. No layout-driving motion properties introduced, but runtime performance was not measured.
- NOT RUN: PostgreSQL-specific Unicode case-variant test (skipped), live database checks, full test suite or unrelated audits.
- NOT RUN: external inspiration scraping, production collectstatic/deployment, dependency installation or Git write commands.
- Entrance runs once per document render; navigating/searching/filtering/paginating loads a new document and may run a fresh entrance. No animation persistence across page loads was requested or introduced.

Stopped after the scoped implementation, checks and new report.
