# UI-05 — Task due-date presets — 2026-11-11

## Changes
- `templates/task_form.html`: shared Create/Edit Today, Tomorrow, +7 days and accessible clear-date (X) buttons below the existing Django due-date field. All are `type="button"`. VI/EN labels provided in-template to keep locale files outside scope. Removed only the decorative settings icon beside “Task detail”; heading/layout retained.
- `static/js/task-form.js`: editor-only deferred script; presets use the local calendar at click time, format `YYYY-MM-DD` without UTC conversion, and update the real date field with bubbling input/change events. Clear assigns an empty value. Initial values are never changed on load; controls appear only after initialization.
- `static/css/app.css`: scoped neutral preset chips, wrapping layout, theme-token colors, inherited keyboard focus and 44px touch/mobile targets. Removed the unused heading-icon rule. All other CSS preserved.
- This new report. Views, models, database, shared fields, shell, global app JS, translations and dependencies unchanged; pre-existing work retained.

## Actual checks
Commands ran from the repo. `$T` denotes `C:\Users\Ky\AppData\Local\Temp\opencode`; `python` below was `.venv\Scripts\python.exe`.

| Command | Exit | Result |
|---|---:|---|
| `node --check static/js/task-form.js` | 0 | JavaScript syntax valid. |
| `node $T\task-date-presets-check.cjs` | 0 | **22 Create/Edit clock scenarios** across six time zones passed, plus four defensive cases and click-time date refresh. Covers initial values, all presets, clearing, events, positive/negative UTC offsets, DST, leap day and month/year rollover. Executes actual script with a minimal DOM harness, not a browser. |
| `python $T\task-date-presets-django-check.py` | 0 | **3 tests passed**: VI/EN Create/Edit controls/placement/non-submit types/initial values/icon removal; CSRF-enforced create/edit date saves and clearing to NULL; retained bound errors/values. Scope snapshot assertions also passed. |
| `python $T\ui05-editor-tests.py` | 0 | **4 existing editor checks passed**: bilingual layout, values/errors, save/delete confirmation, CSRF and access controls. |
| `python manage.py check` | 0 | No issues (0 silenced). |
| `git diff --check` | 0 | No whitespace errors; LF→CRLF advisory warnings only. |

Django checks used process-only settings, `DATABASE_URL=sqlite:///:memory:` and `DEBUG=True`. Test fixtures/schema existed only in disposable in-memory databases; no application database connection or user-record writes were performed.

## Limits / remaining failures
No remaining failures in the focused checks. No browser automation or visual/computed-style verification performed. Light/Dark and responsive styling use existing tokens and scoped wrapping/touch rules; real-browser appearance remains unverified. No Git writes, server restart or dependency changes.

## Git status
`main...origin/main`: **20 modified tracked paths, 34 untracked entries including this report, zero staged entries**. This task modified only the already-dirty form template/CSS and added `static/js/task-form.js` and this report. All other uncommitted work retained; nothing staged, committed or discarded.
