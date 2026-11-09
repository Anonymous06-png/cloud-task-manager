# Task 07 — Complete UI refinement

Date: **2026-11-05**. Repository: `C:\ProjectCloud\cloud-task-manager`.

## Result

**IMPLEMENTED; automated checks PASS; isolated-browser functional/visual acceptance PARTIAL. Live port-8000 asset/template adoption now PASS after the user-approved guarded refresh documented at the end of this report. Overall visual/native-interaction acceptance remains PARTIAL, including a newly observed long-account-label sidebar overflow.**

The earlier no-restart/no-collectstatic statements and blocked-live results below describe the initial implementation and pre-approval verification. They are retained as history; the final **Approved guarded refresh** section supersedes their runtime/asset status only, not their functional-test limitations.

The UI now uses a coherent Workspace green/white task-first design. Dashboard, task list, Create/Edit, task detail/delete, navigation, Home, Login, Register and Settings were refined. **59 distinct automated tests passed (51 existing + 8 task-specific disposable tests), zero failures/errors.** These were SQLite tests, not PostgreSQL tests.

This is not an unconditional production-readiness or complete browser-acceptance claim. Native browser automation had intermittent click failures; successful DOM activation fallbacks are identified below. The default Vietnamese interface still has the existing mixed-language translation backlog. No Task 06B/06C repair or launcher verification was resumed.

## Scope and design decisions

Read `CLAUDE.md`, reports 05K, 05R, 05S, the required 06B validation/06C startup reports, and scoped active UI/view/form/settings/test contracts. No legacy Node implementation, design exports or unrelated backend was changed. No Plan Mode, subagents, UI framework, new dependency or security-audit run.

- **Todoist-inspired task hierarchy:** replaced large statistic cards and the decorative Today card with a compact line of real task counts and a primary list. Upcoming deadlines occupy a quiet secondary column; recent completions reuse the task component.
- **One task-row component:** circular 44px-target completion buttons, readable titles, conditional description previews, dates, explicit overdue text (not color alone), quiet status text and named View/Edit/Delete menus. Mobile retains deadlines/status instead of hiding them. Native POST/CSRF forms remain the source of state changes.
- **Compact editing:** shared field rendering, explicit labels, optional markers, Django help/error content, 16px inputs, grouped date/status controls, primary Save and secondary Cancel. The date input renders `Y-m-d` on unbound Edit GET and preserves bound submitted values; no backend widget change. Required browser validation complements, rather than replaces, Django validation.
- **Consistent shell:** pale green sidebar, single directional collapse control, persistent rail state, accessible labels even when captions are hidden, real Create task shortcut, responsive drawer and existing focus trapping. Settings retains only working language/appearance/sidebar/account controls; language now uses an explicit Save button instead of submitting when arrowing between radio choices.
- **Entry pages:** Home/Login/Register share spacing, typography and the explicitly labelled sample preview. Removed invented preview percentages/progress statistics. Sample rows are static illustration text, not fake interactive controls. Login/Register hide the illustration on mobile to prioritize forms.
- **Restrained surface design:** white canvas, existing green accent and dark tokens, separators instead of stacked cards, no gradients/glass effects or new animation. Existing fonts are reused; no new font/package dependency.
- **Minimal JavaScript:** retains theme/sidebar/mobile behavior; closes competing task menus and restores focus on Escape; submission feedback disables only the submitting control, recovers on `pageshow` and after a bounded 10-second wait; focuses invalid fields. No asynchronous CRUD or replacement authentication mechanism.

### Files changed by Task 07

| File | Change |
|---|---|
| `static/css/app.css` | Consolidated in-scope screen styles into one task-focused stylesheet (2650 → 460 lines); removed obsolete statistic/Today/preview-progress layout rules; responsive, dark, focus, reduced-motion styles retained/reworked. This is the largest review surface. |
| `static/css/design-tokens.css` | White canvas and lighter sidebar; existing green/dark palette otherwise retained. |
| `static/js/app.js` | Menu focus/coordination, bounded submit feedback and invalid-field focus. |
| `templates/base.html` | Edit/delete icons, real sidebar Create link, rail-accessible names, public active-page labels. |
| `templates/dashboard.html` | Compact counts, focus/recent task sections and deadline aside. |
| `templates/task_list.html` | Consistent rows, filters/search, visible submit/clear actions, appropriate empty states and preserved pagination query arguments. |
| `templates/includes/task_row.html` | Shared row, contextual action labels, descriptions/deadline/status, server-rendered overdue text. |
| `templates/includes/form_field.html` **NEW** | Shared fields/help/errors and date formatting. |
| `templates/task_form.html` | Compact Create/Edit layout, current task cancel target, CSRF and submission feedback. |
| `templates/task_detail.html` | Matched detail layout, real completion POST, task-list return link, edit/delete actions. |
| `templates/task_confirm_delete.html` | Matched confirmation with clear irreversible warning and Keep task path. |
| `templates/home.html` | Concise supporting copy; shared restyling applies to the existing composition. |
| `templates/includes/workspace_preview.html` | Quiet, explicitly illustrative task list; removed fake percentage meter. |
| `templates/registration/login.html` | Shared field layout, feedback; next/CSRF preserved. |
| `templates/registration/signup.html` | Same entry system as Login; all inherited validation/help fields retained. |
| `templates/settings.html` | Explicit language Save, applicable sidebar preferences, local-preference note. |
| `docs/reports/step-07-complete-ui-refinement.md` **NEW** | This report. |

