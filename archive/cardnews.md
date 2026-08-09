# CCFM 카드뉴스 제작 파이프라인

사용자가 $ARGUMENTS 로 주제를 전달합니다.
예시: `/cardnews 광고비를 태우기 전에 반드시 확인해야 할 5가지 체크리스트`

아래 파이프라인을 **반드시 순서대로** 실행하세요. 단계를 건너뛰지 마세요.

---

## Step 1: 리서치

주제에서 핵심 키워드 3~5개를 추출하고, **WebSearch + Gemini 교차 검증** 체계로 팩트와 수치를 수집합니다.

### 1-1. WebSearch (초기 검색)
- 한국어 + 영어 키워드 병행
- 최소 3개 이상 서로 다른 출처에서 수집
- 출처 우선순위: 공식 리포트 > 업계 미디어 > 블로그
- 1년 이내 데이터 우선

### 1-2. Gemini 그라운딩 검색 (교차 검증)
WebSearch 결과를 확보한 뒤, 동일 주제에 대해 Gemini Google Search Grounding으로 교차 검증합니다.

```bash
node ~/gemini-tools/gemini-search.mjs "검색 키워드"
```

- Gemini가 반환하는 `summary`와 `citations`를 WebSearch 결과와 대조
- 수치가 일치하면 ✅ 검증됨, 불일치하면 ⚠️ 표시 후 추가 확인
- Gemini 출처(`citations`)를 리서치 결과 테이블에 통합

### 1-3. Gemini 딥리서치 (선택, 브라우저 자동화)
사용자가 "딥리서치" 또는 "심층 리서치"를 요청한 경우에만 실행합니다.
Puppeteer로 Gemini 웹을 직접 제어하여 **자동으로 Deep Research를 실행하고 결과를 추출**합니다.

```bash
node ~/gemini-tools/gemini-deep-research.mjs "리서치 주제"
```

- 첫 실행 시 Google 로그인이 필요할 수 있음 (이후 프로필 저장)
- 실행 완료 시 stdout에 JSON `{ report, topic, status }` 출력
- 5~20분 소요, 최대 25분 대기
- 자동 추출 실패 시 사용자에게 결과 복사 요청

### 리서치 규칙
- 핵심 수치는 2개 이상 출처에서 교차 검증 (WebSearch + Gemini 포함)
- Gemini 검색 실패 시 WebSearch 결과만으로 진행 (에러 무시)

수집 완료 후 아래 형식으로 사용자에게 보여줍니다:

```
## 📊 리서치 결과: [주제명]

### 핵심 수치
| # | 팩트 | 수치 | 출처 | 검증 | 날짜 |
|---|------|------|------|------|------|

검증 열: ✅ WebSearch+Gemini 일치 | 🔍 WebSearch만 | 🤖 Gemini만 | ⚠️ 불일치

### 주요 인사이트
### 활용 가능한 사례
### 카드뉴스 앵글 제안
```

---

## Step 2: 기획안 작성

리서치 결과를 기반으로 슬라이드 구조를 설계합니다.

### 기획 원칙
- 슬라이드당 메시지 1개
- 첫 슬라이드 = 훅(Hook), 마지막 = CTA
- 중간: 문제 제기 → 원인 → 해결책 → 실행법 순서 권장
- 데이터 슬라이드와 텍스트 슬라이드 교차 배치

### 슬라이드 유형
- **커버**: 태그 라벨 + 제목(20자 이내, 명령형/질문형) + 부제 1줄
- **내용**: 넘버링 뱃지 + 소제목 + 본문 2~3줄 / 카드형 리스트 / 비교표
- **TIP 박스 포함**: 상단 메인 콘텐츠 + 하단 다크 TIP 박스
- **CTA**: 핵심 메시지 1줄 + 강조 키워드 하이라이트

기획안을 아래 형식으로 사용자에게 보여줍니다:

```
## 📋 카드뉴스 기획안: [제목]

총 슬라이드: [N]장 | 타겟: [독자층] | 핵심 메시지: [한 줄]

### 슬라이드 1 (커버)
- 유형 / 배경 / 태그 / 제목 / 부제

### 슬라이드 2~N
- 유형 / 배경 / 소제목 / 본문 / 비주얼 / TIP 박스
```

---

## Step 3: 승인 대기 ⚠️

**기획안을 보여주고 반드시 사용자 승인을 받으세요.**
- "OK", "좋아", "진행해" 등 명시적 승인이 있을 때만 Step 4로 이동
- 수정 피드백이 오면 기획안 수정 후 다시 승인 요청
- **승인 없이 절대 제작으로 넘어가지 말 것**

