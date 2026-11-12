# Dashboard Upcoming timeline — 2026-11-11

## Changes
- `templates/dashboard.html`: only Upcoming panel markup changed. Added compact calendar-icon heading, one vertical deadline list and one accessible weekday/day chip per task. Removed duplicate date-group headings. Relative time uses Django's localized `timeuntil` and translated “Today”; existing detail URLs retained.
- `static/css/app.css`: only Dashboard Upcoming rules changed. Token-based timeline/dots, soft date chips, restrained separators, compact spacing and clearer task-title hierarchy. Full titles wrap, including unbroken text; singleton rows hide the connector. Existing translated empty message retained.
- This new report.

Main task table, navigation sidebar, other pages, backend and database unchanged. Existing seven-day selection and four-item deadline limit preserved. Shared Direction C Light/Dark colors and existing responsive layout reused; no calendar, mock tasks, dependencies or JavaScript added. Pre-existing uncommitted work preserved.

## Actual verification
- **PASS:** Django system check — `System check identified no issues (0 silenced).` Process-only check settings with in-memory SQLite.
- **PASS:** eight VI/EN authenticated Dashboard server renders using existing stored records in a PostgreSQL read-only transaction: four populated and four empty panels. Checked item counts against the existing seven-day query, single date chips, translated empty/today text, escaped task titles and detail links. Six renders used the current date; two used a test-only clock anchored to an existing deadline date. No records changed or created.
- **PASS:** pre-task snapshot comparisons confirm all template content and CSS outside the Upcoming panel remained identical. Wrapping and single-item connector guards checked in source.
- **PASS:** `git diff --check`, exit 0; only LF→CRLF advisory warnings.
- No browser automation or Git writes. Visual/computed Light/Dark and viewport verification not performed; theme/responsive support is maintained through existing tokens/layout and panel-only CSS.

Verification script (outside repo): `C:\Users\Ky\AppData\Local\Temp\opencode\deadline-panel-check.py`.