No `tasks/*.py`, `config/*`, models, migrations, database configuration, infrastructure, launchers, locale catalog or dependencies were changed by Task 07. Pre-existing modifications to the launchers and two test files are **not** Task 07 changes.

## Verification environment and exact command ledger

All commands ran from the repository root in Git Bash, using the existing Python environment. No private credential file or key was read, printed, copied or replaced. A per-process signing key was generated in memory. No SQL was written; test/preview fixtures use Django ORM.

External disposable directory:

```text
C:\Users\Ky\AppData\Local\Temp\ctm-task07-lut09lww
```

`verify.py` and `test_ui.py` are external QA helpers, not application dependencies or committed tests. `verify.py` accepts repository path and mode; uses process-local settings, `DATABASE_URL=sqlite:///:memory:`, `DJANGO_ENV=local`, DEBUG for source static, and `StaticFilesStorage`. In preview/seed mode only, the database is `preview.sqlite3` inside that directory. Cookie names are `ctm07_preview_session` and `ctm07_preview_csrf`; the browser uses **localhost:8007**, not the active **127.0.0.1:8000** origin. The preview uses `StaticFilesHandler` and Python's WSGI server, not either launcher. Existing migrations were applied only inside disposable SQLite; no project PostgreSQL connection/schema operation occurred.

For the following commands, abbreviations are:

```bash
PY='./.venv/Scripts/python.exe'
W='C:/Users/Ky/AppData/Local/Temp/ctm-task07-lut09lww'
R='C:/ProjectCloud/cloud-task-manager'
```

| Executed command/check | Exit / actual outcome |
|---|---|
| `pwd; git status --short; rg --files ...` and scoped `Read`/`rg`/`wc` | 0 for shell discovery; scoped source/report review. |
| `sha256sum start-web.bat start-web.ps1 tasks/test_task_crud.py tasks/tests.py docs/reports/step-06*.md` before/after | 0; every protected file hash matched. |
| `powershell.exe -NoProfile -NonInteractive -Command 'Get-NetTCPConnection ...'` | 0; 8000 PID 18428; 8007 initially unused. |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B -c 'from pathlib import Path; import tempfile; print(tempfile.mkdtemp(prefix="ctm-task07-"))'` | 0; created external disposable directory. |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/verify.py" "$R" check` | **0**; `System check identified no issues (0 silenced).` |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/verify.py" "$R" test` | **0; 51 tests in 46.240s, OK**, no failures/errors/skips. |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/verify.py" "$R" ui` | **0; 8 tests in 4.030s, OK**, no failures/errors/skips. |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/verify.py" "$R" preview` | Served `http://localhost:8007/`; system check clean. Deliberately stopped with TaskStop after QA; **not** a successful process-exit claim. |
| `PYTHONIOENCODING=utf-8 "$PY" -I -B "$W/verify.py" "$R" seed` | **0**; 9 synthetic rows in disposable preview only, after interactive CRUD test. |
| `node --check static/js/app.js` | **0**, both initial and closing checks. |
| `git diff --check` | **0**, repeated at source milestones and closing; LF/CRLF notices only. |
| `git diff --stat`, `git diff --name-only -- config tasks start-web.ps1 start-web.bat`, `git status --short --branch` | 0; no application backend delta; only pre-existing test/launcher modifications there. |
| Python hashlib/JSON inspection of source and existing `staticfiles/staticfiles.json` | 0; confirmed old collected assets differ from new source; no writes. |
| Closing PowerShell TCP/CIM inspection and manifest SHA-256 | 0; protected runtime identity/manifest unchanged. |

The check/test compound command explicitly printed `CHECK_EXIT=0` and `TEST_EXIT=0`. Browser tool calls have no shell exit code.

### Actual test coverage

**51 existing tests:** `tasks.test_authentication` (22) and `tasks.test_task_crud` (29). Includes registration/login/logout, protected routes, safe next handling, CSRF, ownership, validation, create/read/update/delete/toggle, filtering/search/pagination, both-language forms and sequential Vietnamese/emoji submissions.

**8 disposable UI tests:** ISO edit date/all fields; invalid form retains text/date with error association; authenticated UI pages render in both languages with unique IDs; named row actions/native POST; filter/search pagination links; explicit language submit and real settings choices; public forms/no fake metrics/safe hidden next; detail toggle roundtrip/delete confirmation preserves task before POST.

