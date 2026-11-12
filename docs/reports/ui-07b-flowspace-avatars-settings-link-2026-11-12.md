# UI-07B — Profile avatars and Settings navigation — 2026-11-12

## Delivered

- Signed-in users can upload, replace and remove **only their own** avatar via a separate CSRF-protected POST form on Edit Profile. Successful actions redirect back to Edit Profile with VI/EN feedback. Personal-details Save/Cancel remains separate.
- Accept JPG/JPEG, PNG and WebP, **2 MiB maximum** (2 × 1024² bytes). Check actual size and bounded reads, filename extension, Pillow-identified format, image verification and full decoding. Reject corrupt/truncated/unsupported images and dimensions over 4096 pixels per side. MIME declarations are not trusted. Reject SVG and executable extensions.
- Persist only a fresh, metadata-free, single-frame PNG, reduced to at most 512 × 512 pixels, with a UUID filename through Django default storage. Original filenames, metadata and appended payload bytes are not stored. Validation failures retain the previous avatar.
- Old avatar deletion occurs after database commit; new-file cleanup is attempted on failed database save. Owner-row locking serializes avatar creation/change/remove. Post-commit deletion failures are logged rather than breaking an already-committed change. Crash/storage-outage orphan risks are documented below.
- Uploaded images render on Profile View, Edit Profile, Settings account card and both normal sidebar account identity locations. Existing initials remain the fallback. Images are decorative beside account text (`alt=""`).
- Avatars are **private**: authenticated GET `/profile/avatar/image/` selects only `request.user`, accepts no file/user selector, and streams PNG with `private, no-store` and `nosniff`. No public `/media/` route, catch-all directory serving, third-party avatar service, SVG or executable serving was added.
- Settings now has a right-aligned **View Profile / Xem hồ sơ** link to `tasks:profile`. Existing account copy, theme choices, language form and logout remain intact. No changes to sidebar behavior/JS, Dashboard/Task List source, design tokens or auth/OAuth configuration.

Read both UI-07A implementation/activation reports, current Profile/forms/views/templates/tests, Settings, requirements, ignore rules and existing secure runtime/test launchers. All pre-existing dirty/untracked user work was preserved.

## Changed files

| Paths | Scope |
|---|---|
| `requirements.txt` | Add **Pillow==13.0.0**, previously absent; no existing dependencies upgraded. Installed into the existing local venv. |
| `config/settings.py` | Local `MEDIA_ROOT=BASE_DIR / 'media'`, `MEDIA_URL='/media/'`; no unrestricted serving route. |
| `tasks/models.py`, `tasks/migrations/0003_profile_avatar.py` | Optional avatar FileField and UUID upload path. Permit an empty stored display-name override for avatar-only profiles; existing full-name/username fallbacks remain unchanged. Explicit ProfileForm display-name validation stays required, 2–50 characters. Existing profile values are not rewritten. |
| `tasks/avatars.py` | Bounded server-side validation and pixel-only normalization. |
| `tasks/forms.py` | Dedicated AvatarForm and associated help/error IDs; original details fields unchanged. |
| `tasks/views.py`, `tasks/urls.py` | Owner-only POST avatar action and private image GET; transaction/storage cleanup; details saves update only name/date, not a potentially stale avatar field. Avatar-only profiles prefill the original account name in the details form. |
| `templates/includes/avatar.html`, `templates/includes/profile_identity.html`, `templates/base.html`, `templates/settings.html`, `templates/profile_edit.html` | Shared image/initials rendering, genuine upload/change/remove controls, accessible error feedback, Settings Profile link. |
| `static/css/app.css` | Small scoped avatar sizing/object-fit, upload controls and Settings-link responsive styles using existing theme tokens/Inter. |
| `locale/vi/LC_MESSAGES/django.po`, `locale/vi/LC_MESSAGES/django.mo` | Ten avatar translations added; all 218 existing runtime messages preserved exactly. |
| `tasks/test_avatars.py` | 18 new focused avatar/navigation tests. |
| `tasks/test_profile.py` | Remove obsolete UI-07A prohibition against real file controls; retain other existing checks. |
| `docs/avatar-media-storage.md` | Validation, storage/deletion policy, private serving, persistence/backup prerequisites and Docker limitations. |
| `docs/reports/ui-07b-flowspace-avatars-settings-link-2026-11-12.md` | This new report. |

