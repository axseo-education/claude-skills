# CCFM Viz — 시각화 스킬

아이디어, 데이터, 콘텐츠를 CCFM 브랜드 아이덴티티가 적용된 단일 HTML 시각화로 변환합니다.

사용자가 $ARGUMENTS 로 시각화 요청을 전달합니다.
예시: `/viz AI 교육 프로그램 3개월 성과 대시보드`

## Step 0: 리서치 (자동)

시각화 제작 전, 주제에 대한 팩트와 수치를 수집합니다.
사용자가 직접 데이터(CSV/JSON/URL)를 제공한 경우 이 단계를 생략합니다.

### 0-1. WebSearch (초기 검색)
- 주제에서 핵심 키워드 3~5개 추출
- 한국어 + 영어 키워드 병행
- 최소 3개 이상 서로 다른 출처에서 수집
- 출처 우선순위: 공식 리포트 > 업계 미디어 > 블로그
- 1년 이내 데이터 우선

### 0-2. Gemini 그라운딩 검색 (교차 검증)
WebSearch 결과를 확보한 뒤, Gemini Google Search Grounding으로 교차 검증합니다.

```bash
node ~/gemini-tools/gemini-search.mjs "검색 키워드"
```

- Gemini가 반환하는 `summary`와 `citations`를 WebSearch 결과와 대조
- 수치가 일치하면 ✅ 검증됨, 불일치하면 ⚠️ 표시 후 추가 확인
- Gemini 출처를 리서치 결과에 통합

### 리서치 규칙
- 핵심 수치는 2개 이상 출처에서 교차 검증 (WebSearch + Gemini)
- Gemini 검색 실패 시 WebSearch 결과만으로 진행 (에러 무시)

수집 완료 후 간략한 리서치 요약을 사용자에게 보여준 뒤 시각화 제작으로 넘어갑니다.

## 파일 생성 후 필수 작업

**HTML 파일 생성 후 반드시 아래 3가지를 모두 수행:**

1. **브라우저 자동 열기:** `start <filename>.html` 실행
2. **클릭 가능한 URL 반환:** `file://<절대경로>` 형태로 응답에 포함
3. **Vercel 자동 배포:** 아래 절차에 따라 웹 배포 후 공유 URL 제공

### 자동 배포 절차

1. **프로젝트명 생성**: 한글 파일명의 의미를 영어로 번역하여 slug 생성 (음역 금지, 의미 번역)
   - 접두사: `ccfm-viz-`
   - 예: `q4-성과-대시보드.html` → `ccfm-viz-q4-performance-dashboard`
   - 예: `메타-광고-분석.html` → `ccfm-viz-meta-ad-analysis`
   - 간결하고 직관적인 2~5단어 slug
2. **배포 디렉토리 구성**: `$TEMP/{프로젝트명}/` 생성 후 HTML 파일을 `index.html`로 복사
3. **Vercel 배포**: `cd $TEMP/{프로젝트명} && vercel --yes --prod` 실행
4. **URL 제공**: 배포된 URL을 사용자에게 제공

응답 예시:
```
시각화를 생성했습니다! 브라우저에서 열고 있습니다...
file:///Users/junseok/Downloads/q4-성과-대시보드.html
배포 완료: https://ccfm-viz-q4-performance-dashboard.vercel.app
```

## 필수 요구사항 (NON-NEGOTIABLE)

**모든 파일은 반드시 아래 스켈레톤 템플릿에서 시작 — 전체 템플릿을 복사한 후 콘텐츠를 추가합니다.**

