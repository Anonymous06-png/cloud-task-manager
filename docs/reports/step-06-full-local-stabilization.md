# Task 06 — Full local stabilization

Date: 2026-11-05 (host logs); repository `C:\ProjectCloud\cloud-task-manager`.

## Result: PARTIAL acceptance — not full PASS

- **PostgreSQL regression suite PASS: 64/64**, no skips, failures or errors, 46.446 s. Baseline was **57 run / 55 pass / 2 fail**, 37.357 s.
- **Real local HTTP workflow PASS**: Register → Logout → Login → Create → List/detail → Edit → Change Status → Filter → app-only restart/persistence → Delete → Logout; invalid title and missing-CSRF rejection included.
- **Reported create-page HTTP 500 NOT REPRODUCED.** Authenticated GET returned 200 on both the untouched existing port-8000 process and a fresh PostgreSQL-backed port-8006 process. Authenticated real browser GET also rendered the form. There is no captured HTTP-500 traceback and no established root cause for that historical symptom. No speculative application fix was made.
- **Real browser verification PARTIAL**, documented separately below. Full browser CRUD/Login/Logout journey, sidebar behavior and desktop Dashboard visual acceptance were not completed. Do not treat HTTP or Django test-client success as browser success.
- Final Django system check, migration-drift check and tracked whitespace check PASS.
- No Plan Mode, subagents, Git writes, branch switch, dependency change, `.env` change, schema change, production/security-setting change, database reset, Docker/WSL/cloud operation or publication.

## Inputs and starting state

Read `CLAUDE.md`, latest reports 05S, 05R and 05T, `docs/requirements.md`, runtime/test helpers, relevant forms/models/views/routes/templates/tests/settings, and local PostgreSQL/PGPASSFILE memories. No `AGENTS.md` found by the workspace-parent search. No 06A report present in `docs/reports/`.

Initial actual Git status: clean `main...origin/main`, HEAD `a9c301b` (05T report). Existing source/settings/launchers and earlier reports were preserved.

05T supersedes the 05S test count: it records two stale assertions, not one. Both reproduced against PostgreSQL in this task.

## Environment and safe runtime configuration

| Item | Verified value |
| --- | --- |
| OS/shell | Windows 10.0.26100 x64; Git Bash, PowerShell for listener inspection |
| Python | existing `.venv/Scripts/python.exe`, 3.11.9 |
| Django | 5.2.18 |
| PostgreSQL | 16.15, Visual C++ build 1944, 64-bit |
| Real app database | `cloudtask_dev`, role `cloudtask_app`, `127.0.0.1:55432` |
| Regression database | existing isolated `cloudtask_test_04k`, same role/server; asserted vendor, name, host identity and owner before tests |
| Authentication | existing `%LOCALAPPDATA%\CloudTaskManager\pgpass.conf`, never displayed |
| Fresh server | `127.0.0.1:8006`, `runserver --noreload`, existing local configuration, DEBUG=False |
| Local security settings | `DJANGO_ENV=local`, ALLOWED_HOSTS localhost/127.0.0.1; secure-cookie/HTTPS defaults false for local HTTP as already designed; no settings file change |
| Migration state | all existing migrations applied in dev; `makemigrations --check --dry-run` says no changes |
| Static serving | hashed CSS/JS returned HTTP 200; collected files byte-equal to current source |

Existing port-8000 listener PID **14592**, command `python.exe manage.py runserver 127.0.0.1:8000 --noreload`, was identified but never stopped. PostgreSQL listener PID **13292** remained unchanged, listening on 127.0.0.1 and ::1. The temporary task-owned app PID was **18648**, then **11040** after restart. Only these owned background tasks were stopped, using TaskStop. These are intentional killed processes, not clean-exit claims.

Process-only secret configuration and QA passwords were generated randomly. The fresh app used the same temporary signing key across its restart. No secret values or cookie values are included in this report. No `.env` was present in the initial directory listing and none was created.

