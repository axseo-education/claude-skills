---
name: competitor
description: 경쟁사 분석 — 검색량·광고·리뷰·커뮤니티를 모아 7개 섹션 대시보드 한 장으로 낸다.
---

# /competitor — 경쟁사 분석 (교육용)

```
/competitor 우리브랜드
/competitor A브랜드 vs B브랜드 vs C브랜드
/competitor 우리브랜드. 뷰티 디바이스 카테고리. 경쟁사 자동으로 찾아줘
```

교육용 판본입니다. **직원 PC 에서 Claude Code 만으로 완주**하도록 구성했습니다.
사내 서버·크롤러는 쓰지 않고, 필요한 도구는 아래 준비 단계에서 직접 설치합니다.

산출물은 **7개 섹션 대시보드 HTML 한 장**입니다. 섹션 순서는 고정입니다.

---

## 준비 — 처음 한 번만

이 스킬은 **웹 검색만으로는 안 됩니다.** 검색량과 광고 데이터가 있어야 판정이 됩니다.
아래 두 가지를 먼저 갖춘다. **Claude 가 직접 실행한다. 사용자에게 떠넘기지 않는다.**

### 1) 브라우저 도구 설치

메타 광고 라이브러리는 화면을 그려야 내용이 나오는 페이지라 일반 웹 요청으로는 못 읽는다.

```bash
mkdir -p ~/competitor-tools && cd ~/competitor-tools
npm init -y
npm i playwright
npx playwright install chromium
```

`node` 가 없다는 오류가 나면 Node.js 부터 설치한다 (`brew install node`, 윈도우는 nodejs.org).
받는 용량이 100MB 가까워 처음 한 번은 시간이 걸린다고 사용자에게 알린다.

### 2) 네이버 API 키 발급

사용자에게 **한 번만** 부탁한다. 둘 다 무료이고 발급이 어렵지 않다.

| 무엇 | 어디서 | 받는 것 |
|------|--------|---------|
| **검색광고 API** — 월간 검색량 | 네이버 검색광고 → 도구 → API 사용 관리 | 액세스라이선스 · 비밀키 · CUSTOMER_ID |
| **데이터랩 API** — 월별 트렌드 | 네이버 개발자센터 → 애플리케이션 등록 → 데이터랩(검색어트렌드) 선택 | Client ID · Client Secret |

받은 값은 `~/competitor-tools/.env` 에 저장한다. **대화창에 키를 다시 출력하지 않는다.**

```bash
cat > ~/competitor-tools/.env <<'EOF'
SEARCHAD_API_KEY=
SEARCHAD_SECRET=
SEARCHAD_CUSTOMER_ID=
DATALAB_CLIENT_ID=
DATALAB_CLIENT_SECRET=
EOF
```

키가 없으면 **01 섹션을 만들 수 없다.** 그때는 키 없이 진행할지 사용자에게 묻고,
진행한다면 01 섹션을 빼고 6개 섹션으로 내되 **뺐다는 사실을 결과에 적는다.**

---

## Step 0 — 비교 대상 정하기

입력을 읽고 판별한다.

| 입력 | 처리 |
|------|------|
| 브랜드가 둘 이상 | 그대로 비교 대상으로 삼는다 |
| 브랜드가 하나 | 같은 카테고리에서 **광고를 실제로 돌리는** 브랜드를 찾아 후보를 제시하고 고르게 한다 |
| 브랜드가 없음 | **묻는다.** 무엇을 분석할지 없이는 시작하지 않는다 |

**브랜드명이 여러 업종에 걸쳐 있으면 어느 쪽인지 먼저 묻는다.** (같은 이름의 다른 회사가 흔하다)
카테고리를 잘못 잡으면 그 뒤 전부가 헛돈다.

**기준 브랜드가 어디인지 정한다.** 입력에 안 드러나면 묻는다.
분석 전체가 "기준 브랜드가 무엇을 할 수 있나"로 수렴하므로 이게 없으면 방향이 안 잡힌다.
기준 브랜드가 없는 제3자 조사라면 **중립 비교로 전환**하고, 뒤의 해석을 실행 주체 없이
"시장에서 읽히는 것"으로만 낸다.

### 후보 필터 — 아무나 넣지 않는다

경쟁사는 "같은 걸 파는 곳"이 아니라 **"같은 방식으로 같은 고객을 두고 다투는 곳"**이다.

