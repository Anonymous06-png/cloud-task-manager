[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 8000,
    [switch]$NoBrowser,
    [switch]$SkipCollectStatic
)

$ErrorActionPreference = "Stop"
$exitCode = 1
$browserJob = $null
$previousSecretKey = $env:SECRET_KEY

function Assert-PrivatePath($Path, $Sid, $Directory) {
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer -ne $Directory -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "The local signing-key store has an unsafe path type."
    }
    $acl = Get-Acl -LiteralPath $Path
    $rules = @($acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]))
    if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $Sid.Value -or
        !$acl.AreAccessRulesProtected -or $rules.Count -ne 1 -or
        $rules[0].IdentityReference.Value -ne $Sid.Value -or
        $rules[0].AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
        ($rules[0].FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -ne [Security.AccessControl.FileSystemRights]::FullControl) {
        throw "The local signing-key store must be restricted to the current Windows user."
    }
}

function Get-ProcessChain($Process) {
    $chain = @()
    for ($depth = 0; $Process -and $depth -lt 4; $depth++) {
        $chain += $Process
        if (!$Process.ParentProcessId) { break }
        $Process = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $Process.ParentProcessId)
    }
    return $chain
}

function Import-PrivateOAuthKeys($PrivateRoot) {
    # Optional Google OAuth credentials (django-allauth), read from the
    # private keys file when present. Values are never printed or logged;
    # already configured environment variables are never overwritten; with
    # no credentials (or an absent file) the app stays on username/password
    # login. Returns the names of the variables that were set.
    $known = @('GOOGLE_OAUTH_CLIENT_ID', 'GOOGLE_OAUTH_CLIENT_SECRET')
    $oauthFile = Join-Path $PrivateRoot "oauth-keys-backup.env"
    if (!(Test-Path -LiteralPath $oauthFile -PathType Leaf)) { return @() }
    if ((Get-Item -LiteralPath $oauthFile -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw "The private OAuth credentials file cannot be a reparse point."
    }
    $loaded = @()
    foreach ($line in [IO.File]::ReadAllLines($oauthFile)) {
        if ($line -match '^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*?)\s*$') {
            $name = $Matches[1]
            $value = $Matches[2]
            if ($known -notcontains $name) { continue }
            if ([string]::IsNullOrEmpty($value)) { continue }
            if ([string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($name, 'Process'))) {
                [Environment]::SetEnvironmentVariable($name, $value, 'Process')
                $loaded += $name
            }
        }
    }
    return $loaded
}

try {
    Set-Location $PSScriptRoot
    $entryUrl = "http://127.0.0.1:$Port/"
    $listener = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
    if ($listener.Count) {
        $owner = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $listener[0].OwningProcess)
        $chain = @(Get-ProcessChain $owner)
        $djangoPattern = 'manage\.py["'']?\s+runserver\s+.*(?:127\.0\.0\.1:)?' + $Port + '(?:\s|"|''|$)'
        $django = @($chain | Where-Object { $_.CommandLine -match $djangoPattern })
        $autoreload = @($django | Where-Object { $_.CommandLine -notmatch '--noreload' })
        $repositoryPath = [regex]::Escape($PSScriptRoot)
        $ownedByRepository = @($django | Where-Object { $_.CommandLine -match $repositoryPath })
        try {
            $response = Invoke-WebRequest -Uri $entryUrl -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200 -and $autoreload.Count -and $ownedByRepository.Count) {
                Write-Host "Verified autoreloading Cloud Task Manager is already running at $entryUrl" -ForegroundColor Green
                if (!$NoBrowser) { Start-Process $entryUrl }
                exit 0
            }
        } catch { }
        if ($response -and $response.StatusCode -eq 200 -and $django.Count -and $ownedByRepository.Count) {
            $chainSummary = ($chain | ForEach-Object { "$($_.ProcessId):$($_.Name)" }) -join ', '
            Write-Host "Port $Port is occupied by the verified older supervised Django server." -ForegroundColor Yellow
            Write-Host "Process chain: $chainSummary"
            $approval = Read-Host "Type TRANSITION to replace only this verified server with autoreload"
            if ($approval -cne 'TRANSITION') {
                throw "Transition not approved. Existing server was left untouched."
            }
            $before = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
            $beforeOwner = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $before[0].OwningProcess)
            $beforeChain = @(Get-ProcessChain $beforeOwner)
            $beforeDjango = @($beforeChain | Where-Object { $_.CommandLine -match $djangoPattern })
            if (!$beforeDjango.Count -or !(@($beforeDjango | Where-Object { $_.CommandLine -match $repositoryPath }).Count)) {
                throw "Verified ownership changed; no process was stopped."
            }
            foreach ($target in @($beforeChain | Sort-Object ProcessId -Descending)) {
                Stop-Process -Id $target.ProcessId -Force -ErrorAction Stop
            }
            Start-Sleep -Milliseconds 500
            if (@(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue).Count) {
                throw "The verified server transition did not release port $Port."
            }
        } else {
            throw "Port $Port is occupied by another application or an unverified server. No existing process will be stopped."
        }
    }

    $python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    $privateRoot = Join-Path $env:LOCALAPPDATA "CloudTaskManager"
    $root = Join-Path $privateRoot "postgresql16"
    $ctl = Join-Path $root "binaries\bin\pg_ctl.exe"
    if (!(Test-Path -LiteralPath $python -PathType Leaf) -or !(Test-Path -LiteralPath $ctl -PathType Leaf)) {
        throw "The existing local Python or PostgreSQL installation is unavailable."
    }
    if ((Get-Item -LiteralPath $privateRoot -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw "The private configuration directory cannot be a reparse point."
    }
    $env:PGPASSFILE = Join-Path $privateRoot "pgpass.conf"
    if (!(Test-Path -LiteralPath $env:PGPASSFILE -PathType Leaf)) {
        throw "The private PGPASSFILE is missing. Configure it privately before startup."
    }
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    $env:DATABASE_URL = "postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_dev_utf8_06b"
    $env:DJANGO_ENV = "local"
    $env:DEBUG = "True"
    $env:SECURE_SSL_REDIRECT = "False"
    $env:SESSION_COOKIE_SECURE = "False"
    $env:CSRF_COOKIE_SECURE = "False"
    $env:ALLOWED_HOSTS = "localhost,127.0.0.1"
    $env:PYTHONIOENCODING = "utf-8"

    & $ctl -D "$root\data" status 2>$null
    $status = $LASTEXITCODE
    if ($status -eq 3) {
        & $ctl -D "$root\data" -l "$root\server.log" -w start
        if ($LASTEXITCODE -ne 0) { throw "PostgreSQL startup failed." }
    } elseif ($status -ne 0) {
        throw "PostgreSQL status could not be verified; startup stopped."
    }

    $identityCheck = @'
import json
import sys
import psycopg2
try:
    with psycopg2.connect(host="127.0.0.1", port=55432, dbname="cloudtask_dev_utf8_06b", user="cloudtask_app", connect_timeout=5) as connection:
        connection.set_session(readonly=True)
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(),current_user,host(inet_server_addr()),inet_server_port(),pg_encoding_to_char(encoding),pg_get_userbyid(datdba) FROM pg_database WHERE datname=current_database()")
            identity = cursor.fetchone()
        if identity != ("cloudtask_dev_utf8_06b", "cloudtask_app", "127.0.0.1", 55432, "UTF8", "cloudtask_app"):
            raise ValueError("Unexpected database identity")
        print("Local database identity PASS: " + json.dumps(identity))
    connection.close()
except Exception:
    print("Local database authentication/identity check failed; no credentials disclosed.", file=sys.stderr)
    sys.exit(1)
'@
    $identityCheck | & $python -I -B -
    if ($LASTEXITCODE -ne 0) { throw "UTF8 database preflight failed." }

    # DPAPI protects the key at rest; plaintext is passed only in the process environment.
    Add-Type -AssemblyName System.Security
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $secretDirectory = Join-Path $privateRoot "secrets"
    $secretFile = Join-Path $secretDirectory "django-secret-key.dpapi"
    if (Test-Path -LiteralPath (Join-Path $PSScriptRoot ".env")) {
        throw "An existing .env requires signing-key configuration review; it will not be overwritten."
    }
    if (!(Test-Path -LiteralPath $secretFile) -and $env:SECRET_KEY) {
        throw "An existing SECRET_KEY will not be replaced by automatic provisioning."
    }
    if (!(Test-Path -LiteralPath $secretDirectory)) {
        $directoryAcl = [Security.AccessControl.DirectorySecurity]::new()
        $directoryAcl.SetOwner($sid)
        $directoryAcl.SetAccessRuleProtection($true, $false)
        $directoryAcl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new(
            $sid, "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow"))
        [IO.Directory]::CreateDirectory($secretDirectory, $directoryAcl) | Out-Null
    }
    Assert-PrivatePath $secretDirectory $sid $true
    if (!(Test-Path -LiteralPath $secretFile)) {
        $fileAcl = [Security.AccessControl.FileSecurity]::new()
        $fileAcl.SetOwner($sid)
        $fileAcl.SetAccessRuleProtection($true, $false)
        $fileAcl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid, "FullControl", "Allow"))
        $random = New-Object byte[] 64
        $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
        $stream = $null
        try {
            $rng.GetBytes($random)
            $encrypted = [Security.Cryptography.ProtectedData]::Protect($random, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
            $stream = [IO.FileStream]::new($secretFile, [IO.FileMode]::CreateNew,
                [Security.AccessControl.FileSystemRights]::Write, [IO.FileShare]::None,
                4096, [IO.FileOptions]::None, $fileAcl)
            $stream.Write($encrypted, 0, $encrypted.Length)
            $stream.Flush($true)
        } finally {
            if ($stream) { $stream.Dispose() }
            $rng.Dispose()
            [Array]::Clear($random, 0, $random.Length)
        }
        Write-Host "Created the protected local signing-key store."
    }
    Assert-PrivatePath $secretFile $sid $false
    $plain = $null
    try {
        $plain = [Security.Cryptography.ProtectedData]::Unprotect(
            [IO.File]::ReadAllBytes($secretFile), $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
        if ($plain.Length -ne 64) { throw "Unexpected local signing-key format." }
        $localKey = [Convert]::ToBase64String($plain)
        if ($env:SECRET_KEY -and $env:SECRET_KEY -cne $localKey) {
            throw "The inherited SECRET_KEY conflicts with the protected local key."
        }
        $env:SECRET_KEY = $localKey
        $localKey = $null
    } finally {
        if ($plain) { [Array]::Clear($plain, 0, $plain.Length) }
    }
    Write-Host "Protected local signing key loaded; value not displayed."

    $oauthKeys = Import-PrivateOAuthKeys $privateRoot
    if ($oauthKeys.Count) {
        Write-Host ("Optional Google OAuth credentials loaded for: " + ($oauthKeys -join ', '))
    }

    & $python manage.py check
    if ($LASTEXITCODE -ne 0) { throw "Django system checks failed." }
    if (!$SkipCollectStatic -and $env:DEBUG -ne "True") {
        & $python manage.py collectstatic --noinput
        if ($LASTEXITCODE -ne 0) { throw "collectstatic failed." }
    }

    $entryUrl = "http://127.0.0.1:$Port/"
    Write-Host "`nWebsite: $entryUrl" -ForegroundColor Green
    if (!$NoBrowser) {
        $browserJob = Start-Job -ArgumentList $entryUrl, $Port, $PID -ScriptBlock {
            param($url, $port, $launcherPid)
            for ($attempt = 0; $attempt -lt 30; $attempt++) {
                try {
                    $listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction Stop
                    $process = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $listener.OwningProcess)
                    for ($depth = 0; $process -and $process.ProcessId -ne $launcherPid -and $depth -lt 4; $depth++) {
                        $process = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $process.ParentProcessId)
                    }
                    if ($process.ProcessId -eq $launcherPid) {
                        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
                        if ($response.StatusCode -eq 200) { Start-Process $url; return }
                    }
                } catch { }
                Start-Sleep -Seconds 1
            }
            Write-Warning "Server did not become ready; open the URL manually."
        }
    }
    & $python manage.py runserver "127.0.0.1:$Port"
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "Local startup stopped: $($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
} finally {
    if ($browserJob) {
        Stop-Job $browserJob -ErrorAction SilentlyContinue
        Receive-Job $browserJob -ErrorAction SilentlyContinue
        Remove-Job $browserJob -ErrorAction SilentlyContinue
    }
    if ($null -eq $previousSecretKey) {
        Remove-Item Env:SECRET_KEY -ErrorAction SilentlyContinue
    } else {
        $env:SECRET_KEY = $previousSecretKey
    }
}
exit $exitCode
