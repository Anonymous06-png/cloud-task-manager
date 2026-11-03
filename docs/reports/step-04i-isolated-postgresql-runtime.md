# Task 04I-E — Isolated PostgreSQL runtime

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell.

## Result

The approved isolated PostgreSQL 16.15 cluster is running without a Windows service. Its data directory is `C:\Users\Ky\AppData\Local\CloudTaskManager\postgresql16\data`; binaries are in the sibling `binaries\bin` directory, and its server log is `server.log` under the same root. `pg_ctl status` identified PID **21440** and the extracted `postgres.exe`; the actual listeners on port **55432** were `127.0.0.1` and `::1`, both owned by that PID. `pg_isready` reported `127.0.0.1:55432 - accepting connections` (exit 0). `pg_isready` is a readiness probe, not proof of successful authentication or Django connectivity.

All four extracted programs executed with exit 0 and reported PostgreSQL **16.15**: `postgres`, `initdb`, `pg_ctl`, and `pg_isready`. Together with the extraction exit 0 recorded in Task 04I-D, these checks verify the requested binaries execute, but do not constitute a full cryptographic audit of every extracted file. The running process is the verified `postgres.exe`; no authenticated SQL version query was performed.

Before first startup, `postgres -D ... -C` returned `listen_addresses=localhost`, `port=55432`, and `password_encryption=scram-sha-256`. The newly generated `pg_hba.conf` was narrowed and verified to contain exactly these two active rules:

```text
host all all 127.0.0.1/32 scram-sha-256
host all all ::1/128 scram-sha-256
```

The user entered and confirmed the bootstrap password in a separate interactive `initdb -W` window; no password was supplied in commands or conversation. `initdb` exited 0 and created PostgreSQL's built-in cluster data and administrative identity. No project database or role was created. Changes are confined to the new cluster data, its server log, and this report; no Windows service, application source, existing PostgreSQL instance, Python environment, Docker/cloud resources, or Git history was intentionally changed. SCRAM stores a password verifier in PostgreSQL's protected cluster data; no plaintext password was written to a command, file, log, or report by this workflow.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes. The temporary process window was visible for user password input.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04i-extractor-diagnostics.md, docs\reports\step-04i-postgresql-safe-local-runtime.md` | 0 | Read extraction evidence and approved isolation plan. |
| `$bin = Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\binaries\bin'; foreach ($name in @('postgres.exe','initdb.exe','pg_ctl.exe','pg_isready.exe')) { $path=Join-Path $bin $name; if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Write-Error "Missing $name"; exit 1 }; Write-Output "--- $name ---"; & $path --version; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` | 0 | Four tools each reported PostgreSQL 16.15. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; $data=Join-Path $root 'data'; if (Test-Path -LiteralPath $data) { Write-Error 'Data path exists'; exit 1 }; if (@(Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 }).Count -ne 0) { Write-Error 'Port occupied'; exit 1 }; $exe=Join-Path $root 'binaries\bin\initdb.exe'; $p=Start-Process -FilePath $exe -ArgumentList @('-D',('"'+$data+'"'),'-U','postgres','-A','scram-sha-256','-W','-c','listen_addresses=localhost','-c','port=55432') -WindowStyle Normal -PassThru -Wait; Write-Output "initdb exit code: $($p.ExitCode)"; exit $p.ExitCode` | 0 | New data path and port checked; interactive initdb exited 0. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; $data=Join-Path $root 'data'; $exe=Join-Path $root 'binaries\bin\postgres.exe'; foreach ($key in @('listen_addresses','port','password_encryption')) { Write-Output "${key}:"; & $exe -D $data -C $key; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }; Write-Output 'Active pg_hba.conf entries:'; Get-Content -LiteralPath (Join-Path $data 'pg_hba.conf') \| Where-Object { $_ -match '^\s*[^#\s]' }` | 0 | Effective values as above; initial HBA had loopback and replication/local SCRAM entries. |
| `$data=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\data'; $hba=Join-Path $data 'pg_hba.conf'; @('host all all 127.0.0.1/32 scram-sha-256','host all all ::1/128 scram-sha-256') \| Set-Content -LiteralPath $hba -Encoding ASCII; $actual=@(Get-Content -LiteralPath $hba \| Where-Object { $_ -match '^\s*[^#\s]' }); if ($actual.Count -ne 2 -or $actual[0] -ne 'host all all 127.0.0.1/32 scram-sha-256' -or $actual[1] -ne 'host all all ::1/128 scram-sha-256') { Write-Error 'HBA verification failed'; exit 1 }; $actual` | 0 | Exactly two loopback SCRAM rules verified before startup. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; $data=Join-Path $root 'data'; $ctl=Join-Path $root 'binaries\bin\pg_ctl.exe'; $log=Join-Path $root 'server.log'; if (Test-Path -LiteralPath $log) { Write-Error 'Log path exists'; exit 1 }; if (@(Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 }).Count -ne 0) { Write-Error 'Port occupied'; exit 1 }; & $ctl -D $data -l $log -w start; exit $LASTEXITCODE` | 0 | `server started`. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; $bin=Join-Path $root 'binaries\bin'; $data=Join-Path $root 'data'; & (Join-Path $bin 'pg_ctl.exe') -D $data status; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; & (Join-Path $bin 'pg_isready.exe') -h 127.0.0.1 -p 55432; exit $LASTEXITCODE` | 0 | PID 21440 running from isolated binary/data paths; accepting connections. |
| `Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess; Get-CimInstance Win32_Process -Filter "Name='postgres.exe'" \| Select-Object ProcessId,ParentProcessId,ExecutablePath` | 0 | Listeners `::1` and `127.0.0.1`, both PID 21440. |
| `git status --short --branch; Test-Path -LiteralPath docs\reports\step-04i-isolated-postgresql-runtime.md` | 0 | `main` has no commits, project entries untracked, report path was absent. |

## NOT RUN and risks

**0 Django tests executed, 0 passed, 0 failed.** Django database creation, roles, migrations, authenticated SQL, application startup, and tests were **NOT RUN**. No Windows service was installed; this is a manually started local process, and persistence across logoff or reboot is not established. PID and listeners are point-in-time evidence and may change. The existing password must be retained securely by the user; it was not captured here.

## Git status and next step

`main` has no commits; `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/` are untracked. This report is inside already-untracked `docs/`. Nothing was staged, committed, pushed, reset, or cleaned.

**Next step:** separately authorize creation of dedicated Django development/test database resources and an appropriately scoped role, using secure credentials and preserving the built-in cluster.
