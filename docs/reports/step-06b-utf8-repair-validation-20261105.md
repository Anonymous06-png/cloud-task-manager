# Task 06B — UTF8 restore, validation, runtime cutover and preservation gate

Date: **2026-11-05**. Workspace: `C:\ProjectCloud\cloud-task-manager`.
Continuation of `step-06b-utf8-repair-continuation.md`; earlier reports were not overwritten.

## Outcome

**UTF8 functionality is repaired and verified on local port 8000. Final all-row preservation acceptance is BLOCKED.**

- Both new databases authenticated as `cloudtask_app`; both were empty before preparation.
- A fresh uniquely named source backup was taken after establishing an offline write boundary. The old backup was not reused as the cutover snapshot.
- Restore into `cloudtask_dev_utf8_06b` succeeded. **Before cutover, all 80 source rows in 11 tables, all primary keys, owners, 10 foreign-key relationships, and 10 sequence definitions/states matched.** Logical schema matched.
- Previously failing Unicode regression: **1/1 PASS**. Affected PostgreSQL suite: **65/65 PASS**, including that regression. These are 66 test invocations / 65 distinct tests, not 66 distinct tests.
- Real HTTP: **64/64 assertions across 46 requests PASS**, split between CRUD/security and corrected restart-persistence runs. No HTTP 500 in these requests.
- Browser: repeated Vietnamese/emoji creation, read/edit/delete, completed filtering, required input, missing CSRF, and persistence across a correctly owned restart verified. Browser click tooling needed DOM activation; this was not a pure native-click acceptance run.
- Current listener: **127.0.0.1:8000, PID 18428**, parent/supervisor **21348**, current user's ownership verified, connected to **cloudtask_dev_utf8_06b / UTF8**.
- **Closing strict preservation check failed, exit 5:** 1 of the 7 original `django_session` rows is absent from the live UTF8 target after signing-key changes and browser session activity. All original users/tasks and every original non-session row remain exact. The original database and fresh backup still contain all 80 original rows, including all 7 original sessions.
- Work stopped on that final data-equivalence gate. **No session was silently reinserted, no database reset/cleanup or rollback occurred, and no further database/runtime changes were made after the final blocker.** Read-only diagnostics and this report followed.

Do not describe the entire task as unconditionally complete. The functional Unicode repair and pre-cutover restore equivalence passed; the final literal all-row-preservation condition did not.

## Scope and unchanged state

No application/UI source changes, dependency installation, stack change, audit rerun, Git state-changing command, database creation/drop/reset, privilege/authentication change, or `.env` write.

- Root `.env` was absent at preflight and at closing check; none was created.
- `start-web.ps1` was not edited. It still selects **old WIN1252 `cloudtask_dev`** and generates a new `SECRET_KEY` per invocation. **Do not use it to restart the repaired runtime unchanged.**
- Existing modifications to `tasks/test_task_crud.py` and `tasks/tests.py` were preserved byte-for-byte by SHA-256 checks.
- All three earlier Task 06/06B reports were preserved byte-for-byte.
- Only this new report was added inside the repository. Scripts, logs and database archives are in the private external directory below.
- The read-only exploration agent located settings, test selectors and launcher behavior; it did not run tests or access databases.

Initial status:

```text
## main...origin/main
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
?? docs/reports/step-06b-task-create-post500-root-cause.md
?? docs/reports/step-06b-utf8-repair-continuation.md
```

## Private evidence and command notation

All Python shell invocations used the existing project environment, from the repository root, with `-I -B`. Trusted helper modules were explicitly added to `sys.path`. No downloaded code was involved.

For the exact commands below, these abbreviations expand as follows:

```bash
W='C:/Users/Ky/AppData/Local/CloudTaskManager/repair-evidence/task06b-20261105T003400Z-af01b85c'
P='C:/Users/Ky/AppData/Local/CloudTaskManager/postgresql16/binaries/bin'
PY='./.venv/Scripts/python.exe'
D="$W/cloudtask-dev-final-20261105T005007Z-1ced3f84.dump"
```

Authentication used the already-authorized exact scopes in:

```text
%LOCALAPPDATA%\CloudTaskManager\pgpass.conf
```

