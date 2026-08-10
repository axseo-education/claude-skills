#!/usr/bin/env python3
"""figure.illo 전수 캡처 + pageerror 카운트.

Usage: python3 shot.py <html경로> <출력프리픽스>
출력: <프리픽스>-illo1.png, -illo2.png … / 콘솔에 개수·에러

캡처한 PNG는 반드시 눈으로 확인한다 — 직선 트랩(수직·수평선 소실)과
레이아웃 실패(라벨 잘림·화살표 오지시)는 코드 리뷰로 잡히지 않는다.
"""
import sys
from playwright.sync_api import sync_playwright

src, out = sys.argv[1], sys.argv[2]
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=2)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("file://" + src)
    page.wait_for_timeout(2500)  # 웹폰트(Gaegu) 로드 대기

    figures = page.query_selector_all("figure.illo")
    for i, fig in enumerate(figures, 1):
        fig.screenshot(path=f"{out}-illo{i}.png")

    print(f"figures={len(figures)} pageerrors={len(errors)}")
    if errors:
        print("\n".join(errors[:3]))
    browser.close()
