# Run this file in a visible PowerShell terminal. It never receives or stores a password.
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'
$bin = Join-Path $root 'binaries\bin'
$psql = Join-Path $bin 'psql.exe'
$pgIsReady = Join-Path $bin 'pg_isready.exe'

if (-not (Test-Path -LiteralPath $psql)) { throw 'psql.exe was not found in the isolated PostgreSQL installation.' }
& $pgIsReady -h 127.0.0.1 -p 55432
if ($LASTEXITCODE -ne 0) { throw "pg_isready failed with exit code $LASTEXITCODE" }

Write-Host 'Step 1: inspect approved test database. Enter the cloudtask_app password when prompted.'
& $psql -W -h 127.0.0.1 -p 55432 -U cloudtask_app -d postgres -v ON_ERROR_STOP=1 -c "SELECT datname, pg_get_userbyid(datdba) AS owner, datallowconn FROM pg_database WHERE datname IN ('cloudtask_dev', 'cloudtask_test_04k') ORDER BY datname;"
if ($LASTEXITCODE -ne 0) { throw "cloudtask_app inspection failed with exit code $LASTEXITCODE" }

Write-Host 'If cloudtask_test_04k is absent, run this separate command and enter the postgres password when prompted:'
Write-Host "$psql -W -h 127.0.0.1 -p 55432 -U postgres -d postgres -v ON_ERROR_STOP=1 -c \\"CREATE DATABASE cloudtask_test_04k OWNER cloudtask_app;\\""
Write-Host 'Do not run that CREATE command if cloudtask_test_04k already exists.'

Write-Host 'Step 2: verify application-role login to the approved database. Enter the cloudtask_app password when prompted.'
& $psql -W -h 127.0.0.1 -p 55432 -U cloudtask_app -d cloudtask_test_04k -v ON_ERROR_STOP=1 -c "SELECT current_database(), current_user, inet_server_addr()::text, inet_server_port(), pg_get_userbyid(datdba) AS owner FROM pg_database WHERE datname = current_database();"
if ($LASTEXITCODE -ne 0) { throw "cloudtask_app test-database login failed with exit code $LASTEXITCODE" }
