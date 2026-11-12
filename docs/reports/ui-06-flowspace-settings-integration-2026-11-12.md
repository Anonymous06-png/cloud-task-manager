# UI-06 — Flowspace Settings integration — 2026-11-12

## Delivered
- `templates/settings.html`: approved single-column layout with account summary, two theme-preview choices, vertical language cards, Save language footer and session logout. Account name/username/email come from `request.user` and remain read-only; optional email is omitted when absent. No Profile link or route introduced.
- `static/css/app.css`: isolated Settings block for Direction C Inter typography, restrained surfaces/borders, independent light/dark miniature previews, selected states, wrapping account details and mobile stacking. Existing native radios, fieldset legends and visible keyboard-focus treatment retained.
- This new report. Shared Fold/sidebar/header, theme mechanism (`ctm-theme`), global JS, views, URLs, tokens, locale files and all pre-existing work retained. No backend changes needed.

Read ZIP README, both Settings HTML files, DESIGN.md, the latest UI-05 report and previous Settings cleanup report. Verified all four requested reference documents match the ZIP. Followed curated README/HTML rather than stale PNG logout/version copy. No demo accounts, fake Profile links, Tailwind CDN, mock scripts or unsupported functionality imported. New VI/EN copy is localized in-template within the allowed scope.

## Actual commands / results
Commands ran from the repo. `python` means `.venv\Scripts\python.exe`; `$T` is `C:\Users\Ky\AppData\Local\Temp\opencode`.

| Command | Exit | Result |
|---|---:|---|
| `python manage.py check` | 0 | No issues (0 silenced). |
| `python $T\ui06-settings-check.py` | 0 | **6 tests passed**: VI/EN layout/read-only details/native controls, public Settings, real Save language POST/CSRF/cookie/redirect/checked-state behavior, rejected missing CSRF, real POST-only logout/session clearing, optional-field fallback and escaping. Scope and ZIP assertions also passed. |
| `python manage.py test tasks.test_authentication.LogoutTests --noinput --verbosity 1` | 0 | **2 existing logout tests passed**. |
| `node $T\ui06-theme-check.cjs` | 0 | **4 scenarios passed**, executing unchanged theme bootstrap/app JS in a minimal DOM harness: default, saved Light/Dark, storage unavailable, radio changes and header toggle synchronization. |
| `python $T\ui06-settings-pg-check.py` | 0 | **8 VI/EN renders passed** across four existing PostgreSQL accounts: actual escaped details, read-only card, controls, correct session logout copy and POST/CSRF markup, preserved shell and no Profile links. |
| `git diff --check` | 0 | No whitespace errors; LF→CRLF advisory warnings only. |

Django check/fixture tests used process-only settings, `DEBUG=True` and in-memory SQLite. Existing PostgreSQL account verification used the existing runtime URL/PGPASSFILE, `PGOPTIONS='-c default_transaction_read_only=on'` and a verified read-only transaction through `RequestFactory`; no application account or session writes. Both exact logout labels were checked: “Log out of this session” / “Đăng xuất khỏi phiên này”.

## Blockers / limits
- No implementation blocker or remaining failure in the focused checks. Profile remains deferred to UI-07; its absent route is deliberately not linked.
- No browser automation, visual/computed-style viewport verification or screen-reader testing performed. Light/Dark, mobile and keyboard support are implemented and source/behavior checked, not visually certified.
- No dependency changes, application migrations, server restart, staging, commits or other Git writes.

## Git status
`main...origin/main`: **21 modified tracked paths, 35 untracked entries including this report, zero staged entries**. UI-06 modified only `templates/settings.html` and the already-dirty `static/css/app.css`, and added this report. All other changes were pre-existing and preserved.
