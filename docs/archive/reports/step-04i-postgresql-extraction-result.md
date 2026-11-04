# Task 04I recovery — extraction result

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell.

## Status: BLOCKED during extraction

The user approved extraction-only setup. The installer passed the signature and hash checks and was launched with extraction-only options into the approved isolated location. The directory became populated, but **the extractor did not report completion or an exit code** after repeated waits. An attempt to stop the extractor process returned **Access is denied**; at the last check the installer process (PID 14836) remained listed. Its final state is unknown. Do not assume extraction completed, and do not reuse, remove, or overwrite the partially populated directory until the process and its outcome are established.

No `data` directory was present at the last check. No password was requested, and no cluster initialization or PostgreSQL server startup was attempted. No PostgreSQL-named service, `postgres.exe` process, or listener on port 55432 was returned by the final checks. This is a point-in-time observation, not proof of all system state. The extracted directory includes `bin`, `doc`, `include`, `installer`, `pgAdmin 4`, `scripts`, and `share`; `bin\initdb.exe` exists but its usability and the extraction's completeness are **not verified**.

Changes: a potentially incomplete `C:\Users\Ky\AppData\Local\CloudTaskManager\postgresql16\binaries` tree, any installer-created temporary files, and this new report. No application source, Python environment, existing PostgreSQL data, Docker/cloud configuration, WebIOT, or Git history was intentionally changed. No cleanup was attempted.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes. The extraction command has **no final exit code** because it remained running at the last poll.

| Command | Exit | Result |
| --- | ---: | --- |
| `$root = Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; if (Test-Path -LiteralPath $root) { Write-Error 'Target already exists'; exit 1 }; $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 }); if ($listeners.Count -ne 0) { Write-Error 'Port 55432 is occupied'; exit 1 }; $installer = Join-Path $env:TEMP 'postgresql-16.15-1-windows-x64-ctm.exe'; $sig = Get-AuthenticodeSignature -LiteralPath $installer; if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'EnterpriseDB' -or (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash -ne 'DE926FEFAD00E313E212CD438C0F04BF033E200099AD56C012724EFCEBED79F2') { Write-Error 'Installer verification failed'; exit 1 }; Write-Output 'Target absent; port free; installer signature and hash verified'` | 0 | Target absent, port free, installer signature and hash verified. |
| `$installer = Join-Path $env:TEMP 'postgresql-16.15-1-windows-x64-ctm.exe'; $destination = Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\binaries'; $p = Start-Process -FilePath $installer -ArgumentList @('--mode','unattended','--unattendedmodeui','none','--extract-only','1','--prefix',('"' + $destination + '"'),'--install_runtimes','0') -WindowStyle Hidden -Wait -PassThru; Write-Output "Extractor exit code: $($p.ExitCode)"; exit $p.ExitCode` | **Pending** | Started extractor; no completion or exit code observed. |
| `Get-CimInstance Win32_Process \| Where-Object { $_.Name -match 'postgres\|installbuilder' } \| Select-Object Name,ProcessId,ParentProcessId` | 0 | Extractor PID 14836 listed. |
| `Stop-Process -Id 14836 -ErrorAction Stop` | 1 | Access denied; process was not confirmed stopped. |
| `Get-ChildItem -Path "$env:LOCALAPPDATA\CloudTaskManager\postgresql16\binaries\bin" -Filter 'initdb.exe' -ErrorAction SilentlyContinue \| Select-Object FullName,Length; Get-CimInstance Win32_Process -Filter "Name='postgres.exe'" \| Select-Object ProcessId; Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess` | 0 | `initdb.exe` exists; no server process or listener output. |
| `Test-Path -LiteralPath docs\reports\step-04i-postgresql-extraction-result.md; Test-Path -LiteralPath "$env:LOCALAPPDATA\CloudTaskManager\postgresql16\data"; Get-CimInstance Win32_Service -Filter "Name LIKE '%postgres%' OR DisplayName LIKE '%postgres%'" \| Select-Object Name,State; Get-CimInstance Win32_Process -Filter "Name='postgres.exe'" \| Select-Object ProcessId; Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess` | 0 | Report path and data path absent at check; no service, server process or listener output. |
| `git status --short --branch` | 0 | `main` has no commits and project entries remain untracked. |

## NOT RUN / limitations

`initdb`, password entry, SCRAM configuration, loopback pre-start verification, server version and readiness verification, `pg_isready`, project databases/roles, Django tests and migrations are **NOT RUN**. **0 Django tests executed, 0 passed, 0 failed.** The in-progress extractor and access-denied termination are the immediate blockers. The visible files are not evidence of a successful or safe extraction.

## Git status and next step

`main` has no commits. Untracked entries: `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. This report is inside already-untracked `docs/`. Nothing was staged, committed, pushed, reset or cleaned.

**Next step:** investigate the extractor process and its permissions/exit state through Windows, without overwriting or deleting the partial directory; only resume initialization after successful extraction and the required security checks can be established.