| 조건 | 왜 | 뺄 예 |
|------|-----|-------|
| **검색량이 같은 밴드인가** | 규모가 다르면 예산 단위가 달라 배울 게 없다 | 대기업 계열, 전국 매스 광고 브랜드 |
| **온라인 광고를 돌리고 있는가** | 광고를 안 하면 비교할 소재가 없다 | 유통 입점 위주 브랜드 |
| **꾸준히 집행하는가** | 한 달 몰아 태운 건 브랜드 캠페인이지 퍼포먼스가 아니다 | 런칭 때 한 번만 태운 곳 |
| **오프라인·홈쇼핑 전용이 아닌가** | 볼 수 있는 소재가 안 나온다 | TV홈쇼핑만 하는 브랜드 |

**검색량 밴드가 1차 관문이고 광고 수가 2차다.** 검색량이 기준 브랜드와 자릿수가 다르면
광고를 아무리 많이 돌려도 비교 대상이 아니다.

통과 못 한 곳은 **왜 뺐는지 한 줄로 적어** 사용자에게 보여준다. 조용히 빼지 않는다.

### 후보 제시 형식

```
## 경쟁사 후보

1. {브랜드} — {같은 밴드로 본 이유} / 검색량 {값} / 활성 광고 {값}
2. {브랜드} — {이유} / 검색량 {값} / 활성 광고 {값}
3. {브랜드} — {이유} / 검색량 {값} / 활성 광고 {값}

### 뺀 곳
- {브랜드} — {뺀 이유}

이대로 갈까요? 빼거나 더할 곳이 있으면 말씀해 주세요.
```

**비교 대상은 기준 브랜드 포함 3개가 기본이다.** 둘이면 대비가 안 서고 넷 이상이면 화면이 뭉개진다.

---

## Step 1 — 데이터 수집

### 1-A. 검색량 (섹션 01 재료)

```bash
cd ~/competitor-tools && node volume.mjs "브랜드A" "브랜드B" "브랜드C"
```

`~/competitor-tools/volume.mjs` 로 저장할 스크립트:

```javascript
// 브랜드별 월간 검색량 + 파생 키워드. 사용법: node volume.mjs "브랜드1" "브랜드2"
import { createHmac } from 'node:crypto';
import fs from 'node:fs';

var env = {};
for (var line of fs.readFileSync(new URL('.env', import.meta.url), 'utf8').split('\n')) {
  var i = line.indexOf('=');
  if (i > 0) env[line.slice(0, i).trim()] = line.slice(i + 1).trim();
}

async function keywordTool(seed) {
  var ts = String(Date.now());
  var path = '/keywordstool';
  var sig = createHmac('sha256', env.SEARCHAD_SECRET).update(ts + '.GET.' + path).digest('base64');
  var url = 'https://api.searchad.naver.com' + path + '?hintKeywords=' +
            encodeURIComponent(seed) + '&showDetail=1';
  var res = await fetch(url, { headers: {
    'X-Timestamp': ts, 'X-API-KEY': env.SEARCHAD_API_KEY,
    'X-Customer': env.SEARCHAD_CUSTOMER_ID, 'X-Signature': sig } });
  if (!res.ok) throw new Error('searchad ' + res.status + ' ' + (await res.text()).slice(0, 120));
  return (await res.json()).keywordList || [];
}

function num(v) { return typeof v === 'number' ? v : parseInt(String(v).replace(/[^0-9]/g, ''), 10) || 0; }

var out = {};
for (var brand of process.argv.slice(2)) {
  var list = await keywordTool(brand);
  var rows = list
    .filter(function (k) { return k.relKeyword.replace(/\s/g, '').includes(brand.replace(/\s/g, '')); })
    .map(function (k) { return { keyword: k.relKeyword, volume: num(k.monthlyPcQcCnt) + num(k.monthlyMobileQcCnt) }; })
    .sort(function (a, b) { return b.volume - a.volume; });
  out[brand] = { total: rows.reduce(function (s, r) { return s + r.volume; }, 0), keywords: rows.slice(0, 20) };
  console.log(brand, '합산', out[brand].total, '· 파생 키워드', rows.length);
}
fs.writeFileSync(new URL('volumes.json', import.meta.url), JSON.stringify(out, null, 2));
```

**월별 트렌드**는 데이터랩으로 따로 받는다. `~/competitor-tools/trend.mjs`:

