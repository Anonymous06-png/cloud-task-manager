# UI-07A — authenticated Flowspace Profile View / Edit Profile — 2026-11-12

## Outcome and activation prerequisite

Implemented authenticated `/profile/` and `/profile/edit/`, real account details, owner-only Django form persistence, validation, CSRF, Cancel, error feedback and success POST-redirect-GET. The account dropdown now links to the real Profile route, including a no-JS fallback. **Stopped at UI-07A; no avatar upload/removal controls or UI-07B work.**

**Migration `tasks.0002_profile` is tested but NOT applied to the running development database.** Read-only `showmigrations` confirms it is pending. Apply it with the existing, verified runtime environment before activating/using this source, including authenticated pages whose account footer now reads profile data. The normal command is `python manage.py migrate tasks 0002_profile --noinput`; it was **not run against the development or production database** in this task. Do not use the disposable test signing key for the running app.

## References and design boundaries

- Read the Edit Profile README, Light/Dark HTML and PNG references and supplemental DESIGN.md. Byte comparisons confirm all six reviewed files exactly match `frontend/Flowspace-Edit-Profile-Reference.zip`.
- Read `docs/reports/ui-06-flowspace-settings-integration-2026-11-12.md` and `docs/reports/ui-11-flowspace-account-dropdown-2026-11-12.md`, plus relevant models/forms/views/routes/templates/tests/settings and local launchers.
- Found and read the previously approved Profile Light PNG/central HTML and README under `frontend/Flowspace-Settings-Profile-Clean-Reference/`. Used its identity header and read-only details ledger; Dark derives from the same structure and existing semantic tokens, not the rejected old Dark structure.
- Edit follows the narrow, left-aligned central heading, initials/identity area, personal-details fields, read-only identity rows and Save/Cancel footer. Uses existing Inter, Fold shell, sidebar, header, theme tokens, focus styles and responsive spacing. No reference shell, demo identity, CDN, font import, mock JS, fake links or unsupported account/age/workspace/support claims were added. The existing shell's pre-existing font links were left unchanged.
- No new dependencies, theme-token changes, application JavaScript changes, auth/provider/password changes, server restart, static collection, browser automation, production deployment or Git writes.

## Changed files — this task only

| Path | Change |
|---|---|
| `tasks/models.py` | Minimal `Profile`: OneToOne owner, 2–50-character display name, nullable birth date. No User/auth schema changes. |
| `tasks/migrations/0002_profile.py` | Additive profile-table migration with swappable User dependency and unique ownership. |
| `tasks/forms.py` | Explicit two-field ModelForm; trimmed required display name, ISO date parsing, optional/clearable birth date, future-date rejection, localized errors and associated help/error markup. No arbitrary minimum-age rule. |
| `tasks/views.py` | Login-required, method-limited owner-only view/edit handlers; no user identifier accepted; valid Save redirects to Profile with success message. GET and invalid POST do not create profiles. |
| `tasks/urls.py` | Real `tasks:profile` and `tasks:profile_edit` routes. |
| `templates/profile.html` | Read-only identity/details ledger and real Edit/Settings navigation. |
| `templates/profile_edit.html` | Server-rendered CSRF form, bound fields/errors, immutable username/email details, real Save/Cancel. |
| `templates/includes/profile_identity.html` | Shared escaped identity and username-initials placeholder; no photo controls. |
| `templates/base.html` | Activate existing My Profile action, current-page state and no-JS link; prefer saved display name in account identity. Shell outside sidebar footer unchanged. |
| `templates/settings.html` | Only the account display-name expression changes; Settings controls/layout remain unchanged. |
| `static/css/app.css` | Isolated Profile-only insertion: Inter heading, narrow card/ledger/form layout, semantic Light/Dark surfaces, responsive stacking/wrapping. No pre-existing CSS removed/changed. |
| `locale/vi/LC_MESSAGES/django.po` | Append 24 Profile messages. |
| `locale/vi/LC_MESSAGES/django.mo` | Add those 24 runtime translations, preserving all 194 pre-existing catalog entries exactly. Existing source-only translation work was not inadvertently compiled. |
| `tasks/test_profile.py` | 23 focused Profile regressions. |
| `tasks/test_sidebar.py` | Adapt the existing seven regressions to enabled real Profile navigation; preserve remaining assertions. This was already untracked user work. |
| `tasks/test_sidebar.cjs` | Add Profile to existing disclosure fixtures; verify first keyboard action and ordinary navigation. Same 14-check dependency-free harness, no browser. Already untracked user work. |
| `docs/reports/ui-07a-flowspace-profile-view-edit-2026-11-12.md` | This new report. |