1. **CSS Custom Properties:** 정확한 이름 필수: `--bg, --surface, --surface-hover, --border, --text, --text-secondary, --accent, --accent-secondary, --positive, --negative, --warning` — 다른 이름 금지
2. **유틸리티 메뉴 시스템 (필수):** `.viz-menu` 요소, `.viz-menu-toggle` 버튼, `.viz-menu-dropdown` 컨테이너, PNG 다운로드 버튼 (`onclick="downloadImage()"`), 인쇄 버튼 (`onclick="window.print()"`), html-to-image CDN 스크립트
3. **테마 클래스 (필수):** `.theme-light`과 `.theme-dark` 클래스를 반드시 정의. `:root`만 사용하거나 `@media (prefers-color-scheme)` 사용 금지
4. **시맨틱 HTML:** `<main id="main-content">` 요소, 복수의 `<section>` 요소, skip-to-content 링크
5. **Chart.js 요구사항:** CDN 포함, `Chart.defaults.animation = false;` 필수, ChartManager 패턴 사용, `maintainAspectRatio: false`, `responsive: true`, 툴팁 활성화
6. **반응형 디자인:** 섹션 간격 48px 이상, 375px 뷰포트에서 가로 스크롤 금지, 폰트 사이즈 계층 필수 (h1>=2.5rem, h2>=2rem, h3>=1.5rem, body=1rem)
7. **인쇄 및 접근성:** `@media print` 스타일, `@media (prefers-reduced-motion: reduce)` 정의
8. **입장 애니메이션 (필수):** `.animate` 클래스, `data-reveal` 속성, CSS `@keyframes`
9. **JavaScript 함수:** `cycleTheme()`, `toggleMenu()`, 최상위 변수는 반드시 `var` 사용 (`let`/`const` 금지)

**스켈레톤 복사 -> "콘텐츠 입력" 부분에 내용 추가 -> 파일 저장**

## 핵심 원칙

1. **단일 HTML 파일** — CSS/JS 인라인. 모든 브라우저에서 열림, 오프라인 작동
2. **라이트 테마 최적화** — 현대적 디자인은 라이트 모드 품질 우선. 다크 테마 토글 제공
3. **기본이 아름답게** — 첫 출력물이 별도 수정 없이 프로페셔널하게 보여야 함
4. **콘텐츠 우선** — 시각화는 메시지를 전달. 미학을 위해 명확성 희생 금지
5. **반응형** — 데스크톱, 태블릿, 모바일에서 작동
6. **시각적 절제** — 떠다니는 그라디언트 오브, 무지개 테두리, 장식용 애니메이션 금지

## CCFM 브랜드 가이드

**모든 시각화에 CCFM 브랜드 아이덴티티를 적용합니다.**

### 브랜드 컬러
- **Primary Accent:** `#e5007e` (CCFM 핑크)
- **Secondary Accent:** `#ff4da6` (연한 핑크)
- 다크모드 accent: `#e5007e`, 라이트모드 accent: `#d1006f`
- 차트 컬러 시퀀스: `#e5007e, #ff4da6, #8b5cf6, #f59e0b, #10b981, #06b6d4, #f43f5e`

### 타이포그래피
- **Primary 폰트:** Pretendard (한국어 최적화)
  - CDN: `https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css`
- **대체 폰트:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **코드 폰트:** JetBrains Mono / `'SF Mono', 'Fira Code', 'Consolas', monospace`
- **기본 언어:** 한국어 (`<html lang="ko">`)
- **한국어 line-height:** 본문 1.7, 제목 1.2
- **letter-spacing:** 한국어 제목 `-0.02em`, 한국어 본문 `0em`, 영문 제목 `-0.03em`, 라벨/대문자 `0.05em`

### CCFM 브랜드 워터마크
모든 시각화 하단에 CCFM 로고 텍스트를 포함 (선택적):
```html
<footer class="ccfm-footer">
  <span class="ccfm-brand">CCFM</span>
</footer>
```
```css
.ccfm-footer { text-align: center; padding: 24px 0 16px; border-top: 1px solid var(--border); }
.ccfm-brand { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.15em; color: var(--text-secondary); text-transform: uppercase; }
```

## 출력 규칙

