# Step 10C — Docker Handoff Fixes (Localization & Home Regression Test)

Date: 2026-11-09
Repository: `C:\ProjectCloud\cloud-task-manager`
Branch: `main` (`origin/main`)

## 1. Changed Files

| File | Change Summary |
|---|---|
| `Dockerfile` | Added `COPY locale/ ./locale/` to copy compiled Vietnamese gettext catalogs (`locale/vi/LC_MESSAGES/django.po` and `django.mo`) into `/app/locale/` before changing ownership to the non-root `django` user. Preserved Python 3.11-slim, Gunicorn, and PostgreSQL runtime architecture. |
| `tasks/test_authentication.py` | Replaced the stale `class="workspace-login"` CSS-class check in `PublicEndpointTests.test_home_is_public` with `self.assertContains(response, _('Make room for the work that matters.'))` and `self.assertNotIn('_auth_user_id', self.client.session)` to verify public translated hero copy and anonymous session state without altering application code. |
| `docs/reports/step-10c-docker-handoff-fixes.md` | Recorded handoff verification evidence, remaining risks, and Git status. |

## 2. Evidence & Verification

### Issue 1 — Docker Localization Requirement
- `config/settings.py` sets `USE_I18N = True`, `LANGUAGE_CODE = 'vi'`, `LOCALE_PATHS = [BASE_DIR / 'locale']`, and enables `config.middleware.default_language_middleware` + `django.middleware.locale.LocaleMiddleware`.
- `.dockerignore` does not exclude `locale/`, so adding `COPY locale/ ./locale/` to `Dockerfile` ensures `/app/locale/vi/LC_MESSAGES/django.mo` is present inside the container image at runtime.

### Issue 2 — Home Regression Test Reproduction & Fix
- **Pre-fix reproduction:**
  - Command: `.\.venv\Scripts\python.exe manage.py test tasks.test_authentication.PublicEndpointTests.test_home_is_public`
  - Result: **FAIL** (exit code `1`, `Ran 1 test`, `failures=1` — `AssertionError: Couldn't find 'class="workspace-login"' in the following response`).
- **Post-fix verification commands & results:**

| Command | Exit Code | Result |
|---|---:|---|
| `.\.venv\Scripts\python.exe manage.py check` | `0` | **PASS** — `System check identified no issues (0 silenced).` |
| `.\.venv\Scripts\python.exe manage.py test tasks.test_authentication -v 2` | `0` | **PASS** — `Ran 22 tests in 10.409s — OK` (`22/22` passed, including `test_home_is_public`) |
| `.\.venv\Scripts\python.exe manage.py test tasks` | `0` | **PASS** — `Ran 65 tests in 47.879s — OK` (`65/65` passed across `tasks.tests`, `tasks.test_authentication`, `tasks.test_task_crud`) |
| `docker compose config --quiet` *(with non-secret placeholders `POSTGRES_PASSWORD=placeholder-non-secret`, `SECRET_KEY=placeholder-non-secret`)* | `0` | **PASS** — Compose configuration syntax validated |
| `git diff --check` | `0` | **PASS** — No whitespace or conflict marker errors |
| Full `docker compose build` / container runtime boot | — | **NOT EXECUTED** — Only static `docker compose config --quiet` was executed in this step; container image build and runtime verification belong to the Docker team member handoff |

## 3. Remaining Risks

1. **Container Build & Runtime Verification Pending:** `docker compose up --build -d` was not executed in this step; the Docker team member should verify container build, migrations, `collectstatic`, `/health/` readiness, and Vietnamese UI rendering on port `8080`.
2. **Untranslated Sample Preview Strings in `locale/vi/LC_MESSAGES/django.po`:** Six sample preview strings in `templates/includes/workspace_preview.html` remain untranslated in the Vietnamese catalog and fall back to English until compiled with `msgfmt`.
3. **Historical / Legacy Files in Repository:** Legacy `backend/`, `docs/archive/`, and `design-reference/` directories remain tracked pending separate cleanup approval.

## 4. Git Status

- Tracked branch: `main` (`origin/main`)
- Staged & committed files in this handoff fix: `Dockerfile`, `tasks/test_authentication.py`, `docs/reports/step-10c-docker-handoff-fixes.md`
- Working tree clean of tracked modifications after commit; untracked local environment artifacts (`.venv/`, `staticfiles/`, editor/agent folders) remain untracked and ignored.
