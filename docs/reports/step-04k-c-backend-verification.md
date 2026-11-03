# Task 04K-C — Complete Isolated Backend Tests

Date: 2026-11-03  
Workspace: `C:\ProjectCloud\cloud-task-manager`

## Result

**BLOCKED / NOT EXECUTED in this agent session.** The prior 04K-B run established that the agent command runner cannot safely complete an interactive `getpass` prompt. This task therefore did not execute `psql -W`, did not request or receive a password, did not create or alter a PostgreSQL database, and did not run Django tests. Per instruction, interactive authentication and actual test execution are delegated to the user in a visible PowerShell terminal.

The supplied manual commands and launcher are intentionally non-secret. They never contain a password literal, never print a password, and do not connect to `cloudtask_dev` for tests. Actual database existence, application-role login, ownership, isolation, test totals, failures, errors, and exit codes remain **NOT VERIFIED** until the user runs the commands manually and supplies sanitized outputs/exit codes.

## Files read

- `docs/reports/step-04k-b-backend-test-results.md`
- `config/settings.py`
- `tasks/test_authentication.py`
- `tasks/test_task_crud.py`

`config/settings.py` requires `SECRET_KEY` and `DATABASE_URL` from environment configuration and parses the URL. It does not define a static test database name. The prepared launcher requires a process-scoped `DATABASE_URL`, verifies the parsed host, port, engine, and database name, sets Django `DATABASES['default']['TEST']['NAME']` to the same approved name, then verifies the authenticated live connection before tests.

## User-run manual database commands

Run `tools\step-04k-c-manual.ps1` in a visible PowerShell terminal. It performs:

1. Readiness check on `127.0.0.1:55432`.
2. `psql -W -U cloudtask_app -d postgres` query to inspect only `cloudtask_dev` and `cloudtask_test_04k`.
3. It prints, but does not execute, the exact create command. If and only if `cloudtask_test_04k` is absent, run the printed command manually with interactive `postgres` authentication:

```powershell
psql.exe -W -h 127.0.0.1 -p 55432 -U postgres -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE cloudtask_test_04k OWNER cloudtask_app;"
```

Do not run the create command when the database already exists. Never use `DROP DATABASE`, `ALTER ROLE`, password reset, or any command involving `cloudtask_dev` except the read-only inspection query.

4. `psql -W -U cloudtask_app -d cloudtask_test_04k` identity query. Expected sanitized evidence is current database `cloudtask_test_04k`, current user `cloudtask_app`, server `127.0.0.1`, port `55432`, and owner `cloudtask_app`.

Record each command's actual exit code in the final verification update. Do not send passwords or full connection URLs.

## User-run Django test launcher

The non-secret launcher is:

```text
tools\step-04k-c-test-launcher.py
```

It accepts only these suite labels:

```text
tasks.test_authentication
tasks.test_task_crud
```

Before running it, the user must set process-scoped environment variables in the visible PowerShell session. The password must be entered by the user into an environment mechanism they control; it must not be written into this repository or displayed in output. Use a URL whose database component is exactly `cloudtask_test_04k`, host is exactly `127.0.0.1`, and port is exactly `55432`, then set a non-secret local `SECRET_KEY` in that process. Do not use `cloudtask_dev`.

The launcher refuses to proceed unless all of these are true:

- PostgreSQL engine.
- Host `127.0.0.1`.
- Port `55432`.
- URL database `cloudtask_test_04k`.
- Django `TEST.NAME` explicitly set to `cloudtask_test_04k`.
- Live `current_database()` is `cloudtask_test_04k`, never `cloudtask_dev`.
- Live user and database owner are both `cloudtask_app`.
- Live server address and port are `127.0.0.1:55432`.
- `CLOUDTASK_TEST_KEEPDB=1` is explicitly set by the user after confirming the dedicated database is safe to reuse.

Run suites sequentially, capturing each process exit code:

```powershell
$env:CLOUDTASK_TEST_KEEPDB = '1'
& .venv\Scripts\python.exe -I -B tools\step-04k-c-test-launcher.py tasks.test_authentication
$authExit = $LASTEXITCODE
Write-Host "AUTH_EXIT=$authExit"
if ($authExit -ne 0) { exit $authExit }

& .venv\Scripts\python.exe -I -B tools\step-04k-c-test-launcher.py tasks.test_task_crud
$crudExit = $LASTEXITCODE
Write-Host "CRUD_EXIT=$crudExit"
exit $crudExit
```

