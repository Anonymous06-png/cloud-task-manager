# Task 04K — Local PostgreSQL recovery

Date: 2026-11-03. Workspace: `C:\ProjectCloud\cloud-task-manager`.

## Outcome

The original isolated PostgreSQL 16 cluster was stopped and port 55432 was free. Its stale PID 21440 was not in use. The cluster was started with its original `pg_ctl`, data directory, and existing server log. After startup, `pg_ctl status` and `pg_isready` exited 0; PID 21200 was the expected isolated `postgres.exe` with the expected data directory, and its only port 55432 listeners were `127.0.0.1` and `::1`.

The requested `docs/reports/step-04k-backend-tests-direct.md` does not exist in this workspace. Topic context lookup also failed (session not found). Consequently the previously approved 04K workflow, exact test command, test database safety constraints and completed inspections cannot be established. **Stopped without running tests** rather than guessing or risking `cloudtask_dev`. Test counts for this recovery: **0 executed, 0 passed, 0 failed**; previously completed test counts are unknown. Readiness is not proof of authentication or Django connectivity.

No cluster recreation, password reset, intentional database modification, service change, Docker, cloud, WebIOT, Git history operation or subagent launch occurred. Startup may perform ordinary PostgreSQL recovery and writes to the existing cluster and log. The cluster remains running.

## Exact commands and results

Commands below were issued through Git Bash; PowerShell ran with `-NoProfile`. The initial report reads used the file-reading tool: `docs/reports/step-04i-isolated-postgresql-runtime.md` succeeded; `docs/reports/step-04k-backend-tests-direct.md` returned file not found.

1. `ls docs/reports/*04k* docs/reports/*04i*` — exit **2**, no 04K match; 04I reports listed.

2. Initial checks — shell exit **0**, despite the explicitly reported CIM query error (the script did not make it terminating). All specified paths existed; `PG_VERSION` was `16`; `pg_ctl status` exit **3**, no server running; effective listen address `localhost` and port `55432`, both config commands exit **0**; active HBA rules were exactly loopback IPv4 and IPv6 SCRAM; no listener on port 55432; `pg_isready` exit **2**. The CIM filter was invalid and process output from this command is not evidence; corrected in command 3.

```bash
powershell.exe -NoProfile -Command '$root=Join-Path $env:LOCALAPPDATA "CloudTaskManager\postgresql16"; $data=Join-Path $root "data"; $bin=Join-Path $root "binaries\bin"; Write-Output "ROOT=$root DATA=$data BIN=$bin"; foreach($p in @($data,(Join-Path $data "PG_VERSION"),(Join-Path $bin "pg_ctl.exe"),(Join-Path $bin "postgres.exe"),(Join-Path $bin "pg_isready.exe"))){Write-Output "PATH $p exists=$(Test-Path -LiteralPath $p)"}; if(Test-Path (Join-Path $data "PG_VERSION")){Get-Content (Join-Path $data "PG_VERSION")}; & (Join-Path $bin "pg_ctl.exe") -D $data status; Write-Output "PG_CTL_EXIT=$LASTEXITCODE"; foreach($k in @("listen_addresses","port")){& (Join-Path $bin "postgres.exe") -D $data -C $k; Write-Output "CONFIG_${k}_EXIT=$LASTEXITCODE"}; Write-Output "HBA:"; Get-Content (Join-Path $data "pg_hba.conf") | Where-Object {$_ -match "^\s*[^#\s]"}; Write-Output "LISTENERS:"; Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 55432} | Format-Table LocalAddress,LocalPort,OwningProcess -AutoSize; Write-Output "POSTGRES PROCESSES:"; Get-CimInstance Win32_Process -Filter "Name=\u0027postgres.exe\u0027" | Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine | Format-List; & (Join-Path $bin "pg_isready.exe") -h 127.0.0.1 -p 55432; Write-Output "PG_ISREADY_EXIT=$LASTEXITCODE"'
```

3. Corrected process and port checks — exit **0**; no postgres processes and no TCP connections with local port 55432. Existing `postmaster.pid` named PID 21440 and the expected data directory; `postmaster.opts` named the expected executable and directory; `postgresql.auto.conf` contained only its default comments.

```bash
powershell.exe -NoProfile -Command '$ErrorActionPreference="Stop"; Write-Output "POSTGRES PROCESSES:"; Get-CimInstance Win32_Process | Where-Object {$_.Name -eq "postgres.exe"} | Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine | Format-List; Write-Output "PORT 55432 CONNECTIONS:"; Get-NetTCPConnection -ErrorAction Stop | Where-Object {$_.LocalPort -eq 55432} | Select-Object LocalAddress,LocalPort,State,OwningProcess | Format-Table -AutoSize; Write-Output "CONTROL FILES:"; $d=Join-Path $env:LOCALAPPDATA "CloudTaskManager\postgresql16\data"; foreach($f in @("postmaster.pid","postmaster.opts","postgresql.auto.conf")){ $p=Join-Path $d $f; Write-Output "$f exists=$(Test-Path $p)"; if(Test-Path $p){Get-Content $p} }; exit 0'
```

