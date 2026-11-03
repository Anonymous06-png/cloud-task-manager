# Task 04L — Agent non-interactive testing via PGPASSFILE (preflight)

Date: 2026-11-03  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / Git Bash; project `.venv` Python 3.11.9 / Django 5.2.18.

## Result: BLOCKED at authentication preflight

The PGPASSFILE mechanism itself works (libpq located and read the password file), but the password stored in the file failed SCRAM authentication for role `cloudtask_app`. Per the task's stop rule, no retry, no password reset, no speculative re-prompt was attempted. Everything after the preflight (Django connectivity, app run, endpoint checks, browser acceptance) is **NOT RUN**.

Exact sanitized error (contains no credentials):

```text
psql: error: connection to server at "127.0.0.1", port 55432 failed:
FATAL:  password authentication failed for user "cloudtask_app"
password retrieved from file "C:/Users/Ky/AppData/Local/CloudTaskManager/pgpass.conf"
psql -w exit=2
```

## What was verified before the blocker

| Command (abbreviated, non-secret) | Exit | Result |
| --- | ---: | --- |
| `pg_ctl -D %LOCALAPPDATA%\CloudTaskManager\postgresql16\data status` | 3 | Isolated cluster was not running (expected: manually started process from 04I does not survive reboot). |
| `pg_ctl -D <data> -l <server.log> -w start` | 0 | Isolated cluster started (documented 04I startup step). |
| `pg_isready -h 127.0.0.1 -p 55432` | 0 | `127.0.0.1:55432 - accepting connections`. |
| `psql -X -w -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U cloudtask_app -d cloudtask_dev -c "SELECT ..."` with `PGPASSFILE=%LOCALAPPDATA%\CloudTaskManager\pgpass.conf`, `PSQL_HISTORY=NUL` | **2** | Authentication failed; the `password retrieved from file` line confirms libpq read the dedicated file (mechanism OK). |

No existing credential file was overwritten: `%APPDATA%\postgresql\` and `%LOCALAPPDATA%\CloudTaskManager\pgpass.conf` were both absent before setup; the setup command refuses to run when the target file exists.

## One-time user setup command (reusable; run in a visible PowerShell window)

The password is entered privately via `Read-Host -AsSecureString` and never displayed, echoed, logged, or written anywhere except the file below. The command refuses to overwrite an existing file:

```powershell
$pgpass = Join-Path $env:LOCALAPPDATA 'CloudTaskManager\pgpass.conf'
if (Test-Path -LiteralPath $pgpass) { Write-Error "Refusing to overwrite existing password file: $pgpass"; exit 1 }
$sec = Read-Host -AsSecureString 'Password for cloudtask_app (input hidden)'
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
try { $pass = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
if ([string]::IsNullOrEmpty($pass)) { Write-Error 'No password entered'; exit 1 }
$esc = $pass -replace '\\','\\\\' -replace ':','\\:'
$lines = @(
  "127.0.0.1:55432:cloudtask_dev:cloudtask_app:$esc",
  "127.0.0.1:55432:cloudtask_test_04k:cloudtask_app:$esc"
)
[IO.File]::WriteAllLines($pgpass, $lines, (New-Object System.Text.UTF8Encoding($false)))
Remove-Variable pass, esc, lines, bstr, sec -ErrorAction SilentlyContinue
icacls $pgpass /inheritance:r /grant:r "$env:USERNAME:F" | Out-Null
Write-Output "Password file ready: $pgpass (contents never displayed)"
exit 0
```

Design points: file lives outside the repository; two exactly-scoped entries (no wildcards) cover `cloudtask_dev` and the isolated test database `cloudtask_test_04k` so both the app and the existing 04K suites can run non-interactively; UTF-8 without BOM (`pgpass` would otherwise mis-parse the first line); ACL restricted to the current user.

## Reusable non-interactive test procedure (after a successful preflight)

Prefix every agent command with:

```bash
export PGPASSFILE="C:/Users/Ky/AppData/Local/CloudTaskManager/pgpass.conf"
export PSQL_HISTORY=NUL
export DATABASE_URL="postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_dev"
```

1. **Preflight**: `psql -X -w -h 127.0.0.1 -p 55432 -U cloudtask_app -d cloudtask_dev -c "SELECT current_database(), current_user, host(inet_server_addr()), inet_server_port(), pg_get_userbyid(datdba) FROM pg_database WHERE datname = current_database();"` — expect exit 0 and row `cloudtask_dev | cloudtask_app | 127.0.0.1 | 55432 | cloudtask_app`. Any failure: stop and report sanitized error.
2. **Django**: same environment plus `SECRET_KEY` (ephemeral test value), `DJANGO_ENV=local`, `DEBUG=False`, `SECURE_SSL_REDIRECT=False`; then `.venv/Scripts/python.exe -I manage.py check` and a connection identity query through `django.db.connection`.
3. **App**: `.venv/Scripts/python.exe -I manage.py runserver 127.0.0.1:8000 --noreload` (background); verify `/health/` (200 JSON), `/login/`, `/register/` (200 HTML) with `curl`.
4. **Browser acceptance**: only after confirming stable browser automation; do not install new frameworks.
5. **Test suites** (isolated from `cloudtask_dev`): the existing `tools/step-04k-d-run-tests.py` prompts via `getpass`; non-interactive alternative is `tools/step-04k-c-test-launcher.py` per suite with `DATABASE_URL=postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_test_04k`, `CLOUDTASK_TEST_KEEPDB=1`, `SECRET_KEY`, and the PGPASSFILE export above — the launcher already refuses `cloudtask_dev` and enforces the approved host/port/database.

## Blockers

- `cloudtask_app` SCRAM authentication fails with the password currently stored in the pgpass file (likely a mistyped entry or a different account's password). Remediation is user-side: delete `%LOCALAPPDATA%\CloudTaskManager\pgpass.conf` and re-run the setup command above with the correct `cloudtask_app` password, then re-run the preflight in step 1.

## NOT RUN

Django connectivity check, `manage.py check`, server start, `/health/`, `/login/`, `/register/` verification, browser-automation assessment, Django test suites. No database data was created, modified, or destroyed; no application source, settings, permissions, pg_hba rules, Docker, Azure or WebIOT configuration was changed.

## Git status

`git status --short --branch` exit 0: `main` has no commits; `.dockerignore`, `.env.example`, `.gitignore`, `.mimosa/`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, `templates/`, `tools/` untracked. This report is the only new file added by this task. Nothing staged, committed, pushed, or reset.