Display name lives in Profile instead of repurposing User.first_name/last_name, preserving provider-supplied identity. Existing users fall back to full name, then username until their first valid save. Username/email are escaped account data, not writable form fields. Owner selection always comes from `request.user`, never GET/POST IDs. Forged IDs, email, username, names, password, provider and external-next fields are ignored.

## PostgreSQL isolation and actual verification

All final Django tests ran on **actual local PostgreSQL 16**, not SQLite. Verified the running per-user installation with `pg_ctl status`, repository launchers, and live database/user/address/port/owner queries. Final tests additionally assert UTF8 encoding. The final target is the existing dedicated **`cloudtask_test_utf8_06b`, `cloudtask_app`, `127.0.0.1:55432`**; not the development database or a production target.

The application role lacks CREATEDB. The external test runner creates a random `ui07a_<uuid>` schema in that verified test database, sets `search_path` to **only that schema (no public fallback)**, applies all migrations there and runs Django DiscoverRunner/TestCase. Its `finally` removes only its newly created schema. Every run verified cleanup and unchanged pre-existing public table lists/row counts. No database was created/dropped, no public-schema migration was applied, and no existing account/session/task row was intentionally written. No credential values were printed or added to the repository.

Commands ran from `C:\ProjectCloud\cloud-task-manager`. Below, `PY` = `.venv\Scripts\python.exe`, `$T` = `C:\Users\Ky\AppData\Local\Temp\opencode`. Check/migration-inspection commands used process-only `SECRET_KEY='ui07a-disposable-local-check-key'`, `DEBUG=True`, `DJANGO_ENV=local`, and the existing private `PGPASSFILE`. Final check/consistency commands selected `postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_test_utf8_06b`; `showmigrations` selected the verified `cloudtask_dev_utf8_06b`. The external runner sets its own disposable environment. Configured OAuth uses dummy test credentials only; redirect assertions do not contact Google.

| Actual command / diagnostic | Exit | Actual result |
|---|---:|---|
| `git status --short` (task start) | 0 | Dirty baseline recorded; 22 modified tracked paths, 44 untracked entries, no staged entries. |
| PowerShell tool/environment discovery (`Get-Command psql,docker ...`) | 1 | `psql` not on PATH; Docker executable found. Did not start Docker. |
| `pg_ctl.exe -D <existing per-user PostgreSQL data directory> status` | 0 | Existing local server running; no startup/restart. |
| Inline `psycopg2` local identity preflight including `SHOW data_directory` | 1 | `InsufficientPrivilege` on data-directory inspection; no privilege escalation. |
| Inline `psycopg2` read-only identity/role preflight without privileged inspection | 0 | Launcher-matching local dev identity/UTF8 confirmed; CREATEDB false. |
| Inline dedicated test-DB identity preflight | 0 | Existing `cloudtask_test_04k` identity/owner confirmed; subsequently identified as old WIN1252 target by Unicode tests. |
| `PY $T\ui07a-compile-catalog.py` | 0 | 24 additions; all 194 old runtime translations preserved. |
| `PY manage.py check` (initial old-test target and final UTF8 test target) | 0 each | No issues, 0 silenced. |
| `PY manage.py makemigrations --check --dry-run` (initial and final) | 0 each | No changes detected; models and migration consistent. |
| `PY -I -B $T\ui07a-pg-tests.py tasks.test_profile tasks.test_sidebar tasks.test_authentication tasks.test_google_oauth` — initial runner targeting old test DB | 1 | 61 discovered; 1 failure, 21 errors, 5 skips (subtests included). Caught missing `endfor`, Unicode storage rejection in WIN1252 and an overbroad test that rejected pre-existing shell font links. Fixed template; scoped asset assertion to new central content; switched runner to verified existing UTF8 test DB with explicit encoding guard. Cleanup passed. |
| Same four-suite runner command — UTF8 retry, before two extra tests | 0 | 61 discovered: 56 passed, 5 mode-dependent skips. Cleanup passed. |
| `PY -I -B $T\ui07a-pg-tests.py --google-enabled tasks.test_google_oauth tasks.test_profile tasks.test_sidebar` — before two extra tests | 0 | 39 discovered: 38 passed, 1 mode-dependent skip. Cleanup passed. |
| **Final** `PY -I -B $T\ui07a-pg-tests.py tasks.test_profile tasks.test_sidebar tasks.test_authentication tasks.test_google_oauth` | **0** | **63 discovered: 58 passed, 5 OAuth-enabled skips; 15.868s. All 23 Profile, 7 sidebar and 22 authentication tests passed.** Cleanup passed. |
| **Final** `PY -I -B $T\ui07a-pg-tests.py --google-enabled tasks.test_google_oauth tasks.test_profile tasks.test_sidebar` | **0** | **41 discovered: 40 passed, 1 OAuth-disabled-route skip; 3.956s.** Includes all five enabled OAuth tests skipped above. Cleanup passed. |
| `node --check static/js/app.js` | 0 | Unchanged application JS parses. |
| `node tasks/test_sidebar.cjs` (initial and final) | 0 each | **14 checks passed** each run, including Profile keyboard entry/navigation, Light/Dark, mobile/rail, themes, logout and disclosure cleanup. |
| Inline Python ZIP byte comparison, piped to `PY -` | 0 | README, both HTMLs/PNGs and DESIGN.md match reviewed extracted files. |
| Inline baseline diff review, piped to `PY -` (first attempt) | 1 | Windows cp1252 stdout could not print Vietnamese; no source validation result claimed from this failed print. |
| Inline baseline assertions/diff review with `PYTHONIOENCODING=utf-8`, piped to `PY -` | 0 | CSS is insertion-only; base shell unchanged outside account footer. Task-specific diffs reviewed. |
| `PY manage.py showmigrations tasks --plan` — local dev, read-only | 0 | `tasks.0001_initial` applied; **`tasks.0002_profile` pending**, intentionally not applied to runtime. |
| `git diff --check` | 0 | No whitespace errors; existing LF→CRLF advisory warnings only. |
| Final inline Python porcelain-count / text-whitespace check, piped to `PY -` | 0 | Confirmed 25 modified tracked paths, 50 untracked entries, zero staged entries; all 16 task text files (including untracked files/report) have no trailing whitespace. |
| `git diff --stat`, `git status --short --branch`, porcelain-count query | 0 each | Reviewed combined dirty-tree status; task changes distinguished from baseline below. |

