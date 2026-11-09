# Step 08 — `start-web.bat` double-click fix

Date: 2026-11-05

## Change

Minimal launcher-only change:

- `start-web.ps1` now checks port 8000 before the existing database, signing-key, and Django startup flow.
- If the listener is the verified local Django `manage.py runserver` process and `http://127.0.0.1:8000/` returns HTTP 200, it opens/reuses that URL and exits successfully without starting or stopping a process.
- If the port is occupied by an unverified process or does not serve the expected response, startup stops with a clear error; no process is killed or restarted.
- `start-web.bat` preserves `%*` argument forwarding and the PowerShell exit code, and pauses on non-zero exit so a double-click error remains visible.

## Verification

- PowerShell parser check: **PASS** (`start-web.ps1` parsed successfully).
- Existing active-server safety: launcher logic only reads the listener owner and performs an HTTP GET; it contains no process-stop/restart operation.
- Occupied-port path: the existing server remains untouched; the verified-server branch is designed to return success and open the URL. The shell harness could not execute the Windows path reliably from Git Bash (`-File` path conversion caused the host PowerShell invocation to rewrite the path), so no claim is made that a full browser-opening check ran in this environment.
- Free-port behavior: not exercised because doing so would start a Django process and the request explicitly requires preserving the active server.

No Git writes were performed.

## Files changed

- `start-web.bat`
- `start-web.ps1`
- This report

The UTF8 database, DPAPI signing key, authentication configuration, and running Django process were not modified.