No full unrelated suite, PostgreSQL-backed tests, migration changes, deployment checks or full security audit. Existing tests were not edited to make results pass. The final whitespace-only separator edits were included in the eight-test UI run; the first 51-test run preceded those two presentational whitespace edits.

Private logs retained outside Git:

- Existing regression/check log: `C:\Users\Ky\AppData\Local\Temp\zcode-bash-1TUKw7\sess_0fa4d2ed-41d3-43f9-9615-4aec9f301ae4\call_7iQnEruOgZR8wZqNQSyBIpEX-stdout.log`
- Eight-test UI log: same directory, `call_MqGEjlrPWSv8K5tUdixiEsE8-stdout.log`.
- Preview access log: same directory, `call_JRL2l0ABinoG3n6vg6tTTBtM-stdout.log`.

## Static freshness: verified, not guessed

The protected live browser at `127.0.0.1:8000/dashboard/` loaded:

```text
/static/css/app.0a2830e26a9c.css
/static/css/design-tokens.044880a298ae.css
/static/js/app.975f35d2df79.js
```

These correspond to the old collected files, not the edited source. The browser showed the old metric cards. This is consistent with the already-documented DEBUG=False/no-reload/cached-template runtime. Query strings would not refresh cached templates or rewrite manifest mappings, so none were added as a workaround.

**The preview browser fetched both source CSS files with status 200 and computed SHA-256 values matching the filesystem:**

| Source | SHA-256 |
|---|---|
| `static/css/app.css` | `0489855683e03ffa902e91837621db5a510d9c5aba23e2f17350ed22e8b24b25` |
| `static/css/design-tokens.css` | `4a43179e1a7cc60d53a139889250f1241d3e7039fcdac49e6f746da300aed7fd` |
| `static/js/app.js` (filesystem; browser behavior exercised) | `950455b110ec5f6614a5c623bf8a43d88cdc74317022dbb08706c00dbc708729` |

Shared static manifest SHA-256 before/after: `86faf9aa89d4fc5add32a61acef7349698a03f86399b25fa894addb0b60a21bb`.

**No collectstatic, asset overwrite or port-8000 restart.** Fresh-source preview evidence does not establish that the protected runtime has adopted these edits.

## Browser functional and visual results

ZCode in-app browser. No external browser automation was substituted. QA account `qa07-preview` exists only in disposable SQLite; its randomly generated password was not displayed/stored. Existing live account/session was not logged out or mutated. One read-only live Home navigation redirected to the already-authenticated dashboard; QA writes thereafter were isolated.