- `~/Downloads/` (또는 사용자 지정 경로)에 `.html` 파일 작성
- 파일명: 설명적 케밥 케이스, 예: `q4-매출-대시보드.html`, `메라블-브랜드-덱.html`
- **CDN 라이브러리 적극 활용:**
  - **Chart.js** — `https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js`
  - **D3.js** — `https://cdn.jsdelivr.net/npm/d3@7`
  - **Mermaid** — `https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js`
  - **Reveal.js** — 반드시 numeric dimensions 사용
  - **Leaflet** — 지도/지리 데이터
  - **Tailwind CSS** — `https://cdn.tailwindcss.com`
- 아이콘은 인라인 SVG만 (이모지 금지)
- CSS 애니메이션 우선

## 시각화 타입

| 타입 | 사용 시점 | 핵심 기능 |
|------|----------|----------|
| **슬라이드 덱** | 프레젠테이션, 피치 | 16:9, 키보드 네비게이션 |
| **인포그래픽** | 데이터 요약, 비주얼 스토리 | 롱 스크롤, 큰 숫자 |
| **대시보드** | 지표, KPI | 카드 그리드 + 차트 |
| **플로우차트** | 프로세스, 아키텍처 | Mermaid/SVG |
| **타임라인** | 시간순 이벤트 | 좌우 교차, 스크롤 |
| **비교표** | 비교 분석 | 기능 매트릭스, 장단점 |
| **데이터 시각화** | 차트, 데이터 스토리 | Chart.js/D3 |
| **원페이저** | 요약, 브리프 | 단일 뷰포트, 인쇄 |
| **캐러셀 카드** | SNS 카드뉴스 | 1080x1080, 스와이프 |
| **이벤트 포스터** | 컨퍼런스, 웨비나 | 세로 A4, 일시/장소 |
| **광고 성과 리포트** | 퍼포먼스 마케팅 | ROAS, CPA, CTR |
| **교육 자료** | 강연, 워크숍 | 단계별 설명, 체크리스트 |
| **브랜드 보고서** | 월간/주간 보고 | KPI + 진행률 + 하이라이트 |

### CCFM 마케팅 전용 타입

#### 광고 성과 대시보드
- **필수 KPI:** ROAS, CPA, CTR, CVR, 광고비, 매출
- **차트:** 일별 추이 (라인), 채널별 비교 (바), 매출 비중 (도넛)
- **필터:** 기간, 채널(네이버/카카오/메타/구글), 브랜드
- **컬러:** ROAS >= 300% → `var(--positive)`, < 200% → `var(--negative)`

#### 브랜드 월간 보고서
- **구조:** 핵심 지표 → 채널별 성과 → 이슈/액션 → 다음 달 계획
- **KPI:** 매출, 객단가, 재구매율, 신규 고객 수
- **시각화:** 전월 대비 증감 화살표, 목표 대비 달성률 게이지

#### 교육 슬라이드
- **구조:** 문제 정의 → 핵심 프레임워크 → 실행 단계 → 체크리스트 → Q&A
- **특징:** 코드/수식은 JetBrains Mono, 큰 숫자 강조, Before/After 비교

### 캐러셀 카드 (카드뉴스)
- 1080x1080px 정사각형
- 카드당 하나의 아이디어, 볼드 헤드라인 + 1-2 보조 포인트
- 스와이프 + 키보드 + 도트 네비게이션
- 카드 카운터 "3 / 8"
- PNG 개별/전체 다운로드
- 최대 10장

### 싱글 스크린 규칙 (포스터, 카드, 원페이저)
- 9:16: `1080x1920px`, 1:1: `1080x1080px`, 4:5: `1080x1350px`, 16:9: `1920x1080px`
- `overflow: hidden` 필수, `justify-content: space-between`, `flex: 1`
- 햄버거 메뉴 없음 (스크린샷/내보내기용)

## 슬라이드 덱 규칙

- 16:9 비율, 콘텐츠 중앙 정렬
- 슬라이드당 하나의 아이디어, 최대 40단어 (한국어 20어절)
- 헤드라인 최대 12자 (한국어)
- 키보드 ← → , Space, Enter / 터치 스와이프
- 진행 바 + 슬라이드 카운터
- 테마별 그라디언트: 다크=깊고 채도 높음, 라이트=부드럽고 파스텔

