# Task 04I continuation — PostgreSQL installation verification

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell.

## Status: BLOCKED before installation

The user approved installation, and the official EDB installer was downloaded and signature-checked. **The installer was not run:** a loopback-only listener at its first automatic startup could not be verified or enforced from the inspected installer documentation before execution. PostgreSQL itself defaults to `localhost`, but [EDB notes that packaged builds can override that default](https://www.enterprisedb.com/blog/how-to-secure-postgresql-security-hardening-best-practices-checklist-tips-encryption-authentication-vulnerabilities). The EDB graphical installation documentation inspected does not establish the exact first-start `listen_addresses` behavior for this installer. The user's instruction requires stopping if loopback-only access cannot be verified, so a post-start check alone would not satisfy it.

No PostgreSQL installation, service, cluster, project database, role, or password was created. No application source, Python environment, existing data, Docker, cloud, or WebIOT was changed. The downloaded installer remains at `%TEMP%\postgresql-16.15-1-windows-x64-ctm.exe`; this report is the only intentional workspace change.

## Evidence

The prior Task 04I report was read. `C:\Program Files\PostgreSQL\16` and this report path were absent at the check. No PostgreSQL-named Windows service or TCP listener on 5432 was returned. This check does not establish that all possible custom data directories, service names, nonstandard ports, or remote instances are absent. Default data directory would be beneath the absent install directory; no independent alternate data directory was selected. The proposed installer is [EDB PostgreSQL 16.15-1 x64](https://get.enterprisedb.com/postgresql/postgresql-16.15-1-windows-x64.exe), from the vendor reached via the [PostgreSQL Windows installer page](https://www.postgresql.org/download/windows/).

The downloaded file's Authenticode status was `Valid`, with signer subject `CN=EnterpriseDB Corporation, O=EnterpriseDB Corporation, L=Wilmington, S=Delaware, C=US`; SHA-256 was `DE926FEFAD00E313E212CD438C0F04BF033E200099AD56C012724EFCEBED79F2`. The signature check establishes the observed Windows signature status and publisher; the hash is recorded for identification, not as an independently verified vendor checksum.

## Commands and results

Commands ran from `C:\ProjectCloud\cloud-task-manager`; exit codes are process exit codes.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04i-postgresql-local-setup.md` | 0 | Read prior checkpoint and proposed constraints. |
| `git status --short --branch` | 0 | `main` has no commits; project entries untracked. |
| `Test-Path -LiteralPath docs\reports\step-04i-postgresql-install-verification.md; Test-Path -LiteralPath 'C:\Program Files\PostgreSQL\16'; Get-CimInstance Win32_Service -Filter "Name LIKE '%postgres%' OR DisplayName LIKE '%postgres%'" \| Select-Object Name,DisplayName,State; Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 5432 } \| Select-Object LocalAddress,LocalPort,OwningProcess` | 0 | Both paths returned `False`; no service or listener returned. |
| `$installer = Join-Path $env:TEMP 'postgresql-16.15-1-windows-x64-ctm.exe'; if (Test-Path -LiteralPath $installer) { Write-Error 'Installer destination already exists'; exit 1 }; Invoke-WebRequest -Uri 'https://get.enterprisedb.com/postgresql/postgresql-16.15-1-windows-x64.exe' -OutFile $installer -ErrorAction Stop; $sig = Get-AuthenticodeSignature -LiteralPath $installer; Write-Output "Signature status: $($sig.Status)"; Write-Output "Publisher: $($sig.SignerCertificate.Subject)"; Write-Output "SHA256: $((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash)"; if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'EnterpriseDB') { exit 1 }` | 0 | Downloaded installer; signature `Valid`, publisher and SHA-256 above. |

## NOT RUN / risks

Installation, first startup, installed server version, service state, listener verification, and `pg_isready` are **BLOCKED / NOT RUN**. No password was requested or exposed. **0 Django tests run, 0 passed, 0 failed**; database operations and migrations were not run. An existing nonstandard PostgreSQL setup may exist; conflict checks must be repeated immediately before a future installation.

## Git status and next step

Initial `git status --short --branch` reported `main` with no commits; untracked entries were `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. This report is inside already-untracked `docs/`. Nothing was staged, committed, pushed, reset or cleaned.

**Next step:** establish an EDB-supported way to enforce `listen_addresses` as loopback-only before the installer's first server start, then perform the approved installation and verification if that condition is met.
