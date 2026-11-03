# Task 03 — Django Authentication (Register / Login / Logout)

**Ngày**: 2026-10-22
**Workspace**: `C:/ProjectCloud/cloud-task-manager`
**Git root**: `C:/ProjectCloud/cloud-task-manager` (nhánh `main`, **0 commit**)
**Kết quả tổng thể**: **PASS (source + runtime trên PostgreSQL 16)** — không có
Docker/WSL nào bị thay đổi.

---

## 1. Phạm vi và môi trường

### Phạm vi thực hiện

Chỉ làm **authentication** (Task 03):

- Đăng ký (register) bằng `UserCreationForm` của Django.
- Đăng nhập / đăng xuất bằng `LoginView` / `LogoutView` của Django.
- Xác thực bằng **session phía server** (không JWT, không package mới).
- Form đổi trạng thái (register / login / logout) có **CSRF protection**.
- Khu vực cá nhân (`/dashboard/`) được bảo vệ server-side bằng `@login_required`.
- `/health/` vẫn public.

**Không** triển khai CRUD task (add/edit/delete/filter), không sửa Docker/WSL,
không deploy Azure, không sửa Caddy, không nâng cấp dependency, không xoá file
legacy, không đụng `.env`, không stage/commit/push Git.

### Môi trường thực thi

| Hạng mục | Giá trị |
|----------|---------|
| Hệ điều hành | Windows (PowerShell 5.1) |
| Python local | 3.14.3 (venv tạm ở `C:\Users\Ky\AppData\Local\Temp\opencode\ctm-venv`, **ngoài repo**) |
| Django | 5.2.18 (đúng version trong `requirements.txt`) |
| Database | PostgreSQL **16.15** (thật, không phải SQLite) |
| Docker Engine | **không khả dụng** (giống Task 02D) → không build image được |
| WSL | có distro `Ubuntu` nhưng không dùng, không sửa |

**Vì sao vẫn chạy được test thật?** Docker daemon không chạy, nên PostgreSQL
16.15 được cài **tạm thời ngoài repo** bằng gói `postgresql-binaries==16.15.0`
(bản PostgreSQL chính thức cho Windows), chạy trên `127.0.0.1:55432` với data
dir trong thư mục tạm. Ứng dụng **vẫn dùng PostgreSQL đúng như cấu hình**,
không có SQLite fallback, không sửa `config/settings.py` cho mục đích test.

**Lệch lệch môi trường (đã biết, không sửa repo):**

- `psycopg2-binary` trong `requirements.txt` là `2.9.10`, bản này **không có
  wheel cho cp314** → không cài được trên Python 3.14 local (cần `pg_config` +
  compiler). Venv local dùng `psycopg2-binary==2.9.13` để chạy test. Container
  chính thức dùng Python 3.11 → `2.9.10` có wheel cp311, không bị ảnh hưởng.
  → **Không sửa `requirements.txt`.**
- `SECRET_KEY` dùng cho mọi lệnh local là **giá trị giả, chỉ dùng cho kiểm
  tra cục bộ** (`local-verification-only-not-a-real-secret`). Không có secret
  thật nào bị in ra hoặc lưu vào repo.

**Dọn dẹp sau khi kiểm chứng**: PostgreSQL tạm đã được `pg_ctl stop` (exit 0),
user smoke test đã xoá, venv + data dir nằm ngoài repo trong thư mục tạm. Không
còn tiến trình `postgres` nào chạy. Repo **không** chứa file tạm, log hay
database.

---

## 2. File đã thay đổi và lý do

### 2.1 Tạo mới

| File | Mục đích |
|------|----------|
| `tasks/forms.py` | `SignUpForm(UserCreationForm)` — thêm email tuỳ chọn, kế thừa toàn bộ validate của Django (độ dài mật khẩu, độ tương tự username, mật khẩu phổ biến/số, username trùng) |
| `tasks/test_authentication.py` | 17 test tập trung cho register / login / logout / session / CSRF / trang bảo vệ / endpoint public |
| `tasks/migrations/__init__.py`, `tasks/migrations/0001_initial.py` | Migration cho model `Task` **đã có sẵn** trong repo. Bắt buộc để test chạy được trên PostgreSQL: app `tasks` không có migration thì Django chạy `run_syncdb` **trước** khi apply migration của `auth`, nên `tasks_task` (FK → `auth_user`) được tạo trước khi bảng `auth_user` tồn tại → `ProgrammingError: relation "auth_user" does not exist`. Đã xác minh lỗi này xảy ra trước khi thêm migration và biến mất sau khi thêm |
| `templates/base.html` | Layout chung: thanh điều hướng (Login/Register/Dashboard/Logout), CSS inline, hiển thị message. Không dùng `{% static %}` vì `CompressedManifestStaticFilesStorage` cần `collectstatic` (sẽ lỗi khi DEBUG=False) |
| `templates/registration/login.html` | Trang đăng nhập (`{{ form.as_p }}` + `{% csrf_token %}` + hidden `next`) |
| `templates/registration/signup.html` | Trang đăng ký |
| `templates/registration/logged_out.html` | Fallback template của `LogoutView` khi không có `LOGOUT_REDIRECT_URL` |
| `templates/dashboard.html` | Trang cá nhân, chỉ truy cập được khi đã đăng nhập |

