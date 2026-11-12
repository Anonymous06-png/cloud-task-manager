# UI-04 — Stitch Task List integration — 2026-11-11

## Delivered
- `templates/task_list.html`: approved Direction C heading/count summary, data-derived progress, filter/search/create toolbar and separate pending/overdue and completed groups. Native keyboard-accessible disclosures; existing shared rows, URLs, CSRF, return fields, translations and empty states retained.
- `static/css/app.css`: List-only block for approved typography, spacing, aligned columns, status pills, completed-title strikethrough (also on hover), quiet rust overdue labels and responsive Light/Dark styling. All pre-task CSS outside this block preserved.
- This new report. No view/context, model, migration, shared shell, shared row, token, JavaScript or locale changes.

Grouping uses only the existing filtered seven-task page, pending first, preserving existing order within each group. Group counts describe that page; heading/filter/progress totals remain account-wide. Pagination, search and All/Incomplete/Completed filters are unchanged.

Read the latest relevant Dashboard/List/branding reports and reference `screen.png`, `code.html`, `DESIGN.md`; all three extracted files were verified byte-identical to the supplied ZIP. No reference demo records, Tailwind CDN, mock scripts, bulk selection, quick-add, shortcut hints or archiving imported.

## Actual verification
| Check | Result |
|---|---|
| `.venv\Scripts\python.exe manage.py check` | **PASS**, no issues (0 silenced). |
| `manage.py test tasks.test_task_crud --noinput --verbosity 1` | **28 passed, 1 failed** out of 29; existing Dashboard mismatch below. |
| Additional focused List regression suite | **7/7 passed**: VI/EN empty states; mixed grouping/counts/order/escaping; today/no-date handling; completed-only progress; search/filter/pagination; CSRF-enforced toggle/reopen/return URL; anonymous redirect. |
| Existing PostgreSQL data | **188 VI/EN server renders passed**, across 10 existing accounts, using a database-enforced read-only transaction. Verified owner-scoped page membership, groups/order/counts, search/status filters, actual action links, CSRF/return fields, escaping, unique IDs and shared controls. Included 8 mixed-group renders and 10 overdue-row appearances. No application records created or changed. |
| Scope isolation | **PASS**: views, base template, shared row, JS and tokens byte-identical to pre-task snapshots; removing the new CSS block exactly reproduces the pre-task stylesheet. |
| `git diff --check` | **PASS**, exit 0; LF→CRLF advisory warnings only. |

System check and automated regression tests used process-only settings and isolated in-memory SQLite; regression fixtures never touched application PostgreSQL. Existing-data renders used PostgreSQL through `RequestFactory`, avoiding session writes. Pagination is covered by regression fixtures; selected live accounts did not exercise populated pagination. Verification scripts are outside the repo: `C:\Users\Ky\AppData\Local\Temp\opencode\ui04-list-check.py` and `ui04-focused-tests.py`. Initial standalone anonymous validation needed an explicit localhost request host; the complete rerun passed.

## Blockers / limits
- Existing `TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks` expects “Your list is clear.”, while the unchanged Dashboard renders “Start with one clear next step.” Reproduced the same failure with the pre-UI-04 List template loaded in memory. Left this unrelated test/Dashboard mismatch untouched; the broader CRUD suite is not fully green.
- No browser automation or visual/computed-style viewport/theme verification performed. Theme tokens and responsive source rules retained and checked; pixel-level approval remains unverified.
- No backend integration blocker. No server restart, database configuration change or Git writes.

## Git status
`main...origin/main`; **19 modified tracked paths, 29 untracked entries including this report, zero staged entries**. UI-04 modified only `templates/task_list.html` and the already-dirty `static/css/app.css`, and added this report. The other 18 modified paths and 28 untracked entries were pre-existing and retained; nothing staged, committed, reset or discarded.