4. Start — exit **0**; stale PID 21440 not in use, status exit **3**, no listening port conflict, configuration `localhost` / `55432`; `pg_ctl` warned another server might be running because the PID file existed, then reported `server started`; start exit **0**. PostgreSQL managed its own stale PID file; it was not manually removed.

```bash
powershell.exe -NoProfile -Command '$ErrorActionPreference="Stop"; $root=Join-Path $env:LOCALAPPDATA "CloudTaskManager\postgresql16"; $d=Join-Path $root "data"; $bin=Join-Path $root "binaries\bin"; $ctl=Join-Path $bin "pg_ctl.exe"; $pidfile=Get-Content (Join-Path $d "postmaster.pid"); $oldpid=[int]$pidfile[0]; $old=Get-Process -Id $oldpid -ErrorAction SilentlyContinue; if($old){Write-Output "STALE_PID_IN_USE: $($old.Id) $($old.ProcessName)"; exit 10}; Write-Output "STALE_PID_NOT_IN_USE=$oldpid"; & $ctl -D $d status; $s=$LASTEXITCODE; Write-Output "PG_CTL_STATUS_EXIT=$s"; if($s -ne 3){exit 11}; $listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 55432}); if($listeners.Count -ne 0){Write-Output "PORT_CONFLICT"; exit 12}; & (Join-Path $bin "postgres.exe") -D $d -C listen_addresses; if($LASTEXITCODE -ne 0){exit 13}; & (Join-Path $bin "postgres.exe") -D $d -C port; if($LASTEXITCODE -ne 0){exit 14}; & $ctl -D $d -l (Join-Path $root "server.log") -w start; $s=$LASTEXITCODE; Write-Output "PG_CTL_START_EXIT=$s"; exit $s'
```

5. Verification — exit **0**. `pg_ctl status` exit **0**, PID **21200**; process executable `C:\Users\Ky\AppData\Local\CloudTaskManager\postgresql16\binaries\bin\postgres.exe`, command line specified `C:/Users/Ky/AppData/Local/CloudTaskManager/postgresql16/data`; child PostgreSQL processes had the same executable. Only `::1:55432` and `127.0.0.1:55432` listened, both owned by PID 21200; listener and identity check passed; `pg_isready` exit **0**, accepting connections.

```bash
powershell.exe -NoProfile -Command '$ErrorActionPreference="Stop"; $root=Join-Path $env:LOCALAPPDATA "CloudTaskManager\postgresql16"; $d=Join-Path $root "data"; $bin=Join-Path $root "binaries\bin"; & (Join-Path $bin "pg_ctl.exe") -D $d status; Write-Output "PG_CTL_STATUS_EXIT=$LASTEXITCODE"; $clusterPid=[int](Get-Content (Join-Path $d "postmaster.pid") | Select-Object -First 1); Write-Output "CLUSTER_PID=$clusterPid"; Get-CimInstance Win32_Process | Where-Object {$_.Name -eq "postgres.exe"} | Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine | Format-List; Write-Output "PORT LISTENERS:"; $ls=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object {$_.LocalPort -eq 55432}); $ls | Select-Object LocalAddress,LocalPort,OwningProcess | Format-Table -AutoSize; if($ls.Count -eq 0 -or @($ls | Where-Object { $_.LocalAddress -notin @("127.0.0.1","::1") -or $_.OwningProcess -ne $clusterPid }).Count -gt 0){Write-Output "LISTENER_CHECK_FAILED"; exit 20}; $p=Get-CimInstance Win32_Process -Filter "ProcessId=$clusterPid"; if($p.ExecutablePath -ne (Join-Path $bin "postgres.exe") -or $p.CommandLine -notlike "*$d*" -and $p.CommandLine -notlike "*$($d.Replace("\", "/"))*"){Write-Output "IDENTITY_CHECK_FAILED"; exit 21}; Write-Output "LISTENER_AND_IDENTITY_CHECK=PASS"; & (Join-Path $bin "pg_isready.exe") -h 127.0.0.1 -p 55432; $s=$LASTEXITCODE; Write-Output "PG_ISREADY_EXIT=$s"; exit $s'
```

6. Topic context lookup via `ReadSessionContext` with strategy `topic` and query `Task 04K previously approved workflow, exact test commands, isolation and completed inspections, and location of step-04k-backend-tests-direct report` returned `Session sess_d548fb23-bf49-4b62-a4a7-aa5684d9e57f was not found`. `ls docs/reports` exited **0** and confirmed no 04K report.

## Remaining blocker

Provide the missing 04K report or the previously approved workflow and test isolation details, including the completed inspections, to resume without repeating them. No claim is made that a prior 04K test run passed or failed.