```javascript
// 브랜드별 월별 상대 트렌드. 사용법: node trend.mjs 2025 "브랜드1" "브랜드2"
import fs from 'node:fs';
var env = {};
for (var line of fs.readFileSync(new URL('.env', import.meta.url), 'utf8').split('\n')) {
  var i = line.indexOf('='); if (i > 0) env[line.slice(0, i).trim()] = line.slice(i + 1).trim();
}
var year = process.argv[2];
var brands = process.argv.slice(3);
var res = await fetch('https://openapi.naver.com/v1/datalab/search', {
  method: 'POST',
  headers: { 'X-Naver-Client-Id': env.DATALAB_CLIENT_ID,
             'X-Naver-Client-Secret': env.DATALAB_CLIENT_SECRET,
             'Content-Type': 'application/json' },
  body: JSON.stringify({
    startDate: year + '-01-01', endDate: year + '-12-31', timeUnit: 'month',
    keywordGroups: brands.map(function (b) { return { groupName: b, keywords: [b] }; }) }) });
if (!res.ok) throw new Error('datalab ' + res.status + ' ' + (await res.text()).slice(0, 120));
var data = await res.json();
fs.writeFileSync(new URL('trend.json', import.meta.url), JSON.stringify(data, null, 2));
for (var g of data.results) console.log(g.title, g.data.map(function (d) { return d.ratio.toFixed(0); }).join(' '));
```

**기간 규칙** — 직전 연도의 **1월~12월 전체**를 쓴다. 시즌성을 보려는 것이므로
"최근 12개월 롤링"은 쓰지 않는다. 2026년에 돌리면 2025-01-01 ~ 2025-12-31.

데이터랩은 **상대값(0~100)**이라 그 자체가 검색량이 아니다. 절대 검색량은 검색광고 API 값을 쓰고,
데이터랩은 **월별 오르내림 모양**에만 쓴다.

### 1-B. 광고 (섹션 04 재료)

```bash
cd ~/competitor-tools && node ad-count.mjs "브랜드A" "브랜드B" "브랜드C"
```

`~/competitor-tools/ad-count.mjs`:

```javascript
// 메타 활성 광고 수 + 게재 시작월 분포. 사용법: node ad-count.mjs "브랜드1" "브랜드2"
import { chromium } from 'playwright';
var names = process.argv.slice(2);
if (!names.length) { console.error('브랜드명을 인자로 주세요'); process.exit(1); }
var browser = await chromium.launch({ headless: true });
var page = await (await browser.newContext({ locale: 'ko-KR' })).newPage();
for (var q of names) {
  try {
    await page.goto('https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=KR&q=' +
      encodeURIComponent(q) + '&search_type=keyword_unordered', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(9000);
    for (var i = 0; i < 12; i++) { await page.mouse.wheel(0, 4000); await page.waitForTimeout(900); }
    var r = await page.evaluate(function () {
      var t = document.body.innerText || '';
      var count = t.split('\n').map(function (s) { return s.trim(); })
        .find(function (l) { return /결과/.test(l) && /\d/.test(l); }) || '결과 표시 없음';
      var dates = [...t.matchAll(/(\d{4})\.\s*(\d{1,2})\.\s*\d{1,2}\.\s*에 게재 시작함/g)]
        .map(function (m) { return m[1] + '-' + String(m[2]).padStart(2, '0'); });
      var months = {}; for (var d of dates) months[d] = (months[d] || 0) + 1;
      var copy = [...new Set(t.split('\n').map(function (s) { return s.trim(); })
        .filter(function (l) { return l.length >= 12 && l.length <= 90 &&
          !/라이브러리 ID|게재 시작함|광고 상세|드롭다운|플랫폼|활성|검색|필터|정렬|Meta/.test(l); }))].slice(0, 20);
      return { count: count, sampled: dates.length, months: months, copy: copy };
    });
    console.log(JSON.stringify({ brand: q, ...r }, null, 1));
  } catch (e) { console.log(JSON.stringify({ brand: q, error: e.message.slice(0, 80) })); }
}
await browser.close();
```

읽는 법 — `count`는 후보 간 **상대 비교**용, `months`는 **여러 달에 퍼지면 상시 / 한 달에 몰리면 버스트**,
`copy`는 섹션 04 카피 카드의 재료다.

