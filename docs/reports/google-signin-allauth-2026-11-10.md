# Report: Google Sign-In via django-allauth (2026-11-10)

Task: add "Continue with Google" to Login and Register using django-allauth
with the existing Django session authentication, without disturbing
username/password authentication, task ownership, or uncommitted work.

## Changed files (this task)

New:
- `tasks/context_processors.py` — exposes `google_oauth_enabled` to templates.
- `tasks/test_google_oauth.py` — focused tests (disabled/enabled modes + safe-linking guards).
- `templates/includes/google_button.html` — shared Flowspace-styled Google button (POST to the provider login URL).
- `templates/socialaccount/signup.html`, `templates/socialaccount/authentication_error.html`, `templates/socialaccount/login_cancelled.html` — Flowspace-styled allauth flow pages.
- `docs/google-oauth-setup.md` — Google Cloud Console setup, exact callback URLs, env-var configuration, account-linking safety notes.
- `docs/reports/google-signin-allauth-2026-11-10.md` — this report.

Modified:
- `requirements.txt` — added `django-allauth==65.21.1` and `requests==2.34.2` (allauth OAuth2 client requirement).
- `config/settings.py` — allauth apps, `AUTHENTICATION_BACKENDS` (ModelBackend + allauth backend), `AccountMiddleware`, context processor, env-driven Google provider config (`GOOGLE_OAUTH_CLIENT_ID`/`GOOGLE_OAUTH_CLIENT_SECRET` via `python-decouple`), safe-linking guards (`SOCIALACCOUNT_EMAIL_AUTHENTICATION=False`, `SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT=False`, `SOCIALACCOUNT_EMAIL_REQUIRED=True`).
- `config/urls.py` — `path('accounts/', include('allauth.urls'))`.
- `tasks/views.py` — `login(request, user, backend='django.contrib.auth.backends.ModelBackend')` in `register` (required once multiple auth backends exist; registration still authenticates via ModelBackend only).
- `.env.example` — commented-out `GOOGLE_OAUTH_*` placeholders with the local callback URL.
- `templates/registration/login.html`, `templates/registration/signup.html` — include `google_button.html` (both files already carried uncommitted redesign changes; only the one-line include was added).
- `static/css/app.css` — appended `.login-divider`, `.login-google`, `.btn-google`, `.google-g` classes (file already carried uncommitted changes; nothing else touched).

All other pre-existing uncommitted changes (locale, `design-tokens.css`, `app.js`, `test_authentication.py`, `base.html`, `home.html`, `workspace_preview.html`, `frontend/`, `static/flowspace/`, `static/fonts/`, other docs) are preserved untouched. No Git writes were made.

## Configuration behaviour

- Credentials come **only** from the environment (`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, both non-blank). No secrets in source, fixtures, tests or docs.
- With credentials set, the Google provider app is registered via allauth's settings-based `SOCIALACCOUNT_PROVIDERS['google']['APPS']` — no `SocialApp` database rows required; only allauth's own migrations (its tables) need `python manage.py migrate` once when enabling.
- Without credentials: no button rendered, `/accounts/google/login/` is a 404 (provider URLs are only registered when configured), username/password flows unchanged.
- Successful Google login redirects to `/dashboard/` via the existing `LOGIN_REDIRECT_URL`.
- Email-based automatic linking/takeover is disabled (see `docs/google-oauth-setup.md` §4); a Google login with an email matching an existing local account always goes through the explicit social-signup flow.

## Verification results (actual)

Environment: project `.venv` (Django 5.2.18), local PostgreSQL 16 at 127.0.0.1:55432, tests executed against the pre-created `cloudtask_test_utf8_06b` (`TEST['NAME']` pointed at itself, `--keepdb` equivalent, because `cloudtask_app` has no CREATEDB privilege). `DEBUG=True` / `DJANGO_ENV=local` as set by `start-web.ps1`.

1. `python manage.py check` — without Google credentials: **System check identified no issues (0 silenced).**
2. `python manage.py check` — with runtime-generated dummy `GOOGLE_OAUTH_*` values: **System check identified no issues (0 silenced).**
3. Focused tests, unconfigured mode (`tasks.test_google_oauth` + `tasks.test_authentication`): **33 tests — 32 passed, 5 skipped** (enabled-mode tests, correctly skipped), **1 pre-existing failure** (see below).
4. Focused tests, enabled mode (dummy credentials generated at runtime by the test shell — no literals committed): **33 tests — 32 passed, 1 skipped** (route-404 test, only valid unconfigured), **same 1 pre-existing failure**.

The enabled-mode tests verified: button present on login/signup, provider app config sourced from the environment (`client_id`/`secret` equal to the process env), `POST /accounts/google/login/` returns 302 to `https://accounts.google.com/o/oauth2/...` with `client_id=` (locally generated redirect, no network call), `/accounts/google/login/callback/` route registered, and `can_authenticate_by_email` returns `False` for a Google login matching an existing user's email.

**Real Google OAuth login: NOT RUN** — no real Google OAuth client credentials exist in this environment. Manual verification (button → Google consent → redirect back to `/dashboard/`) remains to be done once credentials are configured; see `docs/google-oauth-setup.md` §5.

## Pre-existing failure (not caused by this task)

`tasks.test_authentication.PublicEndpointTests.test_login_logout_entry_journey` fails on
`assertTemplateUsed(response, 'includes/workspace_preview.html')` after logout. The uncommitted
Flowspace redesign removed the `workspace_preview.html` include from `templates/registration/login.html`
(`git show HEAD:templates/registration/login.html` still contains it; the working-tree file does not —
the file was already listed as modified in the starting git status). Left as-is to preserve uncommitted work.

## Blockers

- Real OAuth credentials required for end-to-end verification (documented above).
- `cloudtask_app` cannot CREATE DATABASE: the Django test runner cannot create a fresh test DB; the established project pattern (pre-created `cloudtask_test_utf8_06b`, `TEST['NAME']` = `NAME`, keepdb) was used.
- When enabling credentials on any real deployment, run `python manage.py migrate` once for allauth's own tables.

## Git status (after this task)

Modified: `.env.example`, `config/settings.py`, `config/urls.py`, `requirements.txt`, `tasks/views.py`, plus pre-existing modifications (`locale/vi/*`, `static/css/*`, `static/js/app.js`, `tasks/test_authentication.py`, `templates/base.html`, `home.html`, `includes/workspace_preview.html`, `registration/login.html`, `registration/signup.html`).

Untracked: `tasks/context_processors.py`, `tasks/test_google_oauth.py`, `templates/includes/google_button.html`, `templates/socialaccount/`, `docs/google-oauth-setup.md`, this report, plus pre-existing untracked entries (`frontend/`, `static/flowspace/`, `static/fonts/`, other docs).

Nothing committed; no Git writes performed.
