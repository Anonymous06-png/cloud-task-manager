# Report: Update outdated workspace_preview test assertion (2026-11-10)

Task: update the outdated `includes/workspace_preview.html` assertion in the
failing authentication test to match the approved Flowspace Login layout.
Follow-up to `docs/reports/google-signin-allauth-2026-11-10.md` (pre-existing
failure, §"Pre-existing failure").

## Change

`tasks/test_authentication.py`, `PublicEndpointTests.test_login_logout_entry_journey` (line 264):
replaced

```python
self.assertTemplateUsed(response, 'includes/workspace_preview.html')
```

with

```python
# The approved Flowspace login layout (2026-11 redesign) renders the
# standalone workspace-login panel; the workspace preview no longer
# appears on the login page.
self.assertContains(response, 'login-form-panel')
```

Rationale: the approved Flowspace login layout (uncommitted redesign) renders
the standalone `workspace-login`/`login-form-panel` panel and no longer
includes the workspace preview on the login page. The `login-form-panel`
marker is OAuth-mode independent (the Google button only renders when
credentials are configured). `workspace_preview.html` itself remains in use on
the home page and its home-page assertions are unchanged.

No production code, OAuth configuration, templates or other tests were
modified. No browser automation, no broad audits, no Git writes.

## Commands and results (actual)

Environment: project `.venv` (Django 5.2.18), local PostgreSQL 16 at
127.0.0.1:55432, tests against the pre-created `cloudtask_test_utf8_06b`
(`TEST['NAME']` pointed at itself, `keepdb=True`; `cloudtask_app` has no
CREATEDB privilege), `DEBUG=True` / `DJANGO_ENV=local` as `start-web.ps1` sets.

1. Affected test only — `tasks.test_authentication.PublicEndpointTests.test_login_logout_entry_journey`:
   `Ran 1 test in 0.926s` — **OK**, exit code **0**.
2. Focused suites, unconfigured mode — `tasks.test_google_oauth` + `tasks.test_authentication`:
   `Ran 33 tests in 13.294s` — **OK (skipped=5)**, exit code **0**.
   Count: **28 passed, 0 failed, 5 skipped** (the 5 enabled-mode tests correctly skip without OAuth credentials).
3. Focused suites, enabled mode (dummy `GOOGLE_OAUTH_*` generated at runtime in the test shell; no literals committed):
   `Ran 33 tests in 12.486s` — **OK (skipped=1)**, exit code **0**.
   Count: **32 passed, 0 failed, 1 skipped** (route-404 test, only valid unconfigured).

The previous failure (`test_login_logout_entry_journey` asserting
`workspace_preview.html` on the login page) no longer occurs.

## Git status (after this task)

Diff vs HEAD for this task: `tasks/test_authentication.py` only (+5/−2 lines,
of which one line — the `'Tidy work today.'` assertion at line 235 — was a
pre-existing uncommitted change from the Home redesign; this task changed only
the line-264 assertion plus its comment).

Untracked/modified tree otherwise unchanged from the previous report
(allauth integration files and pre-existing uncommitted work all preserved).
Nothing committed; no Git writes performed.
