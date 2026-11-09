# Task 09 — Local Development Runtime Validation

**Date:** 2026-11-05  
**Status:** PARTIALLY VERIFIED / AUTORELOAD TRANSITION BLOCKED

## Scope

This report records the runtime validation performed against the existing uncommitted Task 09 implementation. The existing port-8000 Django server was not stopped or replaced because the one-time transition had not been approved. No PostgreSQL restart, secret modification, refactoring, dependency change, or Git write was performed.

## Results summary

| Check | Result | Exit code / evidence |
|---|---|---|
| Windows PowerShell 5.1 parser | **PASS** | `parse_errors=0`, exit `0` |
| Existing port-8000 process identified | **PASS** | `manage.py runserver 127.0.0.1:8000 --noreload` |
| Existing server preserved | **PASS** | Listener remained present after launcher refusal |
| Guarded launcher refusal without approval | **PASS** | `launcher_exit=1`; no process transition |
| HTTP home page | **PASS** | HTTP `200` |
| CSS serving | **PASS** | Both referenced CSS files HTTP `200` |
| JavaScript serving | **PASS** | Referenced JS file HTTP `200` |
| PostgreSQL UTF8 runtime connection | **BLOCKED** | Not run during the safe no-transition validation |
| DPAPI signing-key continuity | **BLOCKED** | Not run during the safe no-transition validation |
| DEBUG/autoreload runtime | **BLOCKED** | Requires approved transition from `--noreload` |
| Hot refresh after temporary edit | **BLOCKED** | Requires DEBUG/autoreload transition |
| `start-web.bat` reuse after transition | **BLOCKED** | Requires DEBUG/autoreload transition |
| Existing task-data continuity | **BLOCKED** | No transition/runtime database validation performed |

## Actual commands and evidence

### 1. PowerShell parser check

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command '$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile("C:\ProjectCloud\cloud-task-manager\start-web.ps1",[ref]$t,[ref]$e)|Out-Null; Write-Output ("parse_errors="+$e.Count); if($e.Count -ne 0){exit 1}; exit 0'
```

Output:

```text
parse_errors=0
```

Result: **PASS**, exit code `0`.

### 2. Port-8000 process inspection

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000
Get-CimInstance Win32_Process -Filter ("ProcessId=" + $listener.OwningProcess)
```

The listener command line was:

```text
"C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
```

Result: **PASS**. The process was identified as the existing Django server and was not stopped or replaced.

### 3. Guarded launcher refusal

```powershell
Set-Location -LiteralPath "C:\ProjectCloud\cloud-task-manager"
& .\start-web.ps1 -NoBrowser -SkipCollectStatic
```

The guarded launcher reported:

```text
Port 8000 is occupied by the verified older supervised Django server.
Process chain: 20308:python.exe, 21348:python.exe, 16752:powershell.exe, 21296:cmd.exe
Local startup stopped: Windows PowerShell is in NonInteractive mode. Read and Prompt functionality is not available.
launcher_exit=1
```

Result: **PASS** for safe refusal. The explicit `TRANSITION` token was not supplied, so no existing process was stopped. The port-8000 listener remained present.

### 4. Home HTML response

```text
curl.exe -sS -D - --max-time 5 http://127.0.0.1:8000/ -o C:/Windows/Temp/cloudtask-home.html
```

Observed response:

```text
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
```

Result: **PASS**, curl exit code `0`, HTTP status `200`.

### 5. Referenced CSS and JavaScript responses

```text
curl.exe -sS -o NUL -w "%{http_code}" http://127.0.0.1:8000/static/css/design-tokens.4331be124e23.css
curl.exe -sS -o NUL -w "%{http_code}" http://127.0.0.1:8000/static/css/app.cfc79580bf75.css
curl.exe -sS -o NUL -w "%{http_code}" http://127.0.0.1:8000/static/js/app.fde9240fd0e9.js
```

Observed statuses:

```text
200 /static/css/design-tokens.4331be124e23.css
200 /static/css/app.cfc79580bf75.css
200 /static/js/app.fde9240fd0e9.js
```

Result: **PASS** for all three asset requests; curl exit codes were `0`.

## Checks not executed

The following checks remain **BLOCKED**, not failed, because they require the explicit one-time transition that was not approved:

- Transition from the old `--noreload` process to `DEBUG=True` autoreload.
- Health endpoint validation after transition.
- Temporary HTML/CSS edit followed by browser refresh without collectstatic or manual restart.
- `start-web.bat` reuse of the already-running autoreload server.
- PostgreSQL UTF8 connection identity validation during the guarded launcher startup.
- DPAPI signing-key continuity validation during the guarded launcher startup.
- Existing task-data continuity validation after transition.

## Remaining risks

1. The new autoreload runtime path has not been proven in the live environment because transition approval was not granted.
2. Hot-refresh behavior is unverified; the currently running server uses `--noreload`.
3. Database UTF8 and signing-key continuity were preserved by not entering the transition path, but were not revalidated in this runtime pass.
4. Existing task-data continuity remains unverified for the same reason.
5. The prior one-line Django settings check failed due to test-command quoting (`SyntaxError: unterminated string literal`, exit code `1`); this was a test harness failure before Django import, not an application failure.

## Safety record

- Existing port-8000 server: preserved.
- PostgreSQL: not restarted.
- PostgreSQL data: not modified.
- DPAPI secrets: not modified.
- Temporary application edits: none made.
- Git: no writes, commits, staging, or resets.

## Final status

**PASS** for parser validation, guarded no-transition behavior, and live HTML/CSS/JS serving.  
**BLOCKED** for the transition-dependent runtime checks listed above.  
No application **FAIL** was observed in the checks that were executed.
