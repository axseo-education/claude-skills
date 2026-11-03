$ErrorActionPreference = 'Stop'
$existingScopes = @('User', 'Process', 'Machine') | Where-Object {
    -not [string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable('ACCESS_TOKEN', $_))
}
if ($existingScopes) {
    Write-Warning ("기존 토큰이 있습니다. 공용 토큰이면 관리자에게 확인 (범위: " + ($existingScopes -join ', ') + ')')
    if ($existingScopes -contains 'Machine') {
        Write-Host 'Machine 토큰이 있습니다. 새 프로세스에서는 User 값이 우선 적용됩니다.'
    }
    if ((Read-Host '계속하려면 Y를 입력하세요') -cne 'Y') {
        Write-Host '토큰 교체를 취소했습니다.'
        exit 1
    }
}
$secret = Read-Host '담당 계정 전용 토큰을 입력하세요' -AsSecureString
$pointer = [IntPtr]::Zero
try {
    if ($secret.Length -eq 0) { throw '빈 토큰은 등록할 수 없습니다.' }
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    [Environment]::SetEnvironmentVariable(
        'ACCESS_TOKEN',
        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer),
        'User'
    )
    Write-Host '등록했습니다. Claude Code와 터미널을 모두 다시 여세요.'
} catch {
    Write-Host '토큰 등록에 실패했습니다. 빈 입력 여부와 사용자 환경변수 권한을 확인하세요.'
    exit 1
} finally {
    if ($pointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
    $secret.Dispose()
}
