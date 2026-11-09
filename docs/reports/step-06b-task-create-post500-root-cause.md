# Task 06B — Task-create POST 500 root cause

Date: 2026-11-05. Repository: `C:\ProjectCloud\cloud-task-manager`.

## Current result: REPRODUCED / ROOT CAUSE CONFIRMED / FIX BLOCKED

**Not FIXED.** Real HTTP POST to the unchanged normal port-8000 server reproduces the 500 with valid Vietnamese input. The exact application save path raises PostgreSQL SQLSTATE **22P05**, `psycopg2.errors.UntranslatableCharacter`, wrapped in Django `DataError`.

**Both local databases were created with WIN1252 encoding.** Client encoding is already UTF8. WIN1252 cannot represent normal Vietnamese characters or emoji. Changing client encoding, refreshing templates, catching exceptions, or stripping/transliterating user text would not fix data storage correctly.

The correct repair is a **data-preserving migration into explicitly UTF8-created PostgreSQL databases**, followed by an explicitly authorized normal-runtime configuration switch/restart. PostgreSQL does not support converting a populated database's server encoding in place. **The user has now explicitly authorized the additive UTF8 repair and subsequent identified-runtime switch/restart.** A private backup has been created successfully, but no restore, database rename/drop/reset, configuration switch, server termination or restart has occurred. The current blocker is privileged database creation: the app role lacks CREATEDB/superuser capability, so local database-owner participation is needed; no credential discovery or privilege escalation was attempted.

## Scope and preserved work

Read Task 06 report and only relevant task-create source/form/model/migration/tests, then inspected live runtime and actual database metadata. Initial status:

```text
## main...origin/main
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
```

Task 06 changes are preserved. Added only a Unicode task-create regression in `tasks/test_task_crud.py` plus this new report. No application logic, template, UI, settings, dependencies, authentication, CSRF or validation change. No Plan Mode, subagents, Git writes, staging/commit/push/reset/clean, cloud/Docker/WSL action or `.env` write.

## Runtime ownership and database state

- Port **8000** listener: PID **2472**, owner **`LAPTOP-214UR8HL\Ky`**.
- Process: system Python 3.11 `python.exe manage.py runserver 127.0.0.1:8000 --noreload`.
- Parent PID **13552**: project `.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload`.
- Both are distinct from Task 06's earlier runtime PIDs. Neither was stopped/restarted or injected into.
- PostgreSQL listener: PID **18392**, 127.0.0.1/::1 port **55432**.
- Authenticated identity: **cloudtask_dev**, **cloudtask_app**, 127.0.0.1:55432. Existing external PGPASSFILE used without displaying contents.
- `SHOW server_encoding` → **WIN1252**; `SHOW client_encoding` → **UTF8**.
- `pg_database`: **cloudtask_dev and cloudtask_test_04k both WIN1252**, collate/ctype `English_United States.1252`.
- Role `cloudtask_app`: **rolcreatedb=false**, **rolsuper=false**.
- Initial task rows: **4**, ID min=1, max=6; sequence last_value=6/is_called=true. Sequence aligned; not a primary-key collision.
- Actual constraints: primary key on id; owner foreign key to auth_user(id). No extra noninternal triggers. Identity id, bigint; title varchar; description/status text-compatible fields and expected timestamps/date/user_id. No schema divergence explaining the failure.

## Exact reproduction: normal unchanged runtime

A new uniquely named QA account was registered through real HTTP with generated private credentials. No existing account/password was changed.

Account: **task06b-a451cf94**; task prefix: **Task06B 2b9f3928**.

The HTTP helper used cookie-jar sessions and actual CSRF tokens. Redirect following was explicitly disabled, so these are original response statuses, not final Dashboard statuses.

| Request | Actual result |
| --- | --- |
| GET `/register/` | 200 |
| POST valid registration | 302 `/dashboard/` |
| GET `/tasks/create/` authenticated | 200 |
| Five sequential ASCII-only task POSTs, due_date=2026-11-14 | **302 each**, `/dashboard/` |
| POST valid Vietnamese title `Công việc tiếng Việt – kiểm tra` and Vietnamese description | **500**, no Location header |
| POST empty title | **200**, controlled invalid form |
| POST invalid status | **200**, controlled invalid form |
| POST invalid date | **200**, controlled invalid form |

The 500 is tied to text representability, **not the ordinal number of the POST**. An ASCII submission can work first and Vietnamese submissions then fail repeatedly. This explains how Task 06's ASCII-generated fixtures passed despite a Vietnamese-facing app being broken.

### PostgreSQL record accounting

