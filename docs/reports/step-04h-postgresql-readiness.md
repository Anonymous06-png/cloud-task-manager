# Task 04H — Local PostgreSQL readiness inspection

Date: 2026-10-31  
Environment: Windows / PowerShell; workspace `C:\ProjectCloud\cloud-task-manager`; existing project `.venv` as recorded in Task 04G.

## Findings

**No usable local PostgreSQL instance was identified in the checked locations.** No matching Windows service or `postgres.exe` process was returned; no listener was returned on ports 5432, 5433, or 55432. PostgreSQL client/server commands were not found on PATH, common installation directories and the prior temporary `opencode` location had no matches, and the checked installation registry and uninstall entries had no matching installation. This does not prove PostgreSQL is absent from all paths, hosts, or nonstandard ports. No service was started or stopped and no database connection was attempted.

`config/settings.py` requires nonblank `SECRET_KEY` and `DATABASE_URL`, and parses the latter as a database URL. `.env.example` provides placeholder PostgreSQL fields and a URL using host `db`, which it identifies as the container service hostname; a native Windows process needs a reachable local host and port instead. No real credentials were read or displayed. Local mode can use `DJANGO_ENV=local`; actual database access additionally requires an existing server, appropriate credentials and database. The presence, server version, access rights, and isolation of any database are **not verified**.

The smallest safe setup for local development and tests is a separately provisioned local PostgreSQL instance (or an identified existing suitable instance), a dedicated development database and least-privilege development role, plus a separate test database or test role arrangement with the privileges Django's test runner needs to create and destroy its isolated test database. Confirm the target and permissions before database operations. Supply a local-only `SECRET_KEY` and database URL through an approved secret handling method or process-scoped environment. Then, with separate authorization, apply migrations to the dedicated development database and run tests against the isolated test database. This is a proposed setup, not completed work; it requires service/software and database changes that were outside this inspection.

## Commands and results

Commands ran from the workspace. Exit codes are command-runner process exit codes; no-output results apply only to the queried names and paths.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04g-django-system-check.md, config\settings.py, .env.example` | 0 | Reviewed previous check and expected settings; `.env.example` contains placeholders. |
| `git status --short --branch` | 0 | `main` has no commits; project entries untracked. |
| `Test-Path -LiteralPath docs\reports\step-04h-postgresql-readiness.md` | 0 | `False`; report path available. |
| `Get-Command psql,postgres,pg_ctl,pg_isready -All -ErrorAction SilentlyContinue \| Select-Object Name,Source` | 1 | No commands returned on PATH. |
| `Get-CimInstance Win32_Service -Filter "Name LIKE '%postgres%' OR DisplayName LIKE '%postgres%'" \| Select-Object Name,DisplayName,State,StartMode,PathName` | 0 | No matching service returned. |
| `Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -in 5432,5433,55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess` | 0 | No listeners returned on those ports. |
| `Get-ChildItem 'C:\Program Files\PostgreSQL','C:\Program Files (x86)\PostgreSQL','C:\PostgreSQL',"$env:LOCALAPPDATA\Programs\PostgreSQL" -ErrorAction SilentlyContinue \| Select-Object FullName` | 1 | No matching entries returned. |
| `reg query HKLM\SOFTWARE\PostgreSQL\Installations /s` | 1 | Registry key not found. |
| `reg query HKLM\SOFTWARE\WOW6432Node\PostgreSQL\Installations /s` | 1 | Registry key not found. |
| `Get-CimInstance Win32_Process -Filter "Name='postgres.exe'" \| Select-Object ProcessId,ExecutablePath` | 0 | No matching process returned. |
| `where.exe psql` | 1 | No executable found on PATH. |
| `Get-ChildItem C:\Users\Ky\AppData\Local\Temp\opencode -Filter postgres.exe -Recurse -File -ErrorAction SilentlyContinue \| Select-Object FullName` | 0 | No matching executable returned in prior temporary location. |
| `Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue \| Where-Object { $_.DisplayName -match 'PostgreSQL' } \| Select-Object DisplayName,DisplayVersion,InstallLocation` | 0 | No matching uninstall entries returned. |

## Tests, limitations and risks

**0 Django tests run, 0 passed, 0 failed.** The checks above are installation, service, process and listener inspections, not PostgreSQL connection or functional tests. Database connectivity, server version, permissions, database existence, migrations and isolated test execution are **NOT RUN / NOT VERIFIED**. No software, services, roles, passwords, databases, `.env`, existing data, application source, Docker, cloud or WebIOT were changed. A nonstandard or remote PostgreSQL instance may exist; do not assume it is a safe test target without identification and authorization.

## Git status and next step

Initial `git status --short --branch` reported `main` with no commits and untracked `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. This report is inside already-untracked `docs/`. Git history was not modified.

**Next step:** identify a suitable existing PostgreSQL instance or separately authorize provisioning an isolated local instance and dedicated development/test resources before making any database changes.
