# Task 04D — Local Python installation

Date: 2026-10-31  
Environment: Windows / PowerShell; workspace `C:\ProjectCloud\cloud-task-manager`.

## Result and changes

Installed official CPython **3.11.9 x64** per user at `C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe`. The installer exited 0 after the downloaded file matched the checksum published on the [Python 3.11.9 release page](https://www.python.org/downloads/release/python-3119/) and had a valid Python Software Foundation Authenticode signature. Python 3.11.9 is the last 3.11 Windows binary installer; later 3.11 security releases are source-only, so this binary does not include their later fixes. No project dependency or virtual environment was installed or created. Installer options disabled PATH changes and launcher installation; no other Python installation was intentionally modified or removed.

Outside-sandbox verification reported `3.11.9`, `64 bit (AMD64)`, 64 pointer bits, and a successfully imported `venv` module at `C:\Users\Ky\AppData\Local\Programs\Python\Python311\Lib\venv\__init__.py`. Importing `venv` verifies module availability, not virtual-environment creation or package availability.

## Commands and results

Commands ran from the workspace. The installation and successful verification ran outside the sandbox with approval; other commands used the default sandbox.

| Command | Exit | Result |
| --- | ---: | --- |
| `Get-Content -Encoding UTF8 docs\reports\step-04c-local-python-readiness.md` | 0 | Read prior readiness findings. |
| `git status --short --branch` | 0 | No commits on `main`; project entries untracked; global ignore permission warning. |
| `Test-Path docs\reports\step-04d-python-installation.md` | 0 | `False`; report filename was free. |
| `$candidates = @('C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe','C:\Program Files\Python311\python.exe','C:\Python311\python.exe'); $launcher = Get-Command py -ErrorAction SilentlyContinue; if ($launcher) { & $launcher.Source -3.11 -c 'import sys, struct; print(sys.executable); print(sys.version); print(struct.calcsize("P") * 8)' }; foreach ($candidate in $candidates) { if (Test-Path -LiteralPath $candidate -PathType Leaf) { & $candidate -c 'import sys, struct; print(sys.executable); print(sys.version); print(struct.calcsize("P") * 8)' } }; if (-not $launcher -and -not ($candidates \| Where-Object { Test-Path -LiteralPath $_ -PathType Leaf })) { Write-Output 'No Python 3.11 candidate found'; exit 1 }` | 1 | No launcher or candidate found in checked locations. |
| `$installer = Join-Path $env:TEMP 'python-3.11.9-amd64-ctm.exe'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile $installer -ErrorAction Stop; if ((Get-FileHash -LiteralPath $installer -Algorithm MD5).Hash -ne 'E8DCD502E34932EEBCAF1BE056D5CBCD') { Write-Error 'Installer checksum mismatch'; exit 1 }; $signature = Get-AuthenticodeSignature -LiteralPath $installer; if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') { Write-Error 'Installer signature verification failed'; exit 1 }; $process = Start-Process -FilePath $installer -ArgumentList '/quiet','InstallAllUsers=0','PrependPath=0','Include_launcher=0','Include_test=0' -WindowStyle Hidden -Wait -PassThru; Write-Output "Installer exit code: $($process.ExitCode)"; exit $process.ExitCode` | 0 | Downloaded installer to temporary directory, passed both verification gates, installer reported exit 0. |
| `& 'C:\Users\Ky\AppData\Local\Programs\Python\Python311\python.exe' -c "import sys, struct, venv; print('executable:', sys.executable); print('version:', sys.version); print('architecture bits:', struct.calcsize('P') * 8); print('venv module:', venv.__file__)"; exit $LASTEXITCODE` | 0 | **Failed in sandbox:** PowerShell reported executable not found. The process exit 0 is misleading because the call failed before a native exit code was set. |
| `reg query HKCU\Software\Python\PythonCore\3.11\InstallPath /ve` | 1 | Registry key not visible in sandbox. |
| `$exe = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe'; Write-Output "Expected path: $exe"; if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { Write-Error 'Interpreter not found'; exit 1 }; & $exe -c "import sys, struct, venv; print('executable:', sys.executable); print('version:', sys.version); print('architecture bits:', struct.calcsize('P') * 8); print('venv module:', venv.__file__)"; exit $LASTEXITCODE` | 0 | Outside sandbox: expected executable exists and reports 3.11.9, AMD64, 64 bits, and the `venv` module path above. |
| `git status --short --branch` | 0 | Same untracked entries as before installation; warning about inaccessible global ignore file. |

## NOT RUN / limitations

**0 Django tests run, 0 passed, 0 failed.** Project dependencies, virtual environment creation, Django startup, migrations, database changes, `.env`, Docker, cloud and WebIOT operations were **NOT RUN**. The default sandbox did not see the installed executable; future commands may require an appropriate execution context. The installer file remains in the temporary directory; no cleanup was attempted.

## Git status

Branch `main` has no commits; `.dockerignore`, `.env.example`, `.gitignore`, `.zcode/`, `CLAUDE.md`, `Dockerfile`, `README.md`, `backend/`, `config/`, `docker-compose.yml`, `docs/`, `manage.py`, `requirements.txt`, `static/`, `tasks/`, and `templates/` were untracked. This report is under the already untracked `docs/`. No staging, commit, push, reset or clean was performed.

## Next allowed step

With separately authorized scope, create an isolated project-local virtual environment using the verified interpreter and assess the pinned dependencies before attempting Django checks.