### 2.2 Sửa

| File | Thay đổi | Lý do |
|------|----------|-------|
| `config/settings.py` | `LOGIN_REDIRECT_URL: '/' → '/dashboard/'` | Login thành công → vào thẳng khu vực cá nhân; logout vẫn về `'/'`. `LOGIN_URL='/login/'`, `LOGOUT_REDIRECT_URL='/'` giữ nguyên |
| `tasks/urls.py` | Thêm route `register/`, `login/`, `logout/`, `dashboard/`; dùng `auth_views.LoginView` và `auth_views.LogoutView` | Định tuyến auth trong một namespace `tasks:` duy nhất |
| `tasks/views.py` | Thêm `register()` (GET/POST, validate, `login()`, message) và `dashboard()` (`@login_required`); `home()` cập nhật nội dung; `health_check()` giữ nguyên bản chất JSON | Luồng auth tối thiểu, bảo vệ server-side |
| `templates/home.html` | Dùng `{% extends "base.html" %}` | Trang chủ public, dùng chung layout/nav, hiện trạng đăng nhập |
| `README.md` | Features + danh sách endpoint | Tài liệu khớp với code |
| `docs/requirements.md` | Mục "Implementation Status": chuyển "User authentication (Task 3)" sang Completed | Tài liệu sống khớp thực tế |

### 2.3 Quyết định thiết kế chính

| Quyết định | Lý do |
|------------|-------|
| `LoginView` / `LogoutView` chuẩn của Django, `redirect_authenticated_user=True` | Ít code nhất, đúng chuẩn, không viết lại auth |
| Logout là **POST** (Django 5.x `LogoutView.http_method_names = ["post","options"]`) | State-changing action có CSRF; GET `/logout/` trả 405 |
| Sau register → `login()` tự động → redirect `/dashboard/` | Trải nghiệm liền mạch, redirect nhất quán: login → `/dashboard/`, logout → `/` |
| `@login_required` (session-based), không dùng middleware tự viết | Bảo vệ server-side, redirect `?next=` đúng chuẩn Django |
| Không thêm package mới, không đụng `INSTALLED_APPS` | Ràng buộc kiến trúc |

---

## 3. Các lệnh đã chạy và exit code

Tất cả lệnh dưới đây chạy trong `C:/ProjectCloud/cloud-task-manager` với
`DJANGO_ENV=local`, `DEBUG=False`, `DATABASE_URL` trỏ tới PostgreSQL local
(giá trị không ghi trong báo cáo này).

| # | Lệnh | Kết quả | Exit code |
|---|------|---------|-----------|
| 1 | `python manage.py check` | `System check identified no issues (0 silenced).` | **0** |
| 2 | `python manage.py test --noinput -v 2` (trước khi thêm migration `tasks`) | **FAIL** — `ProgrammingError: relation "auth_user" does not exist` (xem mục 2.1) | **1** |
| 3 | `python manage.py makemigrations tasks` | `tasks\migrations\0001_initial.py + Create model Task` | **0** |
| 4 | `python manage.py test --noinput -v 2` | `Ran 31 tests ... OK` | **0** |
| 5 | `python manage.py migrate --noinput` (DB local, không phải test DB) | Apply đủ 18 migration (contenttypes, auth, admin, sessions, tasks) | **0** |
| 6 | `python manage.py test --noinput -v 1` (chạy lại lần cuối) | `Ran 31 tests in 10.408s` → `OK` | **0** |
| 7 | `python manage.py makemigrations --check --dry-run` | `No changes detected` | **0** |
| 8 | `python -m py_compile` (9 file .py: `manage.py`, `config/settings.py`, `config/urls.py`, `tasks/forms.py`, `tasks/views.py`, `tasks/urls.py`, `tasks/models.py`, `tasks/tests.py`, `tasks/test_authentication.py`, `tasks/migrations/0001_initial.py`) | Biên dịch OK | **0** |
| 9 | Smoke test HTTP thật (`runserver` + `urllib`, script tạm ngoài repo) | 12/12 kiểm tra PASS | **0** |
| 10 | `python manage.py check --deploy` (env local) | 5 warning (W004/W008/W009/W012/W016) — **đều là hệ quả của env local** (`DJANGO_ENV=local` → `SECURE_SSL_REDIRECT/SESSION_COOKIE_SECURE/CSRF_COOKIE_SECURE=False`; W009 do secret giả local) | 0 |
| 11 | Đọc settings với `DJANGO_ENV=production` | `SSL_REDIRECT True`, `SESSION_COOKIE_SECURE True`, `CSRF_COOKIE_SECURE True`, `SECURE_REDIRECT_EXEMPT ['^health/?$']`, `LOGIN_URL /login/`, `LOGIN_REDIRECT_URL /dashboard/`, `LOGOUT_REDIRECT_URL /` | **0** |
| 12 | `git status --short` | Toàn bộ file untracked, **không có gì được stage** | 0 |

