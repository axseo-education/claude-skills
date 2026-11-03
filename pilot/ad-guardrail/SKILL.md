---
name: ad-guardrail
description: 메타 광고비 가드레일. 원화 전환 광고의 상태를 진단하고 확정된 목표로 끄기 후보를 판정한다. 광고마다 사용자 승인 후 일시중지하고 비추천 표본과 시범 지표를 기록한다.
---

# 메타 광고비 가드레일

상시 보호는 메타 네이티브 규칙이 담당한다. 이 스킬은 실행 시점의 정밀 보조층이다.
하루 2회 실행을 권장한다. 서버, 스케줄러, 중앙 집계 기능은 없다.

## 준비

- 설치 경로는 `~/.claude/skills/ad-guardrail/`이다. 스킬 디렉터리를 작업 디렉터리로 사용한다.
- 최초 설치는 [Windows 설치 안내](references/install-windows.md)를 따른다.
- 토큰을 대화에 입력하거나 보여 달라고 요청하지 않는다. 사용자가 별도 PowerShell 창에서
  `& "$HOME/.claude/skills/ad-guardrail/install/set-token.ps1"`을 직접 실행하도록 안내한다.
- 직원별 시스템 사용자에게 담당 계정만 할당하고 `ads_read`, `ads_management` 권한을 사용한다.
  공용 토큰은 사용하지 않는다. 토큰의 자산 범위가 계정 접근 범위다.
- `~/.ad-guardrail/runtime.json`의 `runner` 배열을 확인한다. 아래 예시의 `python3` 자리에
  탐지된 실행기를 사용한다. `uv`는 저장된 옵션을 모두 유지한다.
- 이 파일의 name은 `/ad-guardrail` 호출을 위한 식별자다. 설명과 사용자 안내는 한국어다.

## 진행

1. `python3 scripts/preflight.py --accounts`를 실행한다. 실패하면 원인과 설치 안내를 전달하고 중단한다.
   반환된 KRW 계정 중 사용자에게 선택받는다. 계정 이름이나 ID를 스킬 파일에 저장하지 않는다.
2. `python3 scripts/collect.py --account <계정>`으로 수집한다.
   설정이 없거나 사용자가 점검을 요청하면 `python3 scripts/diagnose.py --snapshot <스냅샷>`을 실행한다.
   항목별 pass/fail/unknown과 차단 레이어를 보여 준다. 손익분기 CPA는 사람이 입력해야 한다.
   `--breakeven <금액>`으로 재진단하고 제안을 보여 준 뒤 목표 CPA와 LPV 비용을 확정받는다.
   제안 unknown이면 직접 입력받는다. 진단 제안을 자동 확정하지 않는다.
3. 사용자 확정값을 로컬 JSON 파일에 `target_cpa`, `breakeven_cpa`, 선택적 `target_lpv`,
   `confirmed: true`로 작성하고 `python3 scripts/settings.py --account <계정> --input <파일>`로 저장한다.
   레이어 `enabled`, 배수 `l1_spend` 등과 상한 `run_limit`, `day_limit`도 변경 가능하다.
   설정 변경 전 현재 설정을 읽어 기존 값을 보존한다. 상한은 하향만 가능하다.
   목표 LPV 비용을 확정하지 않으면 L5가 차단된다. 모든 확정 목표는 양수여야 한다.
4. `python3 scripts/collect.py --account <계정> --judge`로 새 스냅샷과 판정 run을 만든다.
   판정 수와 활성 전환 광고 수를 비교한다. gate이면 중단하고 원인을 해결한다.
   스크립트가 반환한 모든 충족 레이어와 대표 레이어를 그대로 전달한다.
5. OFF 추천마다 끄기 실행 여부와 별개로 `[동의 / 아님 / skip]` 응답을 받는다.
   `python3 scripts/sample.py --run <run> --ad <광고> --kind recommendation --response <yes|no|skip>`으로 기록한다.
   사용자가 끄기를 요청한 광고만 다음 명령을 **광고 1건마다 별도 도구 호출**한다.
   `python3 scripts/pause.py --run <run> --ad <광고>`
   명령줄에 광고 ID가 보여야 한다. Claude Code 승인 프롬프트가 표시되어야 하며 대화 동의로 대신하지 않는다.
   승인이 표시되지 않으면 실행을 중단하고 권한 설치를 점검한다. 성공 표시는 `status == PAUSED` 검증 후만 가능하다.
