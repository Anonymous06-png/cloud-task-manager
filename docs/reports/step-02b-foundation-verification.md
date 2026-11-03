# Task 02B Report: Django Foundation Verification (Static Scope)

**Date**: 2026-10-19
**Workspace**: `C:/ProjectCloud/cloud-task-manager`
**Git root**: `C:/ProjectCloud/cloud-task-manager`
**Branch**: `main` (0 commits, all files untracked)
**Scope**: Independent verification only. Docker daemon unavailable.

## Scope Constraints Honored

- No system software or Python packages were installed.
- PostgreSQL was NOT replaced with SQLite.
- No runtime success is claimed from static inspection.
- No Git staging/commit/push. No destructive cleanup. No Azure operations.
- WebIOT repository was not accessed.

---

## 1. CHECKS ACTUALLY EXECUTED AND THEIR RESULTS

### 1.1 Workspace / environment

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| Working directory | `Get-Location` | `C:\ProjectCloud\cloud-task-manager` | PASS |
| Git root | `git rev-parse --show-toplevel` | `C:\ProjectCloud\cloud-task-manager` | PASS |
| Branch / commits | `git status`, `git log` | `main`, 0 commits, all untracked | INFO |
| Local Python | `python --version` | `Python 3.14.3` | INFO |
| Local Django installed | `python -m pip list` | Django/psycopg not present | INFO |
| Docker client | `docker --version` | `29.8.0, build 88096ef` | PASS |
| Docker Compose | `docker-compose --version` | `v5.5.1` | PASS |
| `.env` present | `Test-Path .env` | `False` | INFO |

### 1.2 Python syntax checks — executed

Command: `python -m py_compile <file>` (Python 3.14.3).

| File | Exit code | Status |
|------|-----------|--------|
| manage.py | 0 | PASS |
| config\settings.py | 0 | PASS |
| config\urls.py | 0 | PASS |
| config\wsgi.py | 0 | PASS |
| config\__init__.py | 0 | PASS |
| tasks\__init__.py | 0 | PASS |
| tasks\models.py | 0 | PASS |
| tasks\views.py | 0 | PASS |
| tasks\urls.py | 0 | PASS |
| tasks\tests.py | 0 | PASS |
| tasks\apps.py | 0 | PASS |
| tasks\admin.py | 0 | PASS |

**Result: 12/12 files compile (exit 0).** This proves syntax validity only, not
importability or runtime correctness (Django is not installed).

### 1.3 Legacy archive integrity — executed

