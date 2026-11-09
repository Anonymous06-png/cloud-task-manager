# Step 08c — Existing-server parent/child detection

Date: 2026-11-05

## Change

Updated only `start-web.ps1` existing-server detection. When port 8000 is listening, the launcher now checks the listener process and up to three parent-process levels for a matching `manage.py runserver` command line. This recognizes the verified Django child/parent arrangement while still requiring the expected port pattern and HTTP 200 response.

## Verification

- Windows PowerShell 5.1 parse of the actual file: **PASS**, `parse_exit=0`, zero parser errors.
- Windows CMD smoke test against the already-running server:
  - Command: `start-web.bat -NoBrowser -SkipCollectStatic`
  - Output: `Verified Cloud Task Manager is already running at http://127.0.0.1:8000/`
  - Exit code: `0`
  - Startup flow was not entered.
- No processes were restarted or stopped. No secrets were accessed. Database and runtime data were not modified.

No Git writes were performed.
