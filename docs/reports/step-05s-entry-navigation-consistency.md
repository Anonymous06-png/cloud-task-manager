# Step 05S — Entry and navigation consistency

Date: 2026-11-04

Repository: `C:\ProjectCloud\cloud-task-manager`

Branch: `handoff/ui-wip-2026-11-04` (unchanged)

## Result

**Implemented; focused Django route/auth tests PASS (22/22), system check PASS, final whitespace check PASS. Browser QA PARTIAL. Existing port-8000 runtime still serves cached old Home and was not restarted.**

Read 05N, 05P and 05Q before editing. Inspected the entry routes/views, Home/Login/Dashboard templates, inherited shell/styles, authentication tests/settings and launchers. No Plan Mode, subagents, Git write operations, dependency updates, schema changes, PostgreSQL service operations, sidebar changes or cloud operations.

## Actual cause: template versus static versus running process

1. There is one existing root route: `config/urls.py` includes `tasks.urls`, whose empty path calls `views.home`. No competing Home route was found or added.
2. `home()` always rendered `home.html`, even for authenticated users. The template still contained the older hero, feature cards, technology badges and version footer. The 05P Workspace split composition existed only in Login. Asset refresh cannot substitute new HTML for that old template.
3. Static collection was **not stale in this checkout**: `staticfiles/staticfiles.json` mapped `css/app.css` to `css/app.938420a2ed96.css`, and that collected file matched `static/css/app.css` byte-for-byte. No stylesheet or collected asset was changed. No cache-busting query, DEBUG relaxation, storage change or collectstatic run was necessary.
4. A separate live-process issue was reproduced: after source edits, the existing `http://127.0.0.1:8000/` still returned the old hero/features/version footer. A fresh process at port 8001 returned the new Home. The launcher uses `DEBUG=False` and `runserver --noreload`; cached template loading/no process reload explains why saved template edits are not immediately reflected. The exact command line of the existing listener was not established; a listener at port 8000 with PID 22788 was observed. It was not stopped or modified.
5. `start-web.bat` contained literal `<CodeBlock ...>` wrappers and was not valid plain batch content. `start-web.ps1` printed `/` but did not open a browser. Neither launcher contained a Login-only bypass; none was added.

## Exact changes in this task

| File | Change |
|---|---|
| `tasks/views.py` | Home redirects authenticated requests to named Dashboard route; anonymous requests render Home. Removed unused landing-page feature/version context. Other view behavior untouched. |
| `templates/home.html` | Replaced the obsolete project-demo landing body with the existing Workspace split shell, welcome mark, description, Login/Register links and shared sample-task preview. Correct Home breadcrumb/title. No new assets or controls. |
| `templates/includes/workspace_preview.html` | New shared include extracted from the existing Login figure without changing its markup; loads i18n locally. |
| `templates/registration/login.html` | Replaced only the preview figure with the include. Re-expanding the include reproduces the initial Login template exactly, allowing CRLF/LF normalization. Form, CSRF, hidden next, errors and Login styling preserved. |
| `tasks/test_authentication.py` | Added five regression tests (authenticated entry pages, full entry journey, protected task paths, logout CSRF, external next). Expanded public-Home test to check template/components and Login/Register URLs. Updated three outdated assertions: translated duplicate-user message, semantic invalid-login error code, redesigned Dashboard template/Overview. Preserved prior 05Q logout assertion. |
| `start-web.bat` | Removed markup wrappers; retained PowerShell invocation and pause. |
| `start-web.ps1` | Uses `$PSScriptRoot`; opens exactly `http://127.0.0.1:8000/` once the public root responds with 200, through a bounded background readiness job; cleans up the job when runserver exits. Existing PostgreSQL, environment, collectstatic and server configuration retained. No authentication-state-dependent launcher behavior. |
| `docs/reports/step-05s-entry-navigation-consistency.md` | New report. |

`config/settings.py`, `static/css/app.css`, `templates/base.html` and their pre-existing changes were not edited; SHA-256 checks against the initial working files passed. Existing references/reports were retained. No changes to URL definitions, authentication redirect settings, task implementation, models or migrations.

## Verified destinations — Django test client