Django's runner warned that it could not connect to the maintenance `postgres` database and would use the first configured PostgreSQL database instead. The only database configured for that test process was **cloudtask_test_04k**; identity and owner checks passed before the runner. `keepdb=True`, `interactive=False`, and explicit TEST.NAME retained the isolated database; **no SQLite substitution**, no dev database selected by the test runner, no database creation/drop/reset request. TestCase data was transactional. No migrations needed applying.

## Reproduction and confirmed root causes

### Reported `/tasks/create/` 500 — unconfirmed

1. Called the current `task_create` view using RequestFactory with an unsaved authenticated user: render returned **200**, without creating users/sessions or tasks.
2. Started fresh owned process on free port 8006 with actual PostgreSQL configuration.
3. Registered a unique QA account through real HTTP and logged in; authenticated GET `/tasks/create/` returned **200**. Invalid bound form also returned **200** with no created task; valid create persisted correctly.
4. Logged the same new QA account into the untouched existing server on 8000; authenticated GET `/tasks/create/` returned **200** there too.
5. Real in-app browser registration created a separate account; after app-only restart, authenticated browser GET `/tasks/create/` returned a fully rendered form with all four fields, CSRF-protected form and Save/Cancel.

There was no exception to sanitize. A failure traceback cannot honestly be supplied. The initial anonymous browser visit redirected to Login as expected; it was not an authenticated reproduction. No claim that the user's earlier 500 is fixed or explained. A matching request/session/time and sanitized original traceback would be needed if it recurs.

### Two confirmed test defects — corrected

1. `TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks` expected the removed English `No tasks found`. Current correct Dashboard uses translated `Your list is clear.` with an empty pending list. Updated assertion to the current VI translation and added empty-context/count/create-link checks. No Dashboard markup or behavior changed.
2. `FoundationSmokeTests.test_task_model_str` assumed `Completed` was always English. The existing model intentionally calls translated `get_status_display()`, and Vietnamese is the default. Test now checks gettext-based expected display in **both vi and en**. No model or translation catalog changed.

## Changed files

| File | Change |
| --- | --- |
| `tasks/test_task_crud.py` | Correct stale Dashboard assertion; add seven focused regression/security tests |
| `tasks/tests.py` | Correct model string assertion for both supported languages |
| `docs/reports/step-06-full-local-stabilization.md` | New report, no earlier report overwritten |

Seven new tests cover: create GET in VI/EN with all fields and CSRF; edit GET with saved values; ignoring submitted owner ID; invalid edit status/date preserving database values; create/edit/toggle/delete CSRF rejection preserving records; POST-only/owner-scoped toggle; owner-scoped search/status/pagination and malformed filter/page/search handling. Existing auth, ownership, invalid-input, CRUD and filter tests remained enabled.

No functional application defect was confirmed; **no changes** to forms, models, views, routes, templates, CSS, JavaScript, settings, translations, requirements, Docker, Gunicorn or database schema. SQL used by task code remains Django ORM parameter binding; diagnostic SQL consisted of constant identity statements without external-input interpolation.

## Exact commands and exit codes

Commands ran from the repository. Temporary scripts and logs live outside it in:

`C:\Users\Ky\AppData\Local\Temp\ctm-task06-20261105`

Define the following literal command abbreviations for this table (not persisted shell changes):

```text
PY = ./.venv/Scripts/python.exe
RUN = C:/Users/Ky/AppData/Local/Temp/ctm-task06-20261105/runtime.py
HTTP = C:/Users/Ky/AppData/Local/Temp/ctm-task06-20261105/httpqa.py
```

`runtime.py` explicitly inserts the repository path after isolated Python startup, sets DJANGO_SETTINGS_MODULE/configuration per process, loads the existing external pgpass file, and generates a private temporary signing key. For `test` only, it selects/validates cloudtask_test_04k, sets TEST.NAME to that same name, and invokes `DiscoverRunner(verbosity=2, keepdb=True, interactive=False).run_tests(['tasks'])`. For dev modes it selects cloudtask_dev. Temporary HTTP scripts use stdlib HTTP with cookie jar and real CSRF tokens, not Django's Client. No credentials are embedded in command lines.