Command: `Get-FileHash -Algorithm SHA256` on originals (`backend\`) and archive
(`docs\archive\legacy-node\backend\`).

| File | Looks directory | Original == Archive |
|------|-----------------|---------------------|
| auth.js | same | MATCH |
| db.js | same | MATCH |
| package.json | same | MATCH |
| server.js | same | MATCH |
| tasks.js | same | MATCH |

Hashes (identical for original and archive):

```
auth.js       2B8456204323EDE01A1678F3FB047E01CF8E278971EC60E23FB4E51071DF1E6D
db.js         CC8B1FC0F8D477998C492D3C6C0E3882A9E3DD9D508CFA0DE1CFEDAA876F0CBA
package.json  55FF0763088522F49D9F30FA06E3C191114966752514F4F361BB1A1D2F4074C5
server.js     3A3840A81241156CF4FA8B411A12E509FD942960A26388EC276BF4ACFC858D15
tasks.js      05ECA64A50EC18998F65D620128AE83A44389C37926D6E43088DE7F4056D246B
```

**Result: 5/5 archived files are byte-identical to originals.** The step-02
report documented only 2 of the 5 hashes; this task verifies all 5.

### 1.4 Secret protection / ignore rules — executed

Command: `git check-ignore -v .env .env.local secrets/test.pem db.sqlite3`

```
.gitignore:29:.env               .env
.gitignore:30:.env.*             .env.local
.gitignore:56:secrets/           secrets/test.pem
.gitignore:23:db.sqlite3         db.sqlite3
```

**Result: PASS** — `.env`, `.env.*`, secret dirs, and SQLite files are ignored.
`.env.example` is preserved by the `!.env.example` negation.

### 1.5 Dependency compatibility (upstream metadata) — executed

Queried PyPI JSON for each pinned version. Container base is `python:3.11-slim`
(Dockerfile:2); local interpreter is 3.14.3.

| Package | Pinned | requires_python | Classifiers (max) | Wheel | Py3.11 (container) | Py3.14 (local) |
|---------|--------|-----------------|-------------------|-------|--------------------|----------------|
| Django | 5.1.3 | `>=3.10` | 3.10–3.13 | yes | COMPATIBLE | NOT SUPPORTED |
| psycopg2-binary | 2.9.10 | `>=3.8` | 3.8–3.13 | yes (many) | COMPATIBLE | NO cp314 wheel |
| dj-database-url | 2.2.0 | (unset) | 3.7–3.12 | yes | COMPATIBLE | UNVERIFIED |
| gunicorn | 23.0.0 | `>=3.7` | 3.7–3.12 | yes | COMPATIBLE | UNVERIFIED |
| python-decouple | 3.8 | (unset) | generic py3 | yes | COMPATIBLE | UNVERIFIED |
| whitenoise | 6.8.2 | `>=3.9` | 3.9–3.13 | yes | COMPATIBLE | UNVERIFIED |

Latest available upstream (queried 2026-10-19): Django 6.1.2, psycopg2-binary
2.9.13, dj-database-url 3.1.2, gunicorn 26.2.0, whitenoise 6.12.0,
python-decouple 3.8.

**Findings:**
- All six pins are compatible with the container's Python 3.11 and have
  prebuilt wheels, so the Docker image install step should resolve.
- **None of the pins are supported on the local Python 3.14.3.** Django 5.1.3
  caps at 3.13, and psycopg2-binary 2.9.10 ships no cp314 wheel. Running the
  pinned stack on the local 3.14 interpreter is unsupported and may fail.
- Django 5.1.3 is **not** the latest stable release; it is an end-of-life
  5.1-series patch. It also carries multiple advisories fixed in 5.1.4–5.1.15
  (e.g., CVE-2024-53907/53908, CVE-2025-26699, CVE-2025-32873,
  CVE-2025-48432, CVE-2025-57833, CVE-2025-59681/59682, CVE-2025-64458/64459/64460,
  CVE-2025-13372). Upstream now labels the 5.1 series "unsupported".

### 1.6 Docker Compose config parse — executed (no daemon required)

Command: `docker compose config --quiet`

```
time="2026-10-19T14:59:02+07:00" level=warning msg="The \"SECRET_KEY\" variable is not set. Defaulting to a blank string."
Exit code: 0
```

**Result: PASS (static parse only).** The compose file is syntactically valid.
The warning confirms `SECRET_KEY` resolves to an empty string with no `.env`
present (see finding 2.3). This does NOT validate image build or runtime.

---

## 2. STATIC FINDINGS THAT STILL NEED RUNTIME VERIFICATION

These are code/config conclusions derived by reading source and official docs.
They are NOT runtime results and must be confirmed before they are claimed fixed.

### 2.1 `STATICFILES_STORAGE` is a removed setting in Django 5.1 (settings.py:112)

`config/settings.py:112` sets `STATICFILES_STORAGE =
'whitenoise.storage.CompressedManifestStaticFilesStorage'`.

Per the official Django deprecation timeline (5.1 section), the
`DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` settings **"will be removed"**
in 5.1 (source: https://docs.djangoproject.com/en/5.1/internals/deprecation/).
Django silently ignores unknown settings, so this will not raise an error but
also will **not configure** WhiteNoise manifest storage. Static file hashing /
cache-busting would be inactive.

- Runtime verification: `python manage.py check`, then `collectstatic` and
  inspect `staticfiles/` for hashed filenames.
- Correction target: use the `STORAGES` dict:
  `STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}`.

### 2.2 Health check vs. forced HTTPS redirect (settings.py:118-119, compose:47, Dockerfile:42-43)

`DEBUG` defaults to `False`, and with `DEBUG=False` the settings enable
`SECURE_SSL_REDIRECT` (default `True`). The container health checks request
`http://localhost:8080/health/` over plain HTTP. With SSL redirect enabled the
app returns a 301 to `https://...`; `urllib` follows it, the TLS handshake
fails (no cert on 8080), and the container can be reported **unhealthy**.

