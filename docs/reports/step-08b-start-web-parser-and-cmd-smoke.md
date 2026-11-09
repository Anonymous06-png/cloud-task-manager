# Step 08b — PowerShell parser and CMD smoke check

Date: 2026-11-05

## Scope

Only the confirmed regex quoting fix in `start-web.ps1` was checked. No refactoring, Git writes, process termination, or data changes were performed by this task.

## Results

- Windows PowerShell 5.1 parser check: **PASS**
  - Actual file: `C:\ProjectCloud\cloud-task-manager\start-web.ps1`
  - Parser error count: **0**
  - Exit code: **0**
- Existing-server `start-web.bat` smoke test from Windows CMD: **BLOCKED / INCONCLUSIVE**
  - Invocation: `cd /d C:\ProjectCloud\cloud-task-manager && start-web.bat -NoBrowser -SkipCollectStatic`
  - The terminal command exceeded its 120-second limit and did not return a final BAT exit code.
  - Captured output showed the launcher proceeded through PostgreSQL/Django startup rather than returning a completed reuse result; therefore no success exit code is claimed for the existing-server path.
  - No further retries were made, per instruction. No process was intentionally stopped or restarted.

The UTF8 database configuration, DPAPI signing key, authentication configuration, and repository data were not edited. The currently running process was not intentionally touched.

No Git writes were performed.