### Bằng chứng rút gọn (sanitized)

```
$ python manage.py check
System check identified no issues (0 silenced).
---check exit: 0---

$ python manage.py test --noinput -v 1
Found 31 test(s).
...............................
Ran 31 tests in 10.408s

OK
---test exit: 0---

$ python manage.py makemigrations --check --dry-run
No changes detected
---makemigrations --check exit: 0---
```

Smoke test HTTP thật (server `runserver` thật, DB PostgreSQL thật):

```
PASS | GET /health/ -> 200 json without login | status=200
PASS | GET /dashboard/ (anon) -> 302 to login | status=302 location=/login/?next=/dashboard/
PASS | GET /register/ -> 200 with csrf token | status=200
PASS | POST /register/ -> 302 to /dashboard/ | status=302 location=/dashboard/
PASS | session cookie issued after register | cookies=['csrftoken', 'messages', 'sessionid']
PASS | GET /dashboard/ (authenticated) -> 200 | status=200
PASS | POST /logout/ -> 302 to / | status=302 location=/
PASS | GET /dashboard/ after logout -> 302 to login | status=302 location=/login/?next=/dashboard/
PASS | POST /register/ (duplicate) -> 200 with form error | status=200
PASS | POST /login/ (bad password) -> 200 with error | status=200
PASS | POST /login/ (valid) -> 302 to /dashboard/ | status=302 location=/dashboard/
PASS | GET /logout/ -> 405 (POST only) | status=405

TOTAL=12 PASS=12 FAIL=0
```

---

## 4. Test đã chạy / pass / fail

Tổng **31 test**, tất cả **PASS** (17 test mới của Task 03 + 14 test nền tảng
cũ của Task 02C vốn chưa từng chạy được).

### 4.1 Test mới — `tasks/test_authentication.py`

| Nhóm | Test | Kết quả |
|------|------|---------|
| Registration | `test_register_page_is_public` | PASS |
| Registration | `test_registration_success_creates_user_and_starts_session` | PASS |
| Registration | `test_duplicate_registration_shows_form_error` | PASS |
| Registration | `test_registration_rejects_password_mismatch` | PASS |
| Registration | `test_registration_rejects_weak_password` | PASS |
| Login | `test_login_page_is_public` | PASS |
| Login | `test_login_success_creates_session` | PASS |
| Login | `test_login_failure_shows_error_and_no_session` | PASS |
| Login | `test_login_failure_for_unknown_user` | PASS |
| Logout | `test_logout_clears_session` | PASS |
| Logout | `test_logout_requires_post` (GET → 405) | PASS |
| CSRF | `test_registration_post_without_csrf_token_is_rejected` (403) | PASS |
| CSRF | `test_login_post_without_csrf_token_is_rejected` (403) | PASS |
| Protected | `test_anonymous_user_is_redirected_to_login` | PASS |
| Protected | `test_authenticated_user_can_access_dashboard` | PASS |
| Public | `test_health_is_public` | PASS |
| Public | `test_home_is_public` | PASS |

Bao phủ đúng các yêu cầu bắt buộc: registration success, invalid/duplicate
registration, login success, login failure, logout, unauthenticated bị redirect
khỏi trang cá nhân, authenticated truy cập được, `/health/` còn public.

### 4.2 Test nền tảng cũ (`tasks/tests.py`) — lần đầu chạy được

