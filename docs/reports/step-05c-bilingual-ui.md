# Task 05C — Vietnamese/English UI and language settings

Date: 2026-11-03  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Django 5.2.18 serving `127.0.0.1:8000` against PostgreSQL `cloudtask_dev` (existing PGPASSFILE configuration).  
Builds on: `step-05b-browser-functional-qa.md` (19/19 PASS).

## Result: PASS — bilingual UI implemented and browser-verified

Vietnamese is the default UI language for first-time visitors; English is selectable via a nav switcher and a new Settings page; the choice persists in a cookie across navigation, login and logout. URLs, field names, stored status values, authentication, CSRF and task ownership are unchanged.

## Changed files

| File | Change |
| --- | --- |
| `config/settings.py` | `LANGUAGE_CODE = 'vi'`; `LANGUAGES = [('vi', …), ('en', …)]` (lazy names); `LOCALE_PATHS = [BASE_DIR / 'locale']`; inserted `config.middleware.default_language_middleware` before `LocaleMiddleware`. |
| `config/middleware.py` (new) | `VietnameseDefaultMiddleware`: while the visitor has made no explicit choice (no `LANGUAGE_COOKIE_NAME` cookie, no session language), rewrites `HTTP_ACCEPT_LANGUAGE` to `'vi'` so first-time visitors always get Vietnamese regardless of browser settings. Stops interfering once a choice exists. |
| `config/urls.py` | Added `path('i18n/', include('django.conf.urls.i18n'))` → Django's `set_language` view at `/i18n/setlang/` (cookie persistence). |
| `tasks/urls.py` | Added `path('settings/', views.language_settings, name='settings')`. |
| `tasks/views.py` | New `language_settings` view (public, works for anonymous users too); success messages and form-page titles wrapped in `gettext`. |
| `tasks/forms.py` | `gettext_lazy` labels for `TaskForm` (`Title`, `Description`, `Due date`, `Status`) and the signup email `help_text`. |
| `tasks/models.py` | `STATUS_CHOICES` display labels wrapped in `gettext_lazy` (stored DB values stay `'pending'`/`'completed'`). |
| `templates/base.html` | `{% load i18n %}`; `<html lang>` from `{% get_current_language %}`; all nav strings translated; **Settings** link; **compact VI/EN switcher** (one form, two submit buttons named `language`, hidden `next={{ request.get_full_path }}`, POST to `set_language`, CSRF kept). |
| `templates/home.html`, `dashboard.html`, `task_form.html`, `task_detail.html`, `task_confirm_delete.html`, `registration/login.html`, `registration/signup.html`, `registration/logged_out.html` | All user-facing strings wrapped in `{% translate %}` / `{% blocktranslate %}` (incl. `Due {{ due }}`, delete-confirmation with task title, empty states). |
| `templates/settings.html` (new) | Settings page: radio list built from `{% get_available_languages %}`/`{% get_language_info_list %}` with the current language pre-checked, POST to `set_language`. |
| `locale/vi/LC_MESSAGES/django.po` (new) | 93 hand-authored msgids/msgstrs (no xgettext on host). |
| `locale/vi/LC_MESSAGES/django.mo` (new) | Compiled binary catalog (94 entries incl. header) used at runtime. |

Not changed: `docker-compose.yml`, `Dockerfile`, `.env*`, database schema/permissions, existing URL paths, view logic, tests. No UI redesign — same layout, only strings added.

## Build tooling note (no installs)

The host has no gettext toolchain (`msgfmt`/`xgettext` absent) and no `polib`. The `.mo` was compiled by a **one-off pure-Python script kept outside the repo** (`%TEMP%\zcode-po2mo\po2mo.py`, not committed). One compiler bug was found and fixed during validation (`unicode_escape` mangled multi-byte UTF-8); after the fix, direct `gettext.GNUTranslations` loading shows clean Vietnamese (`Dashboard => Bảng điều khiển`, `Log in => Đăng nhập`, …).

## Commands and exit codes

- `python po2mo.py locale/vi/LC_MESSAGES/django.po …django.mo` → exit 0, “94 translated strings”
- gettext validation via `gettext.GNUTranslations` + Django `translation.override('vi')` → exit 0 (vi strings resolve; `en` returns originals; `LANGUAGE_CODE: vi`)
- `.venv/Scripts/python.exe manage.py check` → **exit 0** (“System check identified no issues (0 silenced).”)
- Server restarted twice (after compile fix): `taskkill /PID … /F` exit 0; `manage.py runserver 127.0.0.1:8000 --noreload` background; `/health/` → 200 after each restart
- Browser evidence via chrome-devtools (fresh isolated context for the first-visit test; DOM snapshots + in-page JS assertions); focused HTTP smoke via `curl` (exit 0)

