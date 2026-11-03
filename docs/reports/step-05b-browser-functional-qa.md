# Task 05B — Real browser functional acceptance

Date: 2026-11-03  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / Git Bash; Django 5.2.18 on `127.0.0.1:8000`; PostgreSQL `cloudtask_dev` at `127.0.0.1:55432` via existing PGPASSFILE configuration.  
Tooling: session's existing chrome-devtools browser automation (DOM snapshots, navigation, form fills, in-page JS); `curl` for HTTP status evidence. No tools installed, no launchers created, no app code changed.

## Result: PASS — all requested functions verified with browser-visible evidence

No application bugs were found; nothing needed fixing. One environment limitation (screenshot tool timeouts) is recorded as a blocker for image evidence only; DOM/HTTP evidence covers every acceptance item.

## Environment verification

- Server was already running from Task 04L-B (PID 17660); later intentionally killed and restarted (see persistence test).
- `psql -w -h 127.0.0.1 -p 55432 -U cloudtask_app -d cloudtask_dev` with `PGPASSFILE` → exit 0, `cloudtask_dev|cloudtask_app`. Postgres server reused from 04L recovery session (not restarted).
- Behavioral proof the running app targets **PostgreSQL cloudtask_dev, not SQLite**: after browser-side task creation, a read-only psql query against `cloudtask_dev` returned exactly the browser-created rows (see DB evidence below).

## Test accounts (disposable, created during this task)

| Account | Password | Note |
| --- | --- | --- |
| `qa-user-a` | (recorded in test env only, not reproduced here) | Created via /register/ with auto-login |
| `qa-user-b` | (same) | Created via /register/ |

Both accounts and `qa-user-a`'s single task remain in `cloudtask_dev` (deliberately kept as disposable QA data; deletable later by their owner).

## Results matrix

| # | Function | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Registration (User A) | PASS | Form submit → navigated to `/dashboard/`; nav shows `Hi, qa-user-a`; toast "Account created. You are now signed in." |
| 2 | Registration (User B) | PASS | Same flow; nav `Hi, qa-user-b`; empty-state dashboard |
| 3 | Login (wrong password) | PASS | Stays on `/login/`; errorlist: "Please enter a correct username and password. Note that both fields may be case-sensitive." |
| 4 | Login (correct) | PASS | `/login/` → `/dashboard/`; nav `Hi, qa-user-a`; own task listed |
| 5 | Logout | PASS | Nav form submit → redirected to `/`; nav shows `Log in`/`Create account`; anonymous `GET /dashboard/` → 302 → `/login/?next=/dashboard/` (curl, exit 0) |
| 6 | Create task | PASS | `/tasks/create/` (title "QA Task A1 - alpha", description, due 2026-12-25) → `/dashboard/`, toast "Task created."; second task A2 created likewise |
| 7 | List tasks | PASS | Dashboard lists both tasks with status chips (`NOT COMPLETED`/`COMPLETED`) and due dates |
| 8 | View task | PASS | `/tasks/1/` shows title, STATUS "Not Completed", DUE DATE "Dec 25, 2026", NOTES text, Edit/Delete links |
| 9 | Edit task | PASS | `/tasks/1/edit/` pre-filled; retitled to "QA Task A1 - alpha EDITED" + status Completed → toast "Task updated."; dashboard shows COMPLETED chip |
| 10 | Delete task | PASS | `/tasks/2/delete/` confirmation page ("Delete this task?", "Keep task" cancel link) → confirm → toast "Task deleted."; task 2 gone from list |
| 11 | Incomplete filter | PASS | `/dashboard/?status=incomplete` lists only "QA Task A2 - beta" |
| 12 | Completed filter | PASS | `/dashboard/?status=completed` lists only "QA Task A1 - alpha EDITED" |
| 13 | Invalid filter param | PASS | `/dashboard/?status=bogus` degrades gracefully to All tasks, no 500 |
| 14 | Invalid input (task form, server-side) | PASS | Title `required` attribute removed in-browser, empty title submitted → form re-rendered with "This field is required." and `aria-invalid="true"`; no task created |
| 15 | Invalid input (registration mismatch) | PASS | Password ≠ confirmation → stays on `/register/`, inline error "The two password fields didn't match."; then corrected values registered successfully |
| 16 | Ownership isolation (list) | PASS | As User B: dashboard empty state "Start with one clear next step."; User A's tasks absent |
| 17 | Ownership isolation (direct URL) | PASS | As User B: `/tasks/1/`, `/tasks/1/edit/`, `/tasks/1/delete/` each render **"Not Found"** (404) |
| 18 | `/health/` | PASS | `{"status": "ok", "service": "cloud-task-manager", "version": "1.1.0-auth"}`, HTTP 200 (before and after restart) |
| 19 | Persistence after Django-only restart | PASS | Server process killed (`taskkill /PID 17660 /F`, exit 0; port freed) and restarted with same PGPASSFILE/DATABASE_URL; after restart: `/dashboard/` still logged in as `qa-user-a` (DB-backed session), task still listed; `/health/` `/login/` `/register/` `/` all 200 |

## Database evidence (read-only, parameterized)

