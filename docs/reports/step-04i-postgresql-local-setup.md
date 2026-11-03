# Task 04I — Local PostgreSQL 16 setup checkpoint

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell.

## Status: awaiting explicit installation approval

No installation was attempted. Task 04H found no PostgreSQL tools, services, server process, or listeners in its checked locations. A targeted recheck in this task found no matching PostgreSQL Windows service or `postgres.exe` process and no listener on ports 5432, 5433, or 55432. This does not rule out a nonstandard executable, process name, port, or remote instance. No suitable instance was identified or connected to.

## Concrete proposed installation

Use EDB's PostgreSQL **16.15-1 Windows x64** interactive installer, `postgresql-16.15-1-windows-x64.exe`, from `https://get.enterprisedb.com/postgresql/postgresql-16.15-1-windows-x64.exe`. The [PostgreSQL Windows download page](https://www.postgresql.org/download/windows/) directs Windows users to EDB's installer. Verify the downloaded installer's trusted publisher signature before running it. The installer requires administrator authorization, installs server binaries and command-line tools (proposed under `C:\Program Files\PostgreSQL\16`), initializes a new data directory and registers/starts a Windows service. It may install prerequisite runtimes. Select server and command-line tools only where supported, and omit optional pgAdmin/Stack Builder. Use an available local port, proposed 5432 after rechecking immediately before install. Confirm and enforce loopback-only listening and inspect the actual listener afterward; stop and report if that cannot be assured.

The user would enter the installer superuser password directly in the graphical installer; it must not be supplied in commands, chat, or reports. This changes the local Windows system and creates PostgreSQL's own initial cluster and built-in administrative database/role; it does not create project databases or roles. Install path, data directory, port and service name must be checked for conflicts before proceeding; do not reuse or alter an existing cluster. The installer may request Windows UAC approval. The method for ensuring loopback-only access through first startup must be confirmed before execution, not assumed from an unverified installer default.

`config/settings.py` requires a nonblank `SECRET_KEY` and `DATABASE_URL`; `.env.example` uses the container hostname `db`, so a later native Windows setup needs a reachable local host. Neither credentials nor an `.env` file were created. Project database creation, roles, migrations and tests remain outside this task.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04h-postgresql-readiness.md, config\settings.py, .env.example` | 0 | Reviewed prior evidence and configuration; example credentials are placeholders. |
| `Get-CimInstance Win32_Service -Filter "Name LIKE '%postgres%' OR DisplayName LIKE '%postgres%'" \| Select-Object Name,DisplayName,State; Get-CimInstance Win32_Process -Filter "Name='postgres.exe'" \| Select-Object ProcessId,ExecutablePath; Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -in 5432,5433,55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess` | 0 | No matching service, process or listener returned. |
| `git status --short --branch` | 0 | `main` has no commits; project entries untracked. |
| `Test-Path -LiteralPath docs\reports\step-04i-postgresql-local-setup.md` | 0 | `False`; report path available. |

## Checks and limitations

Installation, PostgreSQL version, service status after installation, listener and `pg_isready` verification are **NOT RUN**, pending approval. **0 Django tests executed, 0 passed, 0 failed**. No database connection, project database/role creation, migrations, application changes, Python environment changes, Docker/cloud actions, service changes, or Git history changes occurred. No password was requested, printed, or saved.

## Git status and next step

`main` has no commits. Untracked entries: `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. This report is under already-untracked `docs/`.

**Next step:** obtain explicit approval for the described EDB PostgreSQL 16.15-1 installation, then verify safe loopback-only first startup and conflict-free paths before any installation; stop if these conditions cannot be met.
