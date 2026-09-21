<#
    remote\windows\run_judge_job.ps1 — the headless job runner, safe to fire at
    every logon (startup) thanks to resume logic on both sides.

    Steps:
      1. capture current user + machine identity for the heartbeat line;
      2. wait (bounded) for a local Ollama to answer /api/tags;
      3. if Ollama never answers, start `ollama serve` ourselves (watchdog);
      4. run  python remote\run_judge_job.py --job job.json
      5. append one heartbeat line to job.log (progress visible after reboot).

    The Python driver owns the real state machine (stage_done + chunk journal),
    so a power cut at ANY point resumes cleanly the next time Windows boots.
#>
$ErrorActionPreference = "Continue"
$JobDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # two levels up from remote\windows
$Log = Join-Path $JobDir "job.log"
$Heartbeat = Join-Path $JobDir "job.heartbeat"
$Python = Join-Path $JobDir ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }

Add-Content -Path $Log -Value "[{0}] job runner started on {1}" -f (Get-Date -Format o), $env:COMPUTERNAME

# 1+2. wait for Ollama (bounded)
$ok = $false
for ($i = 0; $i -lt 120; $i++) {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch { }
    Start-Sleep -Seconds 5
}

# 3. watchdog: start ollama ourselves if it never came up
if (-not $ok) {
    Add-Content -Path $Log -Value "[$(Get-Date -Format o)] Ollama down; starting ollama serve"
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 15
}

# 4. run the job (driver is fully resumable)
Add-Content -Path $Log -Value "[{0}] invoking: python remote\run_judge_job.py" -f (Get-Date -Format o)
Push-Location $JobDir
& $Python "$JobDir\remote\run_judge_job.py" --job "$JobDir\job.json"
Pop-Location

# 5. heartbeat
Set-Content -Path $Heartbeat -Value (Get-Date -Format "o") -Force
Add-Content -Path $Log -Value "[{0}] job runner finished" -f (Get-Date -Format o)