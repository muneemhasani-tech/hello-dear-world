# local-setup.ps1 — NINE AI OS workspace migration + cleanup
# Run from PowerShell as: .\local-setup.ps1
# Requires: PowerShell 5.1+ (Windows built-in)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Downloads   = "C:\Users\user\Downloads"
$AI_OS       = "C:\Users\user\AI_OS"
$MRA         = "C:\Users\user\mra-content-auditor"

Write-Host "`n=== NINE AI OS Workspace Migration ===" -ForegroundColor Cyan

# ─────────────────────────────────────────────────────────────
# 1. WIPE INSTALLER WASTELAND
# ─────────────────────────────────────────────────────────────
Write-Host "`n[1] Checking installer files..." -ForegroundColor Yellow

$ollamaExe = "$Downloads\Other\EXE_OllamaSetup_2026-05-18.exe"
$dockerExe  = "$Downloads\Other\EXE_Docker_Desktop_Installer_2026-05-18.exe"

$ollamaRunning = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
$dockerRunning = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

if ($ollamaRunning) {
    Write-Host "  Ollama is running. Removing installer..." -ForegroundColor Green
    if (Test-Path $ollamaExe) { Remove-Item $ollamaExe -Force; Write-Host "  Deleted: $ollamaExe" }
} else {
    Write-Host "  WARNING: Ollama process not detected. Skipping installer delete (run Ollama first)." -ForegroundColor Red
}

if ($dockerRunning) {
    Write-Host "  Docker Desktop is running. Removing installer..." -ForegroundColor Green
    if (Test-Path $dockerExe) { Remove-Item $dockerExe -Force; Write-Host "  Deleted: $dockerExe" }
} else {
    Write-Host "  WARNING: Docker Desktop process not detected. Skipping installer delete." -ForegroundColor Red
}

# ─────────────────────────────────────────────────────────────
# 2. BUILD AND MIGRATE NINE AI OS ARCHITECTURE
# ─────────────────────────────────────────────────────────────
Write-Host "`n[2] Creating AI_OS directory structure..." -ForegroundColor Yellow

$dirs = @(
    "$AI_OS\context",
    "$AI_OS\decisions",
    "$AI_OS\references",
    "$AI_OS\skills\onboard",
    "$AI_OS\skills\audit",
    "$AI_OS\skills\level-up",
    "$AI_OS\skills\cold-email"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
    Write-Host "  Created: $d"
}

$moves2 = @(
    @{ src="$Downloads\Code\CODE_CLAUDE_2026-05-22.md";                      dst="$AI_OS\CLAUDE.md" },
    @{ src="$Downloads\Code\CODE_EXPANSIONS_2026-05-16.md";                  dst="$AI_OS\EXPANSIONS.md" },
    @{ src="$Downloads\Code\CODE_aios_question_2026-05-16.md";               dst="$AI_OS\aios-questionnaire.md" },
    @{ src="$Downloads\Code\CODE_connections_2026-05-16.md";                 dst="$AI_OS\connections.md" },
    @{ src="$Downloads\Code\CODE_about_business_2026-05-16.md";              dst="$AI_OS\context\about-business.md" },
    @{ src="$Downloads\Code\CODE_priorities_2026-05-16.md";                  dst="$AI_OS\context\priorities.md" },
    @{ src="$Downloads\Code\CODE_log_2026-05-16.md";                         dst="$AI_OS\decisions\log.md" },
    @{ src="$Downloads\Code\CODE_voice_2026-05-16.md";                       dst="$AI_OS\references\voice.md" },
    @{ src="$Downloads\Code\CODE_voice_1_2026-05-28.md";                     dst="$AI_OS\references\voice_mra.md" },
    @{ src="$Downloads\Code\CODE_SKILL_2026-05-16.md";                       dst="$AI_OS\skills\onboard\SKILL.md" },
    @{ src="$Downloads\Code\CODE_SKILL_1_2026-05-16.md";                     dst="$AI_OS\skills\audit\SKILL.md" },
    @{ src="$Downloads\Code\CODE_SKILL_2_2026-05-16.md";                     dst="$AI_OS\skills\level-up\SKILL.md" },
    @{ src="$Downloads\Code\CODE_SKILL_cold_email_workflow_2026-05-16.md";   dst="$AI_OS\skills\cold-email\SKILL.md" }
)

Write-Host "`n  Migrating AI_OS files..."
foreach ($m in $moves2) {
    if (Test-Path $m.src) {
        Move-Item -Path $m.src -Destination $m.dst -Force
        Write-Host "  Moved: $(Split-Path $m.src -Leaf) -> $($m.dst.Replace('C:\Users\user\',''))"
    } else {
        Write-Host "  MISSING: $($m.src)" -ForegroundColor Red
    }
}

