# Step 05R — Dashboard sidebar collapse control

Date: 2026-11-04

Repository: `C:\ProjectCloud\cloud-task-manager`

Branch: `handoff/ui-wip-2026-11-04` (unchanged)

## Result

**Implemented; focused Django auth tests PASS (22/22), system check PASS, whitespace check PASS, `collectstatic` PASS. In-browser behavior verified numerically (DOM/geometry/ARIA/icon-state/navigation) on a temporary disposable server. Visual screenshot capture NOT possible (no visible desktop window), so no browser-QA PASS claim is made.**

Read 05S, 05N and 05M before editing. Inspected only `templates/base.html` (sidebar markup), `static/css/app.css` (sidebar/shell sections), `static/js/app.js` (toggle/mobile logic), the existing icons sprite, `settings.html` sidebar radio controls, and the pre-existing uncommitted diff. No Plan Mode, subagents, Git state changes, dependency/database/infra changes.

## Starting point

The 05N/05M uncommitted work already had exactly ONE toggle inside the sidebar header next to "Workspace" (`toggleCount: 1` confirmed in the live DOM), one working collapsed rail, working `localStorage['ctm-sidebar']` persistence and the correct ARIA label cycle. Two gaps remained against this task's requirements:

1. **Not directional:** the header toggle showed the same `#i-panel-left` icon in both states; the paired `icon-collapse`/`icon-expand` markup had been removed with the old bottom button in 05M and never re-added to the header toggle.
2. **Clipped re-entry frame:** expanding re-showed sidebar text through `display:none` mid-transition; at intermediate widths the caption/labels rendered clipped (the truncated "Your …" frame) until the 180 ms width transition settled.

Everything else (header placement, rail geometry, mobile drawer, tooltips, persistence, JS logic, Settings `data-sidebar-choice` radios) was correct and was reused unchanged.

## Changes in this task

| File | Change |
|---|---|
| `templates/base.html` | One line: replaced the single icon `<svg>` in the existing `.sidebar-top-toggle` with the paired directional icons `icon-collapse` (`#i-panel-left-close`) and `icon-expand` (`#i-panel-left`), reusing the class vocabulary the old removed bottom button had. Button attributes (ARIA, labels, `data-sidebar-toggle`) untouched. |
| `static/css/app.css` | (1) Added the directional icon swap near `.sidebar-top-toggle`: expanded shows `icon-collapse` (advertising "collapse"), collapsed shows `icon-expand`. (2) Added a `sidebar-label-in` fade keyframe applied to `.sidebar-label`, `.nav-caption`, `.nav-count`, `.profile-copy`, `.profile-chevron` (180 ms, 40 ms delay): these elements reappear through `display:none` on expand, so the CSS animation restart fades them in while the rail's existing 180 ms width transition runs, eliminating the clipped intermediate frame. No JS changes; existing transitions, tokens (`--dur-slow`), selectors and mobile rules untouched. |
| `staticfiles/` (git-ignored) | Regenerated via `manage.py collectstatic --noinput` so the manifest-served runtime picks up the new stylesheet (`css/app.css` → `app.1582f56b6d84.css`; `app.js` hash unchanged, matches source byte-for-byte). Same approach 05M used. |
| `docs/reports/step-05r-sidebar-collapse-control.md` | This report (new). |

Reduced motion remains covered by the pre-existing global `@media (prefers-reduced-motion: reduce)` block (`animation: none !important`). `config/settings.py`, `tasks/*`, `tests`, launchers and all other pre-existing uncommitted changes were not edited.

## In-browser verification (disposable environment)

Temporary server `127.0.0.1:8001` with a disposable SQLite database in the Temp folder, `DJANGO_ENV=local`, process-only environment/secret; throwaway QA user `qa-05r-verify` created, logged in through the real login form; server stopped and the temp database/script files deleted afterwards. The existing port-8000 process was not touched. No project database, settings or configuration file was modified.

Observed values (In-app browser, DOM/`getComputedStyle`/`getBoundingClientRect`):

| Check | Expanded (settled) | Collapsed (settled) |
|---|---|---|
| Sidebar / content margin | 232 px / 232 px | 76 px / 76 px |
| Toggle state | `aria-expanded=true`, label "Collapse sidebar" | `aria-expanded=false`, label "Expand sidebar" |
| Visible icon | `#i-panel-left-close` shown, `#i-panel-left` hidden | `#i-panel-left` shown, `#i-panel-left-close` hidden |
| `[data-sidebar-toggle]` count | 1 — no duplicate controls | 1 |
| Header layout | one 44 px row (mark + label + toggle at right edge, x=175) | compact stack 44+44 centered (x=16) |
| Rail items | labels visible, `scrollWidth == clientWidth` everywhere (`overflowCount: 0`) | six items 44×44 all at x=16 (neatly aligned), 0 visible labels, floating tooltip attributes intact |
| Navigation from rail | — | click Tasks → `/tasks/` 200; collapsed state persisted via `localStorage['ctm-sidebar']` |
| Console errors | 0 | 0 |

## Commands, exit codes and results

Run from the repository root with the existing `.venv` (Python 3.11.9). Secrets and `DATABASE_URL` were supplied per-command, never persisted; test/check URLs were placeholders exactly as in 05S.

