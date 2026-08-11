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
필요한 도구는 아래 준비 단계에서 직접 설치하며, 전부 이 PC 안에서 돕니다.

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

**키는 각자 본인 계정으로 발급받는다.** 동료의 키를 받아 쓰거나 팀이 하나를 돌려쓰지 않는다 —
한 명이 흘리면 전부 막히고, 사용량이 섞여 누가 얼마나 썼는지 가릴 수 없다.
사용자가 "누구 키 좀 받아서 쓰면 안 되냐" 고 물으면 **직접 발급을 안내한다.**

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

**키가 없으면 브랜드를 자동으로 찾을 수 없다.** 검색량이 후보 필터의 1차 관문이기 때문이다.
그때는 **자동 탐색을 하지 않고**, 사용자가 비교 브랜드를 직접 지정해야 진행한다.

키 없이 진행하는 경우에도 **01 섹션을 빼지 않는다.** 섹션은 그대로 두고 `자료 없음`으로 채운 뒤,
왜 비었는지(키 미발급) 그 자리에 적는다. 7개 섹션 구조는 어떤 경우에도 깨지 않는다.

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

**숫자로 자른다.** 느낌으로 고르면 돌릴 때마다 다른 경쟁사가 나온다.

| 순위 | 조건 | 기준 (그대로 적용) | 왜 |
|------|------|-------------------|-----|
| **1** | 파생 키워드 **합산** 검색량 | **5,000 ~ 50,000** | 5,000 미만은 인지도 부족, 50,000 초과는 규모 상이 |
| **2** | 메타 활성 광고 수 | **50건 이상** | 20건 미만은 브랜딩 한 번 돌린 수준 |
| **3** | 사용자가 직접 지정한 브랜드 | **1·2를 못 넘어도 포함** | "이 브랜드와 비교해줘"는 그대로 따른다 |
| 4 | 게재 시작월 분산 | **2개월 이상** | 한 달 몰아 태운 건 캠페인 버스트지 퍼포먼스가 아니다 |
| 5 | 자사몰 보유 | 있음 | 랜딩을 봐야 전환 구조가 보인다 |
| 6 | 디지털 광고 집행 | 하는 중 | 홈쇼핑·오프라인 전용은 볼 소재가 없다 |

**1번이 2번보다 먼저다.** 검색량 밴드를 벗어나면 광고를 아무리 많이 돌려도 탈락이다.
검색량은 **브랜드명 단독이 아니라 파생 키워드 합산**으로 센다
("브랜드명"보다 "브랜드명 + 대표제품명"이 훨씬 높은 경우가 흔하다).

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

// 네이버는 검색량이 10 미만이면 숫자 대신 "< 10" 을 준다.
// 이걸 10 으로 읽으면 합산이 부풀고 5,000 하한 통과 판정이 틀어진다. null 로 남긴다.
function num(v) {
  if (typeof v === 'number') return v;
  var t = String(v).trim();
  if (t.indexOf('<') === 0) return null;      // "< 10" = 자료 없음
  var n = parseInt(t.replace(/[^0-9]/g, ''), 10);
  return isNaN(n) ? null : n;
}

