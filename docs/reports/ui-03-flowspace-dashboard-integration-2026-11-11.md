# UI-03 — Flowspace Dashboard integration — 2026-11-11

## Changed files

- `templates/dashboard.html`: approved three-card summary, task/filter region, date-grouped deadlines panel and separate first-task empty state. Uses existing owner-scoped Django counts, up to six tasks in existing queryset order, and the backend's four-deadline limit. Completed-only accounts remain populated. Reuses `includes/task_row.html`, existing URLs/CSRF/actions, translations and shared Fold branding.
- `static/css/app.css`: Dashboard-only integration block for Inter typography, reference spacing/columns/cards, tablet stacking and mobile rows. Shared color/status tokens inherited; all pre-existing CSS preserved exactly against the pre-task snapshot.
- This new report.

Read the latest branding report and the ZIP's `index.html`, `flowspace.css` and `dashboard-polish.css`. Shared navigation/sidebar and its existing mobile behavior retained, rather than importing the demo shell. Categories, sample tasks, preview switches/footer, demo dialog and demo JavaScript omitted. Existing translated copy reused instead of adding untranslated reference copy.

## Actual checks

- **PASS — Django:** `.venv\Scripts\python.exe manage.py check` → `System check identified no issues (0 silenced).`
- **PASS — focused rendering:** 14 actual Django client renders (seven scenarios × EN/VI): empty, pending/no date, completed-only, overdue, day-seven exclusion, eight mixed tasks and seven upcoming deadlines. Verified counts, six-row limit, four-deadline limit, date grouping, today/day-six inclusion, ownership isolation, escaping, unique IDs, existing task action URLs, CSRF/return fields, translated Dashboard copy and shared language/theme/Fold controls. Both task-list filters and legacy Dashboard filter URLs also returned correct owner-scoped counts; anonymous Dashboard access redirected to login.
- **PASS — CSS isolation:** removing the new scoped block reproduces the pre-task stylesheet exactly; responsive bands present and no hardcoded colors added. Light/Dark uses existing shared tokens; semantic completion/overdue colors retained.
- **PASS — `git diff --check`:** exit 0; no whitespace errors. LF→CRLF advisory warnings on `.env.example`, `config/urls.py`, `requirements.txt`, `static/css/app.css`, `static/css/design-tokens.css`, `templates/base.html`, `templates/dashboard.html`, and `templates/registration/signup.html`.

Checks used process-only `SECRET_KEY`, `DATABASE_URL=sqlite:///:memory:` and `DEBUG=True`. Render checks used temporary records/migrations only in that in-memory database, not application data. Script: `C:\Users\Ky\AppData\Local\Temp\opencode\flowspace-ui03-render-check.py`. An initial test assumed reverse fixture insertion order; corrected it to verify the existing ORM ordering, then the complete rerun passed.

## Blockers / limits

- No backend blocker; no backend, dependencies, JavaScript, shared templates, tokens or locale files changed by this task.
- Supplied `C:\ProjectCloud\Flowspace-Direction-C-Brand-Reference.zip` was absent. Used the same-named archive at `frontend/Flowspace-Direction-C-Brand-Reference.zip`; identity with the absent file cannot be verified.
- No browser automation or visual viewport/theme verification performed. No Git writes. All pre-existing uncommitted work retained.

## Git status

`git status --short --branch`: `main...origin/main`; 18 modified tracked paths and 20 untracked entries, including this new report. Only Dashboard template/CSS were modified by UI-03; the remaining changes were already present.

```text
## main...origin/main
 M .env.example
 M config/settings.py
 M config/urls.py
 M locale/vi/LC_MESSAGES/django.mo
 M locale/vi/LC_MESSAGES/django.po
 M requirements.txt
 M start-web.ps1
 M static/css/app.css
 M static/css/design-tokens.css
 M static/js/app.js
 M tasks/test_authentication.py
 M tasks/views.py
 M templates/base.html
 M templates/dashboard.html
 M templates/home.html
 M templates/includes/workspace_preview.html
 M templates/registration/login.html
 M templates/registration/signup.html
?? docs/database-design.md
?? docs/google-oauth-setup.md
?? docs/reports/database-design-verification-2026-11-09.md
?? docs/reports/flowspace-auth-layout-fix-2026-11-10-989780a6.md
?? docs/reports/flowspace-dashboard-polish-2026-11-11.md
?? docs/reports/flowspace-direction-c-brand-unification-2026-11-11.md
?? docs/reports/flowspace-home-free-start-cta-2026-11-10-989780a6.md
?? docs/reports/flowspace-home-preview-cta-2026-11-10-989780a6.md
?? docs/reports/flowspace-home-ui-regressions-2026-11-10-989780a6.md
?? docs/reports/google-signin-allauth-2026-11-10.md
?? docs/reports/oauth-env-autoload-startweb-2026-11-11.md
?? docs/reports/ui-03-flowspace-dashboard-integration-2026-11-11.md
?? docs/reports/workspace-preview-assertion-fix-2026-11-10.md
?? frontend/
?? static/flowspace/
?? static/fonts/
?? tasks/context_processors.py
?? tasks/test_google_oauth.py
?? templates/includes/google_button.html
?? templates/socialaccount/
```