| Item | Status | Evidence/limit |
|---|---|---|
| Home desktop, 1280×720 | **PASS** | Screenshot inspected; coherent green/white split, real entry links, clearly labelled illustrative tasks, no horizontal overflow. |
| Home EN language switch and registration navigation | **PASS** | Native browser clicks; correct translated route/page. VI initial text rendered with accents, but mixed-language backlog remains. |
| Registration | **PASS (functional)** | Native field fill and submit created QA account, established session, showed Dashboard success and empty state. Full registration screenshot/mobile matrix NOT RUN. |
| Required task title | **PASS** | Native Save attempt with empty title sets `validity.valueMissing=true` and focuses Title; no task created. |
| Create task form desktop | **PASS (visual)** | Screenshot with exact Vietnamese/emoji title, notes, ISO date; aligned controls/actions, no clipping. |
| Create POST | **PASS with fallback** | Native populated Save click timed out; keyboard Enter returned without submission. Fresh snapshot confirmed unchanged form. `locator.evaluate(el => el.click())` then issued normal browser POST, redirected, showed `Task created.` and exact title/notes/date. |
| Sidebar collapse/navigation persistence | **PASS with fallback** | Native Collapse click timed out; DOM activation produced `aria-expanded=false`. Native Tasks navigation succeeded; screenshot/DOM confirmed persisted collapsed rail and named icon links. |
| Task list desktop, 1280×720 | **PASS (visual)** | Screenshot inspected; quiet list, clear filters/search, deadline/status and rail; no overflow. |
| Task list mobile Dark, 390×844 | **PASS (visual)** | Native theme click selected dark. Screenshot inspected; no horizontal overflow, accessible-size actions, Unicode title, description truncation and metadata retained. |
| Mobile drawer and Escape | **PASS** | Native open click creates navigation dialog; Escape closes it and expanded state returns false. Full Tab/Shift-Tab cycling NOT RUN. |
| Detail/read | **PASS** | Native task-title navigation showed exact saved Unicode title/notes/date, completion/edit/delete actions. |
| Edit | **PASS with fallback** | Native Edit click timed out; DOM activation opened populated form. Date value `2026-11-06` preserved. Title changed to `Kế hoạch tuần — đã cập nhật ✅`, status set to completed, DOM-activated Save returned success and exact updated task. Mobile editor screenshot NOT RUN. |
| Completed filter / search / clear | **PASS with fallback** | Normal browser requests through DOM activation; completed row visible, `không tìm thấy` search returned no-match state, query and selected status persisted, Clear search restored completed result. |
| Completion reversal | **PASS with fallback** | Row POST marked incomplete; task disappeared from Completed filter and reappeared in All with pending status. |
| Task menu and delete | **PASS with fallback** | Menu reveals real View/Edit/Delete links. Confirmation shows exact escaped task title/irreversible warning and Keep links; confirmed deletion of **only QA task ID 1** returned `Task deleted.` and empty Dashboard. Keep link navigation NOT RUN (destination inspected/tests cover preservation). |
| Settings behavior | **PASS with fallback** | Light radio updates theme; expanded-sidebar radio updates button ARIA; explicit Save language POST preserves selected English; account/logout controls present. VI selection through Settings itself NOT RUN (topbar switch exercised). |
| Settings desktop Light, 1280×900 | **PASS (visual)** | Screenshot inspected: aligned two-option groups, simple sections/account sidebar, no excessive cards. Dark Settings screenshot at 1440×1000 timed out: **BLOCKED** for that capture. |
| Populated Dashboard Light, 1280×900 | **PASS (visual)** | Screenshot inspected with 7 pending/2 completed synthetic tasks; list takes primary space, deadlines secondary, real overdue text, no overflow. Larger 1440×1000 capture timed out; later distinct 1280px capture succeeded. Recent-completed section extends below captured viewport; no full-page visual claim. |
| Logout | **PASS with fallback** | Settings account POST cleared disposable session and redirected to Login. |
| Login desktop, 1280×900 | **PASS (visual)** | Screenshot inspected with empty credential fields; consistent form/preview, real register/home links. Successful browser Login submission NOT RUN; automated login coverage passed. |
| Full browser native-click journey | **BLOCKED / partial** | Three native locator timeouts: populated Save, Collapse, mobile Edit. Keyboard Save did not submit. Fallbacks are not native-pointer certification. |
| Live updated UI at port 8000 | **BLOCKED** | Old cached templates/assets intentionally retained. No restart/collectstatic authorization. |
| PostgreSQL persistence / restart durability | **NOT RUN** | No project DB queries or restarts; disposable browser navigation persistence and isolated automated tests only. |
| All screens × mobile/dark/zoom; full accessibility/console audit | **NOT RUN** | Tested samples above only; no blanket responsive/accessibility/console PASS. |

### Screenshot evidence

Images are local artifacts outside the repository. Prefix:

```text
C:\Users\Ky\.zcode\cli\artifacts\sess_0fa4d2ed-41d3-43f9-9615-4aec9f301ae4\
```

- Home: `call_qp5IzdIlYgATmyJQmoKKcOzY-tool-result-8d099a9f-7bed-449a-9f62-90f226f2674f.png`
- Create form: `call_tzLaalAcoZOWH35PS0lhxthX-tool-result-d2669022-3bb5-438f-a382-d19ea50450d9.png`
- Desktop list/rail: `call_cjKmqP0ViuLKXReOVKwRCTru-tool-result-b5d1ce3d-86c8-46ac-849e-a1f58db11eb1.png`
- Mobile Dark list: `call_0FQefH5XrDylKjLvcgCcdrQj-tool-result-58d43656-a30b-4520-953a-276d9e0f7873.png`
- Populated Dashboard: `call_5qNZsblXAnrMCgd9Tb8cebns-tool-result-31bb5527-5b53-4dfa-afeb-537cb05d2acd.png`
- Settings: `call_E5u4Fx6t7sGRCN2locKkskKV-tool-result-03ca4823-e934-47b8-a49a-b3fa3a8f1dfc.png`
- Login: `call_mgqMDjgWpeaAkvMBCeptPLfp-tool-result-2802f7ed-5c61-45a2-b1a1-3d275795fc71.png`

One earlier dashboard screenshot was emitted before a later click failed in the same tool call; it did not reach the visible result and is **not** counted as reviewed evidence. Separate final screenshot above is the actual visual evidence.

## Preservation and remaining issues

