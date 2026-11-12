# Report: start-web.ps1 auto-load of Google OAuth credentials (2026-11-11)

Task: load `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET`
automatically when launching Flowspace via `start-web.bat`, reading them from
the existing private file `%LOCALAPPDATA%\CloudTaskManager\oauth-keys-backup.env`.

## Change

`start-web.ps1` only (+33 lines, no other files touched):

1. New function `Import-PrivateOAuthKeys($PrivateRoot)` (placed with the other
   private-store helpers):
   - Skips silently when the credentials file is absent (username/password
     login keeps working — Django's `GOOGLE_OAUTH_ENABLED` stays `False`).
   - Refuses reparse points on the credentials file.
   - Parses only simple `KEY=value` lines and only the two known variable
     names; unknown keys, blank values and non-matching lines are ignored.
   - Never overwrites an already configured process environment variable.
   - Returns only variable **names**; values are never printed or logged.
2. Call site: after the DPAPI signing-key block and before `manage.py check`;
   prints `Optional Google OAuth credentials loaded for: <names>` (names only)
   when any were set.

DPAPI signing-key provisioning, PGPASSFILE handling and PostgreSQL startup
are untouched. `start-web.bat` needed no changes. The private file was not
modified; no repository `.env` was created; no Git writes performed.

## Verification (actual, secrets never printed)

Isolated checks — the shipped function was extracted verbatim from
`start-web.ps1` via PowerShell AST and executed against test contexts:

| Check | Result |
| --- | --- |
| PowerShell parser on `start-web.ps1` | PASS (0 syntax errors) |
| Absent credentials file (temp private root) | PASS — no variables set |
| No-overwrite (dummy runtime-generated values pre-set in env) | PASS — dummy values kept, 0 names loaded from file |
| Real private file | PASS — both names loaded, process env values byte-identical to file values (compared inside the harness; only booleans printed) |

End-to-end launch through the real entry point
(`start-web.bat -Port 8123 -NoBrowser -SkipCollectStatic` on a spare port):

- Launcher log: `Local database identity PASS: [...]`, `Protected local signing key loaded; value not displayed.`, `Optional Google OAuth credentials loaded for: GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET` (names only).
- `GET /health/` → 200 `{"status": "ok", ...}`.
- `GET /login/` → 200 and contains `accounts/google/login/` (Google button gate active, proving the credentials reached the Django process).
- `GET /register/` → 200.
- No repository `.env` exists; private `oauth-keys-backup.env` timestamp unchanged (Nov 10 23:50, size 159 bytes unchanged).
- Test server stopped afterwards; port 8123 released.

Git status: working tree otherwise unchanged from the previous reports
(allauth integration + pre-existing uncommitted work preserved);
this task adds only `M start-web.ps1` (+33/−0). Nothing committed.

## Notes

- With credentials absent or blank, the app runs username/password-only
  (verified by the isolated absent-file check plus the existing focused
  auth suites from 2026-11-10).
- Real Google OAuth round trip with the provider remains **NOT RUN**
  (requires the redirect URIs to be registered in the Google Cloud Console;
  see `docs/google-oauth-setup.md`).