Direct ORM verification returned exactly **five** tasks for the new account, IDs **7, 8, 9, 10, 11**, titles exactly the generated prefix plus `valid 1` through `valid 5` in order. No extra records from the failed Vietnamese POST or the three invalid submissions. Existing four task records were preserved. The five new QA tasks remain for evidence; no records/accounts were deleted.

## Sanitized exception traceback

The existing server's owning terminal was not accessible through the shell tools and was not restarted. Instead, a diagnostic Python process used **the same existing cloudtask_dev database, current task_create view, TaskForm, model and QA owner** to call the server-side view with valid Vietnamese form data. It ran inside `transaction.atomic()` with rollback on success as a safety measure. It reproduced the same insert exception, without writing a task. No DEBUG enablement or persistent diagnostic logging was needed.

This is an actual server-side view/save-path traceback captured in the diagnostic process, **not a claim to have extracted traceback text from PID 2472**. The separate live HTTP request above establishes the normal runtime's matching failure.

Traceback formatter prints only file/function/line frames and exception types/code, with no local variables, request, SQL parameters, cookies, credentials or session values:

```text
Traceback (most recent call last):
  diagnose.py:50 in <module>
  django/contrib/auth/decorators.py:59 in _view_wrapper
  tasks/views.py:170 in task_create
    task.save()
  django/db/models/base.py:902 in save
  django/db/models/base.py:1008 in save_base
  django/db/models/base.py:1169 in _save_table
  django/db/models/base.py:1210 in _do_insert
  django/db/models/manager.py:87 in manager_method
  django/db/models/query.py:1873 in _insert
  django/db/models/sql/compiler.py:1882 in execute_sql
  django/db/backends/utils.py:79 in execute
  django/db/backends/utils.py:92 in _execute_with_wrappers
  django/db/backends/utils.py:100 in _execute
  django/db/utils.py:91 in __exit__
  django/db/backends/utils.py:105 in _execute

django.db.utils.DataError
Caused by: psycopg2.errors.UntranslatableCharacter
SQLSTATE: 22P05
character with byte sequence [REDACTED] in encoding UTF8
has no equivalent in encoding WIN1252
```

Diagnostic confirmed the actual exception message matches `has no equivalent in encoding` and `WIN1252`, and task count was unchanged. The independent PostgreSQL test traceback also contains `task.save()` → `cursor.execute(sql, params)` → the same error. This is a storage-encoding error, not unsafe SQL construction or form rejection.

## Regression coverage and actual results

Added `TaskCrudTests.test_sequential_unicode_task_submissions_persist_exactly_once`:

1. ASCII title and ASCII description baseline.
2. Vietnamese title and description.
3. Further Vietnamese input.
4. Emoji title.
5. Intentionally repeated Vietnamese title (allowed by existing model).

It asserts each POST redirects successfully, row count increments exactly once, exact text/date/status round trips, order and owner isolation. The test intentionally does **not** encode/strip Unicode to make the broken database pass.

- Initial draft test run: **1 test run, failed**. It accidentally used Vietnamese description even in the first baseline case and continued subtests after the broken transaction, producing six error entries. This was corrected in the test only: baseline is now entirely ASCII and execution stops at the first real failure.
- Final regression run before any fix: **1 test run in 1.189s, 0 pass, 1 error**, exit **1**. ASCII baseline succeeds; Vietnamese submission fails with `DataError` / `UntranslatableCharacter` at `task.save()`. This is the intended red regression and directly reproduces the original scenario.
- Passing-after-fix regression: **BLOCKED**, no UTF8 repair applied.
- Full affected PostgreSQL suite: **NOT RUN in 06B yet**; it cannot certify this new regression before repair. Historical Task 06 64/64 is not a current Unicode acceptance result.
- Django system check: **PASS**, no issues. A clean system check alone does not validate storage encoding.
- `git diff --check`: **PASS**, informational LF/CRLF notices only.

Both isolated databases are WIN1252; creating a default test database from the same incorrectly encoded template would also retain the issue. Repair must explicitly specify UTF8 and a compatible locale/template instead of relying on host Windows defaults.

## Real-browser evidence / limitations

Existing browser tab was recovered, not duplicated. Navigated from the stopped Task 06 port-8006 form to `http://127.0.0.1:8000/tasks/create/`. Browser redirected to the real Login page and rendered username/password controls and normal navigation. No existing Brave session was accessed or impersonated.

**Browser POST reproduction and corrected browser POST verification: NOT RUN / BLOCKED** at the point where the confirmed database-encoding repair requires explicit authorization and privileged database-owner participation. No corrected runtime exists yet. No browser success is inferred from HTTP or Django Client results.

