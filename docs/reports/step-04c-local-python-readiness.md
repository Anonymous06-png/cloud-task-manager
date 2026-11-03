# Task 04C — Local Python runtime readiness

Date: 2026-10-31  
Workspace: `C:\ProjectCloud\cloud-task-manager`  
Environment: Windows / PowerShell, native Windows execution; no Docker or database operations.

## Findings

**A usable local Python interpreter was not found in the checked locations.** Windows uninstall records list Python 3.14.3 components and the Python Launcher, but the records for the core interpreter and executables had empty `InstallLocation`; their installer cache is not evidence of a working interpreter. `python` and `py` were not on PATH, the usual Python registration keys were absent, and the checked standard installation and virtual environment paths contained no executable. No interpreter was run, so its version and ability to create a virtual environment are **NOT VERIFIED**. These checks do not prove there is no Python elsewhere on the machine.

The project's `requirements.txt` pins Django 5.2.18 and `psycopg2-binary==2.9.10`. **64-bit CPython 3.11 is a suitable candidate**: Django's published metadata lists Python 3.11, and the adapter's [release files](https://pypi.org/project/psycopg2-binary/2.9.10/#files) include CPython 3.11 Windows wheels. Django also lists 3.14, but the adapter release does not list a CPython 3.14 Windows wheel; the 3.14 installer records alone therefore do not establish an easy installation of the pinned stack. See [Django release metadata](https://pypi.org/pypi/Django/5.2.18/json). Full dependency installation and compatibility have **not** been tested. The pinned [Gunicorn](https://pypi.org/project/gunicorn/23.0.0/) is a UNIX server, so its presence in the requirements does not establish a working native Windows production server.

No project-local `.venv`, `venv`, or `env` executable was found, and a scan of immediate project directories found no `pyvenv.cfg`. There was no `VIRTUAL_ENV` or `CONDA_PREFIX` in this process. A future separate `.venv` would avoid modifying existing environments, but creation and usability cannot be verified without an interpreter. No environment was created.

## Proposed changes requiring approval

If no usable CPython 3.11 interpreter can be supplied or located, install **64-bit CPython 3.11** using the official Windows installer, preferably per-user, then create a new project-local `.venv` with that interpreter. A later dependency installation would install the existing pinned packages into that isolated environment; native Windows Gunicorn usage would need separate consideration. The project also needs suitable runtime settings and a database for application operation, but those are outside this readiness task and no database configuration is proposed for execution now. **Stop before installation, environment creation, package installation, or configuration changes and obtain user approval.** No such changes were made.

## Commands and actual results

All commands ran in the workspace. Exit codes are the process results returned by the command runner; an exit of 1 from a PowerShell command with suppressed missing-path errors does not necessarily mean every queried location failed.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04b-template-path-fix.md, requirements.txt, manage.py` | 0 | Read prior report, pins and Django settings-module entry point. |
| `git status --short --branch` | 0 | `main`, no commits; project entries untracked. Warning: global Git ignore file inaccessible. |
| `Test-Path docs\reports\step-04c-local-python-readiness.md; Get-Command python,python3,py -All -ErrorAction SilentlyContinue \| Select-Object Name,Source,CommandType` | 1 | Report path absent (`False`); no Python command listed. |
| `where.exe python` | 1 | No matching executable on PATH. |
| `where.exe py` | 1 | No matching executable on PATH. |
| `Get-ChildItem 'HKCU:\Software\Python','HKLM:\Software\Python','HKLM:\Software\WOW6432Node\Python' -Recurse -ErrorAction SilentlyContinue \| Get-ItemProperty -ErrorAction SilentlyContinue \| Select-Object PSPath,ExecutablePath,InstallPath,Version,SysVersion` | 1 | No output; interrupted after it did not finish promptly. Targeted `reg query` checks below replace it. |
| `reg query HKCU\Software\Python /s` | 1 | Key not found. |
| `reg query HKLM\Software\Python /s` | 1 | Key not found. |
| `reg query HKLM\Software\WOW6432Node\Python /s` | 1 | Key not found. |
| `$paths = @('C:\Python*','C:\Program Files\Python*','C:\Program Files (x86)\Python*',"$env:LOCALAPPDATA\Programs\Python\Python*",'.venv\Scripts\python.exe','venv\Scripts\python.exe','env\Scripts\python.exe','C:\Users\Ky\AppData\Local\Temp\opencode\ctm-venv\Scripts\python.exe'); foreach ($path in $paths) { Get-Item $path -ErrorAction SilentlyContinue \| Select-Object FullName,Attributes }` | 1 | No matching paths returned. |
| `Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue \| Where-Object { $_.DisplayName -match '^Python (3\|Launcher)' } \| Select-Object DisplayName,DisplayVersion,InstallLocation` | 1 | Listed Python 3.14.3 components and Python Launcher; install locations were blank. |
| `Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue \| Where-Object { $_.DisplayName -match '^Python 3.14.3 (Executables\|Core Interpreter)' } \| Select-Object DisplayName,InstallLocation,InstallSource,DisplayIcon` | 1 | Empty install locations; installer sources under the user's package cache. |
| `Get-ChildItem C:\Users\Ky\AppData\Local\Microsoft\WindowsApps\python*.exe,C:\Windows\py.exe,C:\ProgramData\Anaconda3\python.exe,C:\Users\Ky\anaconda3\python.exe,C:\Users\Ky\miniconda3\python.exe -ErrorAction SilentlyContinue \| Select-Object FullName,Length,Attributes` | 1 | No matching files returned. |
| `Get-ChildItem -Force -Directory -ErrorAction SilentlyContinue \| Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'pyvenv.cfg') } \| Select-Object FullName` | 0 | No immediate project directory contained `pyvenv.cfg`. |
| `Get-ChildItem Env:LOCALAPPDATA,Env:USERPROFILE,Env:VIRTUAL_ENV,Env:CONDA_PREFIX -ErrorAction SilentlyContinue \| Select-Object Name,Value` | 1 | User and local app data paths present; virtual environment variables absent. |

## NOT RUN / BLOCKED

Interpreter `--version`, `venv` creation and Django checks are **BLOCKED** by the absence of a located usable interpreter. Django tests: **NOT RUN; 0 tests executed, 0 passed, 0 failed**. Package installation, Django startup, migrations, database access, `.env` creation and Docker/cloud actions were **NOT RUN** as instructed.

## Git status and next step

`git status --short --branch` reported no commits on `main`; `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/` were untracked. This report is inside the already untracked `docs/`. Nothing was staged, committed, pushed, reset or cleaned.

**Next step:** obtain approval to install 64-bit CPython 3.11 and create a separate project-local virtual environment, or have the user identify an existing suitable interpreter. Package installation and database setup require their own authorized scope.
