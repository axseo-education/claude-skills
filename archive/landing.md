# CCFM 랜딩페이지 자동 제작

사용자가 $ARGUMENTS 로 랜딩페이지 요구사항을 전달합니다.
예시: `/landing 봄 시즌 프로모션, 20% 할인, CTA "지금 쇼핑하기"`

아래 파이프라인을 **반드시 순서대로** 실행하세요.

---

## Step 1: 요구사항 분석

사용자 입력에서 아래 정보를 추출합니다. 누락된 항목은 합리적으로 추론합니다.

| 항목 | 추출 |
|------|------|
| 목적 | 캠페인/이벤트/제품소개/리드수집 등 |
| 타겟 | 누구를 대상으로? |
| 핵심 메시지 | 한 줄로 요약 |
| USP (차별점) | 왜 선택해야 하는지 |
| CTA | 버튼 텍스트 |
| 톤앤매너 | 전문적/감성적/직설적/긴급 등 |
| 수치/증거 | 할인율, 사례, 통계 등 |

---

## Step 2: 설득 프레임워크 + 섹션 설계

### 기본 프레임워크: PASONA + StoryBrand 하이브리드

PASONA(Problem→Affinity→Solution→Offer→Narrowing→Action)와 StoryBrand(고객=주인공)를 결합합니다.

**흐름**: 고객의 문제 공감 → 해결사 등장 → 증거 제시 → 긴급성 + 행동

### 치알디니 설득 6원칙 (섹션에 반드시 녹일 것)
| 원칙 | 적용 방법 |
|------|----------|
| **사회적 증거** | 후기, 고객 수, "N명이 선택" |
| **권위** | 전문성, 경력, 수상, 미디어 노출 |
| **희소성** | 한정 기간, 잔여 수량, 마감 카운트다운 |
| **호혜성** | 무료 진단, 무료 체험, 무료 리포트 |
| **일관성** | 작은 약속("이메일만 입력") → 큰 전환 |
| **호감** | 친근한 톤, 공감, 스토리텔링 |

### 선택 가능한 프레임워크 (사용자 요청 시)
- **PAS**: Problem→Agitate→Solve — 심플 전환 페이지
- **AIDA**: Attention→Interest→Desire→Action — 범용
- **BAB**: Before→After→Bridge — 변화 강조
- **4P**: Picture→Promise→Prove→Push — 비주얼 중심

### 섹션 풀 (목적에 맞게 **7~12개** 선택)

**필수 (모든 랜딩에 포함):**
1. **Header**: 로고(텍스트) + 네비게이션 + CTA 버튼 (고정)
2. **Hero** [PASONA: Problem + Attention]: 대형 헤드라인(20자 이내, 고객의 고민으로 시작) + 서브카피 + 주 CTA + 신뢰 보조 텍스트
3. **CTA Final** [Action]: 페이지 하단 CTA 반복 (히어로와 다른 카피, 긴급성 추가)

**Problem → Affinity (공감):**
- **문제 제기 (Situation)**: 타겟이 겪는 3가지 고민/문제 카드. "이런 경험, 있으시죠?" 톤
- **고통 증폭 (Agitate)**: 문제를 방치하면 어떻게 되는지 — 비용, 시간 낭비, 기회 손실 (숫자로)
- **Before/After**: 도입 전 vs 후 비교 테이블. 변화를 시각적으로 보여줌

**Solution → Offer (해결 + 제안):**
- **해결책 (Solution)**: "이렇게 해결합니다" — 서비스/제품의 핵심 가치 3~4개
- **특장점 (Features)**: 아이콘 + 제목 + 설명 그리드 (2x2 또는 3열)
- **프로세스 (How it works)**: 3~5단계 스텝 플로우. "이렇게 쉽습니다"
- **가격/혜택 (Pricing)**: 가격 카드 또는 혜택 리스트. 호혜성 원칙 적용

**Narrowing (증거 + 긴급성):**
- **숫자로 보는 성과 (Stats)**: 큰 숫자 3~4개 + 카운터 애니메이션 [권위]
- **사례 (Case Study)**: 실제 고객 성과 사례 카드 [사회적 증거]
- **후기 (Testimonials)**: 별점 + 인용문 + 이름/직책 2~3개 [사회적 증거]
- **팀/강사 소개 (About)**: 전문성 + 경력 [권위]
- **미디어/로고 (Trust Bar)**: 파트너사 로고 나열 [권위]
- **FAQ**: 접을 수 있는 5~6개 Q&A. 구매 장벽 해소 [일관성]
- **긴급성 (Urgency)**: 마감 날짜, 잔여 수량, 한정 혜택 [희소성]

**Action (행동):**
- **폼 (Contact)**: 이름/연락처/이메일 + 제출 버튼. 최소 필드 [일관성]
- **플로팅 CTA**: 스크롤해도 항상 보이는 하단 바 또는 버튼

기획안을 사용자에게 보여주고, 승인 후 제작합니다.

---

## Step 3: HTML 제작

### 디자인 시스템

**레이아웃:**
- max-width: 1200px, 중앙 정렬
- 섹션 간 padding: 96px~120px (데스크톱), 64px (모바일)
- 그리드: CSS Grid, 2~3열
- 모바일 퍼스트 반응형

**타이포그래피:**
- 폰트: Pretendard (CDN: https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css)
- Hero 헤드라인: clamp(2.5rem, 6vw, 4.5rem), font-weight: 800, line-height: 1.1
- 섹션 제목: clamp(2rem, 4vw, 3rem), font-weight: 700
- 본문: 1.125rem, line-height: 1.8
- 색상: #0f172a (라이트), #EDEDED (다크)
- letter-spacing: 제목 -0.03em, 본문 0