```sql
SELECT id, username, is_active FROM auth_user WHERE username IN ('qa-user-a','qa-user-b') ORDER BY id;
-- 1 | qa-user-a | t ; 2 | qa-user-b | t
SELECT t.id, t.title, t.status, t.due_date, u.username AS owner FROM tasks_task t JOIN auth_user u ON u.id = t.user_id ORDER BY t.id;
-- 1 | QA Task A1 - alpha EDITED | completed | 2026-12-25 | qa-user-a
SELECT current_database(), count(*) FROM tasks_task;
-- cloudtask_dev | 1
```

`tasks_task` columns confirmed via `information_schema` (status is a text field: `completed`/`not completed` values — mirrors the UI chips). Deleted task 2 is absent. All queries exit 0 against `cloudtask_dev` only.

## Commands and exit codes (summary)

- `psql -X -w ... -d cloudtask_dev -c "SELECT current_database(), current_user;"` → exit 0
- Browser interactions via chrome-devtools (navigate/fill/click/evaluate_script) — all targeted pages loaded; every assertion above came from live DOM (`document.querySelector`, a11y snapshots) after real form submissions
- `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/dashboard/` → `302` + `Location: /login/?next=/dashboard/` (exit 0)
- `taskkill //PID 17660 //F` → exit 0; restart: `.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --noreload` (background, same env as 04L-B)
- Post-restart sweep: `/health/` `/login/` `/register/` `/` → 200, 200, 200, 200

## Evidence artifacts

- DOM snapshots (a11y trees) captured for every page and assertion, stored in the agent session transcript.
- Screenshots: `browser-home.png`, `browser-login.png`, `browser-register.png` (Task 04L-B session temp files) show styled rendering. **Blocker (image evidence only):** `chrome-devtools take_screenshot` timed out after 30 s repeatedly on dashboard pages during this task; per instruction, screenshot retries were stopped and no CSS was modified. Acceptance relied on DOM snapshots + HTTP status + DB rows instead. Navigation, snapshots, and JS evaluation were unaffected.

## English UI text recorded for future translation (no changes made now)

Navigation/global: "Cloud Task Manager", "Log in", "Create account", "Dashboard", "Hi, {username}", "Log out", "← Back to home".  
Home: "A CALMER WAY TO GET THINGS DONE", "Make room for the work that matters.", "Cloud Task Manager gives your next actions a clear home, so you can capture the details, keep momentum, and finish with confidence.", "Create your workspace", "01 → done", "SMALL STEPS, VISIBLE PROGRESS".  
Register: "A FRESH START", "Create your account", "Create account", "Set up a private workspace for the tasks you want to move forward.", "Username:", "Email:", "Password:", "Password confirmation:", "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", "Optional. Used only to identify your account.", "Enter the same password as before, for verification.", the four password-validator help strings ("Your password can't be too similar…", "…at least 6 characters", "…commonly used password", "…entirely numeric"), "Already have an account? Log in.", "The two password fields didn't match."  
Login: "WELCOME BACK", "Log in", "Pick up where you left off and keep your next steps moving.", "New here? Create your account.", "Please enter a correct username and password. Note that both fields may be case-sensitive."  
Dashboard: "YOUR PRIVATE WORKSPACE", "Dashboard", "A clear view of what is moving, waiting, and done.", "+ New task", "Your tasks", "Filter by progress", "SHOW", "All tasks", "Incomplete", "Completed", "Status", "Apply", "Start with one clear next step.", "Your task list is ready for its first item.", "Create a task", "NOT COMPLETED", "COMPLETED", "No due date", "Due {date}".  
Task create/edit: "MAKE THE NEXT STEP VISIBLE", "Create task", "Edit task", "Add enough detail to make this task easy to pick up again.", "Title:", "Description:", "Due date:", "Status:", "Not Completed", "Completed", "Save task", "Cancel".  
Task detail: "TASK DETAIL", "STATUS", "DUE DATE", "NOTES", "Edit task", "Back to tasks", "Delete".  
Delete confirm: "THIS CANNOT BE UNDONE", "Delete this task?", "You are about to permanently remove “{title}” from your workspace.", "Delete task", "Keep task".  
Toasts/errors: "Account created. You are now signed in.", "Task created.", "Task updated.", "Task deleted.", "This field is required.", 404 page title "Not Found".

## Blockers

- Screenshot capture on dashboard pages (tool timeout, 30 s) — image evidence unavailable beyond the three public-page screenshots from 04L-B; all acceptance evidence is DOM/HTTP/DB based. No functional impact.

## Files changed

- None in application code. Only this report was added. (`staticfiles/` build artifact from 04L-B remains gitignored.)

## Git status

`git status --short --branch` exit 0: `main`, no commits, project entries untracked as before. Nothing staged, committed, pushed, reset, or cleaned.

## Next allowed step

Translation/i18n pass for the recorded UI strings (as a separately authorized task), or continuation of the roadmap steps that depend on a functionally verified app. The 04K isolated suites (`cloudtask_test_04k`) remain runnable non-interactively via the existing PGPASSFILE entry if backend regression coverage is requested.