Scripts set `PGPASSFILE` to that path and remove inherited `PGPASSWORD`; they never read, print, copy or modify the password file. PostgreSQL commands were noninteractive (`--no-password`); no admin/maintenance-database credential fallback was attempted.

The archive contains private account/password-hash/session data. **Do not commit, upload or paste it.** Reports contain counts/hashes and synthetic QA identities, not passwords, cookies or session keys. Credentials and signing keys were generated in memory and not stored in files.

## 1. Identity, emptiness and ownership preflight

`preflight.py`: **exit 0**.

| Database | Address / port | User / owner | Encoding | Collation / ctype |
|---|---|---|---|---|
| cloudtask_dev | 127.0.0.1:55432 | cloudtask_app | WIN1252 | English_United States.1252 |
| cloudtask_dev_utf8_06b | 127.0.0.1:55432 | cloudtask_app | UTF8 | C |
| cloudtask_test_utf8_06b | 127.0.0.1:55432 | cloudtask_app | UTF8 | C |

Server version: **PostgreSQL 16.15**.

Each target had zero user relations, routines, custom types, large objects, prepared transactions, subscriptions and other connections. Only normal `public` schema (`pg_database_owner`) and default `plpgsql` extension were present. Emptiness was rechecked before the dev restore and before test migrations. No existing target objects were cleared to force a restore.

The source had 55 relations and 9 tasks (ID range 1–11), zero prepared transactions/subscriptions/large objects. All three source client TCP connections mapped to:

```text
Listener: 127.0.0.1:8000
Django PID: 2472
Parent: 13552, C:\ProjectCloud\cloud-task-manager\.venv\Scripts\python.exe
Actual child executable: C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe
Command: manage.py runserver 127.0.0.1:8000 --noreload
Owner: LAPTOP-214UR8HL\Ky
Creation: 2026-11-05T07:03:42.5056540+07:00
```

Before stopping it, listener address/PID, creation timestamp, command, parent command/executable and current-user ownership were checked again. PostgreSQL listener PID **18392** was not stopped or restarted.

## 2. Controlled write boundary and fresh backup

The boundary script acquired SHARE locks on all 11 source application tables, allowing reads/dump but preventing table writes. All observed application connections were idle before stopping the identified application. No unknown writer was terminated.

The first boundary attempt stopped the identified PID successfully but then reused PostgreSQL's transaction-cached `pg_stat_activity` snapshot and falsely still saw the old connections. It **exited 6 before backup/restore**, rolled back its lock transaction, and preserved all data. A new read-only connection and Windows TCP/process inventory showed no source clients, no listener, and both old Django processes exited. Subsequent checks explicitly call `pg_stat_clear_snapshot()`.

Fresh final snapshot boundary:

```text
2026-11-05T00:50:07.677088Z
Port 8000 stopped; zero other source connections
SHARE locks on all 11 source tables
```

Exact backup/restore commands executed by the private scripts:

```bash
"$P/pg_dump.exe" --no-password --host=127.0.0.1 --port=55432 \
  --username=cloudtask_app --dbname=cloudtask_dev \
  --format=custom --encoding=UTF8 --file="$D"

"$P/pg_restore.exe" --list "$D"

"$P/pg_restore.exe" --no-password --host=127.0.0.1 --port=55432 \
  --username=cloudtask_app --dbname=cloudtask_dev_utf8_06b \
  --exit-on-error --single-transaction "$D"
```

**All three exit codes: 0.** No `--clean`, `--create`, `--no-owner`, database deletion or overwrite was used.

Fresh archive:

```text
C:\Users\Ky\AppData\Local\CloudTaskManager\repair-evidence\task06b-20261105T003400Z-af01b85c\cloudtask-dev-final-20261105T005007Z-1ced3f84.dump
Bytes: 35913
SHA-256: f22c0bcf32606ef18d76363f08d3e22c47e9c7dff4e4aba5257c868a24b3c0b9
```

The earlier `ctm-task06b-20261105/cloudtask-dev-before-utf8.dump` was not modified or used as final cutover data. The fresh archive's hash was rechecked before validation and at the end. Archive index succeeded and actual restore succeeded; integrity is not inferred from a hash alone.

## 3. Restore comparison

Data was compared in memory as complete rows, using constant SQL and parameter-bound external values. Sensitive row values were not logged. Counts and SHA-256 summaries are retained privately.

