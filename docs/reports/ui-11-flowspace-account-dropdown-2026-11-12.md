# UI-11 — Flowspace account dropdown — 2026-11-12

## Scope and outcome

Integrated only the authenticated bottom-sidebar account disclosure and focused regression tests. Read the supplied reference folder's README, Light/Dark PNGs and HTMLs, Direction C document, UI-06 Settings report, live sidebar template/CSS/JS, relevant URL/logout configuration and focused authentication tests. The supplied design path is an extracted reference folder, not a ZIP file.

- Account button toggles a compact floating panel **8px above** the trigger, with viewport-bounded width/height and internal scrolling. Desktop rail and transformed mobile drawer positioning are handled separately.
- Real escaped authenticated full name (username fallback), username, optional email and username-derived initials; no sample identity or uploaded avatar.
- My Profile / Hồ sơ cá nhân is a native disabled button, explicitly marked Coming soon / Sắp ra mắt. No implemented application Profile route was found; no route or fake link was added.
- One Settings link and one POST/CSRF session-logout action in the normal sidebar panel. Existing `tasks:settings` and `tasks:logout` routes are unchanged. The separate visible sidebar Settings/Logout controls were consolidated, not duplicated from Stitch Dark.
- Separate `<noscript>` Settings and CSRF logout fallback; it is not displayed alongside normal scripted actions. Trigger/panel stay hidden until JS initializes.
- Native disclosure semantics (`aria-expanded`, `aria-controls`, labelled region), ordinary Tab order, optional ArrowDown/ArrowUp entry to Settings/logout, disabled Profile, and visible focus styles. No incomplete ARIA application-menu pattern.
- Closes on toggle, outside click, Escape, focus leaving, ordinary navigation activation and logout submission. Modified/cancelled link activations are not intercepted. Also resets on sidebar resizing/collapse/scroll, drawer closing, breakpoint changes and page lifecycle events.
- Reused the existing document click/Escape and sidebar navigation handlers. Mobile Escape closes the account panel first, then the drawer on a second Escape. Existing mobile focus trap excludes the inert closed panel.
- Light/Dark use live semantic colors; VI/EN use the current language. Scoped 160ms opacity/4px transform motion, with reduced-motion override.

Fold logo, sidebar widths, main navigation, collapse controls, public header, Dashboard/Task List/Settings layouts, theme persistence, authentication/session implementation and routes were not changed. No backend models, Profile editing/upload, dependencies, locale catalogs or migration files changed. No mock Dashboard, CDN, fake hrefs or reference scripts imported.

## Changed files (this task only)

| Path | Change |
|---|---|
| `templates/base.html` | Replace sidebar footer actions with disclosure, identity, disabled Profile, real Settings/logout and no-JS fallback. |
| `static/css/app.css` | Account-only scoped insertion: panel, actions, identity, focus/disabled states, themes and reduced motion. |
| `static/js/app.js` | Account state/positioning/focus; integrate into existing sidebar click, keyboard, navigation and mobile handlers. |
| `tasks/test_sidebar.py` | Seven focused Django regressions. |
| `tasks/test_sidebar.cjs` | Dependency-free Node harness executing real `app.js`; 14 behavior/source checks, not a browser. |
| `docs/reports/ui-11-flowspace-account-dropdown-2026-11-12.md` | New report. |

The three implementation files were already dirty at task start. Their prior content was copied to `C:\Users\Ky\AppData\Local\Temp\opencode\ui11-baseline` before editing. Inline baseline assertions verified that all template content before the sidebar footer and after `</aside>` is unchanged and that CSS changes consist exclusively of the account block insertion. Existing unrelated work was preserved.

## Commands, exit codes and actual results

Working directory: `C:\ProjectCloud\cloud-task-manager`. `python` below means `.venv\Scripts\python.exe`.

Every Django command used these **process-only** PowerShell environment values, without editing settings or runtime environment files:

```powershell
$env:SECRET_KEY='ui11-isolated-check-key-not-for-runtime'
$env:DATABASE_URL='sqlite:///:memory:'
$env:DEBUG='True'
$env:DJANGO_ENV='local'
```

