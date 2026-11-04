# Báo Cáo Task 02C: Sửa các vấn đề nền tảng (không dùng Docker)

**Ngày**: 2026-10-19
**Workspace**: `C:/ProjectCloud/cloud-task-manager`
**Git root**: `C:/ProjectCloud/cloud-task-manager` (nhánh `main`, 0 commit)
**Phạm vi**: Chỉ sửa các vấn đề đã xác định trong Task 02B, không audit lại toàn bộ repo.

---

## 1. Nguồn xác minh phiên bản Django và phiên bản được chọn

- Nguồn chính thức: **https://www.djangoproject.com/download/**
  Bảng "Supported Versions" ghi: `5.2 LTS | 5.2.18 | hết mainstream 2025-12-03 | hết mở rộng 2028-04`.
- Nguồn metadata: **https://pypi.org/pypi/Django/5.2.18/json**
  `requires_python = >=3.10`, classifier gồm `3.10, 3.11, 3.12, 3.13, 3.14`; không bị yank; phát hành 2026-10-06.

**Phiên bản chọn: `Django==5.2.18`** (bản vá mới nhất của dòng 5.2 LTS).

**Tương thích với Python của container**: Dockerfile dùng `python:3.11-slim`.
Django 5.2.18 hỗ trợ Python 3.10–3.14 → **tương thích với Python 3.11 của container**.
Không nâng cấp các dependency không liên quan (psycopg2-binary, dj-database-url,
gunicorn, python-decouple, whitenoise giữ nguyên).

---

## 2. Các file đã thay đổi và lý do

| File | Thay đổi | Lý do |
|------|----------|-------|
| `requirements.txt` | `Django==5.1.3` → `Django==5.2.18` (+ ghi nguồn) | 5.1.3 là dòng EOL, có nhiều CVE; 5.2 là LTS được hỗ trợ |
| `config/settings.py` | Thêm `_required_env()`; dùng `ImproperlyConfigured`; thêm `ENVIRONMENT`; thay `STATICFILES_STORAGE` bằng `STORAGES`; tách bảo mật local/production | Chặn secret rỗng; cấu hình static đúng cho 5.1+; tách HTTP local khỏi HTTPS production |
| `docker-compose.yml` | `${SECRET_KEY:?...}`, `${POSTGRES_PASSWORD:?...}`; thêm `DJANGO_ENV`, `SECURE_SSL_REDIRECT` | Biến bắt buộc thất bại rõ ràng thay vì rỗng; tách local HTTP/production HTTPS |
| `.env.example` | Bổ sung `DJANGO_ENV`, ghi chú biến bắt buộc, chú thích HTTPS | Tài liệu hoá biến bắt buộc và phân tách môi trường |
| `static/.gitkeep` | Tạo mới | Giữ thư mục `static/` trong Git để `COPY static/` build được sau khi clone |
| `tasks/tests.py` | Thêm `ConfigurationTests`, `HealthRedirectTests`, `RequiredEnvTests` | Test tập trung cho hành vi đã sửa |
| `templates/home.html` | Nhãn "Django 5.1" → "Django 5.2" | Đồng bộ phiên bản hiển thị |
| `README.md` | Viết lại theo Django; ưu tiên container; `/health/`; T4 so sánh dữ liệu trước/sau restart | Loại bỏ hướng dẫn Node.js/npm, secret, lệnh PowerShell dở dang |
| `docs/requirements.md` | Cập nhật "Django 5.2 LTS", gỡ known-issue đã sửa | Đồng bộ tài liệu sống |
| `Dockerfile`, `.dockerignore` | Không đổi (đã kiểm tra) | Dockerfile chỉ COPY `static/` (không COPY `frontend/`); `.gitkeep` làm COPY hợp lệ |

---

## 3. Kết quả từng phát hiện

| # | Phát hiện (từ 02B) | Trạng thái |
|---|--------------------|------------|
| 1 | Django 5.1.3 EOL, có CVE | **FIXED IN SOURCE** — nâng lên 5.2.18 (LTS) |
| 2 | Secret thiếu/rỗng/whitespace không bị chặn sớm | **FIXED IN SOURCE** — `_required_env()` + `:?` trong Compose (runtime chưa xác minh) |
| 3 | `SECRET_KEY` Compose rỗng âm thầm | **FIXED IN SOURCE** — Compose fail-fast, không hiển thị giá trị |
| 4 | `STATICFILES_STORAGE` đã bị loại bỏ từ Django 5.1 | **FIXED IN SOURCE** — dùng `STORAGES` (giữ `FileSystemStorage` mặc định) |
| 5 | Health check bị redirect sang TLS không tồn tại | **FIXED IN SOURCE** — `DJANGO_ENV` + `SECURE_REDIRECT_EXEMPT` cho `/health/` (runtime chưa xác minh) |
| 6 | `/health` không nhất quán giữa route/test/compose/docs | **FIXED IN SOURCE** — tất cả dùng `/health/` |
| 7 | `COPY static/` với thư mục rỗng, không được Git track | **FIXED IN SOURCE** — thêm `static/.gitkeep` |
| 8 | Python local 3.14 vs container 3.11 | **FIXED một phần** — Django 5.2.18 hỗ trợ 3.14; nhưng `psycopg2-binary==2.9.10` chưa có wheel cp314 → local vẫn có thể lỗi khi `pip install`. Dùng container để tránh |
| 9 | (`frontend/` rỗng phá build Docker) | **UNRESOLVED / không phải blocker** — Dockerfile không COPY `frontend/`; xem mục 6 |