| Table | Source / restored rows | Final target rows | Original rows still exact at closing |
|---|---:|---:|---:|
| auth_group | 0 / 0 | 0 | 0 / 0 |
| auth_group_permissions | 0 / 0 | 0 | 0 / 0 |
| auth_permission | 28 / 28 | 28 | 28 / 28 |
| auth_user | 10 / 10 | 15 | 10 / 10 |
| auth_user_groups | 0 / 0 | 0 | 0 / 0 |
| auth_user_user_permissions | 0 / 0 | 0 | 0 / 0 |
| django_admin_log | 0 / 0 | 0 | 0 / 0 |
| django_content_type | 7 / 7 | 7 | 7 / 7 |
| django_migrations | 19 / 19 | 19 | 19 / 19 |
| django_session | **7 / 7** | 10 | **6 / 7 — final blocker** |
| tasks_task | 9 / 9 | 18 | 9 / 9 |
| **Total** | **80 / 80** | **97** | **79 / 80** |

### Physical column-number false mismatch, diagnosed before cutover

Initial strict raw catalog comparison exited **5** on `columns, constraints`. Read-only diagnosis established the only difference:

- `django_content_type.app_label`: source physical `attnum=3`, restore `attnum=2`.
- `django_content_type.model`: source `attnum=4`, restore `attnum=3`.
- Unique-constraint attribute numbers changed `[3,4]` → `[2,3]`, while its definition remained exactly `UNIQUE (app_label, model)`.

A dropped historical source column leaves a physical slot; pg_dump does not recreate that slot. The semantic comparator mapped constraint attributes to actual column names and compared logical ordinal order, types/nullability/defaults/identity/generated flags, constraint definitions and all values. It did **not** ignore missing columns or data.

The corrected validation then passed:

- 11 tables / 80 full rows; all 11 primary-key sets exact.
- 52 live columns, 29 constraints, 34 indexes, 55 relations.
- All object ownership/ACL evidence matched; objects owned by `cloudtask_app`, `public` by `pg_database_owner`.
- 10 foreign keys, **zero orphans**, exact child-to-parent values.
- 10 sequence definitions, ownership/dependencies and `(last_value, is_called)` pairs exact; next values exceed existing maxima without consuming/resetting sequences.
- Logical schema SHA-256: `6fc6617c7d5bcfc564c8ab0aafebc3658079974073f5b869bedadf2ff6c5914f`.

Original task primary keys:

```text
1, 3, 4, 6, 7, 8, 9, 10, 11
```

Original task → user ownership edges:

```text
1→1, 3→4, 4→4, 6→10, 7→11, 8→11, 9→11, 10→11, 11→11
```

These remained exact at closing. Original user primary keys were `1,2,3,4,5,6,8,9,10,11`; all remained exact, including existing password hashes and other fields.

### Sequence evidence

| Sequence | Source / restored last_value | is_called | Next value at cutover | Final live target last_value |
|---|---:|---|---:|---:|
| auth_group_id_seq | 1 | false | 1 | 1 |
| auth_group_permissions_id_seq | 1 | false | 1 | 1 |
| auth_permission_id_seq | 28 | true | 29 | 28 |
| auth_user_groups_id_seq | 1 | false | 1 | 1 |
| auth_user_id_seq | 11 | true | 12 | 16 |
| auth_user_user_permissions_id_seq | 1 | false | 1 | 1 |
| django_admin_log_id_seq | 1 | false | 1 | 1 |
| django_content_type_id_seq | 7 | true | 8 | 7 |
| django_migrations_id_seq | 19 | true | 20 | 19 |
| tasks_task_id_seq | 11 | true | 12 | 22 |

Only normal new-user/new-task inserts advanced the target user/task sequences. Original source sequences remained unchanged. Final target next user/task IDs are 17/23; no collisions or orphan ownership relationships.

The source was compared again to the fresh snapshot while locks were reacquired, after tests, at boundary release **00:56:02.250645Z**, and at closing. **All 80 source rows/schema/sequences remain unchanged.** The app remained stopped during the short diagnostic lock gaps; no unaccounted source writes were detected.

## 4. Isolated PostgreSQL tests

