# Task 04J-A — Django development database

Date: 2026-10-31  
Environment: Windows / PowerShell, isolated PostgreSQL cluster at `127.0.0.1:55432`.

## Status: BLOCKED on application-role authentication

The interactive superuser setup session completed with psql exit **0**. Its script checked that role `cloudtask_app` and database `cloudtask_dev` were absent, created a dedicated role, prompted for its password using `\password`, enabled login, and issued `CREATE DATABASE cloudtask_dev OWNER cloudtask_app`. The script used `ON_ERROR_STOP`; the successful process exit is evidence that it completed, but ownership and role attributes have **not** been independently confirmed by an authenticated SQL query.

The subsequent connection attempt as `cloudtask_app` to `cloudtask_dev` exited **2**. A sanitized inspection of the server log found a password-authentication failure. Per instruction, work stopped: no password reset or retry was attempted. The cause was not determined. The requested authenticated connectivity, database ownership and server version query remain **BLOCKED / NOT VERIFIED**. Do not assume the database is ready for Django.

Before the attempt, `pg_ctl status` showed the isolated cluster's data and binary paths and PID 21440; listeners on port 55432 were `127.0.0.1` and `::1`, owned by PID 21440. `pg_isready` reported accepting connections. No application uses the superuser as a runtime account.

## Changes and credentials

The setup script requested `cloudtask_app` with `NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`, initially `NOLOGIN`, then enabled login after the interactive password step; it requested database `cloudtask_dev` owned by that role. The successful psql setup exit supports creation, subject to the verification limit above. The role's `NOCREATEDB` means it cannot create Django's default test database; no test database was requested or created.

Non-secret SQL scripts were written to `%TEMP%\cloudtask-04ja-setup.sql` and `%TEMP%\cloudtask-04ja-verify.sql`; a verification output path `%TEMP%\cloudtask-04ja-verify.txt` was specified. No passwords were placed in those files, commands, conversation, or this report. The PostgreSQL server's normal logs and cluster data may have changed; the setup session set `log_statement=none` and `log_min_error_statement=panic` before the interactive password change. SCRAM stores a verifier in PostgreSQL's cluster data. No `.env`, application source, server configuration, software, or production settings were changed. This report was added.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes. The psql windows were visible for interactive password input.

| Command | Exit | Sanitized result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04i-isolated-postgresql-runtime.md, config\settings.py, .env.example` | 0 | Reviewed cluster evidence and Django configuration; example values are placeholders. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; & (Join-Path $root 'binaries\bin\pg_ctl.exe') -D (Join-Path $root 'data') status; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; & (Join-Path $root 'binaries\bin\pg_isready.exe') -h 127.0.0.1 -p 55432; exit $LASTEXITCODE` | 0 | Isolated server PID 21440 running; readiness probe accepting connections. |
| `Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess; Get-CimInstance Win32_Process -Filter "Name='postgres.exe'" \| Select-Object ProcessId,ParentProcessId,ExecutablePath \| Format-List` | 0 | IPv4/IPv6 loopback listeners owned by PID 21440; executable path belonged to isolated binaries. |
| `$root=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; $exe=Join-Path $root 'binaries\bin\postgres.exe'; $data=Join-Path $root 'data'; foreach ($key in @('log_statement','log_min_error_statement','password_encryption')) { Write-Output "${key}:"; & $exe -D $data -C $key; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` | 0 | `none`, `error`, `scram-sha-256` respectively before session-specific settings. |
| Setup command below | 0 | Interactive psql setup session returned 0. |
| Verification command below | **2** | Application-role psql connection failed; no verification query result. |
| `$log=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\server.log'; Get-Content -LiteralPath $log -Tail 30 \| Where-Object { $_ -match 'FATAL\|ERROR\|authentication\|password' } \| ForEach-Object { if ($_ -match 'password authentication failed') { 'Authentication failed (password not printed)' } elseif ($_ -match 'no password supplied') { 'No password supplied' } elseif ($_ -match 'role .* does not exist') { 'Requested role does not exist' } elseif ($_ -match 'database .* does not exist') { 'Requested database does not exist' } else { 'Other authentication or error log entry (redacted)' } }` | 0 | `Authentication failed (password not printed)`. |
| `git status --short --branch` | 0 | `main` has no commits; project entries untracked. |

Exact setup command, excluding no credentials (the script contains no passwords):

```powershell
$script=Join-Path $env:TEMP 'cloudtask-04ja-setup.sql'; if (Test-Path -LiteralPath $script) { Write-Error 'Setup script path exists'; exit 1 }; $sql=@'
\set ON_ERROR_STOP on
SET log_statement = 'none';
SET log_min_error_statement = 'panic';
DO $$ BEGIN IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'cloudtask_app') OR EXISTS (SELECT FROM pg_database WHERE datname = 'cloudtask_dev') THEN RAISE EXCEPTION 'Requested role or database already exists'; END IF; END $$;
CREATE ROLE cloudtask_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
\password cloudtask_app
ALTER ROLE cloudtask_app LOGIN;
CREATE DATABASE cloudtask_dev OWNER cloudtask_app;
'@; Set-Content -LiteralPath $script -Value $sql -Encoding ASCII; $env:PSQL_HISTORY='NUL'; $psql=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\binaries\bin\psql.exe'; $p=Start-Process -FilePath $psql -ArgumentList @('-X','-W','-h','127.0.0.1','-p','55432','-U','postgres','-d','postgres','-f',('"'+$script+'"')) -WindowStyle Normal -Wait -PassThru; Write-Output "psql setup exit code: $($p.ExitCode)"; exit $p.ExitCode
```

Exact verification command:

```powershell
$query=Join-Path $env:TEMP 'cloudtask-04ja-verify.sql'; $output=Join-Path $env:TEMP 'cloudtask-04ja-verify.txt'; if ((Test-Path -LiteralPath $query) -or (Test-Path -LiteralPath $output)) { Write-Error 'Verification file path exists'; exit 1 }; $sql=@'
\set ON_ERROR_STOP on
SELECT current_user AS role_name, current_database() AS database_name, current_setting('server_version') AS server_version, pg_get_userbyid(datdba) AS database_owner FROM pg_database WHERE datname=current_database();
SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls FROM pg_roles WHERE rolname=current_user;
'@; Set-Content -LiteralPath $query -Value $sql -Encoding ASCII; $env:PSQL_HISTORY='NUL'; $psql=Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16\binaries\bin\psql.exe'; $p=Start-Process -FilePath $psql -ArgumentList @('-X','-W','-h','127.0.0.1','-p','55432','-U','cloudtask_app','-d','cloudtask_dev','-f',('"'+$query+'"'),'-o',('"'+$output+'"')) -WindowStyle Normal -Wait -PassThru; Write-Output "psql verification exit code: $($p.ExitCode)"; if ($p.ExitCode -eq 0) { Get-Content -LiteralPath $output }; exit $p.ExitCode
```

## Tests, limitations and Git status

**0 Django tests run, 0 passed, 0 failed.** Authenticated application SQL failed; database ownership and actual server version via SQL are unverified. Test databases, migrations, Django startup, dependency installation, Docker, cloud and WebIOT actions were **NOT RUN**. No Git staging, commit, push, reset or clean occurred. `main` has no commits; `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/` remain untracked. This report is inside already-untracked `docs/`.

**Next step:** diagnose the application-role authentication failure using a secure interactive workflow, then independently verify the role attributes, database owner, and server version before using the database.
