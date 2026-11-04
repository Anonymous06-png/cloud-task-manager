# Task 04J-A2 — PostgreSQL application authentication diagnostics

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell.

## Findings

The isolated PostgreSQL instance was running under the approved binary and data paths at `127.0.0.1:55432`; `pg_ctl` reported PID 21440 and `pg_isready` reported accepting connections. The two listeners were `127.0.0.1` and `::1`, both owned by PID 21440. These are point-in-time observations.

An authenticated read-only superuser query succeeded (psql exit 0):

- `cloudtask_app` exists, `rolcanlogin=true`, and `rolsuper`, `rolcreatedb`, `rolcreaterole`, `rolreplication`, and `rolbypassrls` are false.
- A SCRAM-SHA-256 password verifier is present. The query returned only a boolean, never the verifier.
- `cloudtask_dev` exists and is owned by `cloudtask_app`.
- The server reports version **16.15**, `listen_addresses=localhost`, and port `55432`.
- `pg_hba_file_rules` reported two parsed host rules for all databases/users: `127.0.0.1/32` and `::1/128`, both `scram-sha-256`, with no parse errors. This view describes the file's parsed rules; no configuration change or reload occurred.

The single controlled application-role psql attempt exited **2**. A sanitized server-log check found `password authentication failed` for `cloudtask_app`. The precise cause is **unresolved**: the evidence does not establish what was entered in the application prompt or why the challenge failed. The process ended before a separate user-input request could be issued, so interactive entry for that attempt was not independently confirmed. The presence of a verifier does not verify a particular password. No retry, password reset, or configuration change was made.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes. The diagnostic and output files in `%TEMP%` contain only non-secret SQL and sanitized query results; no password, verifier or connection string was written to them. PostgreSQL's server log may have received normal authentication events.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04j-a-development-database.md, docs\reports\step-04i-isolated-postgresql-runtime.md` | 0 | Read prior failure and cluster setup. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; & (Join-Path $root 'binaries\bin\pg_ctl.exe') -D (Join-Path $root 'data') status; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; & (Join-Path $root 'binaries\bin\pg_isready.exe') -h 127.0.0.1 -p 55432; exit $LASTEXITCODE` | 0 | PID 21440 running from isolated paths; accepting connections. |
| `Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess; Get-CimInstance Win32_Process -Filter "ProcessId=21440" \| Select-Object ProcessId,ExecutablePath` | 0 | Two loopback listeners, PID 21440. |
| Superuser diagnostics command below | 0 | Sanitized query results as above. |
| Application test command below | **2** | One attempt failed before authenticated SQL ran. |
| `$log=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\server.log'; $lines=Get-Content -LiteralPath $log -Tail 20; foreach ($line in $lines) { if ($line -match 'password authentication failed for user "cloudtask_app"') { Write-Output 'cloudtask_app: password authentication failed' } elseif ($line -match 'no password supplied') { Write-Output 'no password supplied' } elseif ($line -match 'no pg_hba.conf entry') { Write-Output 'HBA entry not found' } }` | 0 | Two matching password authentication failure entries were returned; the tail can include the prior task's event. No credentials printed. |
| `git status --short --branch; Test-Path -LiteralPath docs\reports\step-04j-a2-auth-diagnostics.md` | 0 | No commits on `main`; report path was absent. |

Superuser diagnostic command:

```powershell
$query=Join-Path $env:TEMP 'cloudtask-04ja2-diagnostics.sql'; $output=Join-Path $env:TEMP 'cloudtask-04ja2-diagnostics.txt'; if ((Test-Path -LiteralPath $query) -or (Test-Path -LiteralPath $output)) { Write-Error 'Diagnostic file path exists'; exit 1 }; $sql=@'
\set ON_ERROR_STOP on
SET default_transaction_read_only = on;
SELECT rolname, rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls, (rolpassword IS NOT NULL AND left(rolpassword,13) = 'SCRAM-SHA-256') AS scram_verifier_present FROM pg_authid WHERE rolname='cloudtask_app';
SELECT datname, pg_get_userbyid(datdba) AS owner FROM pg_database WHERE datname='cloudtask_dev';
SELECT current_setting('server_version') AS server_version, current_setting('listen_addresses') AS listen_addresses, current_setting('port') AS port;
SELECT rule_number, type, database, user_name, address, netmask, auth_method, error FROM pg_hba_file_rules ORDER BY rule_number;
'@; Set-Content -LiteralPath $query -Value $sql -Encoding ASCII; $env:PSQL_HISTORY='NUL'; $psql=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\binaries\bin\psql.exe'; $p=Start-Process -FilePath $psql -ArgumentList @('-X','-W','-h','127.0.0.1','-p','55432','-U','postgres','-d','postgres','-f',('"'+$query+'"'),'-o',('"'+$output+'"')) -WindowStyle Normal -Wait -PassThru; Write-Output "psql diagnostics exit code: $($p.ExitCode)"; if ($p.ExitCode -eq 0) { Get-Content -LiteralPath $output }; exit $p.ExitCode
```

Application-role test command:

```powershell
$output=Join-Path $env:TEMP 'cloudtask-04ja2-app-test.txt'; if (Test-Path -LiteralPath $output) { Write-Error 'Application test output path exists'; exit 1 }; $env:PSQL_HISTORY='NUL'; $psql=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\binaries\bin\psql.exe'; $p=Start-Process -FilePath $psql -ArgumentList @('-X','-W','-h','127.0.0.1','-p','55432','-U','cloudtask_app','-d','cloudtask_dev','-c','"SELECT current_user, current_database();"','-o',('"'+$output+'"')) -WindowStyle Normal -Wait -PassThru; Write-Output "psql app test exit code: $($p.ExitCode)"; if ($p.ExitCode -eq 0) { Get-Content -LiteralPath $output }; exit $p.ExitCode
```

## NOT RUN, risks and Git status

**0 Django tests executed, 0 passed, 0 failed.** No migrations, database mutations, password resets, role/database recreation, configuration changes, service changes or `.env` changes were performed. Authentication as the application role and its runtime readiness remain **BLOCKED**. Temporary non-secret SQL and sanitized output files remain in `%TEMP%`; this report is the only intentional workspace change. No password, verifier, PGPASSWORD, plaintext password argument, or `.pgpass` was used.

`git status --short --branch` showed `main` with no commits and untracked `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. This report is under already-untracked `docs/`; Git history was not changed.

**Next step:** arrange a controlled user-visible application-role password entry and diagnose the failed authentication without changing the role; request separate approval before any password reset or configuration change.
