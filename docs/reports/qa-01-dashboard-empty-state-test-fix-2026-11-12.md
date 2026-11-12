# QA-01 — Dashboard empty-state stale test fix — 2026-11-12

## Scope and outcome

Fixed the confirmed stale Dashboard empty-state test `tasks.test_task_crud.TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks`. Only the outdated test expectations changed.

No production behavior, UI markup, CSS, translations (`locale/vi/LC_MESSAGES/django.po` / `.mo`), templates or database models were modified. No Git write commands were run.

## 1. Confirmed approved empty-state behavior

Evidence gathered before editing:

- `templates/dashboard.html` lines 70–77 render the empty state when `total_tasks` is zero:
  - heading `<h2 id="empty-heading">{% translate 'Start with one clear next step.' %}</h2>`
  - body `<p>{% translate 'Your task list is ready for its first item.' %}</p>`
  - CTA `<a class="btn" href="{% url 'tasks:task_create' %}">…{% translate 'Create a task' %}</a>`
- `'Your list is clear.'` is **not** the Dashboard empty-state copy. It belongs to `templates/task_list.html` line 61, where it is used only for the `status_filter == 'completed'` branch. The Dashboard never renders it.
- Vietnamese catalog contains all three Dashboard strings: `locale/vi/LC_MESSAGES/django.po` lines 357–364, and the compiled `django.mo` resolves them to `Bắt đầu bằng một bước tiếp theo rõ ràng.`, `Danh sách công việc sẵn sàng cho mục đầu tiên.`, `Tạo một công việc`.
- Prior reports agree this is the incumbent approved copy: `docs/reports/ui-08-dashboard-micro-animations-2026-11-12.md` (line 42), `docs/reports/ui-04-stitch-task-list-integration-2026-11-11.md` (line 25), `docs/reports/step-05c-bilingual-ui.md` (line 52), `docs/reports/step-05b-browser-functional-qa.md` (lines 45, 82).
- The stale test asserted `gettext('Your list is clear.')` under `override('vi')`, i.e. the Vietnamese `Danh sách của bạn đang trống.`, which the Dashboard response does not contain.

Conclusion: production behavior is correct; the test expectation was outdated.

## 2. Test change

File: `tasks/test_task_crud.py`, method `test_dashboard_shows_empty_state_when_no_tasks` only.

- Replaced the stale `assertContains(response, gettext('Your list is clear.'))` with the three approved Dashboard empty-state strings: `Start with one clear next step.`, `Your task list is ready for its first item.`, `Create a task`.
- Added `assertNotContains(response, gettext('Your list is clear.'))` to pin the Dashboard copy apart from the task-list copy.
- Added `assertEqual(response.context['completed_count'], 0)` alongside the existing `pending_count` check.
- Kept all meaningful empty-list assertions: HTTP 200, `priority_tasks` empty, `pending_count == 0`, and the `tasks:task_create` link present.

Assertions are still evaluated under `override('vi')`, matching the project's Vietnamese default (`config/settings.py` `LANGUAGE_CODE = 'vi'` plus `config/middleware.py` default-language middleware), so the test continues to verify translated output rather than hard-coded English.

## 3. Verification environment

Working directory for every command: `C:\ProjectCloud\cloud-task-manager`. Python: repository `.venv\Scripts\python.exe`. Settings were process-only (`SECRET_KEY`, `DATABASE_URL=sqlite:///:memory:`, `DEBUG`, `DJANGO_SETTINGS_MODULE`); no repository configuration or environment file was edited. Tests used a process-only in-memory SQLite database; no application records or database files were touched.

## 4. Exact commands, exit codes and results

### Pre-fix reproduction of the stale failure — exit 1

```powershell
.\.venv\Scripts\python.exe -c "import os; os.environ.update(SECRET_KEY='qa-01-isolated-verification-only', DATABASE_URL='sqlite:///:memory:', DEBUG='True', DJANGO_SETTINGS_MODULE='config.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'test', 'tasks.test_task_crud.TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks', '--verbosity', '2'])"
```

Result: `Ran 1 test` — `FAILED (failures=1)`, exit code 1.

```
AssertionError: False is not true : Couldn't find 'Danh sách của bạn đang trống.' in the following response
```

The rendered response body was inspected in full and confirmed to contain the approved empty state (`Bắt đầu bằng một bước tiếp theo rõ ràng.`, `Danh sách công việc sẵn sàng cho mục đầu tiên.`, `Tạo một công việc`) and no `Danh sách của bạn đang trống.`.

### Post-fix affected Dashboard tests — exit 0

```powershell
.\.venv\Scripts\python.exe -c "import os; os.environ.update(SECRET_KEY='qa-01-isolated-verification-only', DATABASE_URL='sqlite:///:memory:', DEBUG='True', DJANGO_SETTINGS_MODULE='config.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'test', 'tasks.test_task_crud.TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks', 'tasks.test_task_crud.TaskCrudTests.test_dashboard_shows_only_current_users_tasks', '--verbosity', '2'])"
```

Result: `Ran 2 tests` — `OK`, exit code 0. Both the empty-state test and the ownership-isolation Dashboard test pass.

### Owning module regression check — exit 0

```powershell
.\.venv\Scripts\python.exe -c "import os; os.environ.update(SECRET_KEY='qa-01-isolated-verification-only', DATABASE_URL='sqlite:///:memory:', DEBUG='True', DJANGO_SETTINGS_MODULE='config.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'test', 'tasks.test_task_crud', '--verbosity', '1'])"
```

