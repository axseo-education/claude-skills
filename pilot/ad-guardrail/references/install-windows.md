# 설치와 문제 해결

브랜드 시범용 스킬이다. 배포 위치는 `pilot/ad-guardrail/`이며 전사 설치기와 education manifest에는 넣지 않는다.
Python 3.10 이상, meta CLI, Claude Code를 먼저 준비한다. 공개 배포는 담당자의 export 검사와 승인 후 진행한다.

PowerShell에서 다음 한 줄을 실행한다. 저장소 ZIP 다운로드, 기존 폴더 백업, 스킬 복사, 실행기 탐지,
권한 병합, 토큰이 있으면 사전 점검까지 수행한다.

```powershell
irm https://raw.githubusercontent.com/axseo-education/claude-skills/master/pilot/ad-guardrail/install/install.ps1 | iex
```

이미 내려받은 스킬 폴더를 사용할 때:

```powershell
& .\install\install.ps1 -Source 'C:\pilot\ad-guardrail'
```

- `~/scripts/export-skills.sh`가 있는 원본 관리 기기에서는 중단한다.
- 설치 대상은 `~/.claude/skills/ad-guardrail/`이다. 기존 폴더는 날짜와 난수가 붙은 백업으로 이동한다.
- setup.py는 기존 settings.json과 allow를 보존하며 ask/deny를 병합한다. 변경 전 설정도 백업한다.
- 실행기는 `py -3`, `python3`, `python`, `uv run --python 3.12 --no-project` 순서다.
  탐지에는 다운로드를 허용하지 않으므로 런타임은 미리 준비한다.
- 사용자 ACCESS_TOKEN이 없으면 설치 완료로 표시하지 않고 종료 코드 2와 등록 명령을 안내한다.
  `& "$HOME/.claude/skills/ad-guardrail/install/set-token.ps1"`을 별도 PowerShell에서 직접 실행한다.
  User·Process·Machine 어느 범위든 기존 토큰이 있으면 값 대신 해당 범위 이름과 함께 경고하고 Y 확인을 요구한다.
  Machine 값이 있으면 새 프로세스에서 User 값이 우선 적용됨을 안내한다.
  입력은 화면에 표시되지 않으며 빈 입력은 저장하지 않고 거부한다.
  Claude Code와 터미널을 모두 다시 열고 설치 명령을 재실행한다.
- 토큰이 있으면 현재 설치 프로세스에 반영하고 저장된 runner로 preflight를 실행한다.
  preflight 실패는 종료 코드 1이며 설치 완료 문구가 나오지 않는다. 복사·백업 파일은 보존된다.
- 설치 후 담당 KRW 계정 하나의 수집·진단과 실제 Claude Code 승인 프롬프트를 현장에서 검증한다.
  권한 문자열 시뮬레이터 통과는 실제 하네스 프롬프트 표시를 보증하지 않는다.

## 문제 해결

- 토큰은 담당 계정 전용으로 등록한다. 사용자 환경변수는 같은 사용자 프로세스에 대한 비밀 경계가 아니다.
- `token_missing` 또는 권한 실패: 토큰 등록 후 앱 재시작과 담당 계정 자산 할당을 확인한다.
- meta CLI 없음: Windows는 `meta.exe`, macOS는 `meta`가 PATH에서 발견되어야 한다.
- 시간대: 계정의 숫자 `timezone_offset_hours_utc`로 고정 오프셋을 쓴다. 소수도 지원한다.
  누락·문자열·유효하지 않은 값이면 수집/판정을 중단한다. 시간대 DB 설치는 필요 없다.
- `collect_deadline`: 전체 수집 120초를 넘겨 스냅샷을 저장하지 않았다. 요청별 제한은 최대 20초다.
- `ledger_stale_lock_check_owner`: 60초 넘은 잠금이다. 실행 중인 작업이 없는지 확인한 뒤
  관리자가 `~/.ad-guardrail/ledger.lock`만 제거한다. 원장을 삭제하거나 상한을 우회하지 않는다.
- `ledger_lock_timeout`: 다른 작업이 잠금을 점유했다. 중복 실행을 중단하고 종료를 기다린다.
- JSON 파손: 기존 파일을 덮어쓰지 말고 백업과 비교해 복구한다.
- 비상정지: `~/.ad-guardrail/STOP`을 만든다. 사용자 확인 후에만 제거한다.
- run/일 상한: 실패하거나 검증하지 못한 시도도 소비한다. 오래된 run은 새 수집으로 대체한다.
- 공개 tree에 snapshots, runs, log, 환경 파일 또는 계정 데이터가 있으면 배포를 중단한다.

Graph 버전은 `runtime.py`의 `v22.0`을 유지한다. 수집 시점의 고정 오프셋을 사용하므로
일광절약시간 변경을 과거 날짜에 소급 계산하지 않는다. 현재 KRW 시범 범위의 설계 선택이다.