**색상:**
- Primary Accent: #e5007e (CCFM 핑크) — CTA, 강조, 링크
- Secondary: #ff4da6 (연핑크) — 호버, 보조 강조
- Background: #FAFAF9 (라이트 기본)
- Surface: #FFFFFF (카드)
- Text: #0f172a
- Text Secondary: #64748b
- Success: #10b981 (긍정 수치)
- 그라디언트: linear-gradient(135deg, #e5007e, #ff4da6) — Hero 배경 또는 CTA 버튼

**컴포넌트:**
- CTA 버튼: padding 16px 32px, border-radius 12px, font-weight 700, 그라디언트 배경, 흰 텍스트, box-shadow, hover시 translateY(-2px) + shadow 확대
- 카드: border-radius 16px, padding 40px, box-shadow: 0 1px 3px rgba(0,0,0,0.08), hover 시 shadow 확대
- 통계 숫자: font-size clamp(3rem, 6vw, 5rem), font-weight 800, color accent
- FAQ: `<details>` + `<summary>`, 부드러운 열림 애니메이션
- 네비게이션: 고정 header, backdrop-filter blur, 스크롤 시 축소

**히어로 비주얼 (필수 — 하나 이상 적용):**
- **움직이는 그라디언트 배경**: CSS animation으로 그라디언트 위치/각도 순환. 2~3색 조합, 6~8초 주기
- **Lottie 애니메이션**: CDN(`https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js`)으로 JSON 벡터 애니메이션. 히어로 우측 또는 배경
- **파티클/도트 필드**: Canvas 또는 CSS로 떠다니는 점/선 애니메이션. 마우스 반응형
- **SVG 라인 드로잉**: 히어로 진입 시 SVG path가 그려지는 애니메이션 (stroke-dashoffset)
- **패럴랙스 레이어**: 스크롤 시 배경/전경 다른 속도로 이동
- **영상 임베드**: 사용자가 YouTube/Vimeo URL 제공 시 임베드. 자동 재생, 음소거, 루프

**애니메이션 (필수):**
- 스크롤 리빌: IntersectionObserver, opacity 0→1 + translateY(40px→0), stagger 0.1s
- 숫자 카운터: requestAnimationFrame, easeOut
- Hero: 페이드인 + 위로 올라오기, 딜레이 순차
- 호버: CTA translateY(-2px), 카드 shadow 확대
- 부드러운 스크롤: scroll-behavior: smooth
- 섹션 전환: 각 섹션 진입 시 컨텐츠 순차 등장 (stagger 80ms)
- `@media (prefers-reduced-motion: reduce)` 존중

**반응형:**
```
@media (max-width: 768px) {
  - 그리드 → 1열
  - Hero 텍스트 축소
  - 섹션 패딩 축소
  - 네비게이션 → 햄버거 메뉴
}
@media (max-width: 375px) {
  - overflow-x: hidden
  - 최소 패딩 16px
}
```

### 코드 규칙
- 단일 HTML 파일, CSS/JS 인라인
- 시맨틱 HTML: header, nav, main, section, footer
- 모든 인터랙티브 요소 hover 상태
- `<html lang="ko">`
- 이미지 대신 SVG 아이콘 또는 CSS 그라디언트로 비주얼 처리
- 폼은 프론트엔드만 (실제 제출은 미구현, placeholder)

### HTML 기본 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{페이지 제목}</title>
  <meta name="description" content="{페이지 설명}">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
  <style>/* 전체 CSS 인라인 */</style>
</head>
<body>
  <header><!-- 고정 네비게이션 --></header>
  <main>
    <section id="hero"><!-- Hero --></section>
    <!-- 섹션들 -->
    <section id="cta-final"><!-- 최종 CTA --></section>
  </main>
  <footer><!-- 푸터 --></footer>
  <script>/* 애니메이션, 메뉴 토글, 카운터, 스무스 스크롤 */</script>
</body>
</html>
```

### 품질 기준
- **첫인상**: 2초 안에 "프로페셔널"이라고 느껴야 함
- **모바일**: 375px에서 완벽하게 작동
- **속도**: 외부 이미지 없이 CSS만으로 비주얼 처리
- **CTA 명확성**: 스크롤 어디서든 CTA가 보이거나 접근 가능
- **레퍼런스 수준**: https://vibe-consulting.vercel.app/ , https://www.vrl.co.kr/ 수준

---

## Step 4: 파일 저장 및 확인

1. `~/Downloads/{케밥케이스-파일명}.html`에 저장
2. `start` 명령으로 브라우저에서 열기
3. 모바일 뷰 확인 안내

---

## Step 5: Vercel 배포 (자동)

1. **프로젝트명 생성**: 한글 의미를 영어로 번역 (음역 금지)
   - 접두사: `ccfm-landing-`
   - 예: "봄 세일 프로모션" → `ccfm-landing-spring-sale`
2. **배포**:
   ```
   mkdir -p $TEMP/{프로젝트명}
   cp ~/Downloads/{파일명}.html $TEMP/{프로젝트명}/index.html
   cd $TEMP/{프로젝트명}
   vercel --yes --prod
   ```
3. **URL 제공**: `✅ 배포 완료: https://{프로젝트명}.vercel.app`

---

## 응답 형식
- 기획안 제시: 섹션 목록 + 각 섹션 핵심 내용
- 승인 후 제작
- 제작 완료: 로컬 파일 경로 + Vercel URL