User-reported Brave failure is background evidence; this report's independent executed failure evidence is normal-server HTTP plus same-view/database traceback and isolated PostgreSQL regression.

## Commands and exit codes

All commands from repository root, existing `.venv`, no dependency installs. Temporary scripts/private state/logs live outside Git:

`C:\Users\Ky\AppData\Local\Temp\ctm-task06b-20261105`

Command abbreviations (literal replacements for readability):

```text
PY = ./.venv/Scripts/python.exe
D = C:/Users/Ky/AppData/Local/Temp/ctm-task06b-20261105/diagnose.py
H = C:/Users/Ky/AppData/Local/Temp/ctm-task06b-20261105/httpqa.py
R = C:/Users/Ky/AppData/Local/Temp/ctm-task06-20261105/runtime.py
```

| Exact command/action | Exit / result |
| --- | --- |
| `git status --short --branch` | 0; prior Task 06 changes recorded |
| PowerShell `Get-NetTCPConnection -State Listen` filtered to 8000/8006/55432; `Get-CimInstance Win32_Process`, `Invoke-CimMethod ... GetOwner`; parent lookup | 0; owner/PIDs/commands above; no process stopped |
| `PYTHONIOENCODING=utf-8 PY -I -B D inspect > .../initial-db.log 2>&1` | 0; database identity, constraints/sequence and initial SHA-256 preserved |
| `PYTHONIOENCODING=utf-8 PY -I -B H reproduce > .../http-reproduce.log 2>&1` | 0; five ASCII POSTs 302; no Unicode was in that first script mode |
| `PYTHONIOENCODING=utf-8 PY -I -B H unicode` | **1**; first Vietnamese POST 500; assertion stops, later emoji/repeated-title cases not sent |
| `PYTHONIOENCODING=utf-8 PY -I -B H invalid` | 0; three invalid POSTs 200 |
| `PYTHONIOENCODING=utf-8 PY -I -B D inspect` | 0; WIN1252 server / UTF8 client and unchanged constraints |
| `PYTHONIOENCODING=utf-8 PY -I -B D trace > .../sanitized-trace.log 2>&1` | 0; diagnostic successfully captures expected exception/22P05; no extra row; **not** an application PASS |
| `PYTHONIOENCODING=utf-8 PY -I -B R test tasks.test_task_crud.TaskCrudTests.test_sequential_unicode_task_submissions_persist_exactly_once > .../regression-before.log 2>&1` | **1**; draft test fails, described above |
| `PYTHONIOENCODING=utf-8 PY -I -B D records` | 0; exactly five QA records; both DBs WIN1252; app role lacks CREATEDB/superuser |
| `PYTHONIOENCODING=utf-8 PY -I -B R test tasks.test_task_crud.TaskCrudTests.test_sequential_unicode_task_submissions_persist_exactly_once > .../regression-before-final.log 2>&1` | **1**; final red regression, 1 test / 1 error / 1.189s |
| `PYTHONIOENCODING=utf-8 PY -I -B D check` | **0**; no system-check issues |
| `git diff --check` | **0**; whitespace clean |

The retained Task 06 runner selects **cloudtask_test_04k** only for `test`, validates its identity/owner, sets TEST.NAME explicitly, and uses `keepdb=True, interactive=False`. No test ran against dev. Maintenance `postgres` database connection warning remains; its fallback is that explicitly configured isolated test database. No auth setting was relaxed.

The first diagnostic-file write was blocked by the security hook because a generic `cursor.execute(query)` loop was flagged. Replaced it with explicit constant SQL statements and parameter-bound relation/table/database names before execution; no externally constructed SQL was executed.

## Required repair, authorization boundary and remaining risks

Recommended smallest correct repair:

1. Obtain an explicitly authorized local database-owner connection; do not expose credentials or grant the app role broad privileges merely for convenience.
2. Take a verified private backup of the live database and preserve the existing WIN1252 database unchanged.
3. Create a **new**, explicitly UTF8 database with compatible locale using template0; restore/convert data with PostgreSQL tooling. Create a separately named UTF8 isolated test database. Validate row counts, IDs, ownership, sequence state and exact existing values before switching anything.
4. Validate the red regression and affected suite against the new isolated UTF8 database.
5. Only after explicit approval and identifying the owning terminal, stop/restart **the owned port-8000 app**, using process-only DATABASE_URL pointing to the verified UTF8 clone; do not overwrite `.env`. Keep old database available for rollback.
6. Verify sequential Vietnamese/emoji valid submissions over real HTTP and browser, invalid cases, CSRF, exact records/no unrequested duplicates. Update this report with actual post-fix evidence.