Result: `Ran 29 tests in 34.167s` — `OK`, exit code 0.

### Whitespace check — PASS, exit 0

```powershell
git diff --check
```

Result: exit code 0, no whitespace errors. Git emitted only the existing LF-to-CRLF advisory warnings for already-modified files. Ordinary `git diff --check` does not cover untracked files, including this report.

### Git status — exit 0

```powershell
git status --short
```

```text
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
 M tasks/test_task_crud.py
 M tasks/views.py
 M templates/base.html
 M templates/dashboard.html
 M templates/home.html
 M templates/includes/workspace_preview.html
 M templates/registration/login.html
 M templates/registration/signup.html
 M templates/settings.html
 M templates/task_form.html
 M templates/task_list.html
?? dashboard-task-list-polish-2026-11-11.md
?? docs/database-design.md
?? docs/google-oauth-setup.md
?? docs/reports/dashboard-upcoming-timeline-2026-11-11.md
?? docs/reports/database-design-verification-2026-11-09.md
?? docs/reports/desktop-sidebar-header-correction-2026-11-11.md
?? docs/reports/desktop-sidebar-toggle-regression-fix-2026-11-11.md
?? docs/reports/expanded-logo-to-toggle-restored-2026-11-11.md
?? docs/reports/flowspace-auth-layout-fix-2026-11-10-989780a6.md
?? docs/reports/flowspace-dashboard-polish-2026-11-11.md
?? docs/reports/flowspace-direction-c-brand-unification-2026-11-11.md
?? docs/reports/flowspace-home-free-start-cta-2026-11-10-989780a6.md
?? docs/reports/flowspace-home-preview-cta-2026-11-10-989780a6.md
?? docs/reports/flowspace-home-ui-regressions-2026-11-10-989780a6.md
?? docs/reports/fold-logo-sidebar-toggle-2026-11-11.md
?? docs/reports/google-signin-allauth-2026-11-10.md
?? docs/reports/oauth-env-autoload-startweb-2026-11-11.md
?? docs/reports/sidebar-collapsed-fold-expand-2026-11-11.md
?? docs/reports/sidebar-combined-toggle-controls-2026-11-11.md
?? docs/reports/ui-03-flowspace-dashboard-integration-2026-11-11.md
?? docs/reports/ui-04-stitch-task-list-integration-2026-11-11.md
?? docs/reports/ui-04-task-list-search-i18n-regressions-2026-11-11.md
?? docs/reports/ui-05-stitch-create-edit-integration-2026-11-11.md
?? docs/reports/ui-05-task-date-presets-2026-11-11.md
?? docs/reports/ui-06-flowspace-settings-integration-2026-11-12.md
?? docs/reports/ui-08-dashboard-micro-animations-2026-11-12.md
?? docs/reports/workspace-preview-assertion-fix-2026-11-10.md
?? frontend/
?? static/css/dashboard-motion.css
?? static/flowspace/
?? static/fonts/
?? static/js/task-form.js
?? tasks/context_processors.py
?? tasks/test_google_oauth.py
?? tasks/test_task_list.py
?? templates/includes/google_button.html
?? templates/socialaccount/
```

This QA-01 change set is exactly: modified `tasks/test_task_crud.py` (one test method) and the new report `docs/reports/qa-01-dashboard-empty-state-test-fix-2026-11-12.md`. Every other entry above predates QA-01 and was left untouched.

### Task-level diff

```powershell
git diff -- tasks/test_task_crud.py
```

```diff
@@ -107,10 +107,17 @@ class TaskCrudTests(TaskSetupMixin, TestCase):
     def test_dashboard_shows_empty_state_when_no_tasks(self):
         response = self.client.get(reverse('tasks:dashboard'))
         self.assertEqual(response.status_code, 200)
+        # The approved Dashboard empty state uses its own copy. The
+        # "Your list is clear." string belongs to the task-list page
+        # (status=incomplete branch) and is not rendered here.
         with override('vi'):
-            self.assertContains(response, gettext('Your list is clear.'))
+            self.assertContains(response, gettext('Start with one clear next step.'))
+            self.assertContains(response, gettext('Your task list is ready for its first item.'))
+            self.assertContains(response, gettext('Create a task'))
+            self.assertNotContains(response, gettext('Your list is clear.'))
         self.assertFalse(response.context['priority_tasks'])
         self.assertEqual(response.context['pending_count'], 0)
+        self.assertEqual(response.context['completed_count'], 0)
         self.assertContains(response, reverse('tasks:task_create'))
```

## Remaining risks / limits

- The assertion relies on the project default language being `vi` (`LANGUAGE_CODE = 'vi'` and the Vietnamese default middleware). If the default language or middleware were intentionally changed later, this test would need the same update again.
- `assertNotContains(response, gettext('Your list is clear.'))` intentionally pins the Dashboard copy apart from the task-list copy; a future unified empty-state copy would require updating this test.
- NOT RUN: full repository test suite, browser automation, rendering or visual checks, and unrelated suites/audits — out of scope for QA-01.
- NOT RUN: `git add`, `commit`, `checkout`, `reset`, `stash`, `push` or any other Git write. Existing uncommitted user/agent work was preserved.
- The pre-existing modified/untracked files listed above are outside QA-01 and were not reviewed or altered.

Stopped after the test fix, verification and this new report.