| Command | Exit | Actual result |
|---|---:|---|
| `manage.py collectstatic --noinput` (check-prefix env) | **0** | `1 static file copied … 129 unmodified, 363 post-processed.` Manifest `css/app.css` → `app.1582f56b6d84.css`; collected file verified byte-equal to `static/css/app.css`; `js/app.js` unchanged (`app.432f6cb57234.js` equal to source). |
| `manage.py check` (check-prefix env) | **0** | `System check identified no issues (0 silenced).` |
| `manage.py test tasks.test_authentication -v 1` (test-prefix env) | **0** | **22 tests PASS**, 9.687 s; system check clean inside the test run; disposable test database created/destroyed by the runner. |
| `git diff --check` (initial and final) | **0** | PASS; informational LF-to-CRLF warnings only (same as before this task). |
| `git diff --stat` / `--numstat` / `git status --short` / `git branch --show-current` | 0 | Read-only; footprint of this task = +1 line in `templates/base.html`, +30/−0 lines of new CSS rules in `static/css/app.css`; branch unchanged. |
| Temporary `manage.py runserver 127.0.0.1:8001 --noreload` + In-app browser checks | N/A | Disposable server; stopped via direct process stop (background shell then exited 1 due to the kill, not a server error). First instance served stale cached templates (Django 4.1+ default cached-template loader + `--noreload`); restarting the disposable instance resolved it. Behavioral observations above are from the fresh instance. |

## NOT RUN / BLOCKED checks

- **Visual screenshot capture: NOT performed.** The in-app browser requires a visible desktop window for screenshots; none was available. Verification is numeric DOM/geometry/ARIA only — **no browser-QA PASS claim.**
- **Mid-transition visual smoothness: inspected numerically only** (state/icon/geometry flip correctly; the fade keyframe cannot be judged aesthetics without a screenshot).
- **Mobile/responsive visual QA: NOT RUN.** ≤760 px rules were left untouched (rail toggle stays `display:none`, hamburger + drawer + scrim, `inert` logic unchanged); no mobile viewport was emulated.
- **Keyboard-only walkthrough and Lighthouse a11y audit: NOT RUN** (toggle retains aria-expanded/aria-controls/aria-label; existing focus styles untouched).
- **`tasks.test_task_crud`: NOT RUN** in this task. The one assertion known to be failing (outdated `No tasks found` English text vs. the redesigned localized Dashboard) is pre-existing, unrelated to the sidebar, and documented in 05S; task CRUD scope was deliberately not touched.
- **Real port-8000 runtime restart: NOT RUN** (pre-existing process deliberately left untouched, per 05S risk #1). After this task's template/CSS edits the normal runtime still needs its eventual restart; `collectstatic` has already refreshed the manifest it will serve.
- **Template QA on dark theme/high-zoom: NOT RUN.**

## Remaining risks

1. **Stale runtime:** any long-running instance with `--noreload` keeps serving cached templates and the old manifest entry; a restart through the owning terminal remains required (05S risk unchanged).
2. **Pre-existing task-test mismatch:** `TaskCrudTests.test_dashboard_shows_empty_state_when_no_tasks` still asserts removed English copy; unrelated to this task and left as reported.
3. **Mixed-language sidebar copy** (e.g. English "Overview/Tasks" next to translated items on the Vietnamese UI) is the pre-existing i18n backlog from 05S; no translation workflow was touched.
4. **Fade timing trade-off:** the 40 ms fade delay means label text appears after the icons during rail expansion; duration is token-driven (`--dur-slow`) so it collapses to instant under reduced motion.
5. **Visual confirmation gap:** alignment/clip-free claims rest on measured geometry at settled states and 0 console errors, not on viewed pixel output.

## Git status at delivery

```text
 M config/settings.py
 M static/css/app.css
 M tasks/test_authentication.py
 M tasks/views.py
 M templates/base.html
 M templates/home.html
 M templates/registration/login.html
 ?? design-reference/
 ?? design-system/
 ?? docs/reports/step-05e-complete-ui-integration.md
 ?? docs/reports/step-05m-sidebar-toggle-home-layout.md
 ?? docs/reports/step-05n-sidebar-public-header.md
 ?? docs/reports/step-05p-workspace-login-redesign.md
 ?? docs/reports/step-05q-logout-redirect-fix.md
 ?? docs/reports/step-05s-entry-navigation-consistency.md
 ?? docs/reports/step-05r-sidebar-collapse-control.md
 ?? start-web.bat
 ?? start-web.ps1
 ?? templates/includes/workspace_preview.html
```

`git diff --check` final exit **0**. No branch switch, staging, commit, push, reset, clean or other Git state mutation. All pre-existing uncommitted work preserved (`staticfiles/` is git-ignored). `templates/base.html` and `static/css/app.css` carried pre-existing uncommitted changes from 05M/05N/05S which were retained; this task added only the line and rule counts listed above.

## Next allowed step

On explicit authorization, stop the stale port-8000 process through its owning terminal, restart via the existing launcher, and perform the visual/screenshot QA this task could not complete (expanded/collapsed/transition frames, mobile ≤760 px, dark theme, keyboard) on the real runtime. Separately authorized follow-ups remain: fix the outdated `No tasks found` assertion and the i18n backlog. No Git publication, cloud or infrastructure operation is authorized by this task.