`FoundationSmokeTests` (4), `ConfigurationTests` (5), `HealthRedirectTests` (2),
`RequiredEnvTests` (3) → **14/14 PASS**.

---

## 5. Check / test **BLOCKED / NOT RUN**

| Hạng mục | Lệnh | Trạng thái | Lý do |
|----------|------|------------|-------|
| Build Docker image | `docker compose build` | **BLOCKED** | Docker Engine không chạy (`npipe:////./pipe/dockerDesktopLinuxEngine` không tồn tại). Không sửa Docker/WSL theo ràng buộc task |
| Chạy stack Compose | `docker compose up -d` | **BLOCKED** | Docker Engine không khả dụng |
| Test trong container (Python 3.11 + psycopg2 2.9.10) | `docker compose exec app python manage.py test` | **NOT RUN** | Phụ thuộc Docker Engine |
| `collectstatic` + kiểm tra static trong container | `docker compose exec app python manage.py collectstatic` | **NOT RUN** | Phụ thuộc Docker Engine |
| Kiểm tra runtime với `psycopg2-binary==2.9.10` (đúng pin) | — | **NOT RUN** | Bản này không có wheel cp314; cần build từ source (thiếu `pg_config`/compiler). Không nâng cấp dependency theo ràng buộc |
| `check --deploy` ở chế độ production | `DJANGO_ENV=production python manage.py check --deploy` | **PARTIAL** | Đã đọc được giá trị setting production (mục 3 #11); warning HSTS/W009 còn lại là việc của bước deploy |
| Gunicorn + Caddy + Azure | — | **NOT RUN** | Ngoài phạm vi Task 03 (không deploy) |

---

## 6. Rủi ro còn lại

1. **Docker chưa được xác minh**: image chưa build được trong task này. Logic
   auth không phụ thuộc Docker, nhưng cần chạy lại `docker compose up --build`
   + `manage.py test` trong container khi Docker khởi động được.
2. **`psycopg2-binary==2.9.10` chưa được chạy trên host**: đã xác minh trên
   `2.9.13` (Python 3.14). Cần chạy lại trong container Python 3.11.
3. **Chưa có rate limit / lockout** cho login: brute-force vào `/login/` chưa bị
   chặn. Chưa thuộc yêu cầu Task 03 nhưng nên cân nhắc ở bước deploy.
4. **Chưa có password reset / change password / email verification**: ngoài
   phạm vi Task 03.
5. **Migration `tasks.0001_initial` mới được thêm**: đây là migration cho model
   đã tồn tại, không phải CRUD. Cần đảm bảo `manage.py migrate` chạy trước khi
   dùng app (Compose đã có sẵn bước `migrate`).
6. **Session cookie**: `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` chỉ bật khi
   `DJANGO_ENV=production`; nếu ai đó deploy production mà quên đặt biến này
   thì cookie sẽ không có cờ `Secure`.
7. **CSRF token xoay vòng sau login**: điều này là hành vi chuẩn của Django
   (`rotate_token`), không phải lỗi; client phải lấy token mới từ form login.
8. **Chưa có kiểm thử trình duyệt thực**: mọi kiểm chứng là HTTP thật qua
   `urllib` (12/12 PASS), chưa kiểm thử tay trên trình duyệt.

---

## 7. Git status

```
$ git status -sb
## No commits yet on main
?? .dockerignore
?? .env.example
?? .gitignore
?? CLAUDE.md
?? Dockerfile
?? README.md
?? backend/
?? config/
?? docker-compose.yml
?? docs/
?? manage.py
?? requirements.txt
?? static/
?? tasks/
?? templates/
```

- Nhánh `main`, **0 commit**, **không có file nào được stage/commit/push**.
- `.gitignore` đã loại `__pycache__/` (`git check-ignore -v tasks/__pycache__`
  → khớp `.gitignore:2:__pycache__/`).
- Không xoá file legacy/archive, không tạo `.env`, không in secret.

---

## 8. Bước tiếp theo được phép

**Bước tiếp theo được phép: Task 04 — CRUD task** (add / view / update / delete
/ filter theo trạng thái, dùng model `Task` đã có + migration `0001_initial`),
theo sau **Task 05 — hoàn thiện template giao diện**.

Trước khi bắt đầu Task 04 nên (nếu Docker khởi động được): chạy lại
`docker compose up --build -d` + `docker compose exec app python manage.py test`
để xác minh cùng bộ test trên **đúng** image và **đúng** dependency pin.

Không được triển khai CRUD trong task này — task này dừng ở authentication.

---

## 9. Đường dẫn báo cáo

`docs/reports/step-03-authentication.md`