var out = {};
for (var brand of process.argv.slice(2)) {
  var list = await keywordTool(brand);
  var rows = list
    .filter(function (k) { return k.relKeyword.replace(/\s/g, '').includes(brand.replace(/\s/g, '')); })
    .map(function (k) {
      var pc = num(k.monthlyPcQcCnt), mo = num(k.monthlyMobileQcCnt);
      var known = pc === null && mo === null ? null : (pc || 0) + (mo || 0);
      return { keyword: k.relKeyword, volume: known, source: known === null ? 'no_data' : 'searchad_api' };
    })
    .sort(function (a, b) { return (b.volume || 0) - (a.volume || 0); });
  var counted = rows.filter(function (r) { return r.volume !== null; });
  out[brand] = {
    total: counted.reduce(function (s, r) { return s + r.volume; }, 0),
    counted: counted.length, no_data: rows.length - counted.length,
    keywords: rows.slice(0, 20) };
  console.log(brand, '합산', out[brand].total, '· 집계', counted.length, '· 자료없음', out[brand].no_data);
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

**데이터랩 값은 상대지수(0~100)라 그 자체가 검색량이 아니다.** 차트에 그대로 올리면
축 단위가 거짓이 된다. 아래 둘 중 하나만 한다.

- **(권장) 추정 검색량으로 환산** — 브랜드마다
  `그 달 값 = 검색광고 월간 검색량 × (그 달 상대값 ÷ 그 브랜드 12개월 상대값 평균)`.
  차트 부제는 `네이버 월간 추정 검색량 기준`
- **환산하지 않으려면** 차트 부제를 `상대지수 (0~100)` 이라고 **명시**한다.
  이때는 브랜드 간 절대 크기를 비교하지 말라는 주석을 붙인다

`trend.json` 과 `volumes.json` 을 같이 읽어 환산한다. **둘 중 하나가 없으면 환산하지 않는다.**

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
      // 카피는 페이지 전체가 아니라 광고 카드 안에서만 뽑는다.
      // 전체 innerText 를 긁으면 안내문·필터 문구·다른 광고주 텍스트가 섞인다.
      // "라이브러리 ID" 텍스트에서 위로 올라가며 본문이 담긴 최소 카드 컨테이너를 찾는다.
      var cards = [];
      for (var el of document.querySelectorAll('div, span')) {
        if (!/라이브러리 ID/.test(el.textContent || '')) continue;
        if ([...el.children].some(function (c) { return /라이브러리 ID/.test(c.textContent || ''); })) continue;
        var node = el;
        while (node && (node.innerText || '').length < 80) node = node.parentElement;
        if (node && (node.innerText || '').length <= 2500 && cards.indexOf(node) === -1) cards.push(node);
      }
      var noise = /라이브러리 ID|게재 시작함|광고 상세|드롭다운|플랫폼|^활성$|이 크리에이티브|페이지는|더 보기|Sponsored/;
      var copy = [];
      for (var card of cards) {
        for (var line of (card.innerText || '').split('\n').map(function (x) { return x.trim(); })) {
          if (line.length >= 12 && line.length <= 90 && !noise.test(line)) copy.push(line);
        }
      }
      copy = [...new Set(copy)].slice(0, 20);
      return { count: count, sampled: dates.length, months: months, cards: cards.length, copy: copy };
    });
    console.log(JSON.stringify({ brand: q, ...r }, null, 1));
  } catch (e) { console.log(JSON.stringify({ brand: q, error: e.message.slice(0, 80) })); }
}
await browser.close();
```

읽는 법 — `count`는 후보 간 **상대 비교**용, `months`는 **여러 달에 퍼지면 상시 / 한 달에 몰리면 버스트**,
`copy`는 섹션 04 카피 카드의 재료다(광고 카드 안에서만 뽑는다). `cards`가 0이면 카피를 못 건진 것이니
**카피 카드를 지어내지 말고** 그 사실을 적는다.

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
- **VOC 4분류 카드 (4열)** — 고객이 망설이는 이유를 네 갈래로 나누고
  **각 칸에 실제 고객 문장을 그대로 인용**한다. 요약하지 말고 원문으로 붙인다.
  (예: 가격 저항 / 효과 의심 / 사용 번거로움 / 부작용 우려 — 카테고리에 맞게 정한다)
- **임팩트 박스 — USP 한 문장.** 위 전부를 한 줄로 압축한다

### 03. 타겟 페르소나

- **6개.** 이름을 붙이지 말고 성향과 인구통계로 구분한다
- 각각 **Pain → Desire → Solution** 순서
- Solution 은 **기준 브랜드 제품으로만** 쓴다. 경쟁사 제품을 해결책에 넣지 않는다
- Solution 은 제품명 나열이 아니라 **"그 Pain 을 어떻게 푸는가"**를 쓴다
- **USP 매칭** — 페르소나마다 어느 USP 가 걸리는지 표시한다. 안 걸리는 페르소나가 있으면
  그것도 그대로 둔다 (우리가 아직 못 잡는 층이라는 뜻이다)
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
- **임팩트 박스 — "경쟁사가 잃은 고객 → 우리 기회"** 를 한 문장으로

### 06. 전략적 시사점

- **SWOT 2×2 그리드**, 칸마다 최대 3개 (근거를 통과한 것만)
- 각 항목은 `S1.` `W2.` 번호 + 항목명 + 설명
- 서술형으로 쓴다. 여기서 숫자를 다시 늘어놓지 않는다

### 07. 종합 요약

- **핵심 승부처** 최대 3가지 — 큰 숫자나 짧은 문구 + 설명
- **지금 당장 가능한 것** 최대 3가지
- **반드시 주의할 것** 최대 3가지

---

## 절대 넣지 않는 것

- 이모지
- 단정적 표현 — "1위다", "최고다", "확실하다"
- 비유 — "비타민 같은", "기침약 같은"
- 경쟁사 선정 근거, 사용한 도구·API 이름, 계산식 (읽는 사람에게 필요 없다)
- 같은 내용을 표와 차트로 두 번
- 실행 계획·매체 플랜 (이 스킬의 일이 아니다)

## 해석은 낸다. 단 이 리포트 안의 데이터에 뿌리내려야 한다

해석·시사점·페르소나·요약은 **빼지 않는다.** 문제는 섹션의 존재가 아니라 근거 없는 내용이다.
아래 세 가지만 걸러낸다.

**금지 1 — 관측되지 않은 인과.** 비중이나 상관을 원인으로 단정하지 않는다.
> "브랜드명 검색이 70%다 → 광고로 만들어진 인지다 → 광고를 줄이면 검색도 준다"
> 검색 구성비는 *비중*만 보여준다. 광고 때문인지 카테고리 특성인지 이 데이터로는 모른다.

**금지 2 — 일반론.** 이 브랜드를 조사하지 않았어도 쓸 수 있는 말.
> "지명 검색이 약하니 카테고리 키워드를 먼저 확보"
> 어느 후발 브랜드에나 그대로 붙는다. 게다가 "카테고리 키워드가 더 얻기 쉽다"는 전제부터 검증되지 않았다.

**금지 3 — 완충어로 감싼 단정.** "~로 보입니다"를 붙여도 관측 밖 주장이면 금지다.
**완충어는 근거를 만들지 않는다.**

### 통과 기준 — 해석 하나당 세 문항

1. 뒷받침하는 **이 리포트의 구체 수치·관측**을 댈 수 있는가?
2. **그 근거를 지우면 무너지는가?** 안 무너지면 일반론이다 → 뺀다
3. 경쟁사 대비 **우리만 쓸 수 있는** 이유가 있는가?

> 문장 단위 자가 점검 — **"이 문장을 부정하려면 어떤 데이터가 필요한가? 그게 이 리포트에 있는가?"**
> 없으면 뺀다.

### 개수를 채우려 하지 마라

**위 섹션들의 "3개"는 상한이지 할당량이 아니다.** 기준을 통과한 것만 남긴다.
2개면 2개로 내고, 왜 적은지 한 줄 적는다.
**빈칸을 메우려다 일반론이 끼어드는 것이 이 리포트의 주된 실패 양상이다.**

## 톤

- **가설 기반** — "~로 보입니다", "~를 검토해볼 수 있습니다"
- 읽는 사람이 이 카테고리를 처음 볼 수도 있다고 가정한다

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