### 슬라이드 타입
1. **타이틀** — 그라디언트 배경, 큰 헤드라인
2. **콘텐츠** — 제목 + 불릿/비주얼
3. **섹션 구분** — 액센트 컬러, 타이틀만
4. **스탯** — 큰 숫자 + 라벨 + 인사이트
5. **차트** — Chart.js + 핵심 인사이트
6. **2단** — 비교/분할 레이아웃
7. **인용** — 큰 인용문 + 출처
8. **클로징** — CTA, 연락처

## 타입별 인터랙티비티 (필수)

테마 토글 + 메뉴 외에 최소 하나의 인터랙션 필수:

| 타입 | 필수 인터랙션 |
|------|-------------|
| **대시보드** | 필터 툴바/지표 드릴다운 |
| **보고서** | 접을 수 있는 섹션 (`<details>`) |
| **캐러셀** | 터치 스와이프 + 키보드 + 자동 전환 |
| **슬라이드 덱** | 네비게이션 + 프레젠터 타이머 |
| **타임라인** | 카테고리 필터/클릭 확장 |

## 디자인 시스템

### 테마 시스템
클래스 기반만. `data-theme` 금지. 필수 프로퍼티: `--bg, --surface, --text, --accent, --border`

### 컬러
- 다크: `#0A0A0A` bg, `#EDEDED` text. 라이트: `#FAFAF9` bg, `#0f172a` text
- Accent: `#e5007e` (CCFM 핑크)
- 카드: 8px radius, shadow-only hover
- 시각적 절제: 떠다니는 오브, 그라디언트 텍스트, scale transform, glow 금지

### 컬러 시스템 (클래스 기반)

```css
html.theme-dark {
  --bg: #0A0A0A; --surface: #141414; --surface-hover: #1C1C1C;
  --border: rgba(255,255,255,0.04);
  --text: #EDEDED; --text-secondary: #888888;
  --accent: #e5007e; --accent-secondary: #ff4da6;
  --positive: #10b981; --negative: #f43f5e; --warning: #f59e0b;
  --info: #06b6d4; --muted: #0f0f0f;
}
html.theme-light {
  --bg: #FAFAF9; --surface: #FFFFFF; --surface-hover: #F5F5F4;
  --border: #e5e5e5;
  --text: #1a1a1a; --text-secondary: #666666;
  --accent: #d1006f; --accent-secondary: #e5007e;
  --positive: #059669; --negative: #e11d48; --warning: #d97706;
  --info: #0ea5e9; --muted: #f8fafc;
}
```

### 스탯 값 컬러
의미 있는 경우만 색상 부여. ROAS >= 300% → `var(--positive)`, < 200% → `var(--negative)`. 의미 없으면 `var(--text)`.

### Accent 절제 규칙
- KPI 그리드 4개 이상: 최대 2개 accent 컬러
- 숫자 랜덤 컬러화 금지 — 색상은 시맨틱 의미 있을 때만
- 델타 인디케이터만: `var(--positive)`/`var(--negative)`는 화살표/퍼센트에만

### 타이포그래피
- 폰트 무게: h1=700, h2=600, 카드타이틀=600, 본문=400, 라벨=500
- 텍스트 컬러: 순백/순검 금지. 다크: `#ededed`, 라이트: `#1a1a1a`
- 그라디언트 텍스트 금지
- 타입 스케일: 14 → 16 → 20 → 25 → 31 → 39 → 49px
- 최대 줄 너비: 65-75자
- 반응형: `clamp()` 사용

### 간격
- 8px 그리드 — 4, 8, 12, 16, 24, 32, 48, 64, 96px
- 카드 `padding: 24px`, 컨테이너 `padding: 0 32px`
- 카드 갭: `gap: 24px` 최소

### 카드 시스템

