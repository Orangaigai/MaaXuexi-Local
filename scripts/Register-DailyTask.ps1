param(
    [ValidateRange(0,23)][int]$Hour = 9,
    [ValidateRange(0,59)][int]$Minute = 0,
    [string]$TaskName = 'MaaXuexi-Local-Daily',
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $PSScriptRoot
$pythonw = Join-Path $appRoot '.venv\Scripts\pythonw.exe'
$entry = Join-Path $PSScriptRoot 'Launch-Hidden.py'
if (!(Test-Path -LiteralPath $pythonw)) { throw 'Run Install-MaaXuexi.ps1 first.' }
$arguments = '"' + $entry + '" --daily'
if ($CheckOnly) {
    @{name=$TaskName;executable=$pythonw;arguments=$arguments;time=('{0:D2}:{1:D2}' -f $Hour,$Minute);timezone=(Get-TimeZone).Id;registered=$false} | ConvertTo-Json
    exit 0
}
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) { throw 'This task name already exists; no scheduled task was replaced. Remove it explicitly or choose -TaskName.' }
$action = New-ScheduledTaskAction -Execute $pythonw -Argument $arguments -WorkingDirectory $appRoot
$trigger = New-ScheduledTaskTrigger -Daily -At ((Get-Date).Date.AddHours($Hour).AddMinutes($Minute))
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 3) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
$record = @{enabled=$true;time=('{0:D2}:{1:D2}' -f $Hour,$Minute);timezone=(Get-TimeZone).Id;task_name=$TaskName}
$configRoot = Join-Path $appRoot 'config'
New-Item -ItemType Directory -Path $configRoot -Force | Out-Null
$encoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $configRoot 'schedule-status.json'),($record | ConvertTo-Json),$encoding)
Write-Host ('Registered {0} at {1:D2}:{2:D2} in the current Windows time zone. The computer must be awake and this user signed in.' -f $TaskName,$Hour,$Minute)