| Command/action | Exit/result |
| --- | --- |
| `pwd; git status --short --branch; ls -a; find .. -name AGENTS.md ...; find docs/reports ...` | 0; clean main; inputs located, no 06A |
| `PY --version` | 0; Python 3.11.9 |
| PowerShell `Get-NetTCPConnection -State Listen` filtered to 8000/8001/8006/55432; `Get-CimInstance Win32_Process -Filter "ProcessId=14592"` | 0; listeners and existing server command identified; no secret-bearing environment dump |
| `PY -I -B RUN preflight` | 0; PostgreSQL identity verified, check clean, all migrations applied |
| `PY -I -B RUN reproduce` | 0; CREATE_RESPONSE 200; no traceback |
| `PY -I -B RUN test > .../baseline-tests.log 2>&1` | **1**; 57 run, 55 pass, 2 assertion failures, 37.357 s |
| `PY -I -B RUN serve` (first) | background; PID 18648; intentionally stopped with TaskStop, status killed |
| `PY -I -B HTTP before > .../http-before.log 2>&1` | **0**; real HTTP chain and DB before marker passed; existing-server create also 200 |
| `PYTHONIOENCODING=utf-8 PY -I -B RUN test > .../final-tests.log 2>&1` | **0**; 64 run, 64 pass, 46.446 s; check clean; no migrations to apply |
| PowerShell listener inspection, then `PY -I -B RUN serve` (second) | port 8006 absent before restart, new PID 11040; PG and port 8000 unchanged; intentionally stopped at end with TaskStop |
| `PY -I -B HTTP after > .../http-after.log 2>&1` | **0**; matching persisted task, delete, logout, protected redirect and health passed |
| `PYTHONIOENCODING=utf-8 PY -I -B RUN check` | **0**; calls `check`, then `makemigrations --check --dry-run`: no issues/no changes |
| `PY -I -B .../final-evidence.py` | **0**; PostgreSQL identity; both collected assets match source; task 5 absent; two new QA account passwords rotated |
| `git diff --stat; git diff -- tasks/test_task_crud.py tasks/tests.py; git status --short --branch` | 0; scoped test changes only before report creation |
| `git diff --check` after final source edits and checks | **0**; informational LF-to-CRLF warnings only |

One baseline log contains Windows-encoded translated failure output and could not be reopened with Read after completion. A read-only isolated Python decode extracted its ending, confirming `Ran 57 tests ... FAILED (failures=2)`. Final test log was explicitly UTF-8 and read successfully. No test failure was hidden or skipped.

## PostgreSQL and real HTTP evidence (not browser/test-client evidence)

New HTTP QA account: `task06-e4cea9c2`. Task **pk=5**, marker **`Task06 persistence eac3aaa5d7`**.

| Request/check | Actual result |
| --- | --- |
| GET `/`, `/register/`, `/login/` on fresh server | 200 |
| Valid registration | POST 302 → Dashboard GET 200; row created in PostgreSQL |
| Logout then explicit Login | POSTs 302 → Login/Dashboard GET 200 |
| GET `/tasks/create/` | 200 |
| POST create with empty title | 200 form; no task row created |
| POST valid create | 302 → Dashboard 200; owned row pk=5 present |
| GET `/tasks/`, `/tasks/5/`, `/tasks/5/edit/` | 200 |
| POST edit | 302; row description/date updated |
| POST `/tasks/5/toggle/` without CSRF | **403**, expected; valid token subsequently succeeds |
| POST toggle with CSRF | 302; row status completed |
| GET `/tasks/?status=completed&q=Task06%20persistence%20eac3aaa5d7` | 200; PostgreSQL state verified; detailed search/filter result membership also covered by isolated regression tests |
| Same-account Login and create GET on untouched port 8000 | 302 → Dashboard 200; create GET **200** |
| Restart only owned app | PID **18648 → 11040**; database PID 13292 and port-8000 PID 14592 unchanged |
| GET `/tasks/5/` after restart | 200, title and edited description in response; ORM values below match |
| GET delete confirmation, POST delete | 200, then 302 → Dashboard 200; ORM confirms row absent |
| POST logout, GET Dashboard | 302 → Login; protected Dashboard redirects `/login/?next=/dashboard/`, final 200 Login |
| GET `/health/` | 200 |

