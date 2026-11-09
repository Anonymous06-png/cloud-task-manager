# Task 07 UI cleanup — Settings and Login

Date: **2026-11-05**. Repository: `C:\ProjectCloud\cloud-task-manager`.

## Result: PASS for the two requested removals

Only two application files changed in this cleanup:

- `templates/settings.html`: removed the entire authenticated **Sidebar** preferences section, including Expanded/Collapsed radio options. Language, Appearance, Account and the browser-preference note remain.
- `templates/base.html`: render the public Settings navigation link only when `request.resolver_match.url_name != 'login'`. The authenticated navigation branch is untouched. Home/Register/public Settings retain their Settings link.

The actual sidebar, collapse button, mobile navigation, localStorage behavior, authentication/forms and backend are unchanged. CSS/JS were inspected but not edited: now-unused preference selectors safely match nothing. Shared choice styles remain necessary for Language/Appearance; avoiding static edits also avoids an unnecessary rebuild.

New report: `docs/reports/step-07-ui-cleanup-settings-login.md` (this file). No changes to the existing Task 07 report or earlier reports.

## Focused checks

External check helper: `C:\Users\Ky\AppData\Local\Temp\ctm-task07-cleanup-jgxc2bcd\verify-cleanup.py`.

It uses Django `SimpleTestCase`, unsaved user objects and fresh template rendering; database access is prohibited. A random process-only key and in-memory SQLite configuration avoid real credentials/databases. No migrations, fixtures or persistent data writes.

```bash
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -I -B \
  C:/Users/Ky/AppData/Local/Temp/ctm-task07-cleanup-jgxc2bcd/verify-cleanup.py \
  C:/ProjectCloud/cloud-task-manager
```

**Exit 0; 6 tests in 0.071s, OK; Django system check: 0 issues.**

Tests cover:

1. Authenticated Settings has no sidebar preferences (VI/EN).
2. Settings retains Language, Appearance, Account, real sidebar and one collapse button.
3. Public Login has no Settings link but retains registration/home, login form, CSRF and next (VI/EN).
4. Other public pages retain Settings navigation.
5. Authenticated navigation retains all three Settings destinations.
6. Public Settings retains language/theme controls without an authenticated sidebar.

`git diff --check`: **exit 0**, informational LF/CRLF notices only. No broad auth/CRUD suite was repeated.

## Live browser verification and approved template refresh

Initial live checks showed both old elements because Django was serving cached templates. No restart was performed until the user selected **“Approve template refresh”** in the confirmation question. **No static rebuild was requested or performed.**

After verifying listener PID, parent, creation times, owner and generation-3 state, the existing same-key supervisor was asked to restart only its tracked Django child using:

```text
direct-20261105T011049Z-105d5f-restart-3.json
```

This new control file is in the existing private Task 06B runtime evidence directory. No launcher or supervisor code was edited/executed anew.

- Django **15496 → 16556**; new child created **2026-11-05T10:03:16.6293390+07:00**.
- Supervisor **21348 unchanged**; same in-memory key/environment reused; existing browser session stayed authenticated.
- PostgreSQL **18392 unchanged**. Startup log confirms `cloudtask_dev_utf8_06b / UTF8 / cloudtask_app`; only existing read-only startup gates ran.
- PowerShell listener/ownership/child checks: **exit 0**. No manual process kill, PostgreSQL restart or database mutation.

| Browser check | Actual result |
|---|---|
| Authenticated `http://127.0.0.1:8000/settings/` | **PASS** — reloaded HTTP 200; Sidebar preferences absent; Language, Appearance, Account, Settings navigation and actual sidebar remain. |
| Sidebar collapse/expand | **PASS** — native clicks; `aria-expanded` changes false → true; restored expanded state. |
| Public `http://localhost:8000/login/` | **PASS** — reloaded HTTP 200; navigation shows Log in/Create account only, without Settings. Separate hostname kept the signed-in 127.0.0.1 session intact; no logout/login submission. |
| Desktop visual checks | **PASS for removals** — Settings 1280×720 and Login 1280×900 screenshots inspected. |
| Mobile/Dark/full functional regression | **NOT RUN** — no changes to those styles/behaviors; not claimed as new acceptance. |

Screenshot directory: `C:\Users\Ky\.zcode\cli\artifacts\sess_0fa4d2ed-41d3-43f9-9615-4aec9f301ae4\`.

- Settings: `call_KSlTGB853t89yIAND9xuO0wD-tool-result-e0d18f8b-90d9-4416-8f21-a88bcba4cc0b.png`
- Login: `call_gSDyKkECbJ9V6xHson3Us5LS-tool-result-72826920-5137-4569-8b51-39f9fbce222a.png`

## Preservation, Git and remaining needs

Before/after SHA-256 checks confirm unchanged CSS, design tokens, JS, static manifest, launchers, existing modified test files and the previous Task 07 report. Manifest remains `a1a30683cc049171e0d5fa685a3bce57181a846be45f272c326e808c10cc2fe1`.

Branch remains **main**. All pre-existing tracked modifications/untracked reports remain; this cleanup adds only the two template edits and this new untracked report. No staging, commit, push, reset, clean or branch changes. `git status --short --branch` and scoped inspection commands returned **0**.

The known long-username sidebar/footer overflow and mixed-language backlog are unchanged and outside scope. No blocker remains for these two removals. Browser login submission, full responsive/theme matrix and database-equivalence audit were not rerun. Next allowed step: review the small cleanup diff; any additional UI fix or restart requires separate authorization.