Do not continue to the second suite if the first reports an isolation, connection, permission, setup, failure, or error condition. If Django requires `CREATEDB`, stop and report BLOCKED; do not broaden permissions. Do not run `manage.py migrate` separately and do not run tests against `cloudtask_dev`.

## Test results

| Suite | Result | Tests run | Passed | Failed | Errors | Exit code |
|---|---|---:|---:|---:|---:|---:|
| Authentication (`tasks.test_authentication`) | NOT RUN — user terminal required | 0 | 0 | 0 | 0 | N/A |
| CRUD (`tasks.test_task_crud`) | NOT RUN — user terminal required | 0 | 0 | 0 | 0 | N/A |

Actual totals must be copied from the user's visible terminal output after successful isolated execution. No result is inferred from source inspection.

## Isolation and permission checks

- PostgreSQL readiness: previously verified in 04K-B on the isolated cluster; no new agent-side database connection was made.
- `cloudtask_test_04k` existence: **NOT VERIFIED in this session**.
- `cloudtask_test_04k` owner: **NOT VERIFIED in this session**.
- `cloudtask_app` login to test database: **NOT VERIFIED in this session**.
- Explicit Django `TEST.NAME`: implemented in the prepared launcher, but **NOT EXECUTED**.
- Live database isolation proof: **NOT VERIFIED in this session**.
- CREATEDB requirement: **NOT TESTED**; permissions were not broadened.
- `--keepdb`: launcher supports it only when `CLOUDTASK_TEST_KEEPDB=1` is explicitly set after manual reuse verification; it was **NOT EXECUTED**.
- `cloudtask_dev`: no test connection, migration, modification, deletion, or overwrite was performed.

## Commands and exit codes in this task

| Command/action | Exit/result |
|---|---:|
| Read 04K-B report and settings/test modules | Completed; no command exit code applicable |
| Write `tools/step-04k-c-manual.ps1` | Completed by file tool |
| Write `tools/step-04k-c-test-launcher.py` | Completed by file tool |
| `git status --short --branch` | 0 |
| `psql -W` inspection/creation/login | NOT RUN by agent; user terminal required |
| Authentication suite | NOT RUN |
| CRUD suite | NOT RUN |

## Files changed

New files prepared:

- `tools/step-04k-c-manual.ps1` — visible-terminal readiness, read-only inspection, conditional create instruction, and application-role login checks.
- `tools/step-04k-c-test-launcher.py` — non-secret, explicit isolated Django launcher with live isolation proof and guarded `--keepdb`.
- `docs/reports/step-04k-c-backend-verification.md` — this report.

No application code, existing tests, dependency files, Docker configuration, cloud/WebIOT resources, or Git metadata were changed.

## Git status

At final inspection:

```text
## No commits yet on main
?? .dockerignore
?? .env.example
?? .gitignore
?? .mimosa/
?? .zcode/
?? CLAUDE.md
?? Dockerfile
?? README.md
?? backend/
?? config/
?? docker-compose.yml
?? docs/
?? manage.py
?? requirements.txt
?? static/
?? tasks/
?? templates/
?? tools/
```

## NOT RUN / BLOCKED checks

- Interactive PostgreSQL inspection: **NOT RUN by agent**.
- Conditional database creation: **NOT RUN by agent**.
- Application-role test-database login: **NOT RUN by agent**.
- Django authentication suite: **NOT RUN**.
- Django CRUD suite: **NOT RUN**.
- Test totals/failures/errors: **NOT AVAILABLE** until user execution.
- CREATEDB privilege requirement: **NOT TESTED**.
- `cloudtask_dev` operations: **NOT RUN**.

## Next allowed step

In a visible PowerShell terminal, run `tools\step-04k-c-manual.ps1`, create `cloudtask_test_04k` only if its read-only inspection proves it is absent, verify the sanitized application-role identity, then run the two launcher commands sequentially with `CLOUDTASK_TEST_KEEPDB=1`. Record and return only sanitized output and exit codes; do not provide passwords. Then update this report with the actual totals and evidence.
