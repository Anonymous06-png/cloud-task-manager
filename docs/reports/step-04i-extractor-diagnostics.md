# Task 04I-D — Extractor diagnostics

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell.

## Result

**The extractor ended successfully according to its original command session.** PID 14836 was absent at the diagnostic check. Polling the original command session returned `Extractor exit code: 0` with process exit code 0. The installer log's final lines also recorded completion and exit code 0. This supersedes the earlier report's pending status. These facts establish that the extractor reported success; they do not establish binary completeness, safe PostgreSQL configuration, or readiness for use.

Because PID 14836 had already exited, its current executable identity, owner, start time, state, CPU and I/O activity could not be independently inspected; PID reuse cannot be assessed retrospectively. The previous report recorded its process name and parent PID 12364, but its executable path and command line were unavailable then. The current related-process query returned no matching parent, child, or named extractor. No claims about whether it was previously stalled or required elevation can be established from these observations. The prior stop attempt's access-denied result remains historical evidence only.

## Log and output metadata

`%TEMP%\install-postgresql.log` and `installbuilder_installer.log` each had 3,513,257 bytes and last-write time 15:21:10 local; the inspected log's ending says `Installation completed` and `Exiting with code 0`. Its timestamped lines report 16:21:10, so the differing displayed log and filesystem clock representations were not reconciled. A simple text count found 116 lines containing `error`, 0 containing `fatal`, 11 containing `extract`, 1 containing `success`, and 1 containing `completed`. Keyword counts are not classified failures; no conclusion about individual matching lines is drawn. The log tail contained host/user identifiers, which are intentionally omitted here. No sensitive command lines or credentials are reproduced.

The extraction root's filesystem metadata shows creation at 15:19:00 and last modification at 15:21:03 local; top-level directories and license files are present, including `lib` (last modified 15:21:05). This is metadata only, not an integrity or runtime verification. Two recent installer temporary directories were listed and had no immediate children returned by a metadata query. No contents were modified.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes. No full process command line or secret was requested.

| Command | Exit | Sanitized result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04i-postgresql-extraction-result.md` | 0 | Read earlier pending extraction evidence. |
| `git status --short --branch` | 0 | `main` has no commits; project entries untracked. |
| `Test-Path -LiteralPath docs\reports\step-04i-extractor-diagnostics.md` | 0 | `False`; report path free. |
| `$p = Get-CimInstance Win32_Process -Filter 'ProcessId=14836'; if (-not $p) { Write-Output 'PID 14836 absent'; exit 0 }; $p \| Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CreationDate,KernelModeTime,UserModeTime,ReadTransferCount,WriteTransferCount,ExecutionState; Invoke-CimMethod -InputObject $p -MethodName GetOwner \| Select-Object ReturnValue,Domain,User; Get-CimInstance Win32_Process \| Where-Object { $_.ParentProcessId -eq 14836 -or $_.ProcessId -eq $p.ParentProcessId } \| Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CreationDate` | 0 | PID absent; identity, owner and activity queries did not run. |
| `Get-Process -Id 14836 -ErrorAction SilentlyContinue \| Select-Object Id,ProcessName,StartTime,CPU,Responding,Path,Handles` | 1 | No process output. |
| Original command session poll (`write_stdin`, session 69325, empty input) | 0 | `Extractor exit code: 0`. |
| `Get-CimInstance Win32_Process \| Where-Object { $_.ProcessId -eq 12364 -or $_.ParentProcessId -in 14836,12364 -or $_.Name -match 'postgresql-16.15-1\|installbuilder' } \| Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CreationDate` | 0 | No matching related or named processes returned. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\binaries'; Get-Item -LiteralPath $root -ErrorAction SilentlyContinue \| Select-Object FullName,CreationTime,LastWriteTime; Get-ChildItem -LiteralPath $root -Force -ErrorAction SilentlyContinue \| Select-Object Name,Mode,LastWriteTime,Length; Get-ChildItem -Path $env:TEMP -File -ErrorAction SilentlyContinue \| Where-Object { $_.Name -match 'postgres\|install' } \| Select-Object Name,Length,LastWriteTime` | 0 | Inspected directory and installer log metadata. |
| `Get-ChildItem -Path $env:TEMP -Force -ErrorAction SilentlyContinue \| Where-Object { $_.Name -match 'postgres\|install' } \| Select-Object Name,Mode,Length,LastWriteTime \| Format-List` | 0 | Identified recent installer logs and temp directories. |
| `Get-ChildItem -LiteralPath "$env:LOCALAPPDATA\CloudTaskManager\postgresql16\binaries" -Force \| Select-Object Name,Mode,LastWriteTime,Length \| Format-Table -AutoSize` | 0 | Inspected top-level extraction metadata. |
| `$path=Join-Path $env:TEMP 'install-postgresql.log'; $lines=Get-Content -LiteralPath $path -ErrorAction Stop; Write-Output "Lines: $($lines.Count)"; foreach ($pattern in @('(?i)error','(?i)fatal','(?i)extract','(?i)success','(?i)completed')) { Write-Output "Pattern $pattern count: $(($lines \| Select-String -Pattern $pattern).Count)" }; $lines \| Select-Object -Last 12 \| ForEach-Object { if ($_ -match '(?i)password\|secret\|token\|credential\|command line\|--super') { '[redacted sensitive line]' } else { $_ } }` | 0 | 24,473 lines; sanitized ending and counts above. |
| `Get-ChildItem -LiteralPath "$env:TEMP\postgresql_installer_3e16d4f24b","$env:TEMP\postgresql_installer_9051d686b3" -Force -ErrorAction SilentlyContinue \| Select-Object Name,Mode,Length,LastWriteTime \| Format-Table -AutoSize` | 0 | No immediate children returned. |

## NOT RUN / risks

No process was terminated; no installer was restarted; no extraction output was modified, reused, moved, overwritten or deleted. `initdb`, PostgreSQL startup, service modification, database operations and Django tests are **NOT RUN**. **0 Django tests executed, 0 passed, 0 failed.** Process activity and ownership are **NOT AVAILABLE** after exit. The extraction exit status does not prove a safe server or an intact package; the log's generic completion wording should not be treated as evidence that a Windows service or cluster exists.

## Git status and next step

`main` has no commits; `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/` are untracked. This report is inside already-untracked `docs/`. No Git history was changed.

**Next step:** under a separately authorized setup task, inspect the completed extraction and confirm the isolated pre-start configuration and secure interactive password workflow before initializing or starting a cluster.