| Request | Result |
|---|---|
| Anonymous `GET /` | 200; `home.html` and shared Workspace preview; Login `/login/`, Register `/register/`; both destinations 200. |
| Authenticated `GET /`, `/login/`, `/register/` | Exact single redirect chain `[('/dashboard/', 302)]`; Dashboard template returns 200. |
| Valid `POST /login/` without next | Exact redirect to `/dashboard/`; authenticated session established. |
| Valid login with untrusted external next | Redirects to `/dashboard/`, not external destination. Django safe-next handling retained. |
| Authenticated `POST /logout/` | Exact single redirect to `/login/`, redesigned Login renders, `_auth_user_id` absent. |
| `GET /logout/` | 405; session remains authenticated. |
| Logout POST without CSRF | 403 with session retained. Login/registration missing-CSRF tests also PASS. |
| Anonymous Dashboard after logout | `/login/?next=/dashboard/`. |
| Anonymous task list/create/detail/edit/delete/toggle | `/login/?next=<requested path>` (toggle tested via POST). |

Safe internal `next` handling is intentionally retained; normal Login defaults to Dashboard without weakening protected-page return behavior.

## Commands, exit codes and results

All shell commands were run from the repository in Git Bash, using the existing `.venv/Scripts/python.exe` (Python 3.11.9). Process-only secrets were generated at runtime, never saved or printed. No dependency installs.

Configuration prefixes used:

```bash
# Test configuration (temporary in-memory database; no persistent DB changes):
SECRET_KEY="$(./.venv/Scripts/python.exe -c 'import secrets; print(secrets.token_urlsafe(48))')" DATABASE_URL=sqlite:///:memory: DJANGO_ENV=local

# System-check configuration (parseable placeholder; no DB connection requested):
SECRET_KEY="$(./.venv/Scripts/python.exe -c 'import secrets; print(secrets.token_urlsafe(48))')" DATABASE_URL=postgresql://127.0.0.1/cloudtask_check_only DJANGO_ENV=local
```

Each prefix was applied directly to the corresponding command, not persisted in shell configuration.

| Command/check | Exit | Actual result |
|---|---:|---|
| `pwd; git status --short; ls docs/reports/*05[nNpPqQ]*; ls` | 0 | Recorded initial dirty tree and reports. |
| Scoped `rg`, `ls`, `git diff --stat` and file reads | 0 | Located existing entry routes, auth settings, public CSS, tests and launcher. |
| `./.venv/Scripts/python.exe --version` | 0 | Python 3.11.9. |
| Inline Python SHA-256/manifest comparison | 0 | Initial file hashes recorded; collected stylesheet equals source. |
| Inline Python preview extraction | 0 | Shared include created; existing Login preview extracted unchanged. |
| Test prefix + `./.venv/Scripts/python.exe manage.py test tasks.test_authentication tasks.test_task_crud -v 2` | **1** | 43 tests: **42 PASS, 1 FAIL**, 33.293s. All 22 auth tests PASS. Task failure: `TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks`, `tasks/test_task_crud.py:81`, expects old English `No tasks found`; current Dashboard renders its redesigned Vietnamese empty-state heading/description. Task CRUD and ownership tests otherwise passed. Test database created/destroyed by test runner. |
| Test prefix + `./.venv/Scripts/python.exe manage.py test tasks.test_authentication -v 1` | **0** | **22 tests PASS**, 10.268s; no system-check issues. |
| Check prefix + `./.venv/Scripts/python.exe manage.py check` | **0** | `System check identified no issues (0 silenced).` |
| First `git diff --check` after tests | **2** | Found one new extra blank line at test-file EOF; removed it. The compound check command exited 1 because the whitespace check failed, despite Django check exit 0. |
| `powershell.exe -NoProfile -Command '<Get-NetTCPConnection/Get-CimInstance; Parser::ParseFile(start-web.ps1)>'` | **0** | Port-8000 listener observed; launcher parse returned `LAUNCHER_PARSE_PASS`. Not an end-to-end launcher run. |
| Inline Python preservation/AST assertions | **0** | Settings, stylesheet and base SHA-256 unchanged; Login re-expansion identical after newline normalization; modified Python parses successfully. |
| Test prefix + `./.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8001 --noreload` | N/A | Temporary fresh-process public-page browser check. Intentionally stopped via TaskStop after inspection; background task status `killed`, **not** a clean-exit claim. In-memory SQLite only, no migrations run in this server. Existing port-8000 process untouched. |
| Final `git diff --check` | **0** | PASS; informational LF-to-CRLF warnings only. |
| `git diff -- tasks/views.py templates/home.html`, `git diff --numstat`, `git branch --show-current`, `git status --short` | **0** | Read-only inspection; branch unchanged. |
| Final direct whitespace scan of new report/include/launchers | **0** | PASS: `UNTRACKED_WHITESPACE: []`; final `git diff --check` also returned 0 after report creation. Untracked files are not covered by plain `git diff --check`. |

