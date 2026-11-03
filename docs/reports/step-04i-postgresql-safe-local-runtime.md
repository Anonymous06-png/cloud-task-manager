# Task 04I recovery — Safe local PostgreSQL runtime checkpoint

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`; Windows / PowerShell.

## Status: awaiting approval for alternative method

No extraction, initialization, or server startup was attempted. The previous installer remains at `C:\Users\Ky\AppData\Local\Temp\postgresql-16.15-1-windows-x64-ctm.exe`; its Authenticode signature remains `Valid`, publisher `EnterpriseDB Corporation`, and SHA-256 remains `DE926FEFAD00E313E212CD438C0F04BF033E200099AD56C012724EFCEBED79F2`. EDB documents `--extract-only` as extracting PostgreSQL binaries without performing an installation; its `--prefix` option specifies an installation directory. The exact behavior and output layout of this specific executable remain untested. [EDB command-line documentation](https://www.enterprisedb.com/docs/supported-open-source/postgresql/installing/command_line_parameters/)

## Proposed isolated layout and sequence

Use a new, separate user-owned root `C:\Users\Ky\AppData\Local\CloudTaskManager\postgresql16`, currently absent, with `binaries\` for the extracted files and a separate `data\` for a new cluster; log files would live under the same root. Use TCP port **55432**, which had no listener at inspection time. No Windows service or system PATH change is proposed: the new server would run under the current Windows user and would be started explicitly. It would persist until stopped or the machine/user session ends, subject to Windows process behavior.

After approval, recheck the root, the chosen port and existing services; stop if any conflict exists. Extract only to the new binaries location, verify what was actually written and the version, then use PostgreSQL `initdb` against the new data directory with interactive `--pwprompt` and SCRAM authentication. The user must enter the password directly in a visible interactive terminal, not in chat or tool arguments; if a secure interactive prompt cannot be provided, stop. `initdb` creates its own built-in administrative and template databases, but no Django project database or role. [PostgreSQL initdb documentation](https://www.postgresql.org/docs/16/app-initdb.html)

Before first server startup, explicitly set and inspect `listen_addresses = 'localhost'`, verify `pg_hba.conf` allows only required IPv4/IPv6 loopback clients with `scram-sha-256`, and verify the newly created path has no preexisting cluster or service conflict. Start only this new instance after those checks pass. Verify the server version, actual listener addresses and `pg_isready`; stop and report if any prerequisite or verification fails. Extraction-only and interactive input behavior must be verified rather than presumed, and no data will be overwritten.

## Commands and results

Commands ran from the workspace; exit codes are command-runner process exit codes.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04i-postgresql-install-verification.md` | 0 | Read prior blocked installation and evidence. |
| `$installer = Join-Path $env:TEMP 'postgresql-16.15-1-windows-x64-ctm.exe'; if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) { Write-Output 'Installer absent'; exit 1 }; $sig = Get-AuthenticodeSignature -LiteralPath $installer; Write-Output "Path: $installer"; Write-Output "Signature: $($sig.Status)"; Write-Output "Publisher: $($sig.SignerCertificate.Subject)"; Write-Output "SHA256: $((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash)"; if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'EnterpriseDB') { exit 1 }` | 0 | Installer present, valid EnterpriseDB signature and hash above. |
| `$target = Join-Path $env:LOCALAPPDATA 'CloudTaskManager\postgresql16'; Write-Output "Proposed root: $target"; Write-Output "Root exists: $(Test-Path -LiteralPath $target)"; Get-CimInstance Win32_Service -Filter "Name LIKE '%postgres%' OR DisplayName LIKE '%postgres%'" \| Select-Object Name,State; Get-NetTCPConnection -State Listen -ErrorAction Stop \| Where-Object { $_.LocalPort -eq 55432 } \| Select-Object LocalAddress,LocalPort,OwningProcess` | 0 | Proposed root absent; no matching service or port 55432 listener returned. |
| `git status --short --branch` | 0 | `main` has no commits; project entries untracked. |
| `Test-Path -LiteralPath docs\reports\step-04i-postgresql-safe-local-runtime.md` | 0 | `False`; report path was free. |

## NOT RUN and limitations

Extraction, `initdb`, configuration, server startup, listener checks after startup, `pg_isready`, Django tests and migrations are **NOT RUN**, pending approval. **0 Django tests executed, 0 passed, 0 failed.** No password was requested or stored, no cluster or database was created, and no service or application configuration changed. Only this report was created. Existing nonstandard instances may exist; the checks above are limited to the queried names and port.

## Git status and next step

`main` has no commits. Untracked entries: `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/`. This report is in already-untracked `docs/`; no Git history was changed.

**Next step:** obtain explicit approval for the extraction-only layout and sequence, then repeat conflict checks and proceed only if the secure interactive password prompt and pre-start loopback configuration can be verified.