- Port 8000 remained **PID 18428**, parent **21348**, creation **2026-11-05T08:13:18.9140650+07:00**, address **127.0.0.1**. No launcher execution, process environment extraction, signing-key provisioning or PostgreSQL operation.
- Pre-existing `start-web.bat`, `start-web.ps1`, `tasks/test_task_crud.py`, `tasks/tests.py` and all five initial Task 06 reports matched their before-task SHA-256 values. The shared manifest remained unchanged.
- The disposable preview was deliberately stopped through its own background task. The external SQLite file/helpers remain as local evidence (one synthetic account and nine seeded tasks after QA task deletion); no project data cleanup occurred. The preview browser will not load after shutdown. No credential values were retained in the report/helpers.
- **Translation backlog remains:** existing catalogs do not cover many Workspace strings; newly introduced short UI messages use gettext tags but have not been extracted/translated/compiled. No manual `.mo` generation. Complete VI linguistic polish remains follow-up work, not a passed criterion.
- Large stylesheet consolidation is confined to the requested UI surface but warrants review. Existing JavaScript/font availability and untested screen combinations remain normal regression risks. No new framework or dependency was added.
- Backend redirects after Create/Edit/Delete still go to Dashboard; this behavior was intentionally preserved. No invented priority/subtask/reminder/calendar integrations.
- The historical Task 06B session-preservation issue and Task 06C unverified launcher remain untouched and unresolved by this UI task.

## Closing Git status

Branch **main**, unchanged. No stage, commit, push, reset, clean, branch change or publication.

```text
 M start-web.bat                                      # pre-existing, unchanged
 M start-web.ps1                                      # pre-existing, unchanged
 M static/css/app.css
 M static/css/design-tokens.css
 M static/js/app.js
 M tasks/test_task_crud.py                            # pre-existing, unchanged
 M tasks/tests.py                                     # pre-existing, unchanged
 M templates/base.html
 M templates/dashboard.html
 M templates/home.html
 M templates/includes/task_row.html
 M templates/includes/workspace_preview.html
 M templates/registration/login.html
 M templates/registration/signup.html
 M templates/settings.html
 M templates/task_confirm_delete.html
 M templates/task_detail.html
 M templates/task_form.html
 M templates/task_list.html
?? docs/reports/step-06-full-local-stabilization.md
?? docs/reports/step-06b-task-create-post500-root-cause.md
?? docs/reports/step-06b-utf8-repair-continuation.md
?? docs/reports/step-06b-utf8-repair-validation-20261105.md
?? docs/reports/step-06c-stable-local-startup.md
?? docs/reports/step-07-complete-ui-refinement.md
?? templates/includes/form_field.html
```

## Next allowed step

Review this focused UI diff and visual evidence. **Do not run the unverified launchers or refresh shared static output automatically.** Live adoption requires separate explicit permission for a controlled static collection/restart that preserves the approved UTF8 runtime configuration and signing-key policy, followed by manual/native-pointer QA. Without that permission, only source review and isolated preview verification are appropriate. Translation completion and the remaining native keyboard/pointer/mobile matrix should be separately scoped. No Git publication is implied.

## Additional Task 07 verification — live processes and asset provenance

Requested as a continuation of Task 07, **2026-11-05**, with process inventory observed at **09:36:21.476+07:00**. This section adds current evidence; it does not rerun or relabel the earlier tests. **0 additional automated tests.** Only this existing report is edited in this continuation.

### Current process-to-browser mapping

Read-only Windows TCP/CIM inspection checked all listening addresses for ports **8000, 8001 and 8007**:

| Port | Current listener | Browser use |
|---|---|---|
| 8000 | **127.0.0.1:8000, PID 18428**, Python 3.11, owner `LAPTOP-214UR8HL\Ky`; created `2026-11-05T08:13:18.9140650+07:00`; supervisor PID **21348** | Existing tab `http://127.0.0.1:8000/dashboard/`; authenticated live Django instance. Reloaded read-only during this verification. |
| 8001 | **No TCP listener** | Neither browser tab uses port 8001. No port-8001 Django server can be identified because none is listening. |
| 8007 | **No TCP listener** | Initially active tab `http://localhost:8007/login/` is the **already-loaded, stopped disposable preview**, not a running server. |

Actual port-8000 process command:

```text
C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe -I -B C:\Users\Ky\AppData\Local\CloudTaskManager\repair-evidence\task06b-20261105T003400Z-af01b85c\runtime-entry-direct.py
```

Parent command (PID 21348, created `2026-11-05T08:10:49.5183490+07:00`):

```text
"C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe" -I -B C:/Users/Ky/AppData/Local/CloudTaskManager/repair-evidence/task06b-20261105T003400Z-af01b85c/runtime-supervisor-direct.py
```

The listener's exact entry script was **read, not executed**. It binds `config.settings`, uses this repository's packages, checks the approved `cloudtask_dev_utf8_06b` identity at startup, and calls Django `runserver` on `127.0.0.1:8000` with `use_reloader=False`. Thus this is the earlier directly supervised Django runtime, **not** a new process started by either edited launcher. No process environment or secret was extracted; no fresh direct database identity query was run.

Browser registry returned the two exact tabs above, with **8007 active initially**. The live 8000 tab was subsequently selected for inspection and remains selected after the live screenshot. No third tab/server was created.

### Stopped preview is not current live acceptance

The 8007 tab still has a complete Login DOM, loaded source stylesheets and the Task 07 entry design. Its in-memory CSSOM reports:

