# Task 04J-C — Local Django website preview

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell; project `.venv` Python 3.11.9 / Django 5.2.18; isolated PostgreSQL 16.

## Result

The development server is available at **http://127.0.0.1:8000/**. At the final check its only port-8000 listener was `127.0.0.1`, owned by Python PID **16268** (child of launcher PID 21456). The launcher verified that its authenticated connection targeted `cloudtask_dev`, with current user and owner `cloudtask_app`, on `127.0.0.1:55432`, before starting `runserver` with autoreload disabled. To stop the preview, press **Ctrl+C in the visible Django server window**; closing that window also ends the preview. This does not stop the separately running PostgreSQL instance. Process IDs and listener state are point-in-time evidence.

HTTP requests from this machine returned:

| Path | Status | Result |
| --- | ---: | --- |
| `/` | 200 | HTML; title `Cloud Task Manager` |
| `/login/` | 200 | HTML; title `Login | Cloud Task Manager` |
| `/register/` | 200 | HTML; title `Register | Cloud Task Manager` |
| `/health/` | 200 | JSON reports status `ok`, service `cloud-task-manager`, version `1.1.0-auth` |
| `/dashboard/` | 302 | Redirect to login with original path in `next` |
| `/tasks/create/`, `/tasks/1/`, `/tasks/1/edit/`, `/tasks/1/delete/` | 302 each | Redirect to login with respective original path in `next`; no task existence is inferred. |

**Visual inspection: BLOCKED.** Computer-use inventory returned no browser surfaces and reported the native computer-use pipe unavailable; creating an in-app browser tab returned `Browser is not available: iab`. No screenshots were captured. HTTP and HTML titles establish server responses, not visual appearance, responsiveness, or authenticated page behavior.

The user entered the application password in a visible non-echoing prompt. The temporary non-production secret key and database URL exist only in the server process environment; no `.env` was created or modified. The non-secret launcher script remains at `%TEMP%\cloudtask-04jc-preview.py`. No users, tasks, demo records, migrations, tests, or intentional database changes were made. Server GET requests and normal PostgreSQL/server logs may produce runtime logs; no credentials or full URL were printed by this workflow. This report is the only intentional workspace addition.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04j-b-migration-verification.md, config\settings.py, config\urls.py, tasks\urls.py, manage.py` | 0 | Reviewed migration evidence, settings, URLs and management entry point. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; & (Join-Path $root 'binaries\bin\pg_ctl.exe') -D (Join-Path $root 'data') status; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; & (Join-Path $root 'binaries\bin\pg_isready.exe') -h 127.0.0.1 -p 55432; exit $LASTEXITCODE` | 0 | Isolated PID 21440 running; readiness probe accepting connections. |
| `Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -in 8000,55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess; Get-CimInstance Win32_Process -Filter "ProcessId=21440" \| Select-Object ProcessId,ExecutablePath` | 0 | No listener on 8000; PostgreSQL loopback listeners on 55432. |
| Launcher command below | 0 | Launcher PID 21456; process continues as server PID 16268. Exit 0 is launcher result, not a server exit. |
| `$paths=@('/','/login/','/register/','/health/','/dashboard/','/tasks/create/','/tasks/1/','/tasks/1/edit/','/tasks/1/delete/'); foreach ($path in $paths) { $r=Invoke-WebRequest -Uri ('http://127.0.0.1:8000'+$path) -MaximumRedirection 0 -SkipHttpErrorCheck -ErrorAction Stop; Write-Output ("{0} status={1} location={2} content-type={3}" -f $path,[int]$r.StatusCode,$r.Headers.Location,$r.Headers.'Content-Type') }` | 1 | First four paths returned 200; PowerShell treated the first 302 as maximum-redirection error, so protected-path checks were repeated with curl. |
| `$paths=@('/','/login/','/register/','/health/','/dashboard/','/tasks/create/','/tasks/1/','/tasks/1/edit/','/tasks/1/delete/'); foreach ($path in $paths) { & curl.exe --silent --show-error --output NUL --write-out "$path status=%{http_code} redirect=%{redirect_url} type=%{content_type}`n" ('http://127.0.0.1:8000'+$path); if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` | 0 | All nine statuses and redirect destinations as above. |
| `& curl.exe --silent --show-error http://127.0.0.1:8000/health/` | 0 | JSON health response as above. |
| `$urls=@('/','/login/','/register/'); foreach ($path in $urls) { $r=Invoke-WebRequest -Uri ('http://127.0.0.1:8000'+$path) -ErrorAction Stop; Write-Output ("{0}: status={1}; html={2}; title={3}" -f $path,[int]$r.StatusCode,($r.Content -match '<html'),([regex]::Match($r.Content,'<title>(.*?)</title>').Groups[1].Value)) }` | 0 | Three 200 HTML pages and titles above. |
| `Get-CimInstance Win32_Process -Filter "ProcessId=16268" \| Select-Object ProcessId,ParentProcessId,Name,ExecutablePath \| Format-List` | 0 | Listener process was Python, child of launcher PID 21456. |
| `git status --short --branch; Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 8000 } \| Select-Object LocalAddress,LocalPort,OwningProcess` | 0 | No commits, project entries untracked; listener only `127.0.0.1:8000` PID 16268. |