6. run의 `samples` 최대 3건에 근거 수치를 보여 주고 “꺼야 했나요?”를 질문한다.
   `python3 scripts/sample.py --run <run> --ad <광고> --kind sample --response <yes|no|skip>`으로 기록한다.
7. `python3 scripts/report.py`로 응답률, 동의율, 미탐률, 표본 수, 실행 일수를 보여 준다.
   skip과 무응답을 별도 표시한다. 응답자 기준 비율과 전체 초대 기준 비율을 혼동하지 않는다.
   AC8 문턱은 확정 전 임시 기준이다.
   비추천 표본의 레이어별 미탐률은 적용 가능한 활성 레이어별로 중복 집계한다. 전체 표본 수는 중복하지 않는다.

## 오류별 사용자 안내

사유 코드와 출력 문구 정본은 `scripts/runtime.py`의 `ERROR_MESSAGES`다. 반환된 `message`를 그대로 전달한다.

| reason | 사용자 안내와 다음 행동 |
| :--- | :--- |
| `rate_limited` | 메타 호출 한도다. `retry_after_minutes`가 있으면 해당 분 뒤 다시 실행하도록 안내한다. 값이 null이면 잠시 후 재실행을 안내한다. 자동 재시도하지 않는다. |
| `graph_error` | 메타 조회 실패다. 숫자 `code`가 있으면 관리자에게 전달한다. 원시 오류 메시지·URL·토큰을 요청하거나 노출하지 않는다. |
| `collect_deadline` | 수집 시간 초과다. 잠시 후 다시 수집한다. |
| `operation_failed_check_local_inputs` | 로컬 인자·설정·입력 파일과 파일 접근 권한을 확인한다. |
| `operation_failed` | 기타 작업 실패다. 관리자에게 확인한다. |

5xx·네트워크 오류만 최초 요청 포함 최대 3회 시도한다. 호출 한도는 즉시 중단한다.
PAUSE 뒤 상태 조회 오류도 위 사유로 안내한다. 원장 `not_verified`는 성공을 뜻하지 않으므로 상태를 확인하고, 끄기를 자동 반복하지 않는다.
캠페인 조인 누락은 스냅샷 `complete:false`로 판정을 중단한다. 세트 누락은 L0의 `l0_start_unknown` 안내를 따른다.

## 출력 양식

| 광고 | 판정 | 대표 / 전체 레이어 | 창 | 숙성 지출 / 전체 지출 | 구매 | 문턱 | 관측 | 사유 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

"광고" 열에는 `ad_name`과 `ad_id`를 함께 쓰고 `campaign_name`도 표시한다. 이름이 없으면 ID를 표시한다.
OFF 추천, 관찰, 정상 개수와 gate 사유를 표 아래에 쓴다. 입력 수치, 설정 버전과 run ID를 함께 제시한다.
실행 결과는 success/failed/not_verified/rejected로 구분한다. 미시도는 성공으로 세지 않는다.
레이어 설명은 [layers.md](references/layers.md)를 사용한다.

## 금지와 중단

- 스크립트 없이 판정하거나, Claude가 판정을 바꾸거나 추가하지 않는다.
- PAUSE는 `pause.py`만 사용한다. 원시 CLI, Graph 쓰기, 임의 Python, `python -c` 쓰기 우회 금지.
- 여러 광고를 한 호출, 루프, 파이프, 셸 묶음, 백그라운드 작업으로 끄지 않는다.
- 증액, 예산 변경, ON, 전환 외 캠페인, 비KRW 계정은 처리하지 않는다.
- 토큰 값, 환경변수 덤프, 인증 헤더, 원시 오류 본문을 출력하거나 기록하지 않는다.
- `~/.ad-guardrail/STOP`이 있으면 끄기가 중단된다. 사용자 확인 없이 STOP을 삭제하지 않는다.
- 스냅샷 불완전, 60분 초과, 목표 미확정, 시간대 불명은 판정 중단 사유다.
- ask/deny 규칙은 명령 문자열을 매칭한다. 실행 경로 변형까지 차단하는 보안 경계가 아니다.
  정상 호출은 반드시 설치된 ask 규칙과 승인 프롬프트를 거친다. 자동 승인 우회 모드는 사용하지 않는다.
- 늦게 귀속되는 구매는 숙성 경계 이후에도 생길 수 있다. 승인 전에 사람이 맥락을 검토한다.
