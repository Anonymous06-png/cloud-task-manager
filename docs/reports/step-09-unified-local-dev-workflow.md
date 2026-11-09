# Task 09 — Unified Local Development Workflow

Date: 2026-11-05

## Scope

Verification continued from the existing uncommitted implementation. Only `start-web.ps1` and `config/settings.py` were inspected. No unrelated files were changed, no Git operations were performed, and the existing listener on port 8000 was not stopped or replaced.

## Implementation assessment

- `start-web.ps1`: **PASS — implementation is syntactically valid and preserves the safe transition gate.** It detects the existing supervised Django server, requires the literal `TRANSITION` approval before stopping that verified process chain, refuses unverified occupants, configures `DEBUG=True`, and starts Django with autoreload when a transition is explicitly approved.
- `config/settings.py`: **PASS — confirmed intended behavior.** `DEBUG=True` selects Django `StaticFilesStorage` for local development; non-debug operation keeps WhiteNoise compressed manifest storage.
- No confirmed code defect was found, so no implementation fix was made.

## Verification commands and results

### 1. Windows PowerShell 5.1 parser

Command:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command '$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile("C:\ProjectCloud\cloud-task-manager\start-web.ps1",[ref]$t,[ref]$e)|Out-Null; Write-Output ("parse_errors="+$e.Count); if($e.Count -ne 0){exit 1}; exit 0'
```

Result: `parse_errors=0`; exit code `0` — **PASS**.

A preceding diagnostic command printed `errors=0`. Its first `parse_exit=1` result was a check-expression bug in the test command, not a PowerShell parser error.

### 2. Existing port ownership / preservation

Command inspected the listener and process command line:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000
Get-CimInstance Win32_Process -Filter ("ProcessId=" + $listener.OwningProcess)
```

Result: port 8000 is held by:

```text
"C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
```

The process was not stopped or replaced — **PASS / preserved**.

### 3. Safe launcher refusal path

Command:

```powershell
Set-Location -LiteralPath "C:\ProjectCloud\cloud-task-manager"
& .\start-web.ps1 -NoBrowser -SkipCollectStatic
```

The launcher identified the verified older supervised server and requested the explicit `TRANSITION` token. Because the PowerShell session was non-interactive, it stopped with:

```text
Port 8000 is occupied by the verified older supervised Django server.
Process chain: 20308:python.exe, 21348:python.exe, 16752:powershell.exe, 21296:cmd.exe
Local startup stopped: Windows PowerShell is in NonInteractive mode. Read and Prompt functionality is not available.
launcher_exit=1
```

Result: **PASS — safe stop / no transition occurred**. The process remained listening afterward.

A prior Git Bash invocation attempted to pipe `NO` into `powershell -File` using a Windows path. Git Bash removed the backslashes from the `-File` argument, producing an invalid path and exit code `127`; this was a test harness quoting failure, not a launcher failure. The launcher was then run correctly from PowerShell.

### 4. Fresh HTML and static asset serving

Command:

```text
curl.exe -sS -D - --max-time 5 http://127.0.0.1:8000/ -o C:/Windows/Temp/cloudtask-home.html
curl.exe -sS -o NUL -w "%{http_code}" http://127.0.0.1:8000/static/css/design-tokens.4331be124e23.css
curl.exe -sS -o NUL -w "%{http_code}" http://127.0.0.1:8000/static/css/app.cfc79580bf75.css
curl.exe -sS -o NUL -w "%{http_code}" http://127.0.0.1:8000/static/js/app.fde9240fd0e9.js
```

Results:

- Home HTML: HTTP `200`, `Content-Type: text/html; charset=utf-8` — **PASS**.
- `design-tokens.4331be124e23.css`: HTTP `200` — **PASS**.
- `app.cfc79580bf75.css`: HTTP `200` — **PASS**.
- `app.fde9240fd0e9.js`: HTTP `200` — **PASS**.

The response was served by the existing `--noreload` process, so this verifies fresh HTML/CSS/JS availability but does not prove the new autoreload process behavior.

### 5. Django settings isolated check

Attempted a one-line PowerShell/Python environment check. It failed due to nested quoting in the test command, before Django import:

```text
SyntaxError: unterminated string literal
```

Exit code: `1` — **BLOCKED / test-command failure**, not an application failure. No database connection, file write, or process change occurred. The static backend selection is supported by direct inspection of `config/settings.py` and the existing live asset responses.

## Database, secrets, and data safety

- PostgreSQL UTF8 configuration was not changed.
- DPAPI-protected signing-key storage was not changed or read by the verification commands.
- Existing data and the current port-8000 server were preserved.
- No dependency installation, refactoring, broad audit, or Git write was performed.

## Remaining risks / blockers

1. **Autoreload runtime verification is BLOCKED** while port 8000 is occupied by the existing `--noreload` server. Proving the new autoreload path requires an explicit transition approval because the launcher intentionally stops the verified process chain.
2. A fresh isolated debug/static backend check should be rerun with a file-based PowerShell/Python command if required; the only failure was command quoting.
3. The launcher’s transition path remains intentionally untested to avoid stopping the user’s existing server without explicit approval.

## Final status

**PARTIALLY VERIFIED / SAFE TO STOP.** Parsing, process-preserving refusal behavior, and live HTML/CSS/JS serving passed. Autoreload transition verification remains blocked by the explicit no-stop requirement. No confirmed implementation issue required fixing.

No Git writes were performed.

## Security constraint note

This task did not add or modify server-side outbound URL request code. The repository’s existing request paths remain subject to the project constraint that only `http`/`https` URLs are accepted and localhost, loopback, private, and reserved hosts are rejected before requests.