Exact database values both **before and after app-only restart**:

```text
pk=5
owner=task06-e4cea9c2
title=Task06 persistence eac3aaa5d7
status=completed
due_date=2027-01-03
description=Task06 edited and persisted
```

The HTTP helper automatically follows redirects; its final status 200 does not mean POST returned 200. Raw app logs separately show the 302 statuses listed above and the expected 403. A logged expected CSRF error supplies local request/error logging evidence. No 500 occurred in these logs. Repeated `/favicon.ico` requests returned 404 (non-mandatory cosmetic asset, not changed).

The isolated tests verify cross-user detail/edit/delete/toggle rejection and list/search separation, owner injection protection, invalid statuses/dates, anonymous access and CSRF on all mutating task routes. These security assertions are **test-client evidence**, not a claimed second-user browser attack test.

## Real browser evidence — PARTIAL, separate from HTTP/tests

Browser: ZCode in-app browser; one controlled tab. Desktop 1280×720; mobile 390×844. No external browser runner or hidden browser HTTP calls.

Executed:

1. Existing port-8000 anonymous `/tasks/create/` redirected to Login; redesigned Login DOM with username/password/CSRF-backed form and entry navigation observed. This does not verify authenticated Login submission.
2. Fresh port-8006 Home DOM and desktop screenshot inspected. Header/navigation and split Workspace preview render; lower content/CTA requires vertical scrolling on this short desktop viewport, consistent with prior known layout. No redesign attempted.
3. Header Register high-level click timed out; no navigation. Fresh snapshot and scoped count confirmed one visible destination. Direct navigation to its observed `/register/` URL rendered registration.
4. Entered randomly generated credentials through actual browser form controls. High-level Register submit click timed out; keyboard Enter did not produce verified navigation. Visible-node fallback `dom_cua.click` on the observed submit control subsequently worked: tab changed to `/dashboard/`; server log POST register **302**, Dashboard **200**. New account **`task06-browser-87fb7bcb`**, success message and owner identity verified in DOM.
5. Dashboard DOM included Overview, empty state, task navigation, count 0, one expanded Collapse sidebar control and Logout. Dashboard screenshot **timed out once**; no visual Dashboard PASS claim, no CSS workaround/retry loop.
6. After app-only restart, direct navigation to known `/tasks/create/` rendered authenticated form in the same browser session. Four fields/status choices, Save and Cancel present, **no HTTP 500**.
7. Changed viewport to **390×844**; mobile menu button and task form DOM observed. Measured document width **375**, viewport **390**, no horizontal overflow. Mobile screenshot succeeded: all task fields, status, Save and Cancel fit, text readable, no overlap visible in this form. This is **mobile Task Form layout evidence only**, not full mobile-site acceptance.

Screenshots (local session artifacts, not repository files):

- Home: `C:\Users\Ky\.zcode\cli\artifacts\sess_ffea609a-0808-46a0-b11e-50e2df0811af\call_4XR1eSfw5X1cchwdomxcfFob-tool-result-fb9ee792-d349-4978-ae85-b8e8db78e40f.png`
- Mobile form: `C:\Users\Ky\.zcode\cli\artifacts\sess_ffea609a-0808-46a0-b11e-50e2df0811af\call_cKLH2Cxhte9Ft21KvJ24Gzqv-tool-result-6aa42324-0400-4342-9a00-f1df2cd70a09.png`

