# UI-04 — Task List search / translation repairs — 2026-11-11

## Fixes and causes
- `locale/vi/LC_MESSAGES/django.po` and `django.mo`: added only `Overdue → Quá hạn` and `Clear search → Xóa tìm kiếm`. These missing entries caused the mixed-language heading, overdue label and clear-search link. Existing `Incomplete → Đang làm` retained; all previous runtime translations preserved.
- `tasks/views.py`: PostgreSQL's existing `C` collation makes `UPPER()` ASCII-only, so Django's `icontains` failed for `Điện…` versus `điện…`. Confirmed the stored screenshot title is intact/NFC: old lookup returned zero; Unicode-collated lookup returned one. Apply the already-installed `und-x-icu` collation to **both** title and parameter before Django's uppercase comparison. No database collation/schema changes. Non-PostgreSQL lookup unchanged.
- Added `tasks/test_task_list.py` with focused search/translation regressions. Templates, CSS, approved design, grouping, seven-row pagination, query limit, existing ordering, ownership, filters, actions and CSRF unchanged. Snapshot comparisons confirmed only search/imports and the two PO entries changed in the existing source files.

## Commands and actual results
Commands ran from the repo using `.venv\Scripts\python.exe`; `$T` below is `C:\Users\Ky\AppData\Local\Temp\opencode`. Secrets were process-only and never printed.

| Command | Exit | Result |
|---|---:|---|
| `python manage.py check` | 0 | No issues (0 silenced). |
| `python manage.py test tasks.test_task_list tasks.test_task_crud.TaskFormRenderingTests.test_task_list_search_status_and_pagination_are_owner_scoped --noinput --verbosity 1` | 0 | **10 passed, 1 skipped** of 11. Exact/partial Vietnamese, matches/nonmatches, ownership, status combinations, ordering/pagination, literal wildcards/quotes, VI/EN labels and CSRF covered. |
| `python $T\ui04-regression-diagnose.py` | 0 | Reproduced original PostgreSQL failure, confirmed `C` locale and installed ICU collation; original translations absent. |
| `python $T\ui04-compile-catalog.py` | 0 | Scoped runtime catalog build: exactly two new entries; all previous compiled translations unchanged. No dependency/tool installation. |
| `python $T\ui04-regression-pg-verify.py` | 0 | **528 VI/EN server renders passed** across 8 existing accounts: 54 matching, 474 empty/nonmatching/filter-excluded, including 4 overdue renders. |
| Scope snapshot assertions (`python -`) | 0 | Existing view/PO changes confined to this repair; List and shared-row templates byte-identical. |
| `git diff --check` | 0 | No whitespace errors; LF→CRLF advisory warnings only. |

Check/focused tests used `DATABASE_URL=sqlite:///:memory:` and `DEBUG=True`; fixtures/schema existed only in the disposable test database. The PostgreSQL-only Unicode fixture test was skipped on SQLite, whose built-in case conversion is also limited. The PostgreSQL branch was instead exercised directly against existing data with `PGOPTIONS='-c default_transaction_read_only=on'`, `SET TRANSACTION READ ONLY`, the launcher's existing database URL/PGPASSFILE, and `RequestFactory` (no session writes).

Live queries included `điện toán đám mây`, `ĐIỆN TOÁN ĐÁM MÂY`, `điện`, `toán đám`, `ĐÁM MÂY`, nonmatching text, blank queries, `%`, `_`, backslash and SQL-like quoted text, each combined with All/Incomplete/Completed and VI/EN. Results were checked against owner-scoped stored titles, with counts, ordering, action/CSRF/return fields and translated search/overdue labels verified. No user records changed.

## Remaining failures / limits
- **No remaining failures in the final focused checks.** Initial focused run exited 1 on an insertion-order assumption for equal timestamps; the test now uses the existing ORM ordering, and the rerun passed. No ordering change made.
- Initial catalog-helper guards exited 1 on pre-existing duplicate/source-only entries; no catalog was written during those attempts. Final scoped build retained existing runtime translations and left unrelated pending source translations untouched.
- PostgreSQL application role lacks `CREATEDB`; no PostgreSQL fixture database was created. Real-data PostgreSQL verification was read-only; fixture pagination coverage used SQLite. Existing ICU collation is required for PostgreSQL search and was verified available here.
- Full CRUD suite and its documented unrelated Dashboard failure were **not rerun**. No browser automation, visual redesign, server restart, dependency changes, application migrations or Git writes performed.

## Git status
`main...origin/main`: **19 modified tracked paths, 31 untracked entries including this report, zero staged entries**. This task changed the already-dirty view/PO/MO files and added only `tasks/test_task_list.py` and this report. All pre-existing work retained; nothing staged, committed or discarded.