---

## Step 4: HTML 제작

승인된 기획안을 슬라이드별 독립 HTML 파일로 제작합니다.

### 파일 저장 규칙
- **프로젝트 폴더명**: 사용자가 `/cardnews` 뒤에 입력한 프롬프트 텍스트를 그대로 폴더명으로 사용
  - 예: `/cardnews 이커머스 마케팅 시장 2025 조사` → 폴더명: `이커머스 마케팅 시장 2025 조사`
- **HTML 파일 위치**: `~/cardnews-ccfm/이커머스 마케팅 시장 2025 조사/slide_01.html`, `slide_02.html`, ...
- **PNG 파일 위치**: `~/cardnews-ccfm/output/이커머스 마케팅 시장 2025 조사/slide_01.png`, `slide_02.png`, ...
- 폴더명에 파일시스템 금지 문자(`/ \ : * ? " < > |`)가 포함되어 있으면 해당 문자만 제거

### 디자인 시스템

**캔버스:** 1080 × 1080px

**색상 팔레트:**
- 브랜드 메인: #e5007e (CCFM 핑크)
- 다크 배경: #1a1a1a
- 라이트 배경: #f5f2eb
- 서브 포인트: #fce4ef (연핑크, 카드/박스 배경용)
- 텍스트 (다크 위): #ffffff
- 텍스트 (라이트 위): #1a1a1a
- 강조: #e5007e

**배경 교차 규칙:** 3장 연속 같은 배경 금지. 강조 슬라이드는 #e5007e 배경 + 흰 텍스트 가능.

**폰트:** Pretendard (CDN: https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css)
- 제목: 48~56px, weight 800
- 본문: 28~32px, weight 500
- 캡션: 20~22px, weight 400
- 행간: 1.4~1.6

**레이아웃:** padding 최소 60px, 본문 3줄 이내, border-radius 16px 통일, 그림자 없음

**컴포넌트:**
- 태그/라벨: #e5007e 배경 + 흰 텍스트, border-radius 4px
- 넘버링 뱃지: #e5007e 배경 + 흰 텍스트, 44x44px, border-radius 8px
- 카드: border-radius 16px, padding 32px
- TIP 박스: #1a1a1a 배경, 💡 아이콘, #e5007e 제목, 흰 설명
- 강조 텍스트: color #e5007e
- 체크마크: ✓ 기호, #e5007e 색상