**NOT COMPLETED in real browser:** explicit Login/Logout submission, task create/edit/toggle/filter/delete submissions, sidebar collapse/expand and mobile drawer interaction, desktop Dashboard visual check, full mobile Home/Login/Dashboard walkthrough, dark theme/keyboard/a11y matrix. High-level locator click failures were tool-actionability timeouts; the fallback submit worked, so no source-level navigation defect was established. These incomplete checks prevent full acceptance despite successful real HTTP/backend coverage. Bounded cycle ended rather than repeatedly working around browser tooling.

Browser snapshots unexpectedly included the generated password value for password inputs during diagnostic reads. This was a **throwaway newly generated fixture**, not an existing user credential; its account password (and the HTTP QA account password) was rotated to an undisclosed random value at the end. No such value is in the report or tracked files. Existing users/credentials were not touched.

## Mandatory feature coverage and limits

| Local application capability | Executed evidence |
| --- | --- |
| 1. Register/Login/authenticated workspace | isolated tests + real HTTP; browser registration/Dashboard only |
| 2. Create task with name/description/date/status | isolated tests + real HTTP/ORM; browser form GET only |
| 3. View/list own tasks | isolated tests + real HTTP detail/list; browser Dashboard only |
| 4. Edit tasks | isolated tests + real HTTP/ORM |
| 5. Delete tasks | isolated tests + real HTTP/ORM |
| 6. Change status and filter pending/completed | isolated tests + real HTTP/ORM (both filter states in tests) |
| 7. PostgreSQL persistence across app restart | exact matching owned marker/ID/fields before/after; real HTTP and ORM |

Additional local T1–T7-style checks: local URL, auth, CRUD, restart, health, invalid input and expected error/request logging all exercised. **No public URL/cloud deployment check was performed.** This does not update grading/production T1–T7 to PASS and does not claim Docker/Gunicorn deployment verification.

## Remaining failures, blockers and risks

1. **Reported HTTP 500 remains unexplained, not reproduced.** No sanitized exception traceback exists from this cycle; obtaining actual failing-request evidence is the next diagnostic requirement if it recurs. Do not call it fixed.
2. **Browser acceptance incomplete**, as explicitly listed above. Locator click timeouts and Dashboard screenshot timeout constrain confidence in the complete GUI path. A manual/working-browser final walkthrough remains necessary; HTTP/test-client PASS cannot substitute for it.
3. Maintenance-DB authentication warning remains in tests; the configured fallback was the verified isolated test database. No authentication or role privileges were broadened to suppress it.
4. Existing mixed VI/EN copy and generic Overview breadcrumb on task/registration pages remain cosmetic backlog; no UI changes authorized/made.
5. Expected favicon 404s remain. No impact on mandatory workflow observed.
6. Two new QA accounts remain in dev with **zero tasks** and rotated undisclosed passwords. This cycle deliberately did not delete user accounts or existing user data. Only newly created task 5 was deleted through the explicit CRUD acceptance flow.
7. Temporary scripts/private credentials/cookie files and logs reside outside Git in the named temp directory; treat them as private local QA material, not publication artifacts. The two old fixture passwords no longer authenticate after rotation. No temporary runtime secret is included here.
8. Fresh verification server stopped at completion, so browser tab at port 8006 will not refresh until an explicitly owned server is started again. Unknown existing port 8000 and PostgreSQL were preserved.
9. No dependency installation/upgrades, translation compilation, collectstatic, Docker build, Gunicorn execution, production/cloud test or security-scan publication gate run. None is claimed.

## Git status and next allowed step

Expected final status (verified after writing this new report):

```text
## main...origin/main
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
```

Source diff before report: **2 files, 99 insertions, 3 deletions**. No staged changes; no commit/push/reset/clean or branch change. Earlier reports untouched. Final report whitespace and Git status verification recorded by the closing command.

**Next allowed step:** review the bounded test/report diff and perform a manual or functioning-browser full mandatory GUI walkthrough. If the original 500 recurs, capture its exact URL/time/session context and sanitized server exception before editing application code. Stop the normal server only through its identified owning terminal when separately authorized; never kill an unknown process. Any Git publication, production/Docker/cloud task or broader UI work requires a separate explicit request.
