# TASK 05Q — Post-Logout Redirect Fix

Date: 2026-11-04

Project: `C:\ProjectCloud\cloud-task-manager`

Branch: `handoff/ui-wip-2026-11-04` (unchanged)

Result: **IMPLEMENTED — logout now redirects to `/login/`; focused logout tests PASS; system check PASS; `git diff --check` PASS.**

## Scope and inspection

Read the latest relevant report, `docs/reports/step-05p-workspace-login-redesign.md`, then inspected only:

- `config/settings.py` — authentication URLs.
- `tasks/urls.py` — logout route definition.
- `tasks/test_authentication.py` — logout and authentication tests.
- Logout-related references via read-only search.

Determination: logout uses Django's built-in `LogoutView` (`auth_views.LogoutView.as_view()` in `tasks/urls.py`). There is no custom logout view. Its post-logout destination therefore comes from `LOGOUT_REDIRECT_URL` in `config/settings.py`, which was `'/'`.

No Plan Mode, subagents, browser QA, Git write operations, branch switches, dependency installs, database configuration changes, infrastructure changes, or server start/stop operations were performed.

## Files changed

| File | Change |
|---|---|
| `config/settings.py` | Changed `LOGOUT_REDIRECT_URL` from `'/'` to `'/login/'` and updated the adjacent comment. No other settings changed. |
| `tasks/test_authentication.py` | Updated the existing logout redirect assertion from `reverse('tasks:home')` to `reverse('tasks:login')`. No new test was needed because a focused redirect test already existed. |
| `docs/reports/step-05q-logout-redirect-fix.md` | This new report. |

No templates, CSS, static files, models, migrations, views, dependencies, or infrastructure were changed. All pre-existing modified and untracked files were preserved.

## Behavior preserved

- Django `LogoutView` remains in use; session logout behavior is unchanged.
- Logout remains POST-only. The existing `test_logout_requires_post` still passes and confirms a GET returns `405` without clearing the session.
- CSRF protection is unchanged; the logout form still posts with its CSRF token.
- Login routing, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, registration, and dashboard access logic were not modified.

## Commands and actual results

Commands were run from the project root on Windows PowerShell.

| Command / check | Exit code | Actual result |
|---|---:|---|
| `python manage.py check` | 1 | System Python cannot import Django: `ModuleNotFoundError: No module named 'django'`. Environment limitation, not an application failure. |
| `./.venv/Scripts/python.exe manage.py check` with temporary process-only `SECRET_KEY` and a credential-free `DATABASE_URL` | 0 | **PASS** — `System check identified no issues (0 silenced).` |
| `./.venv/Scripts/python.exe manage.py test tasks.test_authentication.LogoutTests -v 2` with temporary in-memory SQLite and default production settings | 1 | Both tests received `301` instead of the expected logout response because production defaults enable HTTPS redirect. This was a test-environment issue, not a logout failure. |
| Same focused command with `DJANGO_ENV=local` | 0 | **PASS** — 2 tests ran, both passed: `test_logout_clears_session`, `test_logout_requires_post`. |
| `./.venv/Scripts/python.exe manage.py test tasks.test_authentication -v 1` with `DJANGO_ENV=local` | 1 | 17 tests ran; 14 passed and 3 unrelated pre-existing failures remain (see below). |
| `git diff -- config/settings.py tasks/test_authentication.py` | 0 | Diff contains only the redirect setting/comment and the single test assertion change. |
| `git diff --check` | 0 | **PASS** — no whitespace errors. Git emitted informational LF-to-CRLF warnings for modified tracked text files. |
| `git diff --no-index --check -- /dev/null docs/reports/step-05q-logout-redirect-fix.md` | 1 | Git reports the new file differs from `/dev/null` (expected), with zero whitespace diagnostics. A direct trailing-whitespace scan also found none. |
| Browser / visual / live-server logout QA | N/A | **NOT RUN** — not requested and outside scope. |
| Database-backed tests against PostgreSQL | N/A | **NOT RUN** — the focused tests used a temporary in-memory SQLite test database; no project database was changed or queried. |
| Migrations, `collectstatic`, dependency install, server commands | N/A | **NOT RUN**. |