```css
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 24px; transition: box-shadow 0.2s ease;
}
.theme-light .card { box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 0 0 1px rgba(0,0,0,0.03); }
.theme-dark .card { box-shadow: 0 0 0 1px var(--border); }
.card:hover { box-shadow: 0 0 0 1px var(--border), 0 8px 16px rgba(0,0,0,0.08); }
```

NO `translateY`/`scale` on hover. NO 그라디언트 테두리. NO 컬러 보더.

### Chart.js 스타일링
- 컨테이너: `padding: 40px; min-height: 360px`
- `layout: { padding: 30 }`, `borderRadius: 4`
- 그리드: 라이트 `rgba(0,0,0,0.04)`, 다크 `rgba(255,255,255,0.02)`
- 축 라벨 최소 13px
- `Chart.defaults.animation = false`
- 테마 토글 시 차트 파괴 후 재생성
- 명시적 색상값 사용 — CSS 변수 + hex alpha 접합 금지, `rgba()` 사용
- resetCanvas 금지 — 같은 캔버스 재사용, `.destroy()` 후 새 차트 생성
- 레이아웃 안정 후 빌드: `window.addEventListener('load', ...)` + `setTimeout(200)`

### 모바일 반응형 (필수)

```css
@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; gap: 1rem; }
  .chart-section { grid-template-columns: 1fr; }
  .container { padding: 1rem; }
}
@media (max-width: 375px) {
  body { overflow-x: hidden; }
  .container { padding: 0.75rem; }
  .kpi-card, .chart-card { padding: 1rem; }
  .filter-toolbar { flex-direction: column; align-items: stretch; }
}
```

### 배경 분위기 (파일당 하나만)

1. **미묘한 방사형 그라디언트** — CCFM 핑크 기반:
```css
body::before {
  content: ''; position: fixed; inset: 0; z-index: -1;
  background: radial-gradient(ellipse 80% 50% at 50% 20%,
    color-mix(in srgb, var(--accent), transparent 92%), transparent);
}
```
2. 노이즈/그레인 텍스처 (Vercel 스타일)
3. 도트 그리드 (테크/아키텍처에만)

### 시각적 절제 금지사항
- 떠다니는 그라디언트 오브
- 무지개/그라디언트 테두리
- 그라디언트 텍스트
- scale transform on hover
- glow 효과
- 장식용 애니메이션 (회전 링, 파티클)
- 컬러 보더 (왼쪽/위쪽)
- 스탯 숫자 그라디언트 텍스트

## JavaScript 구현 규칙

- 최상위 변수: 반드시 `var` (TDZ 에러 방지)
- 테마: `cycleTheme()` 함수
- 메뉴: `toggleMenu()` + 외부 클릭 핸들링
- 차트: `function onThemeChange() {}` 정의
- 모바일: 375px 뷰포트 테스트

## 시맨틱 HTML

- `<main>`, `<section>`, `<header>`, `<article>` 시맨틱 요소
- `role="img"` + `aria-label` (차트)
- `@media print`, `@media (prefers-reduced-motion)` 정의
- 섹션 간격 48px 이상
- 인터랙티브 요소 hover 상태

## 데이터 수집

- CSV → 자동 파싱, 적절한 차트 렌더링
- JSON → 키=라벨, 값=데이터 추출
- 텍스트 속 숫자 → 스탯 카드 강조
- URL → 크롤링, 핵심 추출, 시각화

---

# 필수 HTML 스켈레톤

**모든 시각화는 이 스켈레톤에서 시작합니다.** 복사 후 콘텐츠를 추가합니다.

