# Hướng dẫn Docker cho thành viên nhóm — Cloud Task Manager

> **Đối tượng:** Thành viên nhận repository để đóng gói, chạy thử và bàn giao Docker cho nhóm môn Cloud Computing.  
> **Nguồn:** Nhánh main của [cloud-task-manager](https://github.com/Anonymous06-png/cloud-task-manager), đối chiếu ngày 09/11/2026 với Dockerfile, docker-compose.yml, .env.example, config/settings.py, tasks/urls.py và [Step 10C](reports/step-10c-docker-handoff-fixes.md).  
> **Trạng thái:** Đây là **hướng dẫn thực hiện**, không phải báo cáo Docker đã PASS. Step 10C đã kiểm tra cú pháp Compose và 65 bài test Django; **chưa build image hay chạy container thực tế**.

## 1. Mục tiêu và kiến trúc

Chạy cùng lúc hai dịch vụ bằng Docker Compose:

~~~text
Trình duyệt trên máy chạy Docker
   └── http://127.0.0.1:8080
         └── container app: Django + Gunicorn (cổng 8080)
               └── mạng nội bộ Docker
                     └── container db: PostgreSQL 16 (cổng nội bộ 5432)
                           └── named volume postgres_data (lưu bền vững)
~~~

Ứng dụng dùng **Django Templates + HTML/CSS/JS, Django session/auth, PostgreSQL, Gunicorn**. Không triển khai Node.js trong thư mục backend/ (đó là mã legacy). Không đổi sang SQLite để vượt qua lỗi PostgreSQL.

**Phạm vi hướng dẫn:** chạy trên máy thành viên để kiểm thử. Chạy local thành công **không đồng nghĩa** có public cloud URL hoặc đã đạt T1–T7 trên cloud.

## 2. Các file cần có — clone toàn bộ repository

| Đường dẫn | Vai trò |
| --- | --- |
| Dockerfile | Tạo image Python 3.11, cài dependencies, sao chép Django/source/locale; chạy Gunicorn |
| docker-compose.yml | Định nghĩa dịch vụ app + db, network, healthcheck, port và volume |
| .dockerignore | Ngăn secrets, cache, tài liệu và file không cần thiết đi vào build context |
| .env.example | Mẫu biến môi trường; dùng để tạo .env riêng trên mỗi máy |
| requirements.txt | Phiên bản thư viện Python |
| manage.py | Lệnh Django migrations, checks, tests |
| config/ | Django settings, WSGI, routes, middleware |
| tasks/ (bao gồm tasks/migrations/) | Model Task, auth, CRUD, schema database và tests |
| templates/ | Giao diện web |
| static/ | CSS/JS và tài nguyên tĩnh |
| locale/ | Bản dịch giao diện; Step 10C đã bổ sung COPY locale/ ./locale/ |
| README.md | Giới thiệu, hướng dẫn cơ bản và quy định dự án |

Không cần gửi file database PostgreSQL từ máy người khác: migration sẽ tạo cấu trúc bảng trên PostgreSQL container mới. **Dữ liệu tài khoản/task cũ không tự xuất hiện** khi clone GitHub.

## 3. Chuẩn bị công cụ, xác định đúng Docker Engine

Cần có Git, Docker Engine đang chạy và Docker Compose plugin. Có thể dùng **Windows + Docker Desktop**, hoặc **Linux/WSL2 với native Docker Engine**; không giả định hai Docker Engine chia sẻ container, image hoặc volume.

Trên **đúng terminal và môi trường** dự định chạy Compose, kiểm tra:

~~~powershell
git --version
docker --version
docker compose version
docker context show
docker info
~~~

- Lệnh docker info phải kết nối được Docker Engine. Có CLI nhưng không có Engine thì chưa chạy được.
- Nếu dùng native Docker trong WSL2: thực hiện clone và toàn bộ lệnh Compose trong **cùng distro/shell**; xác nhận Engine bằng docker info. Không tự dùng Docker CLI Windows rồi giả định đang thao tác trên Engine WSL.
- Nếu Docker Engine đang dùng có container của dự án khác, không dừng/xóa chúng để giải phóng tài nguyên.

## 4. Clone source và tạo .env riêng

### Windows PowerShell

~~~powershell
git clone https://github.com/Anonymous06-png/cloud-task-manager.git
cd cloud-task-manager
git branch --show-current
Copy-Item .env.example .env
notepad .env
~~~

### Linux hoặc shell WSL

~~~bash
git clone https://github.com/Anonymous06-png/cloud-task-manager.git
cd cloud-task-manager
git branch --show-current
cp .env.example .env
nano .env
~~~

Nếu đã clone trước đó, không clone chồng lên thư mục cũ; kiểm tra git status và phối hợp với nhóm trước khi pull để tránh ghi đè thay đổi đang làm.

Trong .env, điền **giá trị riêng** cho ít nhất hai biến:

~~~dotenv
SECRET_KEY=<chuoi_bi_mat_riêng>
POSTGRES_PASSWORD=<mat_khau_postgres_rieng>
DJANGO_ENV=local
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
POSTGRES_DB=taskmanager
POSTGRES_USER=taskuser
~~~

Các giá trị trong khối trên là **minh họa**, không phải secret dùng thật. Giữ dòng DATABASE_URL mẫu trong .env.example để tham khảo: khi chạy Docker Compose, cấu hình **app.environment.DATABASE_URL** trong docker-compose.yml được ghép tự động từ POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB với hostname nội bộ db; nó **ghi đè** dòng DATABASE_URL đọc từ .env của Django container. Còn chạy Django ngoài Compose sẽ cần DATABASE_URL phù hợp riêng.

Tạo chuỗi ngẫu nhiên mạnh bằng Python (nếu máy có Python):

~~~powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "import secrets; print(secrets.token_urlsafe(32))"
~~~

Dùng một chuỗi cho SECRET_KEY, chuỗi khác cho POSTGRES_PASSWORD. Nếu không có Python trên máy nhưng Docker Engine hoạt động, có thể thay lệnh python bằng docker run --rm python:3.11-slim python (cần tải image nếu chưa có). Nên dùng chuỗi URL-safe cho mật khẩu PostgreSQL để tránh ký tự cần URL-encode trong DATABASE_URL.

**Tuyệt đối không** commit/push .env, dán mật khẩu vào chat, ảnh chụp, báo cáo hoặc log. Không ghi đè .env đã tồn tại nếu không biết chủ sở hữu/cấu hình hiện tại.

## 5. Kiểm tra cấu hình và build/chạy

Trong thư mục gốc repository:

~~~powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps
~~~

- config --quiet chỉ kiểm tra cấu hình; không chứng minh container chạy.
- up --build -d build image, tạo/start db và app; Compose đợi db healthy trước khi chạy app.
- app sẽ tự chạy manage.py migrate, manage.py collectstatic rồi Gunicorn.
- Image dự kiến: cloud-task-manager:v1.0-django.
- Container dự kiến: taskmanager-app, taskmanager-db. Nếu tên bị trùng với container có sẵn, **không tự xóa container dự án khác**; báo nhóm.
- **Chỉ** cổng app được bind ra 127.0.0.1:8080. PostgreSQL 5432 ở mạng nội bộ, không mở public.

Xem trạng thái và log ngắn:

~~~powershell
docker compose ps
docker compose logs --tail=80 app
docker compose logs --tail=80 db
~~~

Kiểm tra trang web và health endpoint:

~~~powershell
curl.exe -i http://127.0.0.1:8080/health/
~~~

Với Linux/WSL, dùng curl -i thay cho curl.exe. Mong đợi HTTP 200 và JSON chứa status "ok". Sau đó mở trong trình duyệt của **máy chạy Docker**:

- Home: http://127.0.0.1:8080/
- Đăng ký: http://127.0.0.1:8080/register/
- Đăng nhập: http://127.0.0.1:8080/login/
- Sau đăng nhập: http://127.0.0.1:8080/dashboard/
- Tasks: http://127.0.0.1:8080/tasks/

Nếu máy/engine ở môi trường khác, localhost có thể **không** trỏ tới nơi bạn nghĩ; xác nhận môi trường trước khi đổi port hay firewall.

## 6. Kiểm tra database, migrations và Django

~~~powershell
docker compose exec app python manage.py check
docker compose exec app python manage.py showmigrations tasks
~~~

Kết quả migrations mong đợi có đánh dấu [X] ở 0001_initial. Có thể kiểm tra số task mà Django nhìn thấy:

~~~powershell
docker compose exec app python manage.py shell -c "from tasks.models import Task; print(Task.objects.count())"
~~~

Trên database mới, số task ban đầu có thể là 0; đây không phải lỗi. Dùng đăng ký người dùng qua web để tạo dữ liệu thử nghiệm.

Nếu muốn chạy Django tests trong **môi trường local/kiểm thử được phép**, dùng:

~~~powershell
docker compose exec app python manage.py test tasks
~~~

Lưu **số test và exit code thực tế**; không lấy kết quả 65/65 từ Step 10C để thay thế kiểm thử trong Docker. Django test runner sử dụng database kiểm thử riêng; vẫn không chạy thao tác test/destructive trên môi trường production khi chưa được nhóm duyệt.

## 7. Checklist kiểm thử bắt buộc cho thành viên Docker

| Mã | Cách thử ở môi trường local Docker | Minh chứng cần lưu |
| --- | --- | --- |
| D1 | docker compose up --build -d thành công | Lệnh, exit code, image, docker compose ps |
| D2 | GET /health/ trả HTTP 200 | HTTP status và JSON đã loại thông tin nhạy cảm |
| D3 | Đăng ký, đăng nhập, đăng xuất | Ảnh giao diện/URL, không chụp mật khẩu |
| D4 | Tạo, xem, sửa, xóa task; lọc chưa xong/đã xong | Ảnh và kết quả đúng trên PostgreSQL |
| D5 | Giao diện tiếng Việt, theme, CSS/JS không lỗi tải | Ảnh trang và request asset nếu cần |
| D6 | Gửi dữ liệu không hợp lệ, app vẫn chạy | Thông báo validation và trạng thái dịch vụ |
| D7 | Tạo task đánh dấu, **chỉ restart app**, đăng nhập lại và xác nhận task vẫn còn | Task trước/sau, log ngắn, docker compose ps |
| D8 | Kiểm tra logs app/db; lỗi thử nghiệm có dấu vết phù hợp | Lệnh, log đã che thông tin nhạy cảm |
| D9 | Một thành viên khác làm theo hướng dẫn và dựng lại được | Hệ điều hành, Docker Engine, câu lệnh và kết quả |

Riêng thử nghiệm D7:

1. Tạo tài khoản demo và task có tên dễ nhận diện (ví dụ: kiem-tra-persistence).
2. Ghi nhận task trong UI.
3. Chạy **docker compose restart app** (KHÔNG restart/xóa db hoặc volume).
4. Mở lại web, đăng nhập và kiểm tra task vẫn còn; nếu cần xác minh thêm bằng ORM ở mục 6.

**Không** chạy docker compose down -v, docker volume rm, docker system prune hoặc xóa thư mục dữ liệu PostgreSQL. Những lệnh đó có thể làm mất dữ liệu và ảnh hưởng dự án khác.

### Phân biệt với kiểm thử cloud của đề bài

D1–D9 là kiểm thử **Docker trên máy thành viên**. T1 (public URL) và T1–T7 trên môi trường cloud chỉ được đánh dấu PASS khi nhóm kiểm thử **deployment thật**; local 127.0.0.1 không đáp ứng T1. Application logs có thể cần cấu hình riêng để hiển thị đầy đủ access requests; việc xem được log container không tự chứng minh T7 đã đạt.

## 8. Xử lý lỗi thường gặp (không phá dữ liệu)

| Triệu chứng | Kiểm tra an toàn |
| --- | --- |
| Cannot connect to Docker daemon | Kiểm tra docker info, đúng Docker context/Engine, trạng thái daemon; không reset/shutdown WSL hoặc Docker bừa |
| POSTGRES_PASSWORD / SECRET_KEY is required | Kiểm tra tên biến và giá trị thực trong .env **trên máy**, không in secret ra chat hoặc chạy docker compose config không có --quiet rồi chia sẻ |
| db unhealthy hoặc app không lên | docker compose ps, docker compose logs --tail=80 db/app; xác định lỗi migration/kết nối/permission trước khi sửa |
| Lỗi mật khẩu DB sau khi đổi .env | PostgreSQL giữ tài khoản và dữ liệu trong volume cũ; sửa .env không tự đổi mật khẩu bên trong database; không xóa volume để né lỗi |
| Cổng 8080 đang bị dùng | Kiểm tra dịch vụ nào chiếm cổng; không tắt container/process lạ. Nếu cần đổi host port thì thống nhất với nhóm trước |
| CSS/JS lỗi hoặc trang trắng | Kiểm tra collectstatic, log app, HTTP status của /static/... và cache trình duyệt; không sửa backend tùy tiện |
| Một số chữ tiếng Anh ở bản VI | Step 10C ghi nhận còn chuỗi mẫu preview chưa dịch trong catalog; không nhầm với việc thiếu thư mục locale |
| Dockerfile build được nhưng web không truy cập | Build image ≠ runtime PASS; kiểm tra app health, migration, logs và đúng địa chỉ/port |

Nếu vấn đề liên quan WSL/native Docker Engine, ghi rõ distro, shell, working directory và Docker context trước khi kết luận.

## 9. Dừng dịch vụ an toàn và quy tắc bàn giao Git

~~~powershell
docker compose stop
~~~

Lệnh trên dừng container nhưng không chủ động xóa named volume. Để chạy lại: docker compose up -d.

Không commit file .env hoặc bất cứ file chứa mật khẩu, dump PostgreSQL, private key hay dữ liệu người dùng thật.

Khi thành viên làm Docker sửa code:
1. Phối hợp nhánh với nhóm; không ghi đè thay đổi UI đang làm.
2. Commit từng thay đổi nhỏ; không force-push hoặc viết lại lịch sử main.
3. Báo cáo trong docs/reports/ một file Markdown mới, ghi các lệnh đã chạy, exit code, số test PASS/FAIL thực, trạng thái Git, blocker và bước kế tiếp.
4. Với mã nguồn chưa chạy container, ghi FIXED IN SOURCE/NOT RUN, không ghi PASS.

## 10. Biểu mẫu báo cáo kết quả Docker

~~~text
Máy/OS:
Distro WSL (nếu có):
Shell và thư mục dự án:
Docker Engine/context/version:
Git branch và commit:
Build: PASS / FAIL / BLOCKED / NOT RUN; lệnh, exit code
Compose app/db: ...
Health /health/: HTTP status, evidence
Migrations: ...
Django tests trong container: số chạy / PASS / FAIL / NOT RUN
Task CRUD + auth: ...
DB persistence sau restart app: ...
VI/EN và static assets: ...
Log/monitoring: ...
Ảnh chụp/bằng chứng đã sanitize:
Thay đổi file (nếu có):
Git status:
Blocker, rủi ro, bước tiếp theo:
Đường dẫn report: docs/reports/<ten-report-moi>.md
~~~

**Lưu ý cloud:** Nếu nhóm chuyển sang VPS NAT + Cloudflare Tunnel hoặc Azure VM, cần kế hoạch riêng về TLS, hostname, ALLOWED_HOSTS, CSRF, secrets, logs/metrics, budget/cost và URL public. **Không tự mở cổng PostgreSQL hoặc tạo tài nguyên tính phí** chỉ vì hướng dẫn local này.

---

**Nguồn đối chiếu:** [README](../README.md), [Dockerfile](../Dockerfile), [docker-compose.yml](../docker-compose.yml), [.env.example](../.env.example), [Step 10C](reports/step-10c-docker-handoff-fixes.md), [Đề bài](Project-Cloud-Computing.pdf).