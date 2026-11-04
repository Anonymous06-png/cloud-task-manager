# Task 04G — Django local system check

Date: 2026-10-31  
Environment: Windows / PowerShell; workspace `C:\ProjectCloud\cloud-task-manager`; existing `.venv` Python 3.11.9 and Django 5.2.18.

## Result and scope

Django's standard `check` completed with exit code **0**: `System check identified no issues (0 silenced).` It reported **0 warnings and 0 errors**. The check used temporary dummy process environment variables and replaced Django's database connection method with a function that raises an error if called; the check completed without invoking it. This verifies the standard system checks in this environment, not database connectivity, migrations, deployment security, browser behavior, or application tests.

`config/settings.py` requires nonblank `SECRET_KEY` and `DATABASE_URL`. Dummy values were supplied only to the command's PowerShell process; `DJANGO_ENV=local`, `DEBUG=False`, and the project's settings module were explicitly selected. The dummy database URL points to loopback port 1 and was not connected to. `PYTHONDONTWRITEBYTECODE=1` avoided writing Python bytecode. No real secret was read or printed. No `.env` existed at the checked path and none was created or changed. The only intentional workspace change is this report.

## Commands and results

Commands ran from `C:\ProjectCloud\cloud-task-manager`; exit codes are process exit codes.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04f-local-dependencies.md, config\settings.py, manage.py` | 0 | Inspected previous environment report, required settings, and management entry point. |
| `git status --short --branch` | 0 | `main` has no commits; project entries untracked. |
| `Test-Path -LiteralPath docs\reports\step-04g-django-system-check.md; Test-Path -LiteralPath .env` | 0 | Both returned `False` before the check. |
| `.\.venv\Scripts\python.exe -c "import sys, django; print('executable:', sys.executable); print('python:', sys.version.split()[0]); print('Django:', django.get_version())"` | 0 | `.venv\Scripts\python.exe`; Python `3.11.9`; Django `5.2.18`. |
| `$env:SECRET_KEY='temporary-system-check-only'; $env:DATABASE_URL='postgresql://test:test@127.0.0.1:1/check'; $env:DJANGO_ENV='local'; $env:DEBUG='False'; $env:DJANGO_SETTINGS_MODULE='config.settings'; $env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -c "import sys, runpy; from django.db.backends.base.base import BaseDatabaseWrapper; BaseDatabaseWrapper.ensure_connection = lambda self: (_ for _ in ()).throw(RuntimeError('Database connection prohibited during system check')); sys.argv = ['manage.py', 'check']; runpy.run_path('manage.py', run_name='__main__')"; exit $LASTEXITCODE` | 0 | `System check identified no issues (0 silenced).` No warnings or errors; the connection guard did not fire. |

## Tests and limitations

**0 Django tests executed, 0 passed, 0 failed.** The system check is not a test suite. Database connectivity and database-backed CRUD/authentication tests, migrations, server startup, package installation, Docker, cloud and WebIOT actions were **NOT RUN**. The connection guard covers Django's standard database wrapper; this check does not establish anything about a live database. No deployment-specific `check --deploy` was requested or run.

## Git status and next step

Initial `git status --short --branch` reported no commits on `main`; untracked entries were `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. This report is inside already-untracked `docs/`. Nothing was staged, committed, pushed, reset, or cleaned.

**Next step:** plan and obtain authorization for an isolated PostgreSQL test environment before running the existing database-backed CRUD and authentication tests.