| Command | Exit | Actual result |
|---|---:|---|
| `python manage.py check` (initial and final) | 0 | No issues; 0 silenced. |
| `python manage.py test tasks.test_sidebar tasks.test_authentication.LogoutTests --noinput --verbosity 2` (initial) | 1 | Nine tests discovered; one new test failed in three EN subtests because the test request had not selected the app's language cookie. |
| Same nine-test command with `--verbosity 1` (first retry) | 1 | Accept-Language alone still produced VI; same three EN subtest failures. |
| Same nine-test command with `--verbosity 1` (after test cookie fix) | 0 | All nine passed. Only test request language selection changed to fix these failures. |
| `python manage.py test tasks.test_sidebar tasks.test_authentication.LogoutTests tasks.test_authentication.PublicEndpointTests.test_login_logout_entry_journey tasks.test_authentication.PublicEndpointTests.test_logout_without_csrf_keeps_session --noinput --verbosity 1` | 0 | **11 tests passed**, final run, 3.665 seconds. |
| `node --check static/js/app.js` (initial and final) | 0 | Syntax valid. |
| `node tasks/test_sidebar.cjs` (two runs) | 0 | **14 focused JS/source checks passed** each time. |
| Inline Python task-start baseline/whitespace assertions, piped to `python -` | 0 | Template shell unchanged outside footer; CSS account-only insertion; all five changed code/test files have no trailing whitespace. |
| `git diff --no-index -- C:\Users\Ky\AppData\Local\Temp\opencode\ui11-baseline\app.js static/js/app.js` | 1 | Expected comparison exit: task-specific JS differences displayed/reviewed, not a validation failure. |
| `git diff --check` | 0 | No whitespace errors; existing LF-to-CRLF advisory warnings only. |
| `git status --short --branch` / porcelain status-count query | 0 | Dirty working tree on `main...origin/main`, no staged entries; details below. |

Django coverage includes six authenticated renders (Dashboard, Task List, Settings × VI/EN), genuine escaped details, missing-name/email fallback, disabled/no-fake Profile, unique normal sidebar actions, hidden/inert/ARIA markup, Fold/navigation/collapse controls, anonymous login, no-JS CSRF markup, missing-CSRF rejection preserving authentication, valid-CSRF logout clearing the session, POST-only logout and existing login/logout entry journey. Existing migrations ran only inside Django's disposable in-memory test database; no runtime PostgreSQL data was touched.

Node coverage includes Light/Dark × expanded/rail/mobile setup, above-trigger geometry calculations, toggle/outside/Escape/focus closing, keyboard entry, native navigation and submission, modified/cancelled activations, mobile two-stage Escape and focus wrapping, drawer close/scrim/breakpoint cleanup, collapse persistence/focus, unavailable storage, theme choice, resize/scroll/page lifecycle resets, short-height/right-edge calculations and scoped motion source assertions. Geometry uses supplied mock rectangles, not browser layout.

## NOT RUN / risks

- **NOT RUN:** browser automation (explicitly prohibited), manual browser/visual comparison, computed-style/mobile/zoom verification, actual reduced-motion rendering, screen-reader or assistive-technology testing. The Node harness is not visual or browser certification.
- **NOT RUN:** full application suite, deployment/static collection, live PostgreSQL or production authentication/session testing. Focused Django checks used SQLite and process-only local settings.
- Remaining visual risk: confirm panel placement/clipping and focus appearance in real browsers, especially the transformed mobile drawer, short viewports and unusually long user details. Source implements bounded scrolling and wrapping; these have not been visually verified.
- Profile intentionally remains unavailable until a genuine route exists. No implementation blocker or remaining focused-test failure.
- No server restart, dependency changes, application migration command, Git staging, commit or push performed.

## Git status

Task-start status: **22 modified tracked paths, 41 untracked entries, zero staged entries**. Before this report: **22 modified tracked paths, 43 untracked entries, zero staged entries**. With this new report: **22 modified tracked paths, 44 untracked entries, zero staged entries**, on `main...origin/main`.

Task-specific status:

```text
 M static/css/app.css
 M static/js/app.js
 M templates/base.html
?? tasks/test_sidebar.cjs
?? tasks/test_sidebar.py
?? docs/reports/ui-11-flowspace-account-dropdown-2026-11-12.md
```

All other modified/untracked entries were present before this task and were left intact. No Git staging/commits/push. Stopped after the report and final requested checks.