## Browser evidence (actual results)

| Check | Result | Evidence |
| --- | --- | --- |
| First-time visitor sees Vietnamese | PASS | Fresh isolated browser context (no cookies, English-configured automation browser): `/login/` renders `Đăng nhập`, nav `Đăng nhập / Tạo tài khoản / Cài đặt`, `Chào mừng trở lại`, `<html lang="vi">`; Django's own fields render vi (`Tên đăng nhập:`, `Mật khẩu:`) |
| Compact public switcher | PASS | VI/EN buttons in nav on public and authenticated pages; clicking EN → `<html lang="en">`, `Welcome back`, nav `Log in Create account Settings` |
| Settings page | PASS | `/settings/` (public) shows radios `Tiếng Việt (vi)` / `English (en)` with current choice checked + `Apply`; switching vi→en→vi works from both the switcher and the settings page |
| Choice persists across navigation | PASS | After switching to EN: `/register/` and `/settings/` still English |
| Choice persists across login/logout | PASS | Registered/logged out/logged back in as `qa-user-c` — still English after each step |
| Registration errors (EN) | PASS | Mismatch → “The two password fields didn’t match.”; numeric/common → “This password is too common.”, “This password is entirely numeric.” |
| Registration/dashboard (EN) | PASS | `qa-user-c` registered; toast “Account created. You are now signed in.”; empty state “Start with one clear next step.” |
| Task CRUD (EN) | PASS | Create → toast “Task created.”, badge “Not Completed”, “No due date”; completed filter → “No completed tasks yet.” |
| Task CRUD (VI) | PASS | Create → toast “Đã tạo công việc.”; labels `Tiêu đề: / Mô tả: / Hạn chót: / Trạng thái:`; status options `Chưa hoàn thành / Đã xong`; dashboard badge `Chưa hoàn thành`, `Không có hạn chót` |
| Server-side error (VI) | PASS | Empty title → “Trường này là bắt buộc.” with `aria-invalid` |
| Focused English smoke (HTTP) | PASS | `curl` with `django_language=en`: home contains “Make room for the work that matters.”, “Keep the signal.”, “Service health”; `/login/` 200 |
| Vietnamese default home (HTTP) | PASS | `curl` without cookie: “Chừa không gian cho những việc thực sự quan trọng.”, “Giữ trọng tâm.”, “Tình trạng dịch vụ”; status 200 |
| `manage.py check` | PASS | exit 0 |
| `/health/` | PASS | `{"status": "ok", …}` 200 before/after restarts (endpoint untouched, JSON protocol fields intentionally untranslated) |

Test data: new disposable account `qa-user-c` (English-created task `QA Task C1 - english`, Vietnamese-created `QA Task C2 - vietnamese`) remain in `cloudtask_dev`, consistent with the disposable-QA policy from 05B. Prior accounts/tasks untouched.

## PASS/FAIL/NOT RUN summary

All items above PASS; no FAIL. NOT RUN (honestly out of scope per the wrap-up instruction):

- Full page-by-page untranslated-string sweep in both languages (spot checks all passed; the home footer line `{{ version }} · Cloud Task Manager`, the brand name, tech badges “Django 5.2”/“PostgreSQL”, and health-JSON keys are intentionally untranslated as product/protocol identifiers)
- Vietnamese coverage of **delete-confirmation** and **logged-out** pages in the browser (strings are in the catalog and translated; only create/edit/dashboard/login/register/settings/error flows were browser-exercised)
- Re-run of the full 05B 19-case QA matrix (no reason to — no business logic changed; `manage.py check` + targeted flows cover the delta)
- `makemessages`-based extraction audit (requires xgettext; absent on host)

## Outstanding issues

- `xgettext`/`msgfmt` are not installed, so future catalog updates need either the temp compiler approach or an authorized gettext installation.
- Two compiler iterations were needed for the `.mo` (header/charset + UTF-8 escaping); the committed `.po` is the source of truth — recompile after any `.po` edit.

## Git status

`git status --short` exit 0: `main`, still **no commits**; all project entries untracked as before, plus new untracked `locale/` and the modified `config/`, `tasks/`, `templates/` files listed above (still untracked — nothing staged, committed, pushed, reset, or cleaned). No unrelated files touched.

## Local handoff readiness

Ready: server running at `http://127.0.0.1:8000` (background) with the established PGPASSFILE environment; Vietnamese default verified for fresh visitors; English option verified end-to-end; language choice cookie-persistent; existing URLs/business logic intact. Next allowed step: any separately authorized task (e.g. remaining vi page spot-checks, gettext tooling installation, or roadmap features). The translation workflow: edit `locale/vi/LC_MESSAGES/django.po` → recompile `.mo` → restart the dev server (catalogs are cached per process).
