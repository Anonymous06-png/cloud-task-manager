# Step 10B — GitHub Publication & Repository File Inventory

Date: 2026-11-09
Repository: `C:\ProjectCloud\cloud-task-manager`
Remote: `https://github.com/Anonymous06-png/cloud-task-manager` (`origin/main`)

## 1. Publication Scope

Published completed local changes from Tasks 06 through 10A to `main` (36 files total: 20 modified tracked files, 1 new template partial, and 15 reports in `docs/reports/`):

- **Configuration & Local Launchers:** `config/settings.py` (use `StaticFilesStorage` when `DEBUG=True`, retain WhiteNoise `CompressedManifestStaticFilesStorage` when `DEBUG=False`), `start-web.ps1` and `start-web.bat` (UTF-8 database identity preflight, DPAPI-protected local signing key in `%LOCALAPPDATA%\CloudTaskManager\secrets\`, running-server reuse/guarded transition detection, argument forwarding).
- **UI & Templates (Tasks 07–10A):** `static/css/app.css`, `static/css/design-tokens.css`, `static/js/app.js`, `templates/base.html`, `templates/dashboard.html`, `templates/home.html`, `templates/settings.html`, `templates/task_list.html`, `templates/task_detail.html`, `templates/task_form.html`, `templates/task_confirm_delete.html`, `templates/registration/login.html`, `templates/registration/signup.html`, `templates/includes/task_row.html`, `templates/includes/workspace_preview.html`, and new `templates/includes/form_field.html`.
- **Tests (Tasks 06–06B):** `tasks/test_task_crud.py` and `tasks/tests.py` (repaired bilingual/empty-state assertions, added sequential Unicode/Vietnamese/emoji persistence test and form/CSRF/ownership regressions).
- **Engineering Reports:** `docs/reports/step-06-*.md` through `docs/reports/step-10b-github-publish-and-repo-inventory.md` (15 reports).

Excluded from staging (untracked/ignored local state): `.venv/`, `staticfiles/`, `__pycache__/`, `.mimosa/`, `.zcode/`, external `%LOCALAPPDATA%\CloudTaskManager\` secrets/databases, and temporary directories.

## 2. Pre-Commit Checks & Security Review

| Check | Result |
|---|---|
| `git diff --check` | **PASS** (exit 0; informational LF→CRLF warnings only) |
| `python manage.py check` | **PASS** (exit 0; 0 issues) |
| `node --check static/js/app.js` | **PASS** (exit 0) |
| PowerShell 5.1 AST parse of `start-web.ps1` | **PASS** (`ps1_parse_errors=0`, exit 0) |
| `python manage.py test tasks.test_task_crud tasks.tests` (`DEBUG=False`) | **PASS** (43/43 tests OK) |
| `python manage.py test tasks` (`DEBUG=False`) | **64/65 PASS** — 1 stale assertion in untouched `tasks/test_authentication.py:236` (`test_home_is_public` checks `class="workspace-login"` whereas Task 10A updated `templates/home.html` to `class="home-hero"`) |
| Secret & credential scan across all 36 staged files | **PASS** — 0 secrets, tokens, keys, `.env` files, or database dumps |

## 3. Repository File Inventory & Classification

After this publication, Git tracks **190 files** across the repository. No files were deleted, untracked, or removed during this inventory.

### A. REQUIRED — Essential Application, Database, Docker & Runtime Files (36 files)

These files are required for a team member to clone, build, and run the Django + PostgreSQL application with Docker (`docker compose up --build -d` after copying `.env.example` to `.env`):

- **Docker & Environment Bootstrap (6 files):** `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.env.example`, `.gitignore`, `requirements.txt`
- **Django Entry & Project Config (5 files):** `manage.py`, `config/__init__.py`, `config/middleware.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py` *(6 files including `__init__.py`)*
- **Tasks Application & Database Schema (8 files):** `tasks/__init__.py`, `tasks/admin.py`, `tasks/apps.py`, `tasks/forms.py`, `tasks/models.py`, `tasks/urls.py`, `tasks/views.py`, `tasks/migrations/__init__.py`, `tasks/migrations/0001_initial.py` *(9 files)*
- **HTML Templates (13 files):** `templates/base.html`, `templates/home.html`, `templates/dashboard.html`, `templates/settings.html`, `templates/task_list.html`, `templates/task_detail.html`, `templates/task_form.html`, `templates/task_confirm_delete.html`, `templates/registration/login.html`, `templates/registration/signup.html`, `templates/registration/logged_out.html`, `templates/includes/task_row.html`, `templates/includes/workspace_preview.html`, `templates/includes/form_field.html` *(14 files)*
- **Static Assets & Localization (5 files):** `static/css/design-tokens.css`, `static/css/app.css`, `static/js/app.js`, `locale/vi/LC_MESSAGES/django.po`, `locale/vi/LC_MESSAGES/django.mo` *(Note: `Dockerfile` currently copies `config/`, `tasks/`, `templates/`, `static/`; adding `COPY locale/ ./locale/` is recommended so container builds include compiled Vietnamese translations)*

### B. USEFUL — Documentation, Automated Tests & Local Developer Assets (29 files)

- **Automated Test Suite (3 files):** `tasks/tests.py`, `tasks/test_authentication.py`, `tasks/test_task_crud.py`
- **Core Documentation & Course Spec (7 files):** `README.md`, `CLAUDE.md`, `docs/README.md`, `docs/Project-Cloud-Computing.pdf`, `docs/requirements.md`, `docs/reports/README.md`, `docs/design/README.md`
- **Windows Local Dev Launchers & Placeholder (3 files):** `start-web.ps1`, `start-web.bat`, `static/.gitkeep`
- **Active Milestone Reports in `docs/reports/` (16 key reports):** foundational, PostgreSQL, bilingual UI, security/publication, stabilization, and UI refinement reports documenting current architecture and verification state.

### C. REVIEW FOR REMOVAL — Legacy Code, Duplicate Designs & Historical Artifacts (123 files)

Candidates for user review before any cleanup or archiving decision (none removed in this task):

1. **`backend/` (5 files):** `backend/auth.js`, `backend/db.js`, `backend/package.json`, `backend/server.js`, `backend/tasks.js` — Inactive legacy Node.js/Express implementation at the repo root, already duplicated byte-for-byte in `docs/archive/legacy-node/backend/`.
2. **`docs/archive/legacy-node/` (8 files):** `Dockerfile.node`, `docker-compose.node.yml`, `README.md`, and `backend/*.js` — Archived copy of the superseded Node.js stack.
3. **`design-reference/` (51 files) & `design-system/` (11 files):** Full exported 1Design/Figma bundle (~1.6 MB of static HTML screens, JSON metadata, CSS kits, and PNG screenshots) committed during Task 05T. Not referenced at runtime by Django.
4. **`docs/design/` (7 files):** `docs/design/figma-exports/*.png` (5 PNGs duplicating screenshots in `design-reference/`), `task-dashboard-design-spec.md`, `task-dashboard-prototype.html`.
5. **`docs/archive/reports/` (24 files) & incremental sub-step reports in `docs/reports/` (22 files):** Historical troubleshooting logs and intermediate sub-step reports (e.g., `step-04i-*`, `step-04k-*`, `step-04l-*`, `step-05i`–`05s`, `step-06b-*`, `step-08b/c`, `step-09-*`).
6. **`tools/` (3 files):** `tools/step-04k-c-manual.ps1`, `tools/step-04k-c-test-launcher.py`, `tools/step-04k-d-run-tests.py` — One-off Task 04K local PostgreSQL recovery scripts.

### D. MUST NOT COMMIT — Secrets, Local Data, Caches & Generated Outputs (0 tracked; ignored/untracked)

- **Environment & Secrets:** `.env`, `.env.*`, `pgpass.conf`, `*.pgpass`, `*.pem`, `*.key`, `secrets/`, `%LOCALAPPDATA%\CloudTaskManager\secrets\django-secret-key.dpapi`
- **Databases & Backups:** `db.sqlite3`, `*.dump`, `*.sql`, `backups/`, `%LOCALAPPDATA%\CloudTaskManager\postgresql16\data\`
- **Virtualenvs, Caches & Build Outputs:** `.venv/`, `__pycache__/`, `*.pyc`, `staticfiles/` (generated by `collectstatic`), `backend/node_modules/`
- **Agent / Editor State:** `.mimosa/`, `.zcode/`, `.vscode/`, `.idea/`
- **Untracked Empty Directory:** `frontend/` (empty local folder; Git does not track empty directories)
