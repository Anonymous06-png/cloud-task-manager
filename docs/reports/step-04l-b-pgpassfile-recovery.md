# Task 04L-B — PGPASSFILE authentication recovery and app verification

Date: 2026-11-03  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / Git Bash; project `.venv` Python 3.11.9 / Django 5.2.18.  
Continues: `step-04l-agent-pgpassfile-preflight.md` (was BLOCKED at authentication preflight).

## Result: PASS (recovery successful; full chain verified end-to-end)

1. User re-ran the one-time PowerShell setup (guarded replace of only `%LOCALAPPDATA%\CloudTaskManager\pgpass.conf`, password entered via `Read-Host -AsSecureString`, never displayed or sent to the agent; UTF-8 without BOM; ACL restricted to current user). Exit 0, reported by the user.
2. `psql -w` preflight against `cloudtask_dev` via `PGPASSFILE` — **exit 0**, row: `cloudtask_dev | cloudtask_app | 127.0.0.1 | 55432 | owner cloudtask_app`.
3. Django with the same passwordless `DATABASE_URL` — **exit 0**, identity assertion passed; `manage.py check` — **exit 0** (0 issues).
4. App run + endpoint checks — **all 200** after one build step (see "Incident found during verification" below).
5. Browser acceptance via the existing chrome-devtools automation session (no new tooling installed) — `/`, `/login/`, `/register/` all rendered fully styled; screenshots captured.

## Exact commands and exit codes

Preflight (agent, Git Bash; `PGPASSFILE` and `PSQL_HISTORY=NUL` exported; no password in command or URL):

```bash
export PGPASSFILE="C:/Users/Ky/AppData/Local/CloudTaskManager/pgpass.conf"; export PSQL_HISTORY=NUL
"C:/Users/Ky/AppData/Local/CloudTaskManager/postgresql16/binaries/bin/psql.exe" -X -w -v ON_ERROR_STOP=1 \
  -h 127.0.0.1 -p 55432 -U cloudtask_app -d cloudtask_dev \
  -c "SELECT current_database(), current_user, host(inet_server_addr()), inet_server_port(), pg_get_userbyid(datdba) FROM pg_database WHERE datname = current_database();"
# exit 0 — cloudtask_dev | cloudtask_app | 127.0.0.1 | 55432 | cloudtask_app
```

Agent environment for all Django commands (password lives only in the pgpass file):

```bash
export PGPASSFILE="C:/Users/Ky/AppData/Local/CloudTaskManager/pgpass.conf"
export DATABASE_URL="postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_dev"
export SECRET_KEY="local-04l-agent-check-only"   # ephemeral, non-production
export DJANGO_ENV=local DEBUG=False SECURE_SSL_REDIRECT=False
```

Django identity check (repo root must be on `sys.path`; `python -I` removes it and fails with `ModuleNotFoundError: No module named 'config'` — first attempt exit 1, resolved by using `python -B` with an explicit `sys.path.insert(0, os.getcwd())`, matching the existing 04K launcher's approach):

```bash
.venv/Scripts/python.exe -B -c "...django.setup(); cursor SELECT identity query; assert row == ('cloudtask_dev','cloudtask_app','127.0.0.1',55432,'cloudtask_app')"
# exit 0 — DJANGO_DB_IDENTITY=PASS
.venv/Scripts/python.exe manage.py check
# exit 0 — System check identified no issues (0 silenced).
```

Server + endpoint checks:

```bash
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --noreload   # background
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health/     # 200, JSON {"status":"ok","service":"cloud-task-manager","version":"1.1.0-auth"}
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/      # 200, title "Log in | Cloud Task Manager"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/register/   # 200, title "Create account | Cloud Task Manager"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/            # 200, title "Cloud Task Manager"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/static/css/app.5695095752b7.css  # 200 text/css 14632 bytes
```

## Incident found during verification (and fix)

First server start: `/health/` returned 200 but `/`, `/login/`, `/register/` returned **500**. Root cause captured via an in-process reproduction (test client + `django.request` log record, no settings file changes):

```text
ValueError: Missing staticfiles manifest entry for 'css/app.css'
```

`STATIC_ROOT` (`staticfiles/`) did not exist — `collectstatic` had never been run on the host (Docker Compose normally runs it at container startup; the previous 04J-C preview predated no manifest issues because that run also never exercised static assets under DEBUG=False). Fix was the standard build step, not an app change:

```bash
.venv/Scripts/python.exe manage.py collectstatic --noinput
# exit 0 — 128 files copied, 384 post-processed; staticfiles/ is gitignored (.gitignore:25)
```

After restarting the server, all endpoint checks above passed.

## Browser automation availability (task step 8)

The session's existing chrome-devtools MCP browser was used (`list_pages` → stable single-page session; no framework installed). Navigated to `/`, `/login/`, `/register/`; all three rendered with correct titles, styled layout, and intact forms (username/password fields, Log in / Create your account CTAs). Screenshots: session temp files `browser-home.png`, `browser-login.png`, `browser-register.png`.

## PASS / FAIL / NOT RUN summary

| Check | Result |
| --- | --- |
| User password re-entry (private, no exposure) | PASS |
| `psql -w` cloudtask_dev via PGPASSFILE | PASS (exit 0) |
| Django identity with passwordless DATABASE_URL | PASS (exit 0) |
| `manage.py check` | PASS (exit 0) |
| `collectstatic --noinput` | PASS (exit 0) |
| `/health/` `/login/` `/register/` `/` | PASS (all 200) |
| Hashed static CSS asset | PASS (200 text/css) |
| Browser rendering of the three pages | PASS (styled screenshots) |
| Django test suites (04K) | NOT RUN (out of scope for this recovery; reusable command in 04L report) |
| `cloudtask_test_04k` connectivity | NOT RUN (same pgpass entry present, untested this session) |

## Notes, constraints honored

- No credentials displayed, logged, or transmitted; `psql -w` used everywhere; `DATABASE_URL` contains no password.
- No app code, settings, permissions, pg_hba.conf, Docker, Azure or WebIOT changes. Only workspace addition: this report. Build artifacts: gitignored `staticfiles/`.
- Isolated test suites remain separated from `cloudtask_dev` (launcher still refuses it). No destructive test setup ran; `cloudtask_dev` data untouched (read-only identity queries only).
- The dev server is still running in the agent background (`127.0.0.1:8000`, `--noreload`) with the environment above; stop it before reuse if the port conflicts.

## Git status

`git status --short --branch` exit 0: `main` has no commits; project entries untracked as before (`backend/`, `frontend/` now also visible untracked); `docs/reports/` untracked; the only new file from this task is this report. Nothing staged, committed, pushed, or reset.

## Reusable non-interactive procedure (delta from 04L)

The 04L procedure stands, with two additions learned here: (1) repo root must be on `sys.path` (use `python -B` + explicit insert, or run `manage.py` from the repo root without `-I`); (2) run `collectstatic --noinput` once before serving with DEBUG=False, or every page except `/health/` returns 500 on the missing manifest.
