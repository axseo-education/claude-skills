# CCFM 교육용 스킬

CCFM AI 스터디에서 쓰는 Claude Code 스킬 모음입니다.
사내 서버·API 키 없이 **직원 PC 단독으로 도는 것만** 담았습니다.

## 설치

가장 쉬운 방법은 Claude Code 에게 시키는 것입니다.

```
https://github.com/axseo-education/claude-skills 여기 있는 스킬 설치해줘.
```

직접 하려면 — **Mac / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/axseo-education/claude-skills/master/install.sh | bash
```

**Windows** (git·bash 없어도 됩니다)
```powershell
irm https://raw.githubusercontent.com/axseo-education/claude-skills/master/install.ps1 | iex
```

설치 후 Claude Code 를 다시 켜고 `/` 를 누르면 목록에 나타납니다.

## 포함된 스킬

<!-- AUTO:SKILLS -->
| 스킬 | 설명 |
|------|------|
| `/copy` | 매체 불문 고성과 카피 생성 — 프레임워크·후크·심리트리거·채점을 거쳐 변형 3안을 뽑는다. |
| `/design` | (교육용 판본) |
<!-- /AUTO:SKILLS -->

## 매뉴얼

사용법은 [CCFM AI 스터디](https://ccfm-ai-study.vercel.app) 에서 확인하세요.

---

## 관리자용

이 폴더는 **직접 고치지 않습니다.** 정본은 관리자 기기의 `~/.claude/skills/` 이고,
`export-skills.sh` 가 `export.manifest` 를 읽어 여기로 내보냅니다.

```bash
bash ~/scripts/export-skills.sh          # 내보내기 + 검사만
bash ~/scripts/export-skills.sh --push   # 커밋 + GitHub 반영
```

스크립트가 매번 검사하는 것:

- **대외비** — 사내 브랜드명·실명·고객사가 섞였는지
- **인프라 의존** — 직원 PC 에 없는 서버·키·경로를 참조하는지
- **명세 이탈** — `export.manifest` 에 없는 것이 남아 있는지 (있으면 `archive/` 로 옮김)

직원에게 새 스킬을 주려면 `export.manifest` 에 한 줄 추가하고 다시 돌리면 됩니다.