```html
<!DOCTYPE html>
<html lang="ko" class="theme-dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>제목 입력</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
  <!-- CDN 라이브러리 추가 (Chart.js, Mermaid 등) -->
  <script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root { interpolate-size: allow-keywords; }

    /* ===== 테마 (클래스 기반) ===== */
    html.theme-dark {
      --bg: #0A0A0A; --surface: #141414; --surface-hover: #1C1C1C;
      --border: rgba(255,255,255,0.04);
      --text: #EDEDED; --text-secondary: #888;
      --accent: #e5007e; --accent-secondary: #ff4da6;
      --positive: #10b981; --negative: #f43f5e; --warning: #f59e0b;
    }
    html.theme-light {
      --bg: #FAFAF9; --surface: #FFFFFF; --surface-hover: #F5F5F4;
      --border: rgba(0,0,0,0.06);
      --text: #0f172a; --text-secondary: #64748b;
      --accent: #d1006f; --accent-secondary: #e5007e;
      --positive: #059669; --negative: #e11d48; --warning: #d97706;
    }

    body {
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg); color: var(--text);
      line-height: 1.7; -webkit-font-smoothing: antialiased;
      font-feature-settings: 'cv11', 'ss01';
      transition: background 0.3s, color 0.3s;
      scrollbar-gutter: stable;
    }
    h1,h2,h3,h4,h5,h6 { color: var(--text); letter-spacing: -0.02em; line-height: 1.2; text-wrap: balance; }
    h1 { font-weight: 700; }
    h2 { font-weight: 600; }
    body, p, li, td, th, span, label { font-weight: 400; }
    p,li,td,th,span,label { color: var(--text); }
    .text-secondary { color: var(--text-secondary); }

    /* ===== 카드 ===== */
    .card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 8px; padding: 24px; transition: box-shadow 0.2s ease;
    }
    .card:hover { box-shadow: 0 0 0 1px var(--border), 0 8px 16px rgba(0,0,0,0.08); }

    /* ===== 애니메이션 ===== */
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(24px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideInLeft {
      from { opacity: 0; transform: translateX(-40px); }
      to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInRight {
      from { opacity: 0; transform: translateX(40px); }
      to { opacity: 1; transform: translateX(0); }
    }
    .animate { animation: fadeInUp 0.6s ease-out both; }
    .animate.delay-1 { animation-delay: 0.1s; }
    .animate.delay-2 { animation-delay: 0.2s; }
    .animate.delay-3 { animation-delay: 0.3s; }
    .animate.delay-4 { animation-delay: 0.4s; }
    .animate.delay-5 { animation-delay: 0.5s; }
    .animate.delay-6 { animation-delay: 0.6s; }
    .reveal { opacity: 0; transform: translateY(24px); transition: opacity 0.6s ease, transform 0.6s ease; }
    .reveal.visible { opacity: 1; transform: translateY(0); }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation: none !important; transition: none !important; }
      .reveal { opacity: 1; transform: none; }
    }

    /* ===== 인쇄 ===== */
    @media print {
      body { background: white !important; color: black !important; }
      .viz-menu, .reveal { display: revert; opacity: 1 !important; transform: none !important; }
      .card { break-inside: avoid; border: 1px solid #ddd; box-shadow: none; }
      * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
    }
    @page { margin: 1in; }

    /* ===== 메뉴 ===== */
    .viz-menu { position: fixed; top: 16px; right: 16px; z-index: 9999; }
    .viz-menu-toggle {
      width: 44px; height: 44px; border-radius: 12px;
      background: var(--surface); border: 1px solid var(--border);
      color: var(--text); cursor: pointer; display: flex;
      align-items: center; justify-content: center;
      backdrop-filter: blur(12px); transition: all 0.2s;
    }
    .viz-menu-toggle:hover { background: var(--surface-hover); }
    .viz-menu-dropdown {
      position: absolute; top: 52px; right: 0; min-width: 200px;
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 8px;
      opacity: 0; visibility: hidden; transform: translateY(-8px);
      transition: all 0.2s; backdrop-filter: blur(16px);
    }
    .viz-menu-dropdown.open { opacity: 1; visibility: visible; transform: translateY(0); }
    .viz-menu-dropdown button {
      width: 100%; padding: 10px 14px; border: none; border-radius: 8px;
      background: transparent; color: var(--text); font-size: 14px;
      font-family: inherit; cursor: pointer; text-align: left;
      display: flex; align-items: center; gap: 10px; transition: background 0.15s;
    }
    .viz-menu-dropdown button:hover { background: var(--surface-hover); }

    /* ===== Skip to Content ===== */
    .skip-to-content {
      position: absolute; top: -40px; left: 6px; background: var(--accent);
      color: white; padding: 8px 12px; text-decoration: none;
      border-radius: 4px; opacity: 0; pointer-events: none;
      transition: all 0.2s; z-index: 10000;
    }
    .skip-to-content:focus { top: 6px; opacity: 1; pointer-events: auto; }

    /* ===== Details ===== */
    details { overflow: hidden; }
    details summary { cursor: pointer; list-style: none; }
    details summary::-webkit-details-marker { display: none; }
    ::details-content {
      transition: block-size 0.3s ease, opacity 0.3s ease;
      block-size: 0; opacity: 0; overflow: hidden;
    }
    details[open]::details-content { block-size: auto; opacity: 1; }

    /* ===== Popover ===== */
    [popover] {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 8px; padding: 16px; max-width: 320px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2); color: var(--text);
    }
    [popover]::backdrop { background: rgba(0,0,0,0.3); }

    /* ===== Focus ===== */
    *:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }

    /* ===== CCFM 푸터 ===== */
    .ccfm-footer { text-align: center; padding: 24px 0 16px; border-top: 1px solid var(--border); }
    .ccfm-brand { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.15em; color: var(--text-secondary); text-transform: uppercase; }

    .sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }

    /* ===== 여기에 스타일 추가 ===== */
  </style>
</head>
<body>
  <!-- 메뉴 -->
  <div class="viz-menu">
    <button class="viz-menu-toggle" onclick="toggleMenu()" aria-label="메뉴">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="3" y1="5" x2="17" y2="5"/><line x1="3" y1="10" x2="17" y2="10"/><line x1="3" y1="15" x2="17" y2="15"/>
      </svg>
    </button>
    <div class="viz-menu-dropdown" id="vizMenuDropdown">
      <button onclick="cycleTheme()"><span id="themeIcon">🌙</span><span id="themeLabel">다크</span></button>
      <button onclick="downloadImage()"><span>📥</span><span>PNG 다운로드</span></button>
      <button onclick="window.print()"><span>🖨️</span><span>인쇄 / PDF</span></button>
    </div>
  </div>

  <a href="#main-content" class="skip-to-content">콘텐츠로 이동</a>

  <main id="main-content" role="main">
    <!-- 콘텐츠 입력 -->
  </main>

  <footer class="ccfm-footer">
    <span class="ccfm-brand">CCFM</span>
  </footer>

  <script>
    // === 메뉴 ===
    function toggleMenu() {
      var dropdown = document.getElementById('vizMenuDropdown') || document.getElementById('vizMenu');
      if (dropdown) dropdown.classList.toggle('open');
    }
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.viz-menu')) {
        var dropdown = document.getElementById('vizMenuDropdown') || document.getElementById('vizMenu');
        if (dropdown) dropdown.classList.remove('open');
      }
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        var dropdown = document.getElementById('vizMenuDropdown') || document.getElementById('vizMenu');
        if (dropdown) dropdown.classList.remove('open');
      }
    });

    // === 테마 ===
    var savedTheme = localStorage.getItem('viz-theme');
    var currentTheme = savedTheme || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    function applyTheme(t) {
      document.documentElement.className = 'theme-' + t;
      document.getElementById('themeIcon').textContent = t === 'dark' ? '🌙' : '☀️';
      document.getElementById('themeLabel').textContent = t === 'dark' ? '다크' : '라이트';
      localStorage.setItem('viz-theme', t);
      currentTheme = t;
      if (typeof onThemeChange === 'function') onThemeChange();
    }
    function cycleTheme() { applyTheme(currentTheme === 'dark' ? 'light' : 'dark'); }
    applyTheme(currentTheme);

    // === 스크롤 리빌 ===
    document.querySelectorAll('[data-reveal]').forEach(function(el) { el.classList.add('reveal'); });
    var revealObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) { if (e.isIntersecting) { e.target.classList.add('visible'); revealObserver.unobserve(e.target); } });
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal').forEach(function(el) { revealObserver.observe(el); });

    // === 숫자 카운터 ===
    function animateCounters() {
      document.querySelectorAll('[data-count]').forEach(function(el) {
        if (el.dataset.counted) return;
        el.dataset.counted = '1';
        var target = parseFloat(el.dataset.count), prefix = el.dataset.prefix || '', suffix = el.dataset.suffix || '';
        var start = performance.now(), duration = 1200;
        (function tick(now) {
          var p = Math.min((now - start) / duration, 1), eased = 1 - Math.pow(1 - p, 3);
          el.textContent = prefix + Math.round(target * eased).toLocaleString() + suffix;
          if (p < 1) requestAnimationFrame(tick);
        })(start);
      });
    }
    var counterEl = document.querySelector('[data-count]');
    if (counterEl) {
      var cObs = new IntersectionObserver(function(entries) {
        entries.forEach(function(e) { if (e.isIntersecting) { animateCounters(); cObs.disconnect(); } });
      }, { threshold: 0.3 });
      cObs.observe(counterEl);
    }

    // === PNG 다운로드 ===
    async function downloadImage() {
      var menu = document.querySelector('.viz-menu');
      menu.style.display = 'none';
      try {
        var url = await htmlToImage.toPng(document.body, { quality: 1, pixelRatio: 2, filter: function(n) { return !n.classList || !n.classList.contains('viz-menu'); } });
        var a = document.createElement('a'); a.href = url;
        a.download = document.title.replace(/\s+/g, '-').toLowerCase() + '.png'; a.click();
      } catch(e) { console.error('다운로드 실패:', e); }
      menu.style.display = '';
    }

    // === 여기에 스크립트 추가 (최상위 변수는 var 사용) ===
  </script>
</body>
</html>
```