Existing launchers hardcode the old test database, so they were not used unchanged. Private `utf8-tests.py` selects only `cloudtask_test_utf8_06b`, sets both `NAME` and `TEST.NAME`, verifies live identity, and overrides DiscoverRunner database setup/teardown to avoid CREATE, DROP, cloning and maintenance-DB fallback.

Preparation ran all **19 migrations** into the confirmed-empty UTF8 test database. `check` reported zero issues; `migrate --check` found no unapplied migrations. No dev users/tasks were copied to the test target.

All database-using cases were checked to be atomic `TestCase`, not non-atomic `TransactionTestCase`; no database-wide flush, sequence reset, or serialized database restore was allowed. Test teardown rolled back rows and closed connections. Normal test inserts can advance isolated test sequences; they were not reset.

```bash
PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/utf8-tests.py" prepare > "$W/test-prepare.log" 2>&1
PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/utf8-tests.py" regression > "$W/test-regression.log" 2>&1
PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/utf8-tests.py" suite > "$W/test-suite.log" 2>&1
```

| Run | Actual result | Exit |
|---|---|---:|
| Prepare schema / check / migration check | PASS | 0 |
| `tasks.test_task_crud.TaskCrudTests.test_sequential_unicode_task_submissions_persist_exactly_once` | **1 test, 0 failures/errors, 1.394 s** | 0 |
| `tasks.test_task_crud tasks.test_authentication tasks.tests` | **65 tests, 0 failures/errors, 46.690 s** | 0 |

The standalone Unicode regression makes five sequential submissions, including repeated Vietnamese text and emoji, and checks exact persistence and ownership. Suite counts: CRUD 29, authentication 22, foundation/configuration 14.

Closing test database: 28 permissions, 7 content types, 19 migration records; **zero users, tasks, sessions**, all other tables empty. Baseline counts and schema remained unchanged. Original `cloudtask_test_04k` was not used or reset.

## 5. Process-local cutover and restart

Only after restore equivalence and test success, the controlled runtime selected:

```text
DATABASE_URL=postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_dev_utf8_06b
PGPASSFILE=%LOCALAPPDATA%\CloudTaskManager\pgpass.conf
DJANGO_ENV=local
DEBUG=False
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
ALLOWED_HOSTS=localhost,127.0.0.1
PGAPPNAME=task06b-utf8-runtime
```

`SECRET_KEY` was generated in supervisor memory, never printed or persisted. The original launcher's key was not extracted from another process. **Existing signed sessions therefore could require sign-in again.** Each new child verifies exact database/user/host/port/UTF8/owner, invokes Django check and read-only migration check, then serves port 8000. Existing static assets were reused; no collectstatic/dependency work was performed.

### Failed wrapper restart — disclosed, not counted as persistence PASS

First supervisor PID 23516 launched Windows venv wrapper PID 21116, whose actual listener was PID 22920. The ownership inventory explicitly found this distinction. The first restart implementation nevertheless terminated the wrapper rather than managing its actual child. The supervisor refused to launch over occupied port 8000 and **exited 6**. This was an orchestration error, not successful restart evidence.

A subsequent read-only inventory found the wrapper, supervisor and child/listener all exited; no unrelated process was killed. The signing key was lost with that supervisor. The waiting first HTTP process was deliberately stopped rather than claiming its old session survived.

### Corrected directly owned restart — PASS

The replacement supervisor invokes the same installed base Python directly, explicitly using the repository's existing `.venv/Lib/site-packages`. This removes the extra Windows launcher wrapper; it does not install or change the stack.

```text
Launch ID: direct-20261105T011049Z-105d5f
Supervisor PID: 21348
Generation 1 listener: 20956
Generation 1 stopped: exit 1 from intentional Windows termination
Generation 2 listener: 18428
Generation 2 created: 2026-11-05T08:13:18.9140650+07:00
Owner: LAPTOP-214UR8HL\Ky
Django: 5.2.18
Database: cloudtask_dev_utf8_06b / UTF8 / cloudtask_app
```

The old PID was confirmed gone, the new listener's exact PID/parent/command/owner verified, and both real HTTP and browser sessions survived the restart using the same supervisor-held signing key. The current supervisor/runtime remain running; a running server does not have a completed exit code.

Current exact runtime command:

```text
C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe -I -B C:\Users\Ky\AppData\Local\CloudTaskManager\repair-evidence\task06b-20261105T003400Z-af01b85c\runtime-entry-direct.py
```

Do not launch that entry alone without its process environment. `runtime-supervisor-direct.py` contains the guarded configuration and can be consulted for a future explicitly authorized restart. It refuses an occupied port and uses unique log names. A new supervisor creates a new signing key; session continuity across supervisor exit/reboot is **not** provided.

## 6. Real HTTP and browser acceptance

### Real HTTP

`http-acceptance.py` used actual `http.client` requests to fixed loopback port 8000, not Django's in-process Client. Cookie/CSRF values remained in memory. Database assertions used read-only parameter-bound queries.

The first harness attempt had a local `http` variable shadowing the imported module: **exit 9 / UnboundLocalError before any HTTP request or QA writes**. The harness was corrected; the failed log was preserved under its original name.

Corrected CRUD/security phase:

- **39 requests, 54/54 assertions**.
- HTTP statuses: 200 ×18, 302 ×12, 403 ×4, 404 ×4, 405 ×1; **zero 500**.
- Six sequential creations: ASCII baseline, Vietnamese titles, emoji, repeated Vietnamese title; each added exactly one owner-scoped row with exact title/description/date/status.
- Unicode detail/read, edit, completed search/filter, toggle, delete confirmation and deletion.
- Empty title, 256-character title, invalid status/date, invalid edit: no unintended changes.
- Missing CSRF on create/edit/toggle/delete: 403, data unchanged.
- Other-user detail/edit/toggle/delete: 404, owner data unchanged.
- GET toggle: 405; anonymous create redirected to login.
- Deleted only fresh QA task ID 17; retained IDs 12–16.

That process was manually stopped after the wrapper-restart failure; it has no successful full-process exit. Its completed 54 assertions are not conflated with a completed persistence run.

Corrected separate persistence phase, `http-persistence.py`:

- **7 requests, 10/10 assertions, exit 0**.
- Created Unicode task ID 21 under a fresh QA account.
- Same HTTP session remained signed in after PID 20956 → 18428.
- Exact new Unicode row and all 16 earlier original/QA task rows present before that phase survived unchanged.
- Unicode task detail returned 200 after restart.

**Combined actual HTTP evidence: 46 requests / 64 passing assertions.** These are assertions, not additional Django test cases.

### Browser

ZCode in-app browser, real pages at `http://127.0.0.1:8000`, 1280×720. No external browser or server API substituted for the browser observations.

- Registration and task forms were filled via browser locators; generated passwords were not shown or saved.
- Native locator clicks on the home registration link and registration submit timed out; keyboard activation did not submit despite valid fields. Fresh snapshots confirmed state.
- DOM activation (`observedButton.evaluate(el => el.click())`) succeeded, issuing normal browser form requests/navigation. This fallback is disclosed; native click behavior is **not** certified by these results.
- Three sequential browser creations: IDs **18,19,20**, including the identical Vietnamese/emoji title twice. Counts progressed 1 → 2 → 3.
- ID 18 read with exact accents/emoji/description/date; edited to completed with new Unicode title and description.
- Required empty title triggered native validation; no submit occurred.
- Browser-origin request built from the observed form without its CSRF field returned **403**. This particular negative test used browser `fetch`, not a UI click; no token was exposed.
- ID 20 detail and delete-confirmation page inspected, then only that fresh QA row deleted. IDs 18/19 remained exact; completed filter showed ID 18 only.
- Fresh persistence browser account created ID **22**. After the corrected direct restart, reload retained the same authenticated account; title/link still present and detail page showed exact Vietnamese/emoji title and description.
- Read-only DB verification confirmed browser task values and no row from invalid/CSRF attempts.

No screenshots/layout audit were requested or performed. Browser DOM/navigation evidence does not claim a visual-layout audit. Runtime logs contain favicon 404 requests; no scope expansion to fix those assets.

## 7. Final preservation blocker and stop

At **01:15:48Z**, `final-preservation-check.py` exited **5**:

```text
An original row was modified/lost in UTF8 target: django_session
```

Read-only follow-up (`diagnose-postcutover.py`, exit 0) established:

- Original source still contains all 80 rows and original sequence states.
- In the target, all original non-session rows are exact, including all 10 original users and 9 original tasks.
- Of 7 original session rows, **6 remain byte-equivalent in values; 1 is missing; none of the remaining original rows changed**.
- Target has 4 new session rows, for 10 total. The old session's raw key/data were not disclosed.
- Session lifecycle changed after new signing keys/browser registrations. This is consistent with session rotation/invalidation, but no per-statement audit was captured to conclusively attribute the missing original session to a particular request. Do not claim its exact deletion cause was independently traced.
- Missing session remains in the unchanged old database and verified fresh archive.

No reinsertion, session re-signing, credential extraction, DB cleanup, additional runtime restart, or rollback followed this blocker. The last evidence collector is read-only, **exit 0**; that collector success does not clear the preservation failure.

Final UTF8 target: **15 users / 18 tasks / 10 sessions**, zero FK orphans. Original 9 task rows are intact. Five additive synthetic QA users and nine retained QA tasks remain; cleanup is not authorized/performed.

| QA user | User ID | Retained task IDs |
|---|---:|---|
| qa06b-http-af01b85c | 12 | 12,13,14,15,16 |
| qa06b-other-af01b85c | 13 | none |
| qa06b-browser-af01b85c | 14 | 18,19 |
| qa06b-persist-http-af01b85c | 15 | 21 |
| qa06b-persist-browser-af01b85c | 16 | 22 |

Generated QA passwords were discarded, not retained for later sign-in. Existing real users' credentials were not changed.

## 8. Exact orchestration command ledger

Commands below used the `$W`, `$PY`, `$P`, `$D` expansions defined above. The shell wrapper printed the command's exit code and exited with it. Background server statuses are distinguished from completed commands.