- Runtime verification: `docker compose ps` (health status), and
  `curl -i http://localhost:8080/health/`.
- Likely mitigation for local/no-TLS runs: set `SECURE_SSL_REDIRECT=False`
  (or `DEBUG=True`) for the compose health check environment. Requires
  confirmation, not assumed.

### 2.3 Empty `SECRET_KEY` is accepted at startup (settings.py:13-18, compose:35)

Settings only raises when `SECRET_KEY is None`. Compose passes
`SECRET_KEY: ${SECRET_KEY}` with **no default**, so an unset variable becomes an
empty string `""`, which passes the `is None` check. The container could start
with an empty signing key (security risk, not a crash).

- Runtime verification: `docker compose config` output + a container start with
  `SECRET_KEY` unset, then confirm behavior.

### 2.4 Untracked empty `static/` and `frontend/` directories (Dockerfile:29)

`static/` and `frontend/` exist locally but are **empty and therefore invisible
to Git** (`git ls-files static frontend` returns nothing; `git status` does not
list them). On a fresh clone neither directory will exist, so Dockerfile line 29
`COPY static/ ./static/` will fail the build. Locally the build context still
has the empty dir, so this is not reproducible until after a clone/push.

- Additional static consequence: `STATICFILES_DIRS = [BASE_DIR / 'static']`
  (`settings.py:111`) points to a directory that will be absent after clone,
  which raises the `staticfiles.W004` check warning.
- Runtime verification: build from a clean checkout.
- Correction target: commit a placeholder (e.g., `static/.gitkeep`) and/or drop
  the `COPY static/` line.

### 2.5 Local interpreter/container interpreter mismatch

Container uses Python 3.11 (Dockerfile:2); local is 3.14.3. Pinned Django 5.1.3
and psycopg2-binary 2.9.10 do not support 3.14 (section 1.5). Any local
`pip install -r requirements.txt` / `manage.py` verification done on 3.14 may
fail or behave differently from the container.

- Runtime verification: create the venv with a 3.10–3.13 interpreter (or run all
  checks inside the container) before trusting local results.

### 2.6 Other static observations (informational)

- `tasks/tests.py:29` asserts `Content-Type == 'application/json'`. `JsonResponse`
  emits exactly that value, so the assertion is consistent — but the test has
  never been executed.
- `templates/home.html` uses only standard tags (`{{ }}`, `{% for %}`); no static
  tag is referenced, so 2.1 does not break this template.
- `dj_database_url.parse(DATABASE_URL, conn_max_age=600)` (`settings.py:80`) is
  syntactically valid; URL parsing correctness is unverified without Django.
- `.env.example` sets `DATABASE_URL` host to `db`, which only resolves inside the
  compose network; a local non-container run would need a different host.

---

## 3. DOCKER / POSTGRESQL CHECKS MARKED BLOCKED

Docker daemon is not running:

```
docker info
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine;
the system cannot find the file specified.
Exit code: 1
```

| Check | Command | Status |
|-------|---------|--------|
| Docker daemon reachable | `docker info` | BLOCKED |
| Compose services up | `docker compose up -d` | BLOCKED |
| Image build | `docker compose build` | BLOCKED |
| Container health | `docker compose ps` | BLOCKED |
| Django system check (container) | `docker compose exec app python manage.py check` | BLOCKED |
| Migrations applied | `docker compose exec app python manage.py showmigrations` | BLOCKED |
| PostgreSQL connectivity | `docker compose exec db pg_isready` / `psql` | BLOCKED |
| `/health/` HTTP response | `Invoke-WebRequest http://localhost:8080/health/` | BLOCKED |
| Home page HTTP response | `Invoke-WebRequest http://localhost:8080/` | BLOCKED |
| Smoke tests | `docker compose exec app python manage.py test` | BLOCKED |
| Persistent-data restart test (T4) | stop/start + re-query | BLOCKED |

Additionally blocked without a `.env` / secrets: production settings validation
and live database access.

