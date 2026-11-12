# Google Sign-In Setup (django-allauth)

This guide documents how to configure Google OAuth so that the
"Continue with Google" button appears on the login and register pages.

The feature is **fully optional**: if the credentials below are not set, the
button is not rendered, the provider routes are not registered, and
username/password authentication works exactly as before.

## 1. Google Cloud Console configuration

1. Open <https://console.cloud.google.com/> and create (or select) a project.
2. Go to **APIs & Services → OAuth consent screen**:
   - User type: External.
   - App name, support email and developer contact are required.
   - Scopes: keep the defaults (`openid`, `.../auth/userinfo.email`,
     `.../auth/userinfo.profile`). The app only needs the email and profile
     scopes; no sensitive scopes.
   - While the app is in *Testing* mode, add the Google accounts that should
     be able to sign in as **Test users**.
3. Go to **APIs & Services → Credentials → Create credentials → OAuth client
   ID**:
   - Application type: **Web application**.
   - **Authorized JavaScript origins:**
     - `http://127.0.0.1:8000` (local development)
     - your production origin, e.g. `https://your-domain.example`
   - **Authorized redirect URIs (exact callback URL):**
     - `http://127.0.0.1:8000/accounts/google/login/callback/` (local
       development)
     - `https://your-domain.example/accounts/google/login/callback/`
       (production — replace the host with your real HTTPS origin)
4. Copy the generated **Client ID** and **Client secret** into your secret
   store / environment; never commit them.

## 2. Environment variables

Set both variables (they are read through `python-decouple`, i.e. from the
environment or `.env`):

```
GOOGLE_OAUTH_CLIENT_ID=<your-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<your-client-secret>
```

Both must be non-blank. When either is missing, `GOOGLE_OAUTH_ENABLED` is
`False` and the app runs in username/password-only mode.

After enabling the credentials for the first time, apply django-allauth's
database migrations once (its own tables for social accounts/tokens):

```
python manage.py migrate
```

No project data models change; the migrations only create allauth's own
tables (`socialaccount_*`, `account_*`, `socialtoken`).

## 3. Behaviour

- Successful Google login redirects to `/dashboard/` (via the existing
  `LOGIN_REDIRECT_URL` setting).
- The Google button is rendered as a POST form to
  `/accounts/google/login/`, so no extra confirmation page is shown before
  the redirect to Google.
- If the Google account's email does not yet belong to a user, the standard
  allauth social-signup confirmation page (`/accounts/google/login/callback/`
  → `/accounts/social/signup/`) asks the user to confirm the details first.

## 4. Account linking safety

django-allauth is configured so that a Google login can **never** silently
take over an existing account just by presenting a matching email address:

| Setting | Value | Effect |
| --- | --- | --- |
| `SOCIALACCOUNT_EMAIL_AUTHENTICATION` | `False` | A social login is never authenticated against an existing user by email match. |
| `SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT` | `False` | An existing account is never auto-connected to the social account by email match. |
| `SOCIALACCOUNT_EMAIL_REQUIRED` | `True` | Google must hand over a (verified) email address. |

Consequence: if someone signs in with Google using an email address that
already belongs to a local (username/password) account, allauth shows the
explicit social-signup/confirmation flow instead of logging into the
existing account. Deliberate linking can later be offered through the
allauth connections UI; automatic matching is disabled by design.

## 5. Verification status

- `python manage.py check` passes with and without credentials.
- Focused tests: `tasks/test_google_oauth.py` (two modes) plus the existing
  `tasks/test_authentication.py` suite; see
  `docs/reports/google-signin-allauth-2026-11-10.md` for actual results.
- A **real** Google OAuth round trip was **NOT RUN** because no OAuth client
  credentials were available in this environment. Once credentials exist,
  verify manually: click "Continue with Google" → consent screen → redirect
  back to `/dashboard/`.
