# UI-07A-FIX — local Profile migration activation — 2026-11-12

## Outcome

**FIXED:** applied only `tasks.0002_profile` to the confirmed running nonproduction development database. `tasks_profile` now exists, the migration is recorded applied, and authenticated HTTP GETs to `/dashboard/`, `/profile/` and `/profile/edit/` return **200**, without redirects, from the existing port-8000 server.

No application source or migration edits, manual table creation, database recreation/drop, environment-file changes, service restarts, new accounts/sessions, profile/task saves, Git staging/commits/push or production/test-database migrations.

## Exact runtime identity and authorization gates

- Port `127.0.0.1:8000` listener: **PID 14108**, command `manage.py runserver 127.0.0.1:8000`. Parent **17036** is the repository's `C:\ProjectCloud\cloud-task-manager\.venv\Scripts\python.exe`.
- The listener's established PostgreSQL socket is `127.0.0.1:64099 → 127.0.0.1:55432`. A live `pg_stat_activity` query independently maps **client port 64099** to **`cloudtask_dev_utf8_06b` / `cloudtask_app`**. This establishes the actual running server's database rather than merely assuming the launcher target.
- Live identity tuple: database **`cloudtask_dev_utf8_06b`**, user/owner **`cloudtask_app`**, server **`127.0.0.1:55432`**, encoding **UTF8**. Matches the existing local launcher, `DJANGO_ENV=local`, and this task's explicit nonproduction development migration authorization. Neither test nor production database was selected.
- Before any migration: `tasks.0001_initial` applied; `tasks.0002_profile` pending; `public.tasks_profile` absent. Django MigrationExecutor asserted the entire target plan was exactly **one forward migration: `tasks.0002_profile`**. Any different identity or plan would stop execution.
- Used the existing private `PGPASSFILE` and **existing persistent DPAPI-protected signing key**, loaded into child-process memory using the launcher's decryption/base64 procedure. Verified existing key file/owner and rejected conflicting inherited keys or an unexpected `.env`. No key provisioning, replacement, plaintext file, credential output or disposable test SECRET_KEY. An existing session validated with that key and was subsequently accepted by the live server.

Read the UI-07A report, `tasks/migrations/0002_profile.py` and relevant secure local-launcher configuration before activation.

## Actual commands and exit codes

Working directory: `C:\ProjectCloud\cloud-task-manager`. `PY` means `.venv\Scripts\python.exe`; `$T` means `C:\Users\Ky\AppData\Local\Temp\opencode`.

| Command / operation actually run | Exit | Result |
|---|---:|---|
| PowerShell `Get-NetTCPConnection -State Listen -LocalPort 8000`, `Get-CimInstance Win32_Process` for listener/parent; `git status --short --branch` | 0 | Identified owned repository runserver process; recorded dirty baseline. |
| Focused PowerShell listener/socket inspection, followed by inline read-only `psycopg2` `pg_stat_activity` query via `PY -I -B -` | 0 | Correlated listener PID 14108/client port 64099 with the exact dev database and role. |
| `& $T\ui07a-fix-activate.ps1 2>&1 \| Tee-Object -FilePath $T\ui07a-fix-activate.log` (propagating `$LASTEXITCODE`) | **0** | Secure key/environment loading, repeated runtime/database/encoding gates, exact migration-plan assertion, authenticated GETs and data-preservation checks all passed. Calls `PY -I -B $T\ui07a-fix-activate.py`. |
| Within that guarded runner: `call_command('check')` | 0 (runner) | Django: no issues, 0 silenced. |
| `call_command('showmigrations', 'tasks', plan=True)` — before | 0 (runner) | `0001_initial` applied, `0002_profile` pending. |
| `call_command('migrate', 'tasks', '0002_profile', plan=True, interactive=False)` | 0 (runner) | Only `tasks.0002_profile / Create model Profile`. |
| `call_command('migrate', 'tasks', '0002_profile', interactive=False, verbosity=1)` | **0 (runner)** | **Applying tasks.0002_profile... OK**. Equivalent CLI: `PY manage.py migrate tasks 0002_profile --noinput`, under the existing secure runtime configuration. |
| `call_command('showmigrations', 'tasks', plan=True)` — after | 0 (runner) | Both tasks migrations applied. |
| `call_command('migrate', check=True, interactive=False)` | 0 (runner) | No unapplied migrations; equivalent to `manage.py migrate --check`. |
| SQL `to_regclass('public.tasks_profile')`, table count and fresh MigrationExecutor target-plan query | 0 (runner) | Table exists; zero profile rows; no pending target operations. |
| `urllib.request` authenticated HTTP GETs on the existing port-8000 server | 0 (runner) | **3/3 passed:** `/dashboard/`, `/profile/`, `/profile/edit/`, each 200/no redirect with expected page and authenticated account markup. Existing session cookie kept only in memory; no login POST, form POST or session creation. No browser automation. |
| Before/after public-table row-hash multiset and sequence comparisons | 0 (runner) | Every pre-existing row preserved; all non-metadata table contents/counts identical; existing non-metadata sequence values unchanged. |
| Final focused listener/status check and `git diff --check` | 0 | Same server PID; final status below; no whitespace errors (existing LF→CRLF advisories only). |