| Command | Actual exit / state |
|---|---|
| `git status --short --branch` | 0 |
| `powershell.exe -NoProfile -NonInteractive -File "$W/runtime-inventory.ps1"` | 0 |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/preflight.py" > "$W/preflight.log" 2>&1` | 0 |
| Python `ast.parse` of repair helper/boundary scripts | 0, syntax only |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/backup-restore-boundary.py" > "$W/backup-restore-boundary.log" 2>&1` | 6, stale activity snapshot; no backup/restore |
| `powershell.exe -NoProfile -NonInteractive -File "$W/stop-verified-runtime.ps1"` (inside previous command) | 0, identified PID stopped |
| Fresh read-only psycopg2 source-peer query + PowerShell TCP/process query | 0 / 0; zero source peers/listener |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/final-boundary.py" > "$W/final-boundary.log" 2>&1` | 5, raw physical catalog mismatch **after successful backup/restore** |
| pg_dump / pg_restore list / pg_restore commands in section 2 | 0 / 0 / 0 |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/diagnose-equivalence.py" > "$W/equivalence-diagnosis.log" 2>&1` | 0 |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/validate-and-hold.py" > "$W/validate-and-hold.log" 2>&1` | 0 after validated cutover and release |
| `utf8-tests.py prepare`, `regression`, `suite` (section 4) | 0 / 0 / 0 |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/runtime-supervisor.py" > "$W/runtime-supervisor.log" 2>&1` | initially served; later 6 on wrapper restart guard |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/http-acceptance.py" > "$W/http-acceptance.log" 2>&1` | 9, local harness error, no HTTP writes |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/http-acceptance.py" > "$W/http-acceptance-run2.log" 2>&1` | 54 assertions passed; later explicitly stopped while awaiting persistence |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/browser-db-verify.py" > "$W/browser-db-verify.log" 2>&1` | 0 |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/runtime-supervisor-direct.py" > "$W/runtime-supervisor-direct.log" 2>&1` | **RUNNING**, no final exit |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/http-persistence.py" > "$W/http-persistence.log" 2>&1` | 0, 10 assertions |
| PowerShell listener/owner/parent check after direct restart; old PID 20956 absence check | 0 |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/final-preservation-check.py" > "$W/final-preservation-check.log" 2>&1` | **5 — final session-preservation blocker** |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/diagnose-postcutover.py" > "$W/postcutover-diagnosis.log" 2>&1` | 0, read-only |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/collect-final-evidence.py" > "$W/final-readonly-evidence.log" 2>&1` | 0, read-only; blocker retained |
| `git --no-optional-locks diff --check` | 0 before report; only existing LF/CRLF notices |
| `git --no-optional-locks diff --stat` | 0; only pre-existing two test-file modifications |

Supervisor control files were created once with the Write tool, not secret-bearing shell commands:

- `release-boundary.json`: `{"unicode_regression":"PASS","affected_suite":"PASS","runtime_cutover":"validated"}`.
- `restart-generation-1.json`: first, unsuccessful wrapper restart request.
- `direct-20261105T011049Z-105d5f-restart-1.json`: corrected direct-child restart request.
- Both restart requests contained `{"reason":"verify Unicode task and session persistence"}`.
- `check-direct-restart.json`: `{"runtime_generation":2,"old_pid_exited":20956,"new_listener_pid":18428}`.

Read-only runtime queries used `Get-NetTCPConnection`, `Get-CimInstance Win32_Process`, and `Invoke-CimMethod ... GetOwner`. No process environment dump was performed. Current runtime/backup/test/DB evidence files above preserve exact argv, timestamps and exit events. Browser tool calls are in the session tool history, not shell commands; no fictitious browser exit code is assigned.

Automatic pre-write security hooks rejected two helper drafts; the final helper uses literal SQL and bound values. No rejected draft ran; no independent/full security audit was requested or rerun.

## 9. Rollback readiness and remaining risks

### Preserved rollback assets

- **cloudtask_dev / WIN1252**: all 80 original rows/schema/sequences unchanged; zero peer connections at closing.
- **cloudtask_test_04k / WIN1252**: catalog identity/owner preserved; not used for this run.
- Fresh complete source dump above: hash verified, archive index and restore verified.
- Old backup remains untouched.
- UTF8 dev/test databases retained; no drop/reset/recreation.

### Rollback is not a blind switch

The UTF8 target now contains new users/tasks, including characters WIN1252 cannot store. The old source is a safe **pre-cutover snapshot**, not a mirror of post-cutover writes. A lossless rollback would first require an explicitly authorized controlled boundary and new uniquely named **UTF8 target backup**, then reviewed reconciliation/handling of post-cutover writes. Do not replay UTF8-only values into WIN1252, discard them, or overwrite either database. No rollback was executed.

### Outstanding decisions/risks

1. **Final gate blocked on one original session row.** User decision is needed on whether normal session invalidation/rotation is an acceptable post-cutover difference, or whether further narrowly scoped session-preservation work is required. Do not silently recreate a stale session or claim literal all-row preservation.
2. **Startup persistence is not solved.** `.env` is absent/unchanged; repository `start-web.ps1` still targets WIN1252. Current repaired runtime is controlled by the private external supervisor, not a durable service. A separately authorized launcher/configuration change is needed to prevent accidental reversion after reboot/manual restart.
3. **Signing-key continuity.** Same-key child restart was verified; existing sessions were not preserved across supervisor/key replacement. A stable private key policy is a separate decision; no new key storage was silently introduced.
4. **Collation differs:** old English Windows locale → new C locale. Unicode storage/CRUD/security tests passed; locale-sensitive sort/case behavior was not exhaustively certified.
5. **QA residue:** five new accounts and nine retained tasks are intentional evidence. Only two just-created QA tasks were deleted in CRUD tests. No cleanup/reset of pre-existing data.
6. **Browser tooling:** native click/keyboard activation was unreliable; successful DOM activation/form/navigation and browser-origin CSRF checks are documented, not presented as pure user-pointer coverage. No screenshots/layout audit.
7. **Local scope only:** no cloud/Docker/Gunicorn deployment, OS reboot survival, full audit, load test or production certification was performed.
8. **Backup location:** private local evidence directory is not an off-machine disaster-recovery copy; publishing or moving sensitive archives requires separate authorization.

Current live URL: `http://127.0.0.1:8000/`.

## Closing repository status

Expected after this new report and verified by the closing checks:

```text
## main...origin/main
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
?? docs/reports/step-06b-task-create-post500-root-cause.md
?? docs/reports/step-06b-utf8-repair-continuation.md
?? docs/reports/step-06b-utf8-repair-validation-20261105.md
```

No staging, commits, push, reset, clean, branch change or publication. The next permitted step is a user decision on the documented final session-preservation blocker, not another restore or an automatic rollback.