### HTML 템플릿

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1080, initial-scale=1">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 1080px;
      height: 1080px;
      font-family: 'Pretendard Variable', Pretendard, -apple-system, sans-serif;
      overflow: hidden;
    }
    .slide {
      width: 1080px;
      height: 1080px;
      padding: 60px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
  </style>
</head>
<body>
  <div class="slide">
    <!-- 콘텐츠 -->
  </div>
</body>
</html>
```

### 주의사항
- 기획안에 없는 내용 임의 추가 금지
- CSS는 인라인 또는 style 태그 (외부 CSS 파일 금지)
- 이모지는 시스템 이모지 사용

---

## Step 5: PNG 변환 및 검수

puppeteer로 각 HTML을 1080x1080 PNG로 변환하여 `~/cardnews-ccfm/output/[프로젝트 폴더명]/` 에 저장합니다.
프로젝트 폴더명은 Step 4의 파일 저장 규칙을 따릅니다.

```javascript
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function convertToPng(htmlFile, outputFile) {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: 'new'
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1080 });
  const htmlPath = path.resolve(htmlFile);
  const html = fs.readFileSync(htmlPath, 'utf8');
  await page.setContent(html, { waitUntil: 'networkidle0' });
  await page.screenshot({ path: path.resolve(outputFile), type: 'png' });
  await browser.close();
}
```

변환 후 사용자에게 이미지를 보여주고 텍스트 잘림/깨짐 확인을 요청합니다.

---

## Step 6: 웹 배포 (자동)

PNG 변환 및 검수가 완료되면 자동으로 Vercel에 배포하여 공유 가능한 URL을 생성합니다.

### 배포 프로세스

1. **캐러셀 뷰어 HTML 생성**: 모든 슬라이드 PNG를 하나의 캐러셀로 묶은 `index.html`을 생성
2. **프로젝트명 생성**: 한글 폴더명의 의미를 영어로 번역하여 Vercel 프로젝트명으로 사용 (음역 금지, 의미 번역)
   - 예: `광고비 체크리스트` → `ccfm-card-ad-budget-checklist`
   - 예: `이커머스 마케팅 시장 2025 조사` → `ccfm-card-ecommerce-marketing-2025`
   - 프로젝트명 접두사: `ccfm-card-`
   - 간결하고 직관적인 영어 slug로 생성 (2~5단어)
3. **배포 디렉토리 구성**: `$TEMP/ccfm-card-{로마자명}/` 에 `index.html` + PNG 파일들 복사
4. **Vercel 배포**: `vercel --yes --prod` 실행
5. **URL 제공**: 배포된 URL을 사용자에게 제공

### 캐러셀 뷰어 HTML 템플릿

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CCFM 카드뉴스 — {제목}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #1a1a1a; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: -apple-system, sans-serif; }
    .carousel { position: relative; width: 90vmin; max-width: 860px; aspect-ratio: 1; }
    .carousel img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; opacity: 0; transition: opacity 0.3s; border-radius: 12px; }
    .carousel img.active { opacity: 1; }
    .nav { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.9); border: none; width: 48px; height: 48px; border-radius: 50%; cursor: pointer; font-size: 20px; z-index: 10; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
    .nav:hover { background: #fff; }
    .nav.prev { left: -60px; }
    .nav.next { right: -60px; }
    .dots { text-align: center; margin-top: 20px; }
    .dots span { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #555; margin: 0 5px; cursor: pointer; transition: background 0.2s; }
    .dots span.active { background: #e5007e; }
    .counter { text-align: center; color: #999; margin-top: 10px; font-size: 15px; }
    @media (max-width: 860px) {
      .carousel { width: 90vw; }
      .nav.prev { left: 8px; }
      .nav.next { right: 8px; }
      .nav { width: 40px; height: 40px; background: rgba(255,255,255,0.7); }
    }
  </style>
</head>
<body>
  <div>
    <div class="carousel" id="carousel">
      <!-- PNG 이미지들이 여기에 삽입됨 -->
      <button class="nav prev" onclick="move(-1)">‹</button>
      <button class="nav next" onclick="move(1)">›</button>
    </div>
    <div class="dots" id="dots"></div>
    <div class="counter" id="counter"></div>
  </div>
  <script>
    let current = 0;
    const imgs = document.querySelectorAll('.carousel img');
    const dots = document.getElementById('dots');
    const counter = document.getElementById('counter');
    imgs.forEach((_, i) => { const d = document.createElement('span'); d.onclick = () => go(i); dots.appendChild(d); });
    function go(i) { imgs[current].classList.remove('active'); dots.children[current].classList.remove('active'); current = (i + imgs.length) % imgs.length; imgs[current].classList.add('active'); dots.children[current].classList.add('active'); counter.textContent = (current+1) + ' / ' + imgs.length; }
    function move(d) { go(current + d); }
    go(0);
    document.addEventListener('keydown', e => { if(e.key==='ArrowLeft') move(-1); if(e.key==='ArrowRight') move(1); });
  </script>
</body>
</html>
```

### 배포 절차

프로젝트명은 Claude가 한글 제목의 의미를 해석하여 직접 영어 slug를 생성합니다. (별도 스크립트 불필요)

1. `$TEMP/{프로젝트명}/` 디렉토리 생성
2. PNG 파일들 복사
3. 캐러셀 뷰어 `index.html` 생성 (PNG 파일명들을 img 태그로 삽입)
4. `cd $TEMP/{프로젝트명} && vercel --yes --prod` 실행
5. 배포된 URL을 사용자에게 제공: `✅ 웹 배포 완료: https://{프로젝트명}.vercel.app`

---

## 콘텐츠 규칙
- 주제 도메인: 퍼포먼스 마케팅, 광고 운영, 마케팅 전략, 브랜드 운영, 이커머스
- 타겟 독자: 마케터, 브랜드 담당자, 사업가
- 톤앤매너: 전문적이되 쉽게, 명령형 제목, 실무 중심
- 모든 팩트에 출처 명시
- 추상적 서술 금지 → 구체적 수치, 사례, 실행 방법 우선

## 응답 형식
각 단계 시작 시: `📍 현재 단계: Step [N] — [단계명]`
단계 완료 시: `✅ Step [N] 완료. 다음 단계로 넘어갑니다.`
Step 6 완료 시: `✅ 웹 배포 완료: https://{프로젝트명}.vercel.app`
