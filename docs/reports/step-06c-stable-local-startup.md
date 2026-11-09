# Task 06C — Stable local startup launcher changes

Date: **2026-11-05**. Repository: `C:\ProjectCloud\cloud-task-manager`.

## Status: FIXED IN SOURCE; runtime verification BLOCKED

The existing launchers were updated to select the repaired UTF8 database and provision/reuse a protected persistent local signing key. **The updated launchers were not executed. Reliable startup, key provisioning/reuse, authentication and two-launch session continuity are NOT VERIFIED.**

Verification stopped when the automatic pre-write security hook rejected the proposed external verification harness. The user had explicitly required stopping safely if verification was blocked and avoiding additional work. The hook was not bypassed and no alternative execution route was attempted after the stop.

The active Task 06B server remains untouched on port 8000. No database connection, SQL command, application HTTP request, browser action, secret provisioning, PostgreSQL start/stop or Django launch was performed by Task 06C.

## Files changed

| File | Change |
|---|---|
| `start-web.ps1` | Approved UTF8 connection; stable DPAPI key-store implementation; safe port preflight; alternate-port/no-browser/static-reuse options; database identity and Django check gates; explicit exit handling |
| `start-web.bat` | Forward arguments with `%*`, preserve PowerShell exit code, remove unconditional pause |
| `docs/reports/step-06c-stable-local-startup.md` | This new report |

No Django settings, templates, UI, dependencies, `.env`, earlier reports or existing test modifications were changed. No Git staging, commit, push, reset, clean or branch switch.

A private PowerShell process-inspection helper was created but **not executed**:

```text
C:\Users\Ky\AppData\Local\CloudTaskManager\startup-evidence\task06c-20261105T014259Z-f1bbbfd8\process-check.ps1
```

Two proposed versions of `verify-startup.py` were rejected before file write. They did not execute. The private helper is not an application dependency and was not added to the repository.

## Implemented behavior — source inspection, not runtime PASS

### Database and local configuration

The launcher now explicitly sets:

```text
DATABASE_URL=postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_dev_utf8_06b
PGPASSFILE=%LOCALAPPDATA%\CloudTaskManager\pgpass.conf
DJANGO_ENV=local
DEBUG=False
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

No database password literal is present. The existing private PGPASSFILE is reused without reading/displaying its contents; inherited `PGPASSWORD` is removed in the launcher process. The local HTTP cookie flags preserve the intended localhost behavior without disabling authentication or CSRF middleware.

The source includes an exact read-only preflight for database name, user, server address/port, UTF8 encoding and owner, followed by `manage.py check`. It does not restore data, run migrations, reset/drop databases or revive sessions.

Existing PostgreSQL startup behavior is retained but narrowed: `pg_ctl status` code 3 allows starting the existing cluster; other unexpected status codes stop startup. This path was **not exercised**. Default `collectstatic --noinput` remains; `-SkipCollectStatic` avoids changing shared static output during alternate-port verification.

### Port and batch behavior

- `-Port` defaults to 8000 and is validated in the range 1024–65535; serving is bound to `127.0.0.1`.
- An existing listener on the requested port causes a failure before PostgreSQL/key preparation. The launcher contains no command to terminate an existing listener.
- `-NoBrowser` suppresses the existing browser-opening job.
- The browser job checks that the listener descends from this launcher before opening its URL.
- The batch wrapper forwards options and returns the PowerShell exit status instead of always pausing.

Port rejection and batch exit propagation are implemented but **NOT RUN**. A later bind race is still handled by `runserver` failure; no occupied process is replaced.

### Persistent signing-key storage

Intended path:

```text
%LOCALAPPDATA%\CloudTaskManager\secrets\django-secret-key.dpapi
```

Implementation:

- Windows DPAPI `CurrentUser` encryption, with cryptographically generated 64-byte material on first creation.
- Dedicated directory/file with protected current-user-SID FullControl ACLs; existing path type, owner and ACL checked.
- Exclusive `FileMode.CreateNew`: never overwrite an existing key file. Existing ciphertext is decrypted and reused without rewriting.
- Unsafe paths/ACLs, corrupt or unreadable keys, conflicting inherited keys and an existing repository `.env` cause a safe failure, not regeneration or configuration replacement.
- An inherited key is not silently replaced during first provisioning. The previous process `SECRET_KEY` is restored on exit.
- Decrypted signing key exists only in process memory/environment; it is not printed or placed in command arguments, source or dotenv.

**No key file was created in this task.** DPAPI and ACL behavior passed syntax parsing only; they have not been runtime-tested. An existing `.env` intentionally requires a later configuration review rather than automatic import/overwrite.

## Actual verification results

| Check | Status | Exit / count |
|---|---|---|
| Read Task 06B report, launchers and relevant settings | PASS | Read-only inspection |
| Initial Git status / private-path metadata / runtime identity | PASS | 0 |
| PowerShell syntax parse before final small edits | PASS | 0 |
| Final PowerShell syntax parse | PASS | 0 |
| Final `git diff --check` | PASS | 0; existing test-file LF/CRLF notices only |
| Final Git diff stat/status | PASS | 0 |
| Protected port-8000 PID/parent/creation/owner comparison | PASS | Unchanged observations |
| Key file and `.env` absence | PASS | Both absent before/after |
| Verification harness creation | **BLOCKED** | Pre-write hook rejection, no shell exit code |
| Updated launcher execution / occupied-port rejection | **NOT RUN** | 0 launches |
| Exact database identity and encoding, live | **NOT RUN** | 0 database connections in Task 06C |
| Django system checks with new launcher configuration | **NOT RUN** | No `manage.py check` executed |
| DPAPI key creation / restricted ACL / key reuse | **NOT RUN** | Key file absent |
| Alternate-port PowerShell launch | **NOT RUN** | 0 |
| Alternate-port batch launch | **NOT RUN** | 0 |
| Authentication / Unicode persistence / CSRF | **NOT RUN** | 0 HTTP requests |
| Session continuity across two launches | **NOT RUN** | 0 |
| Database row-fingerprint preservation comparison | **NOT RUN** | No baseline/comparison executed |
| Django automated test suite | **NOT RUN** | **0 tests**; no broad suite requested |
| Reboot persistence | **NOT RUN** | No reboot |

Task 06B's successful tests are historical evidence, not Task 06C launcher-test results. No runtime FAIL result is reported because the updated runtime was never started; the present blocker is the verification pre-write gate.

## Commands and exit codes

Working directory remained the repository root. Commands used the existing `.venv`; nothing was installed.

### Read-only status and metadata — exit 0

```bash
git --no-optional-locks status --short --branch
```

PowerShell 5.1 inspection used the following operations in a `powershell.exe -NoProfile -NonInteractive -Command` invocation:

```powershell
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:LOCALAPPDATA 'CloudTaskManager'
foreach ($path in @($root, (Join-Path $root 'secrets'),
    (Join-Path $root 'secrets\django-secret-key.dpapi'),
    (Join-Path $root 'pgpass.conf'))) {
    if (Test-Path -LiteralPath $path) {
        $item = Get-Item -LiteralPath $path -Force
        [pscustomobject]@{
            Path=$path; Exists=$true; Attributes=$item.Attributes.ToString()
            IsDirectory=$item.PSIsContainer
        } | ConvertTo-Json -Compress
    } else {
        [pscustomobject]@{Path=$path; Exists=$false} | ConvertTo-Json -Compress
    }
}
[pscustomobject]@{
    InheritedSecretKeyPresent=[bool]$env:SECRET_KEY
    DotenvExists=(Test-Path -LiteralPath 'C:\ProjectCloud\cloud-task-manager\.env')
    PowerShell=$PSVersionTable.PSVersion.ToString()
} | ConvertTo-Json -Compress
foreach ($l in @(Get-NetTCPConnection -State Listen |
    Where-Object {$_.LocalPort -in @(8000,8001)})) {
    $p = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $l.OwningProcess)
    $o = Invoke-CimMethod -InputObject $p -MethodName GetOwner
    [pscustomobject]@{
        Address=$l.LocalAddress; Port=$l.LocalPort; Pid=$p.ProcessId
        ParentPid=$p.ParentProcessId; Created=$p.CreationDate.ToString('o')
        Owner=($o.Domain+'\'+$o.User); Command=$p.CommandLine
    } | ConvertTo-Json -Compress
}
```

Observed: private pgpass file exists; secret directory/key absent; inherited `SECRET_KEY` absent; root `.env` absent; PowerShell **5.1.26100.9444**. No secret-file contents or process environment contents were read.

### PowerShell parse — exit 0, twice

```powershell
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
    'C:\ProjectCloud\cloud-task-manager\start-web.ps1',
    [ref]$tokens, [ref]$errors
) | Out-Null
if ($errors.Count) {
    $errors | ForEach-Object { Write-Output $_.Message }
    exit 1
}
Write-Output 'FINAL_POWERSHELL_SYNTAX_PASS'
```

Invoked through `powershell.exe -NoProfile -NonInteractive -Command`. The earlier invocation printed `POWERSHELL_SYNTAX_PASS`; final invocation printed `FINAL_POWERSHELL_SYNTAX_PASS`.

### Unique external evidence directory — exit 0

```bash
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -I -B -c 'from pathlib import Path; from datetime import datetime,timezone; import os,uuid; p=Path(os.environ["LOCALAPPDATA"])/"CloudTaskManager"/"startup-evidence"/("task06c-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8]); p.mkdir(parents=True,exist_ok=False); print(p)'
```

This created only the private evidence directory named above, not a signing key or database object.

### Closing static checks — exit 0

```bash
git --no-optional-locks diff --check
git --no-optional-locks diff --stat
git --no-optional-locks status --short --branch
```

Final key/`.env` existence and port-8000 identity were also read using the same PowerShell metadata/TCP/CIM operations. `git diff --check` does not execute application tests or validate DPAPI.

### Commands planned but NOT RUN

```text
powershell.exe -NoProfile -NonInteractive -File C:\ProjectCloud\cloud-task-manager\start-web.ps1 -Port 8001 -NoBrowser -SkipCollectStatic
C:\ProjectCloud\cloud-task-manager\start-web.bat -Port 8001 -NoBrowser -SkipCollectStatic
```

These would use independent launcher processes and an isolated HTTP cookie jar, not the existing browser profile. They are recorded for the next explicitly authorized verification, not as executed commands.

## Blocker details and scope stop

The automatic pre-write hook rejected two drafts of a private `verify-startup.py` harness:

1. Command-injection findings at draft lines 60 and 138, where PowerShell command construction was used.
2. After moving process operations into a fixed PowerShell helper with typed arguments and list-based subprocess calls, findings at draft lines 40, 57 and 137 remained.

The second rejection was treated as a verification blocker. No rejected code was executed, no hook was disabled, no alternate shell/file-write route was used to bypass it, and no further verification architecture was started. Only read-only/static closing checks and this required report followed. The hook's findings concern the candidate verification harness, not an executed database mutation or a runtime test failure.

An initial read-only inventory attempt during Plan Mode was also rejected by the plan-mode tool gate and was not executed then. The inventory was performed only after plan approval.

## Current port-8000 status and data preservation

Before and after Task 06C:

```text
Address: 127.0.0.1:8000
PID: 18428
Parent/supervisor: 21348
Process creation: 2026-11-05T08:13:18.9140650+07:00
Owner: LAPTOP-214UR8HL\Ky
Command: C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe -I -B C:\Users\Ky\AppData\Local\CloudTaskManager\repair-evidence\task06b-20261105T003400Z-af01b85c\runtime-entry-direct.py
```

No listener on port 8001 was observed. Task 06C did not start/stop either listener or supervisor and did not interact with the ambient browser at `/tasks/22/`.

No preexisting PostgreSQL records were changed by this task; **no database operations were issued**. A fresh all-row comparison was not run, so this report does not claim independently verified database equality or exclude writes by other users/processes. No new QA accounts/tasks/sessions were created. The missing Task 06B legacy session was not revived, and the Task 06B preservation issue remains separate and unresolved.

## Risks and next allowed step

1. **Launcher code is unverified at runtime.** Syntax success is not evidence that PowerShell 5.1 DPAPI/ACL calls, database preflight, process exit propagation or first/second launch succeeds.
2. **Key has not been provisioned.** Its intended location is outside Git, but no actual stable-key reuse result exists yet. Never overwrite a preexisting key to make a test pass.
3. **Current active server has a different in-memory key.** The source change does not retroactively change port 8000's process environment or preserve compatibility with that unavailable key. Do not terminate that server as part of this task.
4. **Cookies are shared across ports on the same host.** Alternate-port verification must use an isolated HTTP cookie jar; using the open browser risks touching existing sessions.
5. **Existing `.env` is fail-closed.** A future `.env` file causes this launcher to stop for review rather than silently choose or overwrite a signing key.
6. **Reboot persistence is NOT TESTED.** No claim is made about reboot/service startup or DPAPI behavior under a different Windows account.
7. Default static collection and PostgreSQL-start paths remain untested. Alternate-port verification should reuse existing static files and the already-running cluster.

**Next allowed step:** explicitly authorize resuming only the blocked focused launcher verification after the security-hook issue is resolved. Then verify first creation/reuse of the protected key and two independent alternate-port launches, with isolated new QA fixtures and before/after preservation checks. No broad suite, UI change, dependency work, database restore/cleanup, current-server termination or Git publication is implied.

## Closing Git status

Before this new report, actual status showed only the two launcher changes plus the preexisting test modifications/reports. Expected closing status, confirmed by the report-finalization check:

```text
## main...origin/main
 M start-web.bat
 M start-web.ps1
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
?? docs/reports/step-06b-task-create-post500-root-cause.md
?? docs/reports/step-06b-utf8-repair-continuation.md
?? docs/reports/step-06b-utf8-repair-validation-20261105.md
?? docs/reports/step-06c-stable-local-startup.md
```

No staging, commit, push, reset, clean, branch switching or deployment.
