# Task 04K-C — Launcher Import Path Fix

Date: 2026-11-03  
Workspace: `C:\ProjectCloud\cloud-task-manager`

## Result

Fixed only the repository import path in `tools/step-04k-c-test-launcher.py` before `django.setup()`. The launcher now resolves the repository root from its own file location and inserts that root into `sys.path` when needed. This preserves Python `-I` mode while allowing `config.settings` and the project packages to be imported when the launcher is invoked by path.

No application code, settings, credentials, database resources, tests, dependencies, Docker/cloud/WebIOT resources, or Git metadata were modified.

## Change

Added before importing Django:

```python
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))
```

The existing database safeguards remain unchanged, including the fixed approved target `cloudtask_test_04k`, host `127.0.0.1`, port `55432`, live identity query, refusal of `cloudtask_dev`, explicit `TEST.NAME`, and guarded `keepdb` requirement.

## Verification commands and exit codes

1. Non-database compilation and import-path check, preserving isolated Python mode:

```powershell
cd C:\ProjectCloud\cloud-task-manager
.venv\Scripts\python.exe -I -B -m py_compile tools\step-04k-c-test-launcher.py
.venv\Scripts\python.exe -I -B -c "import runpy; ns = runpy.run_path('tools/step-04k-c-test-launcher.py', run_name='step04kc_import_check'); import config; assert ns['REPOSITORY_ROOT'].name == 'cloud-task-manager'; print('IMPORT_PATH_CHECK=PASS')"
```

Observed output:

```text
IMPORT_PATH_CHECK=PASS
```

Combined command exit code: **0**.

2. Repository status:

```powershell
git status --short --branch
```

Exit code: **0**. The repository remains on `main` with no commits and the existing untracked project entries, including `tools/`.

## NOT RUN / BLOCKED checks

- Django test suite execution: **NOT RUN** by the agent.
- PostgreSQL connection: **NOT RUN**.
- `psql -W` or any password prompt: **NOT RUN**.
- Database creation, migration, modification, deletion: **NOT RUN**.
- `cloudtask_dev`: no connection or test operation performed.
- Authentication and CRUD test totals: **NOT AVAILABLE**; no tests were executed.
- `--keepdb` runtime behavior: **NOT RUN**.

## Exact manual PowerShell test commands for the user

Run these in a visible PowerShell terminal only after the previously documented manual database existence and application-role isolation checks succeed. Do not provide passwords to the agent.

Set process-scoped values without writing credentials to the repository. The `DATABASE_URL` must target only `cloudtask_test_04k` on `127.0.0.1:55432`; do not use `cloudtask_dev`:

```powershell
Set-Location C:\ProjectCloud\cloud-task-manager
$env:DJANGO_SETTINGS_MODULE = 'config.settings'
$env:SECRET_KEY = 'temporary-local-test-key-change-me'
$env:DATABASE_URL = 'postgresql://cloudtask_app:<PASSWORD_URL_ENCODED>@127.0.0.1:55432/cloudtask_test_04k'
$env:CLOUDTASK_TEST_KEEPDB = '1'
```

Replace only `<PASSWORD_URL_ENCODED>` in the visible terminal with the user-controlled URL-encoded password; never commit or paste it into a report. If the password contains URL-reserved characters, URL-encode them before forming the process value.

Run Authentication first and record its real exit code:

```powershell
& .venv\Scripts\python.exe -I -B tools\step-04k-c-test-launcher.py tasks.test_authentication
$authExit = $LASTEXITCODE
Write-Host "AUTH_EXIT=$authExit"
if ($authExit -ne 0) { exit $authExit }
```

Only if Authentication completes without isolation, connection, permission, setup, failure, or error problems, run CRUD:

```powershell
& .venv\Scripts\python.exe -I -B tools\step-04k-c-test-launcher.py tasks.test_task_crud
$crudExit = $LASTEXITCODE
Write-Host "CRUD_EXIT=$crudExit"
exit $crudExit
```

Expected launcher evidence before tests is sanitized and should identify only `cloudtask_test_04k`, `cloudtask_app`, `127.0.0.1`, and port `55432`. Stop immediately if the launcher prints `BLOCKED` or if Django asks for additional `CREATEDB` privileges. Do not broaden privileges or switch databases.

## Next allowed step

The user may run the two manual PowerShell commands above sequentially against the already verified dedicated database, then update the backend verification report with the actual Django test totals, failures, errors, and exit codes. 