`call_command` entries execute in one guarded Python process, not separate shell processes: no command raised an exception and the overall runner exited 0. No standalone exit-code claims are made for embedded calls.

## Data preservation evidence

Before migration and after all authenticated GETs, the runner read each existing public table into SHA-256 multisets of PostgreSQL row-JSON representations, without logging field values. It required every old row hash/multiplicity to remain present and required exact equality outside migration/content-type/permission metadata. Only the new `tasks_profile` table may appear. Existing non-metadata sequences were also compared without advancing them.

| Table | Before | After | Result |
|---|---:|---:|---|
| `auth_user` | 16 | 16 | Exact existing rows preserved. |
| `tasks_task` | 20 | 20 | Exact existing rows preserved. |
| `django_session` | 10 | 10 | Exact existing rows preserved; no new sessions. |
| `django_migrations` | 34 | 35 | Existing rows retained; expected migration addition. |
| `django_content_type` | 12 | 13 | Existing rows retained; Profile content type added normally by Django. |
| `auth_permission` | 48 | 52 | Existing rows retained; four normal Profile permissions added by Django. |
| `tasks_profile` | Absent | 0 | Created by the migration, not manually; no existing account populated/edited. |

Other existing tables were also unchanged by row comparison. No intentional existing-object changes beyond normal migration metadata/sequence advancement. No secrets files were written. External artifacts are only the guarded runner scripts, sanitized log and count-only `$T\ui07a-fix-preservation.json`.

## Warnings / blockers / limits

- No remaining activation blocker or focused-check failure.
- While finding a valid existing session, Django logged **nine `Session data corrupted` warnings** for pre-existing sessions not decodable with the current persistent key. They were not repaired, deleted or re-signed. A valid existing session was found and used successfully; all ten stored sessions were preserved. No broader session/auth investigation was performed.
- No profile Save/Cancel POST tests, OAuth round trip, browser visual tests, full suite or unrelated audit: this task was limited to migration activation and three read-only authenticated page checks.

## Files / Git status

Only repository file created by this fix: **`docs/reports/ui-07a-fix-profile-migration-activation-2026-11-12.md`**. Existing application source, migration files and all pre-existing user changes were left untouched.

Branch `main...origin/main`. Baseline: **25 modified tracked paths / 50 untracked entries / zero staged entries**. Final (directory-collapsed status): **25 modified tracked paths / 51 untracked entries / zero staged entries**, with only this report added by UI-07A-FIX. No Git writes. Stopped after migration activation verification and this report.
