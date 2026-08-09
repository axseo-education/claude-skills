# 일러 카탈로그

검증된 SVG 원본. 좌표를 그대로 쓰거나 라벨만 바꿔 재사용한다.
전부 Playwright 캡처로 눈검증 완료 — 직선 트랩 적용본이다.

---

## funnel-3stage — 3단 퍼널 (넓은 위 → 좁은 아래)

퍼널 단계별로 다른 것을 대응시킬 때. 왼쪽=수단, 오른쪽=대상 설명.
출처: 구글 광고 101 §02 (UF/MF/LF)

```html
<svg viewBox="0 0 880 430" role="img" aria-label="넓은 상단에서 좁은 하단으로 좁혀지는 3단 퍼널">
  <g class="fg">
    <circle cx="266" cy="44" r="7"/><circle cx="322" cy="30" r="7"/><circle cx="380" cy="46" r="7"/>
    <circle cx="438" cy="28" r="7"/><circle cx="496" cy="44" r="7"/><circle cx="548" cy="32" r="7"/>
    <circle cx="296" cy="74" r="7"/><circle cx="358" cy="70" r="7"/><circle cx="462" cy="72" r="7"/><circle cx="522" cy="70" r="7"/>
  </g>
  <path class="sk" d="M250 106 L378 256"/>
  <path class="sk" d="M560 106 L433 256"/>
  <path class="sk" d="M378 256 L379 322"/>
  <path class="sk" d="M432 256 L433 322"/>
  <path class="sk-ax" d="M292 155 L518 156"/>
  <path class="sk-ax" d="M333 205 L477 206"/>
  <text class="lbl" x="405" y="140" text-anchor="middle">UF</text>
  <text class="lbl" x="405" y="190" text-anchor="middle">MF</text>
  <text class="lbl" x="405" y="296" text-anchor="middle">LF</text>
  <text class="lblm" x="606" y="140">넓다</text>
  <text class="lblm" x="606" y="190">탐색 중</text>
  <text class="lblm" x="606" y="296">좁다</text>
  <text class="lbla" x="212" y="140" text-anchor="end">수단 A</text>
  <text class="lbla" x="212" y="190" text-anchor="end">수단 B</text>
  <text class="lbla" x="212" y="296" text-anchor="end">수단 C</text>
  <path class="sk-accent" d="M405 330 L406 368"/>
  <path class="sk-accent" d="M392 353 L406 370 L420 353"/>
  <text class="lbla" x="405" y="404" text-anchor="middle">결과</text>
  <text class="lblw" x="470" y="342">경고 문구</text>
</svg>
```

주의: 퍼널 목 옆에 화살표를 두면 오른쪽 설명 텍스트를 가리키는 것처럼 보인다 → 텍스트만 배치.

---

## flow-3step — 3단계 흐름 (박스 → 화살표 → 박스)

파이프라인·변환 과정. 각 박스 아래에 보조 설명.
출처: 구글 광고 101 §01 (PMax 색인 채굴)

```html
<svg viewBox="0 0 880 300" role="img" aria-label="3단계 흐름">
  <rect class="sk" x="20" y="66" width="196" height="128" rx="14"/>
  <text class="lbl" x="118" y="104" text-anchor="middle">1단계</text>
  <text class="lblm" x="118" y="132" text-anchor="middle">조건</text>
  <circle class="fg" cx="72" cy="162" r="7"/><circle class="fg" cx="96" cy="162" r="7"/>
  <circle class="fg" cx="120" cy="162" r="7"/><circle class="fg" cx="144" cy="162" r="7"/>
  <text class="lblm" x="118" y="228" text-anchor="middle">보조 설명</text>

  <path class="sk-accent" d="M228 130 L297 132"/>
  <path class="sk-accent" d="M282 118 L297 130 L282 142"/>

  <rect class="sk" x="308" y="46" width="232" height="168" rx="14"/>
  <text class="lbl" x="424" y="82" text-anchor="middle">2단계</text>
  <rect class="fa" x="332" y="102" width="128" height="16" rx="6"/>
  <text class="lblm" x="472" y="116">항목 A</text>
  <rect class="fa" x="332" y="130" width="104" height="16" rx="6"/>
  <text class="lblm" x="448" y="144">항목 B</text>
  <rect class="fg" x="332" y="158" width="58" height="16" rx="6"/>
  <text class="lbla" x="424" y="248" text-anchor="middle">판정</text>

  <path class="sk-accent" d="M552 130 L621 132"/>
  <path class="sk-accent" d="M606 118 L621 130 L606 142"/>

  <rect class="sk" x="632" y="66" width="228" height="128" rx="14"/>
  <text class="lbl" x="746" y="102" text-anchor="middle">3단계</text>
  <text class="lblm" x="746" y="130" text-anchor="middle">설명</text>
  <path class="sk-accent" d="M660 182 L698 174 L734 166 L772 156 L816 146"/>
  <path class="sk-accent" d="M800 140 L818 145 L812 162"/>
  <text class="lbla" x="746" y="248" text-anchor="middle">결과</text>
</svg>
```