No `.gitignore` change was needed: `media/` was already excluded. `config/urls.py`, Docker/DevOps files and environment files were not changed.

## Actual commands, exits and checks

Commands ran from `C:\ProjectCloud\cloud-task-manager`; `PY` = `.venv\Scripts\python.exe`; `$T` = `C:\Users\Ky\AppData\Local\Temp\opencode`.

| Actual command / operation | Exit | Result |
|---|---:|---|
| `git status --short --branch`; `PY -c "import PIL; print('Pillow', PIL.__version__)"` | 1 (combined) | Baseline status captured; Pillow probe failed `ModuleNotFoundError`, confirming dependency absent. |
| `PY -m pip index versions Pillow` | 0 | Available latest version 13.0.0. |
| `PY -m pip install Pillow==13.0.0` | 0 | Installed Pillow 13.0.0; existing dependencies not upgraded. |
| `PY $T\ui07b-compile-catalog.py` | 0 | Ten new messages, all 218 existing runtime entries retained. Compiler's reused console label says “UI-07A”; the input marker is UI-07B. |
| `PY manage.py makemigrations --check --dry-run` with isolated process-only check settings and verified UTF8 test connection | 0 | No changes detected. No migration applied by this command. |
| `PY -I -B $T\ui07a-pg-tests.py tasks.test_avatars tasks.test_profile tasks.test_sidebar tasks.test_authentication tasks.test_google_oauth` — initial | 0 | 78 discovered: **73 passed, 5 OAuth-enabled skips**, 15.604s. |
| Same five-suite command — **final**, output retained in `$T\ui07b-pg-final.log` | **0** | **81 discovered: 76 passed, 5 mode-dependent skips**, 16.286s. All **18 avatar, 23 Profile, 7 sidebar and 22 authentication tests passed**. Django check: no issues. |
| `PY -I -B $T\ui07a-pg-tests.py --google-enabled tasks.test_google_oauth` | 0 | **11 discovered: 10 passed, 1 OAuth-disabled-route skip**, 1.517s. Exercises the five cases skipped above using dummy credentials; no provider network call. |
| `node tasks/test_sidebar.cjs` | 0 | **14 checks passed**, including Light/Dark state, mobile/rail, Profile keyboard/navigation, logout and disclosure cleanup. Not a browser test. |
| Focused `Get-NetTCPConnection` / `Get-CimInstance Win32_Process` inspection | 0 | Repository runserver listener and owning venv parent verified. Development autoreloader changed the child during source edits; no explicit service restart. |
| `& $T\ui07b-activate.ps1 2>&1 \| Tee-Object -FilePath $T\ui07b-activate.log`, propagating `$LASTEXITCODE` | **0** | Guarded dev identity/migration activation, four authenticated local HTTP checks and preservation checks passed (details below). |
| Embedded `call_command('check')`, `call_command('makemigrations', check=True, dry_run=True)` | 0 (runner) | No issues; no model/migration drift. |
| Embedded `migrate tasks 0003_profile_avatar --plan`, then `migrate tasks 0003_profile_avatar --noinput` | 0 (runner) | Exact single target migration, forward only; **applied successfully** to authorized local dev DB. |
| Embedded `migrate --check`, `showmigrations tasks --plan` | 0 (runner) | No pending migrations; tasks 0001, 0002 and 0003 applied. |
| Authenticated `urllib.request` local GETs using an existing session in memory | 0 (runner) | **4/4 HTTP 200**, no redirects, expected authenticated markup on `/dashboard/`, `/profile/`, `/profile/edit/` and `/settings/`. |
| `git check-ignore media/avatars/example.png` | 0 | Path ignored by existing `media/` rule. |
| `git diff --check` | 0 | No whitespace errors; existing LF→CRLF advisory warnings only. |
| Porcelain Git status-count query | 0 | Baseline and final status below; no staged entries. |

Embedded management calls ran in one guarded process and completed without exceptions; their exit column refers to the successful runner, not independent shell invocations. External scripts/backups/logs are in `$T`, not application source or media.

### PostgreSQL tests versus runtime activation