No unsafe shortcut taken: no `pg_database` catalog edits, no SET client_encoding workaround, no data sanitization/transliteration, no swallowing failed inserts, no reset/drop, no unknown server kill. Correct Unicode storage requires the migration approval, not a broad source refactor.

Remaining risks: the current normal runtime still returns 500 for unrepresentable text; existing new QA ASCII rows are intentionally retained; role cannot create databases; no corrected HTTP/browser PASS or after-fix test result exists. Temporary QA password/cookie/secret files are private local material and must not be published. Prior Task 06 changes remain intact.

## Authorized backup and current admin prerequisite

After the authorization question, the user selected **Authorize UTF-8 repair (Recommended)**. This authorizes the additive backup/clone repair and later identified-runtime switch/restart after validation, not deletion of the old databases.

Executed from Git Bash, with a pre-existence guard refusing to overwrite the dump:

```text
PGPASSFILE=C:/Users/Ky/AppData/Local/CloudTaskManager/pgpass.conf PGCLIENTENCODING=UTF8 C:/Users/Ky/AppData/Local/CloudTaskManager/postgresql16/binaries/bin/pg_dump.exe --no-password --host=127.0.0.1 --port=55432 --username=cloudtask_app --dbname=cloudtask_dev --format=custom --encoding=UTF8 --file=C:/Users/Ky/AppData/Local/Temp/ctm-task06b-20261105/cloudtask-dev-before-utf8.dump
```

- **pg_dump exit 0**.
- `pg_restore.exe --list <dump>` → **exit 0**, index saved privately as `backup-toc.txt`.
- SHA256: **31ef47dc02516f441184587fd277ee4a65e96af25407e24d4751c70f99e51675**.
- Dump is private outside Git; it contains user data/password hashes/sessions and must not be published. Archive readability is checked; **restore and row-equivalence validation are NOT RUN**.
- The live server has not been stopped, so this dump is a consistent PostgreSQL snapshot but not a final cutover freeze. If any user writes occur before cutover, take a fresh uniquely named final dump or otherwise reconcile them before switching; do not silently lose later writes.

Prepared, **not executed**, additive admin SQL at:

`C:\Users\Ky\AppData\Local\Temp\ctm-task06b-20261105\create-utf8-databases.sql`

It creates `cloudtask_dev_utf8_06b` and `cloudtask_test_utf8_06b`, owner cloudtask_app, `TEMPLATE=template0`, `ENCODING=UTF8`, `LC_COLLATE=C`, `LC_CTYPE=C`. Existing databases are not altered/deleted. C locale supports Unicode storage with deterministic collation; validate any locale-sensitive behavior before adopting permanently.

The user must run the following in a private local PowerShell terminal with a known database-admin role. `-W` prompts only locally; do not paste the password into chat. `-X` ignores user psql startup files and ON_ERROR_STOP prevents continuation on errors:

```powershell
$adminRole = Read-Host 'PostgreSQL database-admin role'
& "$env:LOCALAPPDATA\CloudTaskManager\postgresql16\binaries\bin\psql.exe" -X -W -h 127.0.0.1 -p 55432 -U $adminRole -d postgres -v ON_ERROR_STOP=1 -f "$env:LOCALAPPDATA\Temp\ctm-task06b-20261105\create-utf8-databases.sql"
```

If a target already exists, stop and inspect it rather than dropping/overwriting it. If permission/authentication fails, stop and resolve through the local database owner. No privileged connection has been attempted by the agent and app-role permissions remain unchanged.

Two attempted Python backup-helper writes were blocked by Mimosa despite argument arrays and explicit shell=False; neither helper was executed. The backup was then performed with the fixed, explicit pg_dump/pg_restore commands shown above; no shell interpolation of external input was used.

## Git status / next allowed step

```text
## main...origin/main
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
?? docs/reports/step-06b-task-create-post500-root-cause.md
```

Task 06B delta: one new regression method (Task 06 assertions/tests preserved) plus this report. No application-source change. Prior report, model, form and view hashes were captured before work and preservation is checked at close.

**Next allowed step:** authorization has been received; local database-owner participation is now required to execute the additive UTF8 database-creation SQL above. After that, verify identities, arrange narrowly scoped private authentication for the new databases without exposing credentials, restore the snapshot, compare data, and run the regression before the approved runtime switch. Old databases remain intact. Until the admin prerequisite is completed, stop with this report and intentionally failing regression. Do not claim FIXED until the repair and corrected real HTTP/browser verification actually succeed.