### 스켈레톤 규칙

**허용:** `var` 최상위 변수, `data-reveal` 스크롤 애니메이션, `data-count` 숫자 카운터, `.animate.delay-N` 페이지 로드 애니메이션, CSS `:hover`, `function onThemeChange() {}`, 시맨틱 HTML

**금지:** Motion.js 포함 금지, JS/CSS로 콘텐츠 숨기기 (`data-reveal` 패턴 사용), `let`/`const` 최상위 변수, `.finished` Promise 체인, 네비게이션/차트 셋업 전 크래시 가능 로직

---

# 평가 기준

## 8개 차원

| # | 차원 | 비중 | 체크 |
|---|------|------|------|
| D1 | 첫 인상 | 15% | 2초 직감. 프로페셔널? 명확한 포커스? |
| D2 | 타이포그래피 | 15% | 계층, 크기, line-height, 최대 2 폰트 |
| D3 | 컬러 | 10% | 조화, WCAG AA, accent 목적, 양 테마 |
| D4 | 레이아웃 | 15% | 일관된 간격, 여백, 반응형, 정렬 |
| D5 | 콘텐츠 | 15% | 정확, 5초 내 메시지, 적정 밀도, 필러 없음 |
| D6 | 인터랙티비티 | 10% | 메뉴, 테마, 다운로드, 인쇄, 네비, hover |
| D7 | 기술 | 10% | 에러 0, <200KB, 시맨틱, 인쇄 CSS, a11y |
| D8 | 공유성 | 10% | 트윗할 만한가? Gamma/Canva보다 나은가? |

## 품질 게이트

| 게이트 | 총점 | 최소 | 액션 |
|--------|------|------|------|
| VIRAL | >= 9.5 | >= 9 | 출시 + 홍보 |
| SHIP | >= 9.0 | >= 8 | 릴리스 가능 |
| GOOD | >= 8.0 | >= 7 | 수정 후 피처링 |
| NEEDS WORK | >= 7.0 | any < 7 | 수정 + 재평가 |
| FAIL | < 7.0 | any < 5 | 대규모 재작업 |

**목표: SHIP (>= 9.0)**
