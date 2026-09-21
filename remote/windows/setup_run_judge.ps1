<#
    remote\windows\setup_run_judge.ps1 — one-time setup for the remote executor.

    MANUAL STEP FIRST (cannot be scripted, ~2 minutes on the professor's machine):
      Boot into BIOS/UEFI and find the "AC Power Loss" / "Restore on AC Power
      Loss" / "State After G3" option. Set it to POWER ON (or "Last State").
      This is what makes the PC boot itself when electricity returns after a
      power cut — everything else in this project resumes automatically, but
      only if the box physically powers itself back on.

    Then, in an ADMIN PowerShell from the job directory:
      .\remote\windows\setup_run_judge.ps1 -JobDir "C:\judge"

    What it does:
      1. Optionally installs Ollama (winget) if not present.
      2. Pulls the pinned model tags listed in -Models.
      3. Creates the "JudgeRunner" scheduled task (logs on -> runs the job).
      4. Sets the AC power plan to High performance / never sleep.
      5. Enables AutoAdminLogon for the current user (no-password boot) —
         requires one reboot to take effect. Skip with -SkipAutoLogon.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$JobDir,
    [string[]]$Models = @("qwen3:14b"),
    [switch]$InstallOllama,
    [switch]$SkipAutoLogon
)

$ErrorActionPreference = "Stop"
$Job = Resolve-Path $JobDir

# 1. Ollama ---------------------------------------------------------------
if ($InstallOllama -and -not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Warning "ollama not found. Re-run with -InstallOllama or install from ollama.com."
}

# 2. Pull pinned models ---------------------------------------------------
foreach ($m in $Models) {
    Write-Host "pulling $m ..."
    & ollama pull $m
}

# 3. Scheduled task (logon -> run job) ------------------------------------
$xmlPath = Join-Path $PSScriptRoot "JudgeRunner.xml"
$xml = (Get-Content $xmlPath -Raw) -replace '%JOBDIR%', ($Job -replace '\\', '\\')
$tmp = Join-Path $env:TEMP "JudgeRunner.xml"
$tmp | Set-Content -Value $xml -Encoding UTF8
schtasks /Create /F /TN "JudgeRunner" /XML $tmp | Out-Null
Write-Host "scheduled task JudgeRunner created -> $Job"

# 4. Power plan: no sleep on AC -------------------------------------------
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP STANDBYIDLE 0
powercfg /setactive SCHEME_CURRENT

# 5. AutoAdminLogon --------------------------------------------------------
if (-not $SkipAutoLogon) {
    $env:USERNAME = $env:USERNAME
    $reg = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    New-ItemProperty -Path $reg -Name AutoAdminLogon -Value 1 -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $reg -Name DefaultUserName -Value $env:USERNAME -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $reg -Name DefaultDomainName -Value $env:USERDOMAIN -PropertyType String -Force | Out-Null
    # DefaultPassword is REQUIRED by AutoAdminLogon (stored as plaintext at rest).
    # Set it explicitly:  .\setup_run_judge.ps1 -SkipAutoLogon  then set it via:
    #   $reg = "HKLM:\...\Winlogon"; Set-ItemProperty -Path $reg -Name DefaultPassword -Value "thepassword"
    Write-Host "AutoAdminLogon enabled. You MUST set DefaultPassword (see comment) for it to work."
}
Write-Host "setup complete. Reboot once, then verify:  schtasks /Query /TN JudgeRunner"