# ─────────────────────────────────────────────────────────────
# 3. RESTRUCTURE MRA CONTENT AUDITOR KNOWLEDGE
# ─────────────────────────────────────────────────────────────
Write-Host "`n[3] Creating MRA knowledge directory..." -ForegroundColor Yellow

New-Item -ItemType Directory -Path "$MRA\knowledge" -Force | Out-Null
New-Item -ItemType Directory -Path "$MRA\auditor\data\scripts" -Force | Out-Null
Write-Host "  Created: $MRA\knowledge"
Write-Host "  Created: $MRA\auditor\data\scripts"

$moves3 = @(
    @{ src="$Downloads\Documents\DOC_MRA_SOP_Document_2026-03-02.docx";                      dst="$MRA\knowledge\MRA_SOP_Document.docx" },
    @{ src="$Downloads\Documents\DOC_SOP_Training_Document_2026-03-04.docx";                 dst="$MRA\knowledge\SOP_Training_Document.docx" },
    @{ src="$Downloads\Documents\DOC_MRA_Universal_Sales_Marketing_SOP_2026-03-02.pdf";      dst="$MRA\knowledge\MRA_Universal_Sales_Marketing_SOP.pdf" },
    @{ src="$Downloads\Documents\DOC_mra_studio_setup_2026-05-24.xlsx";                      dst="$MRA\knowledge\mra_studio_setup.xlsx" },
    @{ src="$Downloads\Documents\DOC_MRA_Content_Calendar_Master_2026-05-22.xlsx";           dst="$MRA\knowledge\MRA_Content_Calendar_Master.xlsx" },
    @{ src="$Downloads\Documents\DOC_Map_of_Bashundhara_2026-03-11.docx";                    dst="$MRA\knowledge\Map_of_Bashundhara.docx" },
    @{ src="$Downloads\Documents\DOC_Map_of_Bashundharadocx_2026-03-31.pdf";                 dst="$MRA\knowledge\Map_of_Bashundhara.pdf" },
    @{ src="$Downloads\Documents\DOC_RealEstate_Keyword_Analysis_2026-03-18.pdf";            dst="$MRA\knowledge\RealEstate_Keyword_Analysis.pdf" },
    @{ src="$Downloads\Documents\DOC_Chinese_introductory_video_script_2026-05-29.txt";      dst="$MRA\auditor\data\scripts\Chinese_introductory_video_script.txt" }
)

foreach ($m in $moves3) {
    if (Test-Path $m.src) {
        Move-Item -Path $m.src -Destination $m.dst -Force
        Write-Host "  Moved: $(Split-Path $m.src -Leaf)"
    } else {
        Write-Host "  MISSING: $($m.src)" -ForegroundColor Red
    }
}

# ─────────────────────────────────────────────────────────────
# 4. CONFIGURE MRA ACTIVE ENVIRONMENT
# ─────────────────────────────────────────────────────────────
Write-Host "`n[4] Configuring MRA .env..." -ForegroundColor Yellow

$envFile    = "$MRA\.env"
$envExample = "$MRA\.env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  Created .env from .env.example"
    } else {
        # Create a minimal .env if no example exists
        @"
# MRA Content Auditor — environment variables
HF_TOKEN=your_huggingface_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
"@ | Set-Content $envFile
        Write-Host "  Created minimal .env (no .env.example found)"
    }
} else {
    Write-Host "  .env already exists — skipping."
}

# ─────────────────────────────────────────────────────────────
# 5. PRINT RESTORED WORKSPACE HIERARCHY
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Restored Workspace Hierarchy ===" -ForegroundColor Cyan

Write-Host "`nAI_OS\" -ForegroundColor White
Get-ChildItem $AI_OS -Recurse | ForEach-Object {
    $indent = "  " * ($_.FullName.Split("\").Count - $AI_OS.Split("\").Count)
    Write-Host "$indent$($_.Name)"
}

Write-Host "`nmra-content-auditor\" -ForegroundColor White
Get-ChildItem $MRA -Recurse | ForEach-Object {
    $indent = "  " * ($_.FullName.Split("\").Count - $MRA.Split("\").Count)
    Write-Host "$indent$($_.Name)"
}

Write-Host "`n=== ACTION REQUIRED ===" -ForegroundColor Magenta
Write-Host "Open C:\Users\user\mra-content-auditor\.env and set:"
Write-Host "  HF_TOKEN=<your HuggingFace token>"
Write-Host "  ANTHROPIC_API_KEY=<your Anthropic API key>"
Write-Host "`nAll operations complete." -ForegroundColor Green