- `http://localhost:8007/static/css/design-tokens.css`: 3 top-level rules.
- `http://localhost:8007/static/css/app.css`: 263 top-level rules.

A browser-origin `fetch(location.href, {cache: 'no-store', credentials: 'omit', redirect: 'error', signal: AbortSignal.timeout(1500)})` **timed out** (`TimeoutError: signal timed out`). Combined with no 8007 listener, this confirms the displayed page is retained from the previous preview, **not freshly served now**. The preview tab was not reloaded or restarted. Its earlier CSS hash/screenshot results remain historical preview evidence only.

### Three-way CSS/JS comparison

The current source files and manifest were hashed from disk without importing Django or reading credentials. The current manifest still maps the three assets to the old filenames below. The browser then fetched each **observed same-origin `/static/` URL** with `cache: 'no-store'`, `credentials: 'omit'` and `redirect: 'error'`; all returned **HTTP 200**. No guessed asset path or cache-busting workaround was used.

| Asset | Current source bytes | Browser / manifest-collected bytes | Browser matches collected file | Browser matches source |
|---|---:|---:|---|---|
| `css/app.css` → `css/app.0a2830e26a9c.css` | 32788 | 55686 | **YES**, SHA-256 exact | **NO** |
| `css/design-tokens.css` → `css/design-tokens.044880a298ae.css` | 3828 | 3828 | **YES**, SHA-256 exact | **NO** (equal length, different contents) |
| `js/app.js` → `js/app.975f35d2df79.js` | 7177 | 5883 | **YES**, SHA-256 exact | **NO** |

Current source SHA-256 values match the earlier Task 07 table unchanged. Fresh browser responses and current manifest-collected files both hash to:

```text
app.0a2830e26a9c.css
55f04366f698619190d776d5d785ad55941b55fbf58f5ca8bb329d689d24f48a

design-tokens.044880a298ae.css
fb2f0bfdc802bbf42ffbcf4b3da0f45deb00fdb6392d196200a9cb18ec6d12d4

app.975f35d2df79.js
f4b5a02dd5d42d7807e5174f04fea5b20e06f56c0736073360aa380d55ba72a0
```

Manifest version **1.1**, SHA-256 still `86faf9aa89d4fc5add32a61acef7349698a03f86399b25fa894addb0b60a21bb`. All three served assets report `Cache-Control: max-age=315360000, public, immutable` and `Last-Modified: Thu, 05 Nov 2026 00:03:42 GMT`.

The browser's actually loaded app stylesheet has **316 top-level CSS rules**, includes `.stats-card`, and lacks `.task-summary`. This corroborates the fresh response hashes: the page is applying the old stylesheet, not simply linking an old-looking name to updated bytes.

### Fresh HTML and real visual result

A real browser reload of `/dashboard/` succeeded and retained the existing authenticated session. Its DOM still contains the old summary-card section, zero-padded counts and the **“One task at a time.”** Today panel. A separate cache-bypassing browser GET of the current page returned **HTTP 200** with these exact findings:

```text
oldMetricMarkup (summary stats-card): true
oldTodayCard (today-panel today-card): true
newSummaryNavigation (nav class="task-summary"): false
newSidebarCreate (class="sidebar-create"): false
```

A new screenshot at **1280×720** was captured and inspected. It visibly shows the old large metric band, bordered task panel, square checkbox and Today card, with no Task 07 sidebar Create shortcut. **The new Task 07 UI is NOT visible on the active port-8000 runtime.** The failure is server-side asset/template freshness, not something a browser hard refresh alone resolves.

Current live screenshot:

[Port 8000 still serving the old UI](C:/Users/Ky/.zcode/cli/artifacts/sess_0fa4d2ed-41d3-43f9-9615-4aec9f301ae4/call_b6BC8MvI00D7vRaJrm5jvDK2-tool-result-2e419404-45ad-4d7c-8bce-4bd4cf51e4e8.png)

### Continuation outcomes and commands

