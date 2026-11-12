# Báo cáo xác minh thiết kế database — 2026-11-09

Repository: `C:\ProjectCloud\cloud-task-manager`  
Phạm vi: chỉ đọc các tệp được yêu cầu, kiểm tra SQL/runtime read-only, tạo tài liệu; không sửa application/database/Docker/Git history.

## Files đã tạo

- `docs/database-design.md` — tài liệu thiết kế database tiếng Việt, data dictionary, ERD Mermaid, Docker persistence, hướng dẫn runtime/GUI evidence.
- `docs/reports/database-design-verification-2026-11-09.md` — báo cáo này.
- `docs/database/` — thư mục dành cho SQL evidence; hiện không có SQL file verified vì extraction bị BLOCKED.

## Nguồn đã đối chiếu

- `tasks/models.py`: `Task.user`, `title`, `description`, `status`, `due_date`, timestamps, ordering và hai indexes.
- `tasks/migrations/0001_initial.py`: `BigAutoField`, field definitions, FK tới `settings.AUTH_USER_MODEL`, CASCADE, index names.
- `config/settings.py`: PostgreSQL `DATABASE_URL`, `dj_database_url.parse`, `AUTH_USER_MODEL` mặc định và `BigAutoField`.
- `docker-compose.yml`: PostgreSQL 16 Alpine, app-to-db URL, migration startup, `postgres_data` volume.
- `docs/reports/step-10c-docker-handoff-fixes.md`: trạng thái Docker handoff và bằng chứng trước đó; không coi static compose validation là runtime DB PASS.

## Commands, exit codes và kết quả

| Command | Exit code | Status |
|---|---:|---|
| `./.venv/Scripts/python.exe manage.py sqlmigrate tasks 0001 > docs/database/tasks-0001.sql` | `1` | **BLOCKED** — Django không khởi động vì `SECRET_KEY` bắt buộc chưa có trong shell; không sinh SQL evidence |
| `docker compose ps --format '...'` | `1` | **BLOCKED** — thiếu biến bắt buộc `POSTGRES_PASSWORD` và `SECRET_KEY`; không in secret |
| `docker ps --format '...'` | `1` | **BLOCKED** — Docker daemon `dockerDesktopLinuxEngine` không khả dụng |
| kiểm tra biến môi trường không nhạy cảm | `0` | Không thấy cấu hình PostgreSQL runtime được nạp trong shell; không đọc/ghi secret |
| `pg_isready -h localhost -p 5432` | Chưa chạy | Không có executable `pg_isready` trong PATH; không coi là runtime check |

## Verification status

- **Source model ↔ migration ↔ ERD ↔ data dictionary:** **PASS** cho phạm vi nguồn đã đọc.
- **SQL extraction bằng Django migration:** **BLOCKED**, không được thay bằng SQLite hoặc SQL tự viết.
- **Actual PostgreSQL table/index comparison:** **BLOCKED**, chưa có Docker daemon/runtime credentials trong phiên.
- **Database records:** không truy cập/không thay đổi.
- **GUI evidence:** chưa có; tài liệu đã nêu các bước chụp ảnh sanitized trong pgAdmin/DBeaver.

## Exact manual follow-up

Sau khi nạp environment hiện có một cách an toàn (không đưa secrets vào tài liệu hoặc chat), chạy từ repository:

```powershell
.\.venv\Scripts\python.exe manage.py sqlmigrate tasks 0001 > docs/database/tasks-0001.sql
```

Chỉ ghi nhận SQL extraction PASS nếu exit code là `0`. Sau đó chạy các truy vấn `information_schema` và `pg_indexes` trong `docs/database-design.md` bằng một kết nối read-only để so sánh `auth_user`, `tasks_task`, constraints và indexes.

## Remaining risks / blockers

1. SQL file chưa được tạo vì cấu hình runtime bắt buộc chưa được nạp.
2. Runtime schema có thể khác migration nếu database chưa chạy migrations đầy đủ; cần introspection để xác nhận.
3. `auth_user` schema được mô tả theo Django auth chuẩn, nhưng chưa được introspect runtime trong phiên này.
4. Named volume cung cấp persistence trong Docker host, không thay thế backup/restore.

## Git status

- Branch: `main`.
- Không commit, push, reset, clean hoặc merge.
- Trạng thái ban đầu được cung cấp: working tree sạch (`## main...origin/main`).
- Hai tài liệu mới là các thay đổi được tạo trong task này; không sửa các file application/configuration.
