###############################################
#     _____ _____ _____ _____ _____ _____     #
#    |     |  _  |__   |   | |   __|_   _|    #
#    | | | |     |   __| | | |   __| | |      #
#    |_|_|_|__|__|_____|_|___|_____| |_|      #
#                                             #
#          Copyright (c) 2026 MAZNET          #
#       Author: MAZNET (Mateusz Mazur)        #
#                                             #
###############################################

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Write-Header {
    Write-Host ""
    Write-Host "  +--------------------------------------+" -ForegroundColor Cyan
    Write-Host "  |    UsageMonitor -- Build Tool        |" -ForegroundColor Cyan
    Write-Host "  +--------------------------------------+" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step([string]$text) { Write-Host "  $text" -ForegroundColor Cyan }
function Write-OK([string]$text)   { Write-Host "  $text" -ForegroundColor Green }
function Write-Warn([string]$text) { Write-Host "  $text" -ForegroundColor Yellow }
function Write-Err([string]$text)  { Write-Host "  $text" -ForegroundColor Red }

# --------------------------------------------------------------
# WYKRYWANIE PYTHONA
# --------------------------------------------------------------
function Find-Python {
    foreach ($cmd in @("python", "python3")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) {
            $ver = & $found.Source --version 2>&1
            if ($ver -match "Python 3") { return $found.Source }
        }
    }
    $searchRoots = @(
        "$env:LOCALAPPDATA\Programs\Python",
        "$env:APPDATA\Python",
        "C:\Python*",
        "C:\Program Files\Python*",
        "C:\Program Files (x86)\Python*"
    )
    foreach ($root in $searchRoots) {
        $hits = Get-Item $root -ErrorAction SilentlyContinue
        foreach ($hit in $hits) {
            $exe = Join-Path $hit.FullName "python.exe"
            if (Test-Path $exe) {
                $ver = & $exe --version 2>&1
                if ($ver -match "Python 3") { return $exe }
            }
        }
    }
    return $null
}

# --------------------------------------------------------------
# ODCZYT AKTUALNEJ WERSJI Z version.txt
# --------------------------------------------------------------
function Get-CurrentVersion {
    if (-not (Test-Path "version.txt")) { return "1.0.0" }
    $content = Get-Content "version.txt" -Raw
    if ($content -match "FileVersion'\s*,\s*'([\d.]+)'") {
        return $Matches[1]
    }
    return "1.0.0"
}

# --------------------------------------------------------------
# AKTUALIZACJA version.txt
# --------------------------------------------------------------
function Update-VersionFile([string]$version) {
    $parts  = $version -split "\."
    $tuple  = "($($parts[0]),$($parts[1]),$($parts[2]),0)"
    $content = Get-Content "version.txt" -Raw

    $content = $content -replace 'filevers=\(\d+,\d+,\d+,\d+\)', "filevers=$tuple"
    $content = $content -replace 'prodvers=\(\d+,\d+,\d+,\d+\)', "prodvers=$tuple"

    # Podmien wartosc FileVersion string
    $content = [regex]::Replace(
        $content,
        "(StringStruct\('FileVersion'\s*,\s*')[^']*(')",
        "`${1}$version`${2}"
    )

    Set-Content "version.txt" $content -Encoding UTF8 -NoNewline
    Write-OK "version.txt zaktualizowany -> $version"
}

# ==============================================================
# GLOWNA LOGIKA
# ==============================================================
Write-Header

Write-Step "[0/4] Szukanie interpretera Python..."
$python = Find-Python
if (-not $python) {
    Write-Err "Nie znaleziono Pythona 3. Zainstaluj Python i dodaj do PATH."
    exit 1
}
$pyVersion = & $python --version 2>&1
Write-OK "Znaleziono: $python  ($pyVersion)"

Write-Host ""
$currentVersion = Get-CurrentVersion
Write-Warn "Aktualna wersja: $currentVersion"
$inputVersion = Read-Host "  Podaj nowa wersje (Enter = zachowaj $currentVersion)"
if ([string]::IsNullOrWhiteSpace($inputVersion)) {
    $inputVersion = $currentVersion
}
if ($inputVersion -notmatch "^\d+\.\d+\.\d+$") {
    Write-Err "Blad: wersja musi miec format X.Y.Z (np. 1.2.3)"
    exit 1
}
$version = $inputVersion
Write-Host ""
Write-Warn "Budowanie wersji: $version"
Write-Host ""

Update-VersionFile $version

# --- [1/4] Instalacja zaleznosci ---
Write-Step "[1/4] Instalacja zaleznosci..."

& $python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) { Write-Err "Blad przy instalacji requirements.txt"; exit 1 }
Write-OK "requirements.txt -- OK"

& $python -m pip install --upgrade pyinstaller --quiet
if ($LASTEXITCODE -ne 0) { Write-Err "Blad przy instalacji PyInstaller"; exit 1 }
Write-OK "PyInstaller -- OK"

# --- [2/4] Kompilacja ---
Write-Step "[2/4] Kompilacja PyInstaller..."

$args = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name=UsageMonitor",
    "--version-file=version.txt",
    "--add-data=assets;assets",
    "--add-data=theme;theme",
    "--add-data=core;core",
    "--add-data=ui;ui"
)
if (Test-Path "assets\icon.ico") { $args += "--icon=assets\icon.ico" }
$args += "main.py"

& $python @args
if ($LASTEXITCODE -ne 0) { Write-Err "Kompilacja nie powiodla sie (kod: $LASTEXITCODE)"; exit 1 }
Write-OK "Kompilacja zakonczona sukcesem."

# --- [3/4] Przeniesienie .exe ---
Write-Step "[3/4] Przenoszenie pliku .exe..."

$src = "dist\UsageMonitor.exe"
if (-not (Test-Path $src)) { Write-Err "Nie znaleziono: $src"; exit 1 }

$execDir = "exec"
if (-not (Test-Path $execDir)) { New-Item -ItemType Directory -Path $execDir | Out-Null }

$dst = "$execDir\UsageMonitor-$version.exe"
Move-Item -Path $src -Destination $dst -Force
Write-OK "Plik przeniesiony -> $dst"

# --- [4/4] Czyszczenie ---
Write-Step "[4/4] Czyszczenie plikow tymczasowych..."
foreach ($p in @("build", "dist", "UsageMonitor.spec")) {
    if (Test-Path $p) { Remove-Item $p -Recurse -Force }
}
Write-OK "Wyczyszczono."

Write-Host ""
Write-OK "[DONE] UsageMonitor-$version.exe -> .\$execDir"
Write-Host ""