---

## 4. Kiểm tra thực sự đã chạy (có exit code)

| # | Lệnh | Kết quả | Exit code |
|---|------|---------|-----------|
| 1 | `python -m py_compile` cho 12 file `.py` | 12/12 biên dịch OK | 0 (mỗi file) |
| 2 | `docker compose config --quiet` (KHÔNG có biến bắt buộc) | Lỗi rõ ràng: `required variable POSTGRES_PASSWORD is missing a value`, `required variable SECRET_KEY is missing a value` — không in giá trị | 1 (đúng như thiết kế fail-fast) |
| 3 | `$env:SECRET_KEY=...; $env:POSTGRES_PASSWORD=...; docker compose config --quiet` | Cấu hình hợp lệ, không có cảnh báo rỗng | 0 |
| 4 | `git check-ignore -v static/.gitkeep` | Không match (tức file KHÔNG bị ignore, sẽ được track) | 1 |
| 5 | `git status --short` | `static/` xuất hiện dạng untracked (nhờ `.gitkeep`) | 0 |
| 6 | `grep` nội dung "health" toàn repo | Route, test, compose, Dockerfile, README, template đều dùng `/health/` | 0 |
| 7 | Kiểm tra `Django==5.2.18` trong requirements; base `python:3.11-slim` | Khớp, tương thích | 0 |

**Lưu ý**: các kiểm tra trên chỉ xác nhận cú pháp, tính nhất quán cấu hình và ignore;
**KHÔNG** chứng minh ứng dụng chạy đúng ở runtime.

---

## 5. Test đã viết nhưng CHƯA chạy

Trong `tasks/tests.py` (chưa thể chạy vì chưa cài Django, chưa có Docker):

- `ConfigurationTests`
  - `test_staticfiles_storage_uses_whitenoise`
  - `test_default_file_storage_is_filesystem`
  - `test_removed_staticfiles_storage_setting_absent`
  - `test_health_route_resolves_to_health_slash`
  - `test_health_is_exempt_from_ssl_redirect`
- `HealthRedirectTests`
  - `test_health_not_redirected_when_ssl_redirect_enabled` (mong đợi 200)
  - `test_other_path_redirected_when_ssl_redirect_enabled` (mong đợi 301)
- `RequiredEnvTests`
  - `test_blank_secret_key_is_rejected`
  - `test_blank_database_url_is_rejected`
  - `test_valid_required_env_imports`

Tất cả đánh dấu **NOT RUN**. Không có tuyên bố nào rằng test đã pass.

---

## 6. Ghi chú đính chính báo cáo 02B (overstatement)

1. **02B mục 2.4** ngụ ý Dockerfile COPY cả `static/` và `frontend/`. Thực tế
   Dockerfile chỉ `COPY static/`. Vì vậy `frontend/` rỗng **không** phá build.
2. **02B mục 1.5** nêu "không pin nào hỗ trợ Python 3.14". Sau khi nâng lên
   Django 5.2.18, Django đã hỗ trợ 3.14; chỉ `psycopg2-binary==2.9.10` (không
   nâng theo yêu cầu) là thiếu wheel cp314.
3. **02B mục 2.2** mô tả sự cố redirect/health ở dạng "có thể" (conditional).
   Task 02C xác nhận đây là xung đột cấu hình thực và đã sửa ở mã nguồn.

---

## 7. Kiểm tra runtime còn lại — BLOCKED / NOT RUN

| Hạng mục | Lệnh | Trạng thái |
|----------|------|------------|
| Cài dependency local | `pip install -r requirements.txt` | NOT RUN |
| Django checks | `python manage.py check` | BLOCKED |
| Migrations | `python manage.py makemigrations --check --dry-run` | BLOCKED |
| Test | `python manage.py test` | BLOCKED |
| Build image | `docker compose build` | BLOCKED (Docker daemon) |
| Khởi động stack | `docker compose up -d` | BLOCKED |
| Health HTTP | `Invoke-WebRequest http://127.0.0.1:8080/health/` | BLOCKED |
| PostgreSQL | `docker compose exec db pg_isready ...` | BLOCKED |
| Persistence T4 | marker trước/sau `docker compose restart app` | BLOCKED |

Lý do: Docker daemon chưa chạy và không được phép cài đặt/khởi động phần mềm hệ thống.

---

## 8. Kết luận

- **Report path**: `docs/reports/step-02c-foundation-fixes.md`
- **Blocker**: Docker daemon không khả dụng → toàn bộ kiểm tra runtime bị BLOCKED;
  Django chưa được cài nên test chưa chạy (NOT RUN). Local Python 3.14 vẫn thiếu
  wheel `psycopg2-binary` (dùng container để tránh).
- **Git status**: nhánh `main`, **0 commit**, không có file nào được stage/commit.
  Các thay đổi nằm trong: `requirements.txt`, `config/settings.py`,
  `docker-compose.yml`, `.env.example`, `static/.gitkeep`, `tasks/tests.py`,
  `templates/home.html`, `README.md`, `docs/requirements.md`.
- Dừng tại đây. Không triển khai authentication/CRUD, không xoá mã legacy,
  không thao tác Azure.
