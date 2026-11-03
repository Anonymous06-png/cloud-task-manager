# Task 04K-D — PostgreSQL Isolation Verification Mismatch Fix

Date: 2026-11-03  
Workspace: `C:\ProjectCloud\cloud-task-manager`

## Result

Confirmed and fixed a comparison-format bug in `tools/step-04k-c-test-launcher.py`. The launcher queried `inet_server_addr()::text`, whose PostgreSQL `inet` text representation can include a CIDR suffix. The recovered isolated cluster had previously reported `127.0.0.1/32`; the launcher compared that value directly with the required bare host string `127.0.0.1`, causing:

```text
BLOCKED: authenticated connection is not the approved isolated PostgreSQL
SUITE_EXIT=tasks.test_authentication:2
```

The query now uses PostgreSQL's `host(inet_server_addr())`, which normalizes the address to the bare host string while preserving the exact comparison to `127.0.0.1`. No isolation safeguard was weakened.

The port comparison was inspected as well: `inet_server_port()` is returned by psycopg2 as a Python integer, matching the integer constant `55432`; no port type fix was needed. Database name, owner, current user, host, port, `TEST.NAME`, and explicit refusal of `cloudtask_dev` remain unchanged.

## Exact change

Changed only the selected SQL expression:

```diff
- "inet_server_addr()::text, inet_server_port(), "
+ "host(inet_server_addr()), inet_server_port(), "
```

The query still uses no external inputs. It selects fixed identity fields from the current authenticated connection and retains exact post-query checks:

- database: `cloudtask_test_04k`
- user: `cloudtask_app`
- owner: `cloudtask_app`
- host: `127.0.0.1`
- port: `55432`
- refusal if current database is `cloudtask_dev`

## Non-destructive verification

No database connection, password prompt, migration, Django test, or test runner was executed.

Command:

```powershell
Set-Location C:\ProjectCloud\cloud-task-manager
.venv\Scripts\python.exe -I -B -m py_compile tools\step-04k-c-test-launcher.py tools\step-04k-d-run-tests.py
.venv\Scripts\python.exe -I -B -c "import runpy; ns = runpy.run_path('tools/step-04k-c-test-launcher.py', run_name='step04kc_non_db_check'); assert ns['EXPECTED_DATABASE'] == 'cloudtask_test_04k'; assert ns['EXPECTED_HOST'] == '127.0.0.1'; assert ns['EXPECTED_PORT'] == 55432; print('NON_DATABASE_CHECK=PASS')"
```

Observed:

```text
NON_DATABASE_CHECK=PASS
```

Exit code: **0**.

## NOT RUN / BLOCKED checks

- Django Authentication tests: **NOT RUN**.
- Django CRUD tests: **NOT RUN**.
- PostgreSQL connection or credentials: **NOT RUN**.
- Migrations: **NOT RUN**.
- Database creation or resource modification: **NOT RUN**.
- `cloudtask_dev`: not connected to or modified.
- Actual post-fix live identity output: **NOT RUN** in this non-destructive check; the root cause is confirmed from PostgreSQL address-format semantics and the prior recorded `127.0.0.1/32` evidence.
- Test totals, failures, and errors: **NOT AVAILABLE** from this task.

## Files changed

- `tools/step-04k-c-test-launcher.py` — one confirmed address-format comparison fix.
- `docs/reports/step-04k-d-isolation-mismatch-fix.md` — this report.

No application code, settings, credentials, database resources, Docker/Cloud/WebIOT resources, dependencies, or Git history were changed.

## Git status

Command:

```powershell
git status --short --branch
```

Exit code: **0**.

Observed status:

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

No Git mutation occurred.

## Next allowed step

From a visible Windows PowerShell terminal, rerun the existing `tools\step-04k-d-run-tests.py` wrapper with the already approved interactive password flow. It may proceed only if the corrected live identity check prints sanitized `ISOLATION=PASS`; then it should run Authentication followed by CRUD and stop on any failure. Do not provide credentials to the agent, recreate databases, broaden privileges, or use `cloudtask_dev`.