No PostgreSQL-backed tests, production database queries, Docker build, dependency installation, translation compilation, collectstatic or end-to-end launcher execution were run. The supported 05Q in-memory SQLite test approach was reused. Test-runner application of existing migrations occurred only in the disposable test database, not any persistent project database.

## Browser QA — partial, not equivalent to test-client PASS

Browser available: ZCode in-app browser, viewport 1280 × 720.

- Existing port 8000 root: browser confirmed old Home HTML at `/` after edits. No claim of normal-runtime acceptance.
- Fresh temporary port 8001 root: browser confirmed `/`, Home breadcrumb, Workspace split layout, sample tasks and real Login/Register destinations in DOM.
- Desktop Home screenshot captured and inspected: Workspace header and split preview render with the existing green palette; content extends below the viewport. This is a limited desktop observation, not full responsive/accessibility acceptance.
- Screenshot artifact: `C:\Users\Ky\.zcode\cli\artifacts\sess_fb7f7716-b827-4848-9233-e16a0756cd8f\call_kj3mQjfCNlERhpcOdzKkIq2G-tool-result-27600bf5-7234-4caf-8c7f-d0fc6c3014cf.png`.
- Home header Login click: resulting DOM showed the redesigned Login; subsequent browser tab listing confirmed exact URL `http://127.0.0.1:8001/login/`.
- Header Register click from Login: browser locator click timed out. Subsequent tab listing and fresh snapshot still showed Login. **Browser Register navigation NOT VERIFIED**; no unchanged retry and no success claim. Server test-client Register navigation/rendering PASS.
- Real-account browser registration/login/Dashboard/logout/session journey: **NOT RUN**. Verified only with test client against disposable test DB.
- Mobile, dark theme, zoom, keyboard and full-page layout QA: **NOT RUN**.
- Temporary server stopped; the verification tab may consequently be unavailable on refresh.

## Remaining risks

1. **Restart required on normal runtime:** existing port 8000 still serves old cached templates. Saving source or hard-refreshing CSS is insufficient. The existing process was deliberately not killed.
2. **One unrelated task-test assertion remains failing:** old `No tasks found` text no longer matches redesigned/localized Dashboard. No task test or task implementation was changed to hide this result.
3. **Browser acceptance incomplete:** Register click timeout and no real browser auth/session test. No claim that the entire live journey passed.
4. **Launcher runtime not certified:** PowerShell parsing passed, but default-browser job behavior, startup conflicts, PostgreSQL startup and batch double-click were not executed end-to-end. Do not launch a second port-8000 process while the existing listener is running.
5. **Existing i18n backlog:** shared preview has mixed VI/EN copy. No manual .mo generation or translation workflow changes.
6. **UI reuse tradeoff:** Home intentionally inherits existing Login component spacing; its welcome/CTA area can sit low on short desktop viewports and requires scrolling. No new Home CSS or broad layout redesign was introduced.
7. No PostgreSQL/backend-specific or Docker validation in this bounded task.

## Git status at delivery

```text
 M config/settings.py
 M static/css/app.css
 M tasks/test_authentication.py
 M tasks/views.py
 M templates/base.html
 M templates/home.html
 M templates/registration/login.html
?? design-reference/
?? design-system/
?? docs/reports/step-05e-complete-ui-integration.md
?? docs/reports/step-05m-sidebar-toggle-home-layout.md
?? docs/reports/step-05n-sidebar-public-header.md
?? docs/reports/step-05p-workspace-login-redesign.md
?? docs/reports/step-05q-logout-redirect-fix.md
?? docs/reports/step-05s-entry-navigation-consistency.md
?? start-web.bat
?? start-web.ps1
?? templates/includes/workspace_preview.html
```

No branch switch, staging, commit, push, reset, clean or other Git state mutation. Pre-existing uncommitted work preserved.

## Next allowed step

Review this bounded diff, then explicitly authorize or manually perform the local port-8000 process restart using the existing launcher (after stopping the prior server through its owning terminal). Verify `/` first, then real browser Register/Login/Dashboard/logout and protected-page return behavior. Separately update the stale task empty-state assertion if authorized. No Git publication, cloud operation or broad redesign is authorized by this task.