**단서를 반드시 남긴다.** 이 검색은 브랜드명이 들어간 광고를 넓게 잡아 제휴·리셀러가 섞인다.
모든 후보에 같은 방식을 썼으므로 상대 비교는 유효하지만 절대 건수는 **상한**이다.

### 1-C. 리뷰·커뮤니티 (섹션 03·05 재료)

여기가 이 스킬의 값어치다. 검색량과 광고는 규모만 알려주고, **왜 사고 왜 안 사는지는 여기서 나온다.**

| 어디서 | 무엇을 |
|--------|--------|
| 자사몰·오픈마켓 리뷰 | **1점·2점 리뷰의 공통 불만 TOP 3**. 별점 높은 리뷰는 정보가 적다 |
| 네이버 블로그 | "브랜드명 + 후기" 검색. **내돈내산과 협찬을 구분**해 적는다 |
| 네이버 카페·커뮤니티 | "브랜드명 + 비교 / 실패 / 환불" 검색. 광고가 안 닿는 진짜 대화 |

**1점 리뷰가 USP 의 원천이다.** 경쟁사가 공통으로 욕먹는 지점 = 기준 브랜드가 비집을 자리.
브랜드마다 불만 키워드를 세어 상위 항목을 남긴다. 섹션 05 의 "불만 → 기회 앵글"이 여기서 나온다.

### 리서치 규칙

- **모르는 것은 비워둔다.** 숫자를 추정해 채우지 않는다. `자료 없음`이라고 적는다
- 숫자에는 **출처와 기준 시점**을 함께 적는다. 둘 중 하나라도 없으면 그 숫자를 쓰지 않는다
- 같은 사실을 서로 다른 출처에서 확인한다. 한 곳에서만 나온 값은 그렇다고 표시한다
- 기준 브랜드에만 후하게 쓰지 않는다. 같은 잣대로 적는다

---

## 확인 지점 — 여기서 한 번 멈춘다

수집이 끝나면 **반드시 멈추고** 아래를 보여준 뒤 사용자 응답을 기다린다.

```
## 수집 완료

| 브랜드 | 검색량 | 광고 | 리뷰 | 커뮤니티 |
|--------|--------|------|------|----------|
| {브랜드} | ✅ | ✅ | ⚠ 일부 | ❌ |

### 비어 있는 것
- {브랜드}: {무엇이 없는지}

이대로 만들까요? 더 찾아야 할 것이 있으면 말씀해 주세요.
```

사용자가 보강을 요청하면 그 부분만 다시 모으고 이 지점으로 돌아온다.
**이후로는 멈추지 않고 대시보드까지 간다.**

---

## Step 2 — 대시보드 (7개 섹션, 순서 고정)

파일 하나로 만든다. 좌측에 섹션 네비게이션, 우측에 내용.

### 01. 브랜드 검색량

- 브랜드별 **합산 검색량 카드**. 펼치면 파생 키워드별 검색량 표
- **월별 트렌드 라인 차트** — 직전 연도 1~12월, 브랜드별 선 하나씩
- 부제는 "월별 브랜드 검색 트렌드 ({연도})" · "네이버 월간 검색량 기준"
- **계산식·API 이름을 화면에 쓰지 않는다**

### 02. 시장 분석

- 카테고리 규모·성장률 카드 (**출처 표기 필수**)
- 브랜드별 포지셔닝 카드 — 포지셔닝 / 강점 / 약점. 긴 문단 금지, 불릿으로
- 비교 테이블 — 핵심 기술 · 가격대 · 유통 · 타겟 · 광고 강도
- 인사이트 카드 2개 — 제품 포지셔닝 / 차별화 지점

### 03. 타겟 페르소나

- **6개.** 이름을 붙이지 말고 성향과 인구통계로 구분한다
- 각각 **Pain → Desire → Solution** 순서
- Solution 은 **기준 브랜드 제품으로만** 쓴다. 경쟁사 제품을 해결책에 넣지 않는다
- Solution 은 제품명 나열이 아니라 **"그 Pain 을 어떻게 푸는가"**를 쓴다
- 근거는 1-C 의 리뷰·키워드다. 지어내지 않는다

### 04. 크리에이티브

- 활성 광고 수 표 (한 줄. 차트로 부풀리지 않는다)
- **키워드 히트맵** — 브랜드 탭 전환. 블로그·카페에서 모은 실제 표현 기준.
  건수가 적으면 "표본이 적습니다"라고 적는다
