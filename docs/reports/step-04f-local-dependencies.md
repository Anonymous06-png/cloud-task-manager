# Task 04F — Local Windows Django dependencies

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`  
Scope: install and inspect pinned development dependencies in the existing project-local `.venv`, excluding Gunicorn.

## Result and changes

Installation succeeded for `Django==5.2.18`, `psycopg2-binary==2.9.10`, `dj-database-url==2.2.0`, `python-decouple==3.8`, and `whitenoise==6.8.2`. The PostgreSQL adapter used the CPython 3.11 Windows AMD64 wheel. Pip also resolved transitive dependencies `asgiref==3.13.0`, `sqlparse==0.6.0`, `typing-extensions==4.16.0`, and `tzdata==2026.6`. Gunicorn was intentionally excluded. `pip check` found no broken installed requirements; all five packages imported and their reported versions match the pins.

The existing `.venv` is CPython 3.11.9, 64-bit AMD64, rooted at `C:\ProjectCloud\cloud-task-manager\.venv` with base interpreter `C:\Users\Ky\AppData\Local\Programs\Python\Python311`. Files changed: installed package files inside the Git-ignored `.venv`, pip's normal download cache, and this new report. `requirements.txt` and production configuration were not edited. No temporary requirements file was needed.

## Commands and results

Commands ran in the workspace. Exit codes are command-runner process exit codes.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04e-local-venv-preparation.md, requirements.txt` | 0 | Read previous environment report and pinned dependencies. |
| `git status --short --branch` | 0 | Before and after install: `main` has no commits, project entries untracked. |
| `Test-Path -LiteralPath docs\reports\step-04f-local-dependencies.md` | 0 | `False`; report path was available. |
| `& .\.venv\Scripts\python.exe -c "import sys,struct; print(sys.executable); print(sys.version); print('bits:',struct.calcsize('P')*8); print('prefix:',sys.prefix); print('base_prefix:',sys.base_prefix)"; exit $LASTEXITCODE` | 0 | `.venv` Python 3.11.9, AMD64, 64-bit; prefixes as above. |
| `.\.venv\Scripts\python.exe -m pip install Django==5.2.18 psycopg2-binary==2.9.10 dj-database-url==2.2.0 python-decouple==3.8 whitenoise==6.8.2` | 0 | Installed the five pinned packages and transitive packages listed above. No version changes were made to the project pins. |
| `.\.venv\Scripts\python.exe -m pip check` | 0 | `No broken requirements found.` |
| `.\.venv\Scripts\python.exe -c "import django, psycopg2, dj_database_url, decouple, whitenoise; from importlib.metadata import version; print('Django:', django.get_version()); print('psycopg2:', psycopg2.__version__); print('dj-database-url:', version('dj-database-url')); print('python-decouple:', version('python-decouple')); print('whitenoise:', version('whitenoise'))"` | 0 | Django `5.2.18`; psycopg2 `2.9.10 (dt dec pq3 ext lo64)`; dj-database-url `2.2.0`; python-decouple `3.8`; whitenoise `6.8.2`. |

## Tests, limitations and risks

**0 Django tests executed, 0 passed, 0 failed.** `pip check` verifies installed package metadata consistency, and imports verify module loading; neither verifies Django configuration, database connectivity, application behavior, or a deployment. Django startup, system checks, migrations, PostgreSQL connections, `.env` creation, Docker, cloud and WebIOT actions were **NOT RUN** as instructed. Gunicorn was excluded and is not verified for native Windows. The base Python 3.11.9 interpreter predates later source-only 3.11 security fixes, as documented in Task 04D. Transitive dependencies were resolved at installation time and are not pinned by `requirements.txt`.

## Git status and next step

`main` has no commits. Untracked entries: `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. `.venv/` is ignored. Nothing was staged, committed, pushed, reset or cleaned.

**Next step:** separately authorize a Django system check with safe temporary environment variables, without connecting to or changing a database, before planning isolated database-backed tests.
