param([string]$Source)
$ErrorActionPreference = 'Stop'
$temp = $null
try {
    if (Test-Path (Join-Path $HOME 'scripts/export-skills.sh')) {
        throw '원본 관리 기기에서는 설치를 중단합니다.'
    }
    if (-not $Source) {
        $temp = Join-Path ([IO.Path]::GetTempPath()) ('ad-guardrail-' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $temp | Out-Null
        $zip = Join-Path $temp 'repo.zip'
        Invoke-WebRequest -Uri 'https://github.com/axseo-education/claude-skills/archive/refs/heads/master.zip' -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath $temp
        $Source = Join-Path $temp 'claude-skills-master/pilot/ad-guardrail'
    }
    $Source = (Resolve-Path -LiteralPath $Source).Path
    $manifest = Join-Path $Source 'install/MANIFEST.txt'
    $requiredFiles = @(Get-Content -LiteralPath $manifest -Encoding UTF8 | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($requiredFiles.Count -eq 0) { throw '스킬 원본 파일 목록이 비어 있습니다.' }
    foreach ($required in $requiredFiles) {
        if ($required -notmatch '^[A-Za-z0-9_-][A-Za-z0-9_./-]*$' -or $required.Split('/') -contains '..') {
            throw '스킬 원본 파일 목록의 상대경로가 잘못되었습니다.'
        }
        if (-not (Test-Path -LiteralPath (Join-Path $Source $required) -PathType Leaf)) {
            throw '스킬 원본 파일이 누락되었습니다.'
        }
    }
    $destination = Join-Path $HOME '.claude/skills/ad-guardrail'
    $fullDestination = [IO.Path]::GetFullPath($destination)
    if ($Source -eq $fullDestination -or $Source.StartsWith($fullDestination + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw '설치 대상 내부를 Source로 사용할 수 없습니다.'
    }
    New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
    if (Test-Path -LiteralPath $destination) {
        $backup = $destination + '.backup-' + (Get-Date -Format 'yyyy-MM-dd-HH-mm-ss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 4)
        Move-Item -LiteralPath $destination -Destination $backup
        Write-Host "기존 폴더 백업: $backup"
    }
    Copy-Item -LiteralPath $Source -Destination $destination -Recurse
    $candidates = @(
        @{ Exe = 'py'; Args = @('-3') },
        @{ Exe = 'python3'; Args = @() },
        @{ Exe = 'python'; Args = @() },
        @{ Exe = 'uv'; Args = @('run', '--python', '3.12', '--no-project', '--offline', '--no-python-downloads', 'python') }
    )
    $runner = $null
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $command) { continue }
        $probeArgs = @($candidate.Args) + @('-c', 'import sys; print(str(sys.version_info[0])+chr(46)+str(sys.version_info[1]))')
        try {
            $version = & $command.Source @probeArgs 2>$null
            if ($LASTEXITCODE -eq 0 -and "$version" -match '^3\.(\d+)$' -and [int]$Matches[1] -ge 10) {
                $runner = @($command.Source) + @($candidate.Args)
                break
            }
        } catch { continue }
    }
    if (-not $runner) { throw 'Python 3.10 이상 실행기를 준비하세요.' }
    $executable = $runner[0]
    $setupArgs = @($runner | Select-Object -Skip 1) + @((Join-Path $destination 'scripts/setup.py'))
    & $executable @setupArgs
    if ($LASTEXITCODE -ne 0) { throw '권한 병합에 실패했습니다.' }
    $runtime = Get-Content -LiteralPath (Join-Path $HOME '.ad-guardrail/runtime.json') -Raw | ConvertFrom-Json
    $token = [Environment]::GetEnvironmentVariable('ACCESS_TOKEN', 'User')
    if ([string]::IsNullOrWhiteSpace($token)) {
        Write-Host ('토큰 등록 필요: & "' + (Join-Path $destination 'install/set-token.ps1') + '"')
        Write-Host 'Claude Code와 터미널을 모두 다시 열고 설치 명령을 재실행하세요.'
        exit 2
    }
    [Environment]::SetEnvironmentVariable('ACCESS_TOKEN', $token, 'Process')
    $token = $null
    $executable = $runtime.runner[0]
    $preflightArgs = @($runtime.runner | Select-Object -Skip 1) + @((Join-Path $destination 'scripts/preflight.py'))
    & $executable @preflightArgs
    if ($LASTEXITCODE -ne 0) { throw '사전 점검에 실패했습니다. 설치 안내를 확인하세요.' }
    Write-Host '설치 완료. Claude Code와 터미널을 모두 다시 여세요.'
} catch {
    Write-Host '설치 실패. 원본 관리 기기 여부, Source 파일, 실행기, 권한 및 사전 점검을 확인하세요.'
    exit 1
} finally {
    $token = $null
    if ($temp -and (Test-Path -LiteralPath $temp)) {
        Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