**Tests:** actual local PostgreSQL 16 / UTF8, explicitly verified `cloudtask_test_utf8_06b`, user/owner `cloudtask_app`, `127.0.0.1:55432`. Reused the existing guarded test runner, which creates a random isolated schema, sets `search_path` to that schema only (no public fallback), applies migrations there and removes only its created schema afterward. Every run confirmed schema cleanup and unchanged public table lists/row counts. Temporary avatar storage is a dedicated TemporaryDirectory cleaned after the suite. No SQLite substitute and no accidental migration of existing test/public data.

**Development activation:** the secure launcher-derived runner loaded the **existing DPAPI-protected runtime signing key** and existing private PGPASSFILE. No disposable test key was used against live sessions. It asserted database/user/server/owner/UTF8/environment, authenticated the existing session, and correlated port-8000 server **PID 18580**, client socket **49674 → 55432**, with live `pg_stat_activity` identity **`cloudtask_dev_utf8_06b` / `cloudtask_app`**. The expected pre-migration live request returned the missing-avatar-column error; debug body was checked in memory, not logged. This independently confirmed the source/schema activation gap before applying the exact migration plan.

Only `tasks.0003_profile_avatar` was applied to the authorized local development DB. Before/after row-JSON SHA-256 multiset comparisons retained every existing row value in all public tables (excluding the newly added blank `avatar` key), with only the expected migration row added. **16 users, 20 tasks, 10 sessions, zero profiles retained; migrations 35 → 36.** No existing account/task/session/profile save or real-user upload was performed during local HTTP checks. Uploaded-image HTTP streaming and UI presence were exercised through the PostgreSQL-backed Django Client tests; live HTTP checks covered the existing initials state only.

### Focused coverage

JPEG/PNG/WebP decoding and re-encoding; exact 2 MiB boundary and over-limit rejection; corrupt/truncated/spoofed/unsupported/SVG/executable inputs; oversized dimensions; thumbnail bounds; filename uniqueness/traversal resistance and payload stripping; previous-avatar preservation on errors; replacement/removal cleanup only after commit; new-file cleanup after failed DB save; no-op removal; CSRF rejection/valid actions; anonymous/method restrictions; forged owner/account fields; private/no-store/nosniff image responses and unavailable public media URL; avatar rendering across requested surfaces; fallback after removal; persistence after new login; independent personal-details/avatar preservation; avatar-only name fallback; VI/EN navigation, errors and success. Existing auth/Profile/sidebar regressions passed as above.

## NOT RUN, risks and next step

- **NOT VERIFIED in Docker:** uploaded-media persistence across container recreation, persistent volume permissions, external/private storage, backups/restores or deployment. Current compose setup has no media volume. Container-local files are not durable. **Next deployment prerequisite:** provision and verify persistent private Django media storage and coordinated file/DB backups as described in `docs/avatar-media-storage.md`. No DevOps configuration changed.
- Filesystem/object storage and PostgreSQL are not one atomic transaction. Crashes or deletion failures can leave orphan files; post-commit failures are logged. Direct model/account deletion does not trigger avatar-file deletion and requires reviewed storage reconciliation. No broad cleanup was performed.
- **NOT RUN:** browser automation, manual browser/visual comparison, computed viewport/zoom verification, screen-reader testing, production deployment, full application suite, real OAuth consent/callback, remote-storage failures or load testing. No visual/browser PASS claimed.
- Local HTTP checks intentionally did not upload into an existing account, preserving current user data. Tests used temporary files and isolated test records.
- No remaining focused-test failure or local migration blocker. Stop after UI-07B; no further UI/DevOps work authorized by this task.

## Git status / preservation

Branch `main...origin/main`. Task start: **25 modified tracked paths / 51 untracked entries / zero staged entries**. Final including this report: **25 modified tracked paths / 57 untracked entries / zero staged entries** (directory-collapsed status counts). All pre-existing changes remain. The six new files are `tasks/avatars.py`, `tasks/migrations/0003_profile_avatar.py`, `tasks/test_avatars.py`, `templates/includes/avatar.html`, `docs/avatar-media-storage.md` and this report. Other task files were already dirty/untracked. No Git staging, commits, reset/checkout/clean, merge or push.