**Reason**: Docker Desktop engine is not started. This task is prohibited from
installing or starting system software. No runtime success is claimed.

---

## 4. DOCUMENTATION CORRECTIONS

Applied/identified during this task:

1. **`docs/reports/step-02-django-foundation.md` — false version rationale.**
   Section 4 claimed *"Django 5.1.3: Latest stable release as of 2026-10."* This
   is incorrect: the latest release is 6.1.2 and the 5.1 series is
   end-of-life/unsupported. A correction note has been appended to that report.

2. **`docs/reports/step-02-django-foundation.md` — line-count table inaccuracies.**
   Section 3 lists counts that do not match the files (actual counts in
   parentheses): `settings.py` 135 (129), `tasks/models.py` 31 (32),
   `tasks/views.py` 26 (29), `tasks/urls.py` 11 (12), `tasks/tests.py` 48 (54),
   `tasks/admin.py` 10 (14), `tasks/apps.py` 8 (9), `templates/home.html` 111
   (134), `requirements.txt` 18 (22). Recorded in the appended correction note.

3. **`docs/requirements.md` — status stale.** The "Implementation Status" lists
   "Django project foundation (in progress)". The foundation files are present
   and syntax-valid; status updated to "complete — runtime verification pending
   (Task 02B)". "Known Issues" updated to record the blocked Docker/PostgreSQL
   verification.

4. **Archive-hash coverage gap.** Step-02 documented only 2 of 5 SHA256 hashes;
   section 1.3 of this report supplies all 5 with verified matches.

No files were deleted. All changes are additive or factual corrections.

---

## 5. EXACT REMAINING VERIFICATION COMMANDS (NOT YET RUN)

Run after Docker Desktop is started. Use an interpreter in the 3.10–3.13 range
for local-only steps, or run everything inside the container.

### 5.1 Prerequisites

```powershell
# Generate a real secret key (do NOT commit it)
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
# Create .env from template and fill SECRET_KEY, POSTGRES_PASSWORD
Copy-Item .env.example .env
```

### 5.2 Local Django checks (requires a supported Python + installed deps)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m django --version
$env:SECRET_KEY = "<generated-value>"
$env:DATABASE_URL = "postgresql://taskuser:changeme@localhost:5432/taskmanager"
$env:DEBUG = "True"
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py makemigrations tasks
```

### 5.3 Docker stack

```powershell
docker info                                   # confirm daemon is up
docker compose config                         # static parse
docker compose build
docker compose up -d
docker compose ps                             # verify health, watch finding 2.2
docker compose logs app
docker compose exec app python manage.py showmigrations
docker compose exec app python manage.py check
docker compose exec app python manage.py test
docker compose exec app ls staticfiles        # verify finding 2.1 hashing
```

### 5.4 PostgreSQL connectivity and persistence

```powershell
docker compose exec db pg_isready -U taskuser -d taskmanager
docker compose exec db psql -U taskuser -d taskmanager -c "\dt"
docker compose exec db psql -U taskuser -d taskmanager -c "\d tasks_task"
```

### 5.5 Endpoint and restart (T4/T5)

```powershell
Invoke-WebRequest http://localhost:8080/health/ -UseBasicParsing
Invoke-WebRequest http://localhost:8080/ -UseBasicParsing
docker compose restart app
docker compose exec db psql -U taskuser -d taskmanager -c "SELECT count(*) FROM tasks_task;"
```

---

## 6. SUMMARY

- Executed: workspace confirmation, 12/12 syntax checks, 5/5 archive SHA256
  matches, ignore-rule checks, PyPI dependency compatibility, compose static parse.
- Static findings requiring runtime evidence: removed `STATICFILES_STORAGE`
  (2.1), HTTPS-redirect vs health check (2.2), empty `SECRET_KEY` acceptance
  (2.3), untracked empty `static/`/`frontend/` breaking clean builds (2.4),
  local Python 3.14 vs container 3.11 (2.5), plus informational notes (2.6).
- Blocked: all Docker daemon, image build, container runtime, and PostgreSQL
  checks (section 3).
- No runtime success is claimed. Authentication work was not started.
