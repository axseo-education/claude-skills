# CCFM 교육용 스킬 설치 (Windows PowerShell)
#
#   git 이나 bash 가 없어도 됩니다. PowerShell 에서 아래 한 줄:
#
#   irm https://raw.githubusercontent.com/axseo-education/claude-skills/master/install.ps1 | iex
#
# 이미 저장소를 내려받았다면:  powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = 'Stop'

$repoZip  = 'https://github.com/axseo-education/claude-skills/archive/refs/heads/master.zip'
$skillDir = Join-Path $HOME '.claude\skills'
$cmdDir   = Join-Path $HOME '.claude\commands'

# 스크립트 옆에 education 폴더가 있으면 그걸 쓰고, 없으면 ZIP 을 받아 푼다
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot 'education'))) {
  $src = Join-Path $PSScriptRoot 'education'
  $tmp = $null
} else {
  $tmp = Join-Path $env:TEMP ('ccfm-skills-' + [guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $tmp -Force | Out-Null
  $zip = Join-Path $tmp 'repo.zip'
  Write-Host '스킬을 내려받는 중...'
  Invoke-WebRequest -Uri $repoZip -OutFile $zip
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  $src = Join-Path $tmp 'claude-skills-master\education'
}

if (-not (Test-Path $src)) { throw "education 폴더를 찾지 못했습니다: $src" }

New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
New-Item -ItemType Directory -Path $cmdDir   -Force | Out-Null

$backup = Join-Path $HOME ('.claude\skills-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$n = 0

Write-Host ''
Write-Host 'CCFM 스킬을 설치합니다.'
Write-Host ''

foreach ($d in Get-ChildItem -Path $src -Directory) {
  $dest = Join-Path $skillDir $d.Name
  if (Test-Path $dest) {
    New-Item -ItemType Directory -Path $backup -Force | Out-Null
    Move-Item $dest (Join-Path $backup $d.Name)
  }
  Copy-Item $d.FullName $dest -Recurse
  Write-Host "  /$($d.Name)"
  $n++
}

foreach ($f in Get-ChildItem -Path $src -Filter *.md -File) {
  $name = [IO.Path]::GetFileNameWithoutExtension($f.Name)
  $dest = Join-Path $cmdDir ($name + '.md')
  if (Test-Path $dest) {
    New-Item -ItemType Directory -Path $backup -Force | Out-Null
    Move-Item $dest (Join-Path $backup ($name + '.md'))
  }
  Copy-Item $f.FullName $dest
  Write-Host "  /$name"
  $n++
}

if ($tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host ''
Write-Host "설치 완료 - $n 개."
if (Test-Path $backup) { Write-Host "기존 파일은 $backup 에 옮겨 뒀습니다." }
Write-Host 'Claude Code 를 다시 켜고 / 를 눌러 확인하세요.'