Successful system-check command shape:

```powershell
$env:SECRET_KEY = & .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
$env:DATABASE_URL = "postgresql://127.0.0.1/cloudtask_check_only"
& .\.venv\Scripts\python.exe manage.py check
```

Successful focused test command shape:

```powershell
$env:SECRET_KEY = & .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
$env:DATABASE_URL = "sqlite:///:memory:"
$env:DJANGO_ENV = "local"
& .\.venv\Scripts\python.exe manage.py test tasks.test_authentication.LogoutTests -v 2
```

The temporary variables existed only in each child process environment. The in-memory SQLite database was created and destroyed by Django's test runner.

### Focused test result

```text
test_logout_clears_session ... ok
test_logout_requires_post ... ok

Ran 2 tests in 1.610s

OK
```

### Unrelated full-module failures

The full `tasks.test_authentication` run reported three failures unrelated to this change:

1. `LoginTests.test_login_failure_shows_error_and_no_session` expects the English error text `Please enter a correct username and password`, but the default UI language is Vietnamese.
2. `RegistrationTests.test_duplicate_registration_shows_form_error` expects the English username error, but receives the Vietnamese translation.
3. `ProtectedAreaTests.test_authenticated_user_can_access_dashboard` expects `Dashboard`, but the redesigned page now renders `Overview`.

These are existing English-text assertions that no longer match the Vietnamese default and the redesigned Dashboard. They were not modified because doing so is outside this task's scope.

## Git status at delivery

```text
## handoff/ui-wip-2026-11-04...origin/handoff/ui-wip-2026-11-04
 M config/settings.py
 M static/css/app.css
 M tasks/test_authentication.py
 M templates/base.html
 M templates/registration/login.html
?? design-reference/
?? design-system/
?? docs/reports/step-05e-complete-ui-integration.md
?? docs/reports/step-05m-sidebar-toggle-home-layout.md
?? docs/reports/step-05n-sidebar-public-header.md
?? docs/reports/step-05p-workspace-login-redesign.md
?? docs/reports/step-05q-logout-redirect-fix.md
?? start-web.bat
?? start-web.ps1
```

Only `config/settings.py`, `tasks/test_authentication.py`, and this new report are 05Q changes. `static/css/app.css`, `templates/base.html`, `templates/registration/login.html`, the reference folders, earlier reports, and start scripts predate 05Q and were preserved. No staging, commits, pushes, resets, cleans, merges, or branch switches were performed.

## Remaining risks

1. **Environment-dependent checks:** plain `python manage.py check` fails because system Python lacks Django. The successful check required the project venv plus process-only `SECRET_KEY` and `DATABASE_URL` values.
2. **Production HTTPS redirect in tests:** focused tests must run with `DJANGO_ENV=local` (or equivalent) or the test client receives `301` HTTPS redirects before reaching logout logic.
3. **No PostgreSQL test run:** the focused tests used in-memory SQLite, so database-backend-specific behavior was not exercised. The logout redirect does not depend on database features.
4. **Pre-existing full-suite failures:** three authentication tests still fail for unrelated language/redesign reasons and should be handled in a separate task.
5. **No browser QA:** the redirect was verified through Django's test client, not a live browser session.
6. **Historical report accuracy:** `docs/reports/step-03-authentication.md` documents the old `LOGOUT_REDIRECT_URL='/'` behavior. It was intentionally not rewritten because historical reports must be preserved.

## Next allowed step

Review the small diff, then commit through the project's normal approved Git workflow if desired. A separate follow-up may update the three unrelated authentication assertions, and browser QA of the logout flow can be scheduled separately.