The launcher refused an existing script or occupied port, wrote the following non-secret script to `%TEMP%\cloudtask-04jc-preview.py`, then ran it with `.venv\Scripts\python.exe -B` in a visible window using `Start-Process -WindowStyle Normal -PassThru`:

```python
import getpass, os, sys
from urllib.parse import quote
sys.path.insert(0, os.getcwd())
try:
    password = getpass.getpass('Password for cloudtask_app (not echoed): ')
    os.environ['DATABASE_URL'] = 'postgresql://cloudtask_app:' + quote(password, safe='') + '@127.0.0.1:55432/cloudtask_dev'
    del password
    from django.core.management.utils import get_random_secret_key
    os.environ['SECRET_KEY'] = get_random_secret_key()
    os.environ['DJANGO_ENV'] = 'local'
    os.environ['DEBUG'] = 'False'
    os.environ['ALLOWED_HOSTS'] = '127.0.0.1,localhost'
    os.environ['SECURE_SSL_REDIRECT'] = 'False'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    import django
    django.setup()
    from django.db import connection
    from django.core.management import call_command
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user, pg_get_userbyid(datdba), inet_server_addr()::text, inet_server_port() FROM pg_database WHERE datname=current_database()")
        row = cursor.fetchone()
    if row != ('cloudtask_dev', 'cloudtask_app', 'cloudtask_app', '127.0.0.1/32', 55432):
        raise RuntimeError('Unexpected database target')
    print('Verified isolated database target. Starting loopback preview.', flush=True)
    call_command('runserver', '127.0.0.1:8000', use_reloader=False)
except Exception as exc:
    print('Preview blocked: ' + type(exc).__name__ + ' (details suppressed)', flush=True)
    sys.exit(1)
```

The actual PowerShell wrapper was:

```powershell
$script=Join-Path $env:TEMP 'cloudtask-04jc-preview.py'; if (Test-Path -LiteralPath $script) { Write-Error 'Preview script path exists'; exit 1 }; if (@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object { $_.LocalPort -eq 8000 }).Count -ne 0) { Write-Error 'Port 8000 occupied'; exit 1 }; $code=@'
# The Python script shown immediately above was embedded here verbatim.
'@; Set-Content -LiteralPath $script -Value $code -Encoding UTF8; $python=Join-Path (Get-Location) '.venv\Scripts\python.exe'; $p=Start-Process -FilePath $python -ArgumentList @('-B',('"'+$script+'"')) -WorkingDirectory (Get-Location) -WindowStyle Normal -PassThru; Write-Output "Preview launcher PID: $($p.Id)"; exit 0
```

The placeholder comment in this displayed wrapper stands for the exact Python body shown above; it was not present in the executed here-string.

## NOT RUN, risks and Git status

**0 automated tests executed, 0 passed, 0 failed.** Authenticated pages, creation/edit/delete flows, responsive layout, browser visual quality, and screenshots are **NOT VERIFIED**. No migrations, users, tasks, test databases, package installations, source changes, Docker/cloud actions or WebIOT actions were performed. Django's development server is a local preview and remains running only while its process and PostgreSQL remain available; its temporary signing key changes on restart.

`main` has no commits. Untracked entries: `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. No Git staging, commit, push, reset, or clean occurred.

**Next step:** inspect the public pages visually in a browser and, under separately authorized scope, arrange isolated authenticated CRUD verification without using real user data.