| Check/action | Status | Actual result |
|---|---|---|
| Port/process and parent/owner inventory | **PASS** | PowerShell `Get-NetTCPConnection`, `Get-CimInstance Win32_Process`, `Invoke-CimMethod GetOwner`; exit 0. Current facts above. |
| Source/manifest/collected SHA-256 comparison | **PASS (diagnosis)** | Existing `.venv/Scripts/python.exe -I -B -c` using `pathlib`, `json`, `hashlib`; exit 0. Three mismatches against source. |
| Browser-to-manifest byte equality | **PASS** | Three fresh browser static GETs, HTTP 200, exact collected-file hashes. This proves stale deployment, not new-UI acceptance. |
| Browser reload / uncached HTML / screenshot | **PASS (diagnosis)** | Live server demonstrably returns/renders old UI. |
| Task 07 adoption on port 8000 | **FAIL verification / BLOCKED remediation** | Neither new HTML nor new CSS/JS is served. Rebuild/restart requires permission. |
| Port 8001 browser verification | **NOT RUN** | No listener or browser tab; none started. |
| Fresh 8007 preview availability | **BLOCKED** | No listener; 1.5-second no-cache request timed out. Retained document is not live acceptance. |
| New regression runs | **NOT RUN** | 0 tests; earlier 59 passing tests not repeated. |
| Static rebuild, runtime/preview restart, launcher execution | **NOT RUN** | No approval received or assumed. |
| PostgreSQL operations or data mutation | **NOT RUN** | No direct DB commands or form submissions in this continuation; browser requests were read-only. No new database-equality claim. |
| Git/source scope | **PASS** | `git status --short --branch` exit 0; same dirty tree, no branch or Git write operation. Only this existing report updated. |
| Closing whitespace/preservation check | **PASS** | `git diff --check` exit 0; explicit whitespace scan of this untracked report found no issues; source CSS/JS and manifest hashes unchanged after report update. |

**Approval boundary at that point:** bringing the new UI to port 8000 required rebuilding shared static assets **and** refreshing the cached Django runtime. Neither action was performed before asking. The user subsequently selected **“Approve guarded refresh”**, explicitly authorizing static collection and restart of only the existing Django child through its verified supervisor, preserving signing key and UTF8 configuration and stopping if that could not be verified. The following section records the authorized execution.

## Approved guarded refresh — final live verification

### Authorization and verified restart path

The user approved the guarded refresh through the confirmation question in this Task 07 continuation. No permission for PostgreSQL restart, data writes, unverified launchers or Git publication was inferred.

Read-only inspection of the **existing** `runtime-supervisor-direct.py` established that:

- It retains one `environment` mapping outside its generation loop; the signing key is generated once, before that loop.
- Generation-specific `...-restart-<generation>.json` triggers terminate **only the supervisor's tracked child**, wait for port release, then spawn the next generation with the same environment and key.
- `direct-20261105T011049Z-105d5f-generation-2.json` matched the current supervisor **21348**, child **18428**, address and creation time.
- The generation-2 restart trigger and stop trigger were absent. The current-user ownership and exact PID/creation pair were checked again immediately before requesting restart.

The supervisor itself was **not restarted or edited**, its process environment/key was not extracted, and neither `start-web.ps1` nor `start-web.bat` was executed.

### Static rebuild with verified prior-output backup

Private evidence directory:

```text
C:\Users\Ky\AppData\Local\Temp\ctm-task07-refresh-36sui6oz
```

Before overwriting collected output, inspected the actual `staticfiles` target: **551 files, 4,269,241 bytes**. The external `refresh-static.py` copied the entire directory to a new `staticfiles-before` subdirectory and verified each copied file by SHA-256. It rejected an unexpected manifest/root, snapshotted source/protected-file hashes, and used the existing Django environment with a fresh process-only throwaway key and **in-memory SQLite configuration** for collection. It made no database connection and did not access the live signing key.

Executed from the repository root:

```bash
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -I -B \
  C:/Users/Ky/AppData/Local/Temp/ctm-task07-refresh-36sui6oz/refresh-static.py \
  C:/ProjectCloud/cloud-task-manager
```

The helper calls the standard `call_command('collectstatic', interactive=False, verbosity=1)`. **Exit 0**, actual output:

```text
3 static files copied to 'C:\ProjectCloud\cloud-task-manager\staticfiles', 127 unmodified, 363 post-processed.
```

No `--clear`, cleanup, dependency install or application source edit. Previously published hashed assets were retained and verified unchanged. The three newly collected assets match approved source bytes exactly. Result JSON is `static-refresh-result.json` in the private directory above.

| Asset | New manifest path | Bytes | SHA-256 (source = collected = fresh live browser) |
|---|---|---:|---|
| App CSS | `css/app.cfc79580bf75.css` | 32788 | `0489855683e03ffa902e91837621db5a510d9c5aba23e2f17350ed22e8b24b25` |
| Tokens CSS | `css/design-tokens.4331be124e23.css` | 3828 | `4a43179e1a7cc60d53a139889250f1241d3e7039fcdac49e6f746da300aed7fd` |
| App JS | `js/app.fde9240fd0e9.js` | 7177 | `950455b110ec5f6614a5c623bf8a43d88cdc74317022dbb08706c00dbc708729` |

New manifest SHA-256: `a1a30683cc049171e0d5fa685a3bce57181a846be45f272c326e808c10cc2fe1`.

### Same-supervisor restart — PASS

After collection and the repeated identity/ownership guard passed, wrote exactly one new supervisor control file with the Write tool:

```text
C:\Users\Ky\AppData\Local\CloudTaskManager\repair-evidence\task06b-20261105T003400Z-af01b85c\direct-20261105T011049Z-105d5f-restart-2.json
```

Content:

```json
{"reason":"User-approved Task 07 static refresh; restart exact generation 2 child through existing same-key supervisor"}
```

The running supervisor consumed its documented control condition. No manual PID kill or unrelated process stop was issued.

Read-only post-restart PowerShell inspection, **exit 0**, confirmed:

| Observation | Final value |
|---|---|
| Listener | **127.0.0.1:8000** |
| New Django child | **PID 15496** |
| New child creation | **2026-11-05T09:46:42.2596500+07:00** |
| Parent supervisor | **PID 21348, unchanged** |
| Previous child 18428 | **Absent** |
| PostgreSQL listener | **PID 18392, unchanged** on port 55432 |
| Ports 8001 / 8007 | **No listeners**, neither started |

The new `...-generation-3.json` corroborates generation **3**, same launch/supervisor ID and memory-only secret storage. The new generation log reports:

```text
RUNTIME_DATABASE_IDENTITY_PASS
pid=15496
database=cloudtask_dev_utf8_06b
user=cloudtask_app
host=127.0.0.1
port=55432
encoding=UTF8
owner=cloudtask_app
django_version=5.2.18
```

The existing entry runs Django `check` and read-only `migrate --check` before serving. No migration application/schema mutation occurred. These are the existing startup gates, not a repeated test suite.

### Fresh real-browser verification — new UI is now live

The original browser tab was reloaded at **`http://127.0.0.1:8000/dashboard/`**, using the same pre-restart session. It stayed authenticated as the same existing QA account **without login or cookie replacement**. The existing task ID **22** still appeared with Vietnamese/emoji title and description. This verifies observed session/task continuity; it is **not** an all-table data-equivalence audit.

Browser-origin no-cache GETs of the newly observed CSS/JS URLs returned **HTTP 200** and the exact new source/manifest hashes in the table above. The applied stylesheet now contains **263 top-level CSS rules** and `.task-summary`. A cache-bypassing current-page GET returned **200** with:

```text
newTaskSummary: true
newSidebarCreate: true
oldMetrics: false
oldTodayCard: false
```

**Live asset/template adoption: PASS.** This is current evidence from the real port-8000 server, not the stopped preview or an old cached DOM. The retained 8007 Login tab remains stopped/historical; the active browser tab is now the verified port-8000 dashboard.

A new **1280×720** live screenshot was captured and inspected. It visibly shows the compact summary, primary task list, circular completion affordance, descriptions and sidebar Create shortcut; old metric/Today cards are absent. Document horizontal overflow check returned false.

[Task 07 now visible on live port 8000](C:/Users/Ky/.zcode/cli/artifacts/sess_0fa4d2ed-41d3-43f9-9615-4aec9f301ae4/call_SLrF8xR89hxPhIw2QtHSdss9-tool-result-b3819741-8024-46b5-a0a5-8b8c020882cc.png)

**New visual issue, not hidden by the asset PASS:** the existing long QA username expands the sidebar profile/footer beyond the sidebar. A targeted measurement of the observed Account link returned profile `x=12`, width **299.4125px**, right **311.4125px**, while sidebar right is **232px**: approximately **79.4px** overflow into content. The screenshot corroborates this. This is a **FAIL for long-account-label containment**, not a cache problem. No CSS fix or further rebuild/restart was performed in this verification-only continuation. A narrowly scoped profile/footer `min-width`/truncation correction needs separate implementation authorization.

### Final continuation status and preservation

- **PASS:** approved static rebuild, old-output backup and old hashed-asset preservation; same-supervisor/same-key child replacement; UTF8 startup identity; original browser session continuity; live HTML/CSS/JS source equality; new UI visibly live.
- **FAIL / follow-up:** long-username sidebar profile/footer containment as measured above. Existing incomplete VI translations and earlier native-click/keyboard coverage limits remain.
- **NOT RUN:** new automated test suite (**0 additional tests**), live CRUD writes, full data-equivalence comparison, full mobile/dark/native-interaction regression, PostgreSQL restart, launcher validation. Earlier 59 passing tests were not repeated.
- Source CSS/JS and all protected launcher/test/Task 06 report hashes remained unchanged. Only this existing report was edited among repository sources; ignored `staticfiles/` changed with explicit permission. External evidence/control files are documented above.
- Final `git diff --check`: **exit 0**, LF/CRLF notices only. Git status retains the same dirty tracked/untracked file set on **main**. No stage/commit/push/reset/clean/branch change.
- No application data write was requested. Browser requests were GETs; the restart's standard identity/migration checks were read-only. No secret was printed/persisted, and no earlier session-preservation conclusion is changed by this observation.

**Next allowed step:** use the updated live app at [port 8000](http://127.0.0.1:8000/dashboard/) for review. The one approved rebuild/restart is complete; it is not ongoing restart permission. If desired, authorize the narrow long-username containment fix and its verification separately. No broader refactor, Task 06 repair or Git publication is implied.


