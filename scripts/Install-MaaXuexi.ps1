param(
    [string]$MuMuDirectory,
    [string]$PythonPath,
    [ValidateRange(0,99)][int]$VmIndex = 0,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $PSScriptRoot
$configRoot = Join-Path $appRoot 'config'
$configPath = Join-Path $configRoot 'emulator.json'
$venvPython = Join-Path $appRoot '.venv\Scripts\python.exe'

function Get-MuMuTools([string]$Directory) {
    foreach ($candidate in @($Directory,(Join-Path $Directory 'nx_main'))) {
        $cli = Join-Path $candidate 'mumu-cli.exe'
        $adb = Join-Path $candidate 'adb.exe'
        if ((Test-Path -LiteralPath $cli -PathType Leaf) -and (Test-Path -LiteralPath $adb -PathType Leaf)) {
            return @{mumu_cli=(Resolve-Path -LiteralPath $cli).Path;adb_path=(Resolve-Path -LiteralPath $adb).Path;vm_index=$VmIndex;display_width=1280;display_height=720;dpi=240;app_package='cn.xuexi.android'}
        }
    }
    throw 'MuMu tools not found. Pass -MuMuDirectory pointing to MuMuPlayer or nx_main.'
}

try {
    $emulator = $null
    if ($MuMuDirectory) { $emulator = Get-MuMuTools $MuMuDirectory }
    elseif (Test-Path -LiteralPath $configPath) {
        $emulator = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($tool in @($emulator.mumu_cli,$emulator.adb_path)) {
            if (!(Test-Path -LiteralPath $tool -PathType Leaf)) { throw 'Existing emulator.json contains a missing MuMu executable.' }
        }
    } else { throw 'First install requires -MuMuDirectory. See README.md.' }

    if ($CheckOnly) {
        if (!(Test-Path -LiteralPath $venvPython)) { throw 'The local Python environment is missing. Run installation first.' }
        & $venvPython -c 'import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize(chr(80)) == 8; import maa, fastapi, httpx, numpy, PIL'
        if ($LASTEXITCODE -ne 0) { throw 'Runtime import check failed.' }
        @{status='ready';root=$appRoot;emulator_configured=$true;started_tasks=$false} | ConvertTo-Json
        exit 0
    }

    if (!(Test-Path -LiteralPath $venvPython)) {
        if (!$PythonPath) {
            $PythonPath = (& py -3.12 -c 'import sys; print(sys.executable)')
            if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 x64 from python.org, or pass -PythonPath.' }
        }
        & $PythonPath -c 'import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize(chr(80)) == 8'
        if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 x64 is required.' }
        & $PythonPath -m venv (Join-Path $appRoot '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
    }
    & $venvPython -m pip install --disable-pip-version-check -r (Join-Path $appRoot 'backend\requirements-runtime.lock.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Resolve network/package errors before continuing.' }
    & $venvPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency compatibility check failed.' }
    New-Item -ItemType Directory -Path $configRoot -Force | Out-Null
    if (!(Test-Path -LiteralPath $configPath)) {
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [IO.File]::WriteAllText($configPath,($emulator | ConvertTo-Json -Depth 5),$encoding)
    } elseif ($MuMuDirectory) {
        Write-Host 'Existing emulator.json was preserved. Edit it explicitly to change instances or paths.'
    }
    $plan = Join-Path $configRoot 'local-task-plan.json'
    if (!(Test-Path -LiteralPath $plan)) {
        Copy-Item -LiteralPath (Join-Path $configRoot 'local-task-plan.example.json') -Destination $plan
    }
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut((Join-Path $appRoot 'MaaXuexi-Local.lnk'))
    $shortcut.TargetPath = Join-Path $appRoot '.venv\Scripts\pythonw.exe'
    $shortcut.Arguments = '"' + (Join-Path $PSScriptRoot 'Launch-Hidden.py') + '"'
    $shortcut.WorkingDirectory = $appRoot
    $shortcut.WindowStyle = 7
    $shortcut.Save()
    Write-Host 'Installed. Open MaaXuexi-Local.lnk, then configure your key and choose tasks in the browser.'
    Write-Host 'No task, public comment, paid API request, or scheduled job was started.'
} catch { Write-Error $_.Exception.Message; exit 1 }