주의: 박스 안 상승 화살표는 텍스트 아래(y≥146)로 내려야 겹치지 않는다.

---

## crossing-curves — 반대로 움직이는 두 지표 + 붕괴점

"보이는 숫자는 좋아지는데 실체는 나빠진다" 구조. 위험 구간이 한눈에 보인다.
출처: 구글 광고 101 §06 (리타게팅 함정)

```html
<svg viewBox="0 0 880 380" role="img" aria-label="두 지표가 반대로 움직이다 붕괴하는 그래프">
  <path class="sk-ax" d="M76 40 L78 306"/>
  <path class="sk-ax" d="M76 306 L820 308"/>
  <text class="lblm" x="820" y="336" text-anchor="end">시간 →</text>

  <path class="sk-accent" d="M96 268 C 200 244, 300 206, 400 176 C 470 155, 520 146, 560 142"/>
  <path class="sk-warn" d="M560 142 C 590 148, 606 190, 624 244 C 638 282, 652 296, 676 300"/>
  <text class="lbla" x="238" y="246">보이는 지표</text>
  <text class="lblw" x="646" y="264">붕괴</text>

  <path class="sk" d="M96 96 C 210 118, 330 152, 450 200 C 520 228, 560 254, 596 276"/>
  <text class="lbl" x="120" y="78">실체 지표</text>

  <path class="sk-ax" d="M560 60 L562 306" stroke-dasharray="7 9"/>
  <text class="lblw" x="572" y="80">임계점</text>
  <circle class="fw" cx="560" cy="142" r="9"/>

  <path class="sk-ax" d="M240 322 L241 300"/><path class="sk-ax" d="M360 322 L361 300"/>
  <text class="lblm" x="240" y="348" text-anchor="middle">개입</text>
  <text class="lblm" x="360" y="348" text-anchor="middle">개입</text>
</svg>
```

---

## pool-widen — 좁은 풀 vs 넓힌 풀 (동심원 대비)

모수·후보군이 넓어지면 무엇이 달라지는지. 안쪽 원=기존, 바깥 원=확장분.
출처: 메타 광고 101 §06 (UF로 후보 모수 충전)

```html
<svg viewBox="0 -34 880 374" role="img" aria-label="좁은 풀과 넓힌 풀 대비">
  <circle class="sk" cx="196" cy="150" r="102"/>
  <text class="lbl" x="196" y="42" text-anchor="middle">좁은 모수</text>
  <g class="fw">
    <circle cx="160" cy="118" r="10"/><circle cx="222" cy="112" r="10"/><circle cx="188" cy="158" r="10"/>
    <circle cx="242" cy="162" r="10"/><circle cx="152" cy="182" r="10"/><circle cx="212" cy="200" r="10"/>
  </g>
  <text class="lblw" x="196" y="288" text-anchor="middle">전부 비싼 것뿐</text>

  <path class="sk-accent" d="M330 148 L411 150"/>
  <path class="sk-accent" d="M396 136 L411 148 L396 160"/>
  <text class="lbla" x="370" y="122" text-anchor="middle">투입</text>

  <circle class="sk-accent" cx="646" cy="150" r="150"/>
  <circle class="sk" cx="614" cy="150" r="86"/>
  <text class="lbla" x="646" y="26" text-anchor="middle">넓어진 모수</text>
  <g class="fw">
    <circle cx="586" cy="126" r="10"/><circle cx="638" cy="122" r="10"/><circle cx="602" cy="166" r="10"/>
    <circle cx="654" cy="170" r="10"/><circle cx="578" cy="188" r="10"/>
  </g>
  <g class="fa">
    <circle cx="722" cy="106" r="10"/><circle cx="762" cy="150" r="10"/><circle cx="724" cy="200" r="10"/>
    <circle cx="676" cy="238" r="10"/><circle cx="588" cy="252" r="10"/><circle cx="676" cy="66" r="10"/>
  </g>
  <text class="lbla" x="646" y="322" text-anchor="middle">싼 것이 추가된다</text>
</svg>
```

주의: 원 상단 라벨은 viewBox 상단 여백(`0 -34`)이 없으면 테두리에 걸친다.