Final test logs: `$T\ui07a-pg-final.log` and `$T\ui07a-pg-google-final.log`. External runner/catalog compiler remain in `$T`, not application source or dependencies. Task-start copies are in `$T\ui07a-baseline`.

Coverage includes anonymous GET/POST redirects, authenticated read/edit, no GET writes, method restrictions, real initial data/fallbacks, valid Unicode names and exact length boundaries, whitespace/blank/oversize rejection, valid/leap/invalid/ISO-only/future dates, omitted/cleared optional date, failed-edit preservation, success feedback and refresh-safe PRG, Cancel without writes, persistence after new login, owner-query/POST tampering, unchanged User/social/email identities and session, missing/wrong/valid CSRF, HTML escaping in view/edit/sidebar/Settings/invalid form, localized VI/EN copy/errors/success, real CSRF language-switch cookie/return path, unique ownership/cascade and absence of fake avatar controls/claims.

## NOT RUN / blockers / remaining risks

- **Activation prerequisite:** apply `tasks.0002_profile` to the intended verified runtime before using these sources. Otherwise the new profile-table reads, including the authenticated account footer, will fail. Runtime migration/deployment was not silently performed.
- **NOT RUN:** browser automation (prohibited), manual visual/browser comparison, computed-style/mobile/zoom certification or screen-reader testing. Responsive wrapping, semantic labels/help/errors, focus styling and theme-token usage are source/response checked, not visually certified.
- **NOT RUN:** real Google consent/callback exchange, external provider requests or production session tests. Existing OAuth configuration/safe-linking/session regressions pass locally in both modes; no claim of live provider verification.
- **NOT RUN:** full application suite, deployment/static collection or server restart. The focused tests above are the actual test scope.
- Old `cloudtask_test_04k` remains WIN1252; do not use it as Unicode/Vietnamese persistence proof. No encoding/database repair was attempted. Final tests used the UTF8 test database instead.
- No remaining focused-test failure or implementation blocker. UI-07B photo upload/change/remove remains unimplemented and unexposed by design.

## Git status and preservation

Branch: `main...origin/main`. Start: **22 modified tracked paths / 44 untracked entries / zero staged entries**. End, including this new report: **25 modified tracked paths / 50 untracked entries / zero staged entries** (directory-collapsed `git status --short` counts).

Task-specific status:

```text
 M locale/vi/LC_MESSAGES/django.mo
 M locale/vi/LC_MESSAGES/django.po
 M static/css/app.css
 M tasks/forms.py
 M tasks/models.py
 M tasks/urls.py
 M tasks/views.py
 M templates/base.html
 M templates/settings.html
?? docs/reports/ui-07a-flowspace-profile-view-edit-2026-11-12.md
?? tasks/migrations/0002_profile.py
?? tasks/test_profile.py
?? tasks/test_sidebar.cjs
?? tasks/test_sidebar.py
?? templates/includes/profile_identity.html
?? templates/profile.html
?? templates/profile_edit.html
```

The two sidebar test files and several modified implementation/catalog files were already dirty/untracked at task start; only scoped changes were made. All unrelated baseline changes remain present. No staging, commits, checkout/reset/clean, merges, pushes or other Git writes. Stopped after UI-07A verification and this report.