- **니치 포인트** — 경쟁사에 없는 영역 = 기준 브랜드 기회.
  단 **기준 브랜드 고유 키워드(제품명·자체 용어)는 제외**한다.
  "우리 제품명이 경쟁사에 없다"는 당연한 이야기라 기회가 아니다.
  성분·효능·증상 같은 **카테고리 공통 키워드**에서만 빈 영역을 찾는다
- **카피 카드 6개** — 어두운 배경에 큰 카피 + 소구점·타겟 태그

### 05. 고객 여론

- 브랜드별 **워드클라우드 3개**
- 여론 톤 카드 3개 — 내돈내산 비율이 뜻하는 것, 불만 키워드가 향하는 곳
- **경쟁사 불만 → 기준 브랜드 기회 앵글 3카드** (이 섹션의 핵심)
  - 기준 브랜드: 카테고리 공통 불만
  - 경쟁사 A·B: 그 브랜드 고유 불만 → 기준 브랜드가 잡을 각도

### 06. 전략적 시사점

- **SWOT 2×2 그리드**, 칸마다 3개씩
- 각 항목은 `S1.` `W2.` 번호 + 항목명 + 설명
- 서술형으로 쓴다. 여기서 숫자를 다시 늘어놓지 않는다

### 07. 종합 요약

- **핵심 승부처 3가지** — 큰 숫자나 짧은 문구 + 설명
- **지금 당장 가능한 것 3가지**
- **반드시 주의할 것 3가지**

---

## 절대 넣지 않는 것

- 이모지
- 단정적 표현 — "1위다", "최고다", "확실하다"
- 비유 — "비타민 같은", "기침약 같은"
- 경쟁사 선정 근거, 사용한 도구·API 이름, 계산식 (읽는 사람에게 필요 없다)
- 같은 내용을 표와 차트로 두 번
- 실행 계획·매체 플랜 (이 스킬의 일이 아니다)

## 톤

- **가설 기반** — "~로 보입니다", "~를 검토해볼 수 있습니다", "~일 가능성이 있습니다"
- 읽는 사람이 이 카테고리를 처음 볼 수도 있다고 가정한다
- 근거 없는 해석을 쓰지 않는다. 모든 해석은 위에서 모은 데이터에 닿아 있어야 한다

## 기술 요구사항

- **단일 HTML 파일.** 빌드 도구 없이 더블클릭으로 열려야 한다
- 스타일은 파일 안에. 차트는 CDN 스크립트 한 개까지
- 좁은 화면에서 표·차트만 가로 스크롤되게 하고 페이지 전체가 밀리지 않게 한다
- 왼쪽 네비게이션은 모바일에서 접는다
- **출처 없는 숫자를 화면에 쓰지 않는다.** 없는 칸은 `자료 없음`으로 둔다
- **같은 정의의 지표가 비교 대상 전부에 있을 때만** 한 차트에 넣는다.
  분모가 다른 값을 한 축에 겹치지 않는다. 막대 길이는 값에 비례시킨다

## 저장

`{YYYY-MM}-{기준브랜드}-competitor.html` 로 지금 폴더에 저장하고 경로를 알려준다.
중립 비교라 기준 브랜드가 없으면 `{YYYY-MM}-{카테고리}-competitor.html`.

**파일명 맨 앞의 연월을 빼지 않는다** — 다음 달에 같은 브랜드를 다시 돌릴 때 지난달 파일을
덮어써서 월별 비교가 불가능해진다. 같은 이름이 이미 있으면 덮어쓰지 말고 알린다.

## 마지막에 반드시 밝힐 것

- **못 채운 칸** — 어느 브랜드의 무엇이 비었는지
- **한 출처에서만 나온 값** — 교차 확인이 안 된 것
- **기준 시점** — 언제까지의 정보로 만든 분석인지
- **빼먹은 섹션** — API 키가 없어 01 을 뺐다면 그 사실

## 하지 않는 것

- 못 찾은 수치를 그럴듯하게 채우지 않는다
- 확인 지점을 건너뛰고 끝까지 달리지 않는다
- 기준 브랜드에 유리한 쪽으로 데이터를 고르지 않는다
- 로그인이 필요한 페이지나 유료 자료를 우회해서 가져오지 않는다
- API 키를 대화창이나 결과물에 출력하지 않는다
