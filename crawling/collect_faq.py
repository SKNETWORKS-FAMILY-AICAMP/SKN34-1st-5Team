"""
전기차 기업 FAQ 수집 스크립트
- 현대자동차: Selenium 쿠키 → GW API 호출
- 기아자동차: Selenium 카테고리 탭 클릭 + HTML 파싱
- 제네시스:   정적 HTML 파싱
"""

import csv
import time
import requests
from bs4 import BeautifulSoup
from datetime import date
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "faq"
OUTPUT_DIR.mkdir(exist_ok=True)

TODAY = date.today().isoformat()
FIELDS = ["company", "category", "sub_category", "question", "answer", "collected_at", "source_url"]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def make_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"user-agent={UA}")
    return webdriver.Chrome(options=opts)


def save_csv(rows: list[dict], path: Path):
    if not rows:
        print(f"  저장할 데이터 없음: {path.name}")
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  저장: {path.name} ({len(rows)}행)")


# ── 현대자동차 ───────────────────────────────────────────────────────────────
def scrape_hyundai(driver: webdriver.Chrome) -> list[dict]:
    print("\n[현대] 수집 시작")
    faq_url = "https://www.hyundai.com/kr/ko/e/customer/center/faq"
    api_base = "https://www.hyundai.com/kr/ko/gw/customer-support/v1/customer-support/faq"

    # Selenium으로 페이지 방문해 세션 쿠키 확보
    driver.get(faq_url)
    time.sleep(6)
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

    # category는 GET, list는 POST + JSON body
    get_headers = {
        "User-Agent": UA,
        "Accept": "application/json",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": faq_url,
    }
    post_headers = {
        **get_headers,
        "Content-Type": "application/json",
        "ep-channel": "homepage",
        "ep-ip": "127.0.0.1",
        "ep-jsessionid": "",
        "ep-menu-id": "",
    }

    # 메인 카테고리 (faqCategoryCode=Z019 필수)
    r = requests.get(
        f"{api_base}/category",
        params={"siteTypeCode": "H", "categoryType": "MAIN", "faqCategoryCode": "Z019"},
        headers=get_headers, cookies=cookies, timeout=10,
    )
    resp = r.json()
    main_cats = resp.get("data") or []
    if not main_cats:
        print(f"  카테고리 응답: {resp}")
        return []
    print(f"  메인 카테고리: {[c['faqCategoryName'] for c in main_cats]}")

    rows = []
    for cat in main_cats:
        cat_code = cat["faqCategoryCode"]
        cat_name = cat["faqCategoryName"]

        page = 1
        while True:
            # list API는 POST + JSON body (pageNo 사용)
            r3 = requests.post(
                f"{api_base}/list",
                json={
                    "siteTypeCode": "H",
                    "faqCategoryCode": cat_code,
                    "faqCode": "",
                    "faqSeq": "",
                    "searchKeyword": "",
                    "pageNo": page,
                    "pageSize": 100,
                    "externalYn": "",
                },
                headers=post_headers, cookies=cookies, timeout=10,
            )
            data = r3.json().get("data") or {}
            items = data.get("list") or []
            total = data.get("total", 0)

            for item in items:
                q = (item.get("faqQuestion") or "").strip()
                a_html = item.get("faqAnswer") or ""
                a = BeautifulSoup(a_html, "lxml").get_text(" ", strip=True)
                sub_name = item.get("faqName", "")
                if not q:
                    continue
                rows.append({
                    "company":      "현대자동차",
                    "category":     cat_name,
                    "sub_category": sub_name,
                    "question":     q,
                    "answer":       a,
                    "source_url":   faq_url,
                    "collected_at": TODAY,
                })

            if page * 100 >= total or not items:
                break
            page += 1
            time.sleep(0.3)
        time.sleep(0.5)

    print(f"  수집 완료: {len(rows)}건")
    return rows


# ── 기아자동차 ───────────────────────────────────────────────────────────────
def parse_kia_faq(driver: webdriver.Chrome, category: str) -> list[dict]:
    """현재 렌더링된 기아 FAQ 페이지에서 Q&A 파싱
    구조: .cmp-accor-faq > .cmp-accordion > .cmp-accordion__item
          질문: .cmp-accordion__header button (aria-controls=panel-id)
          답변: #panel-id
    """
    soup = BeautifulSoup(driver.page_source, "lxml")
    rows = []
    seen_q = set()

    # 모든 .cmp-accordion__item 요소 탐색 (PC+모바일 중복 있음)
    items = soup.find_all(class_=lambda c: c and "cmp-accordion__item" in (c if isinstance(c, list) else c.split()))
    for item in items:
        # 질문: 헤더 버튼 텍스트
        header = item.find(class_=lambda c: c and "cmp-accordion__header" in (c if isinstance(c, list) else c.split()))
        if not header:
            continue
        btn = header.find("button")
        if not btn:
            continue
        q = btn.get_text(strip=True)
        if not q or len(q) < 5 or q in seen_q:
            continue
        seen_q.add(q)

        # 답변: aria-controls → 해당 panel div
        panel_id = btn.get("aria-controls", "")
        a_tag = soup.find(id=panel_id) if panel_id else item.find(class_=lambda c: c and "cmp-accordion__panel" in (c if isinstance(c, list) else c.split()))
        a = a_tag.get_text(" ", strip=True) if a_tag else ""

        rows.append({
            "company":      "기아자동차",
            "category":     category,
            "sub_category": "",
            "question":     q,
            "answer":       a,
            "source_url":   "https://www.kia.com/kr/customer-service/center/faq",
            "collected_at": TODAY,
        })

    return rows


def scrape_kia(driver: webdriver.Chrome) -> list[dict]:
    print("\n[기아] Selenium 수집 시작")
    url = "https://www.kia.com/kr/customer-service/center/faq"
    driver.get(url)
    time.sleep(5)

    # PC/모바일 중복 제거 후 유효 탭 이름 추출
    soup0 = BeautifulSoup(driver.page_source, "lxml")
    tab_area = soup0.find(class_=lambda c: c and "cmp-faq-search-tab" in " ".join(c) if isinstance(c, list) else "cmp-faq-search-tab" in str(c or ""))
    seen_tabs, tabs = set(), []
    if tab_area:
        for btn in tab_area.find_all("button"):
            t = btn.get_text(strip=True)
            if t and t not in seen_tabs and t != "TOP 10":
                seen_tabs.add(t)
                tabs.append(t)
    print(f"  수집 탭: {tabs}")

    all_rows = []

    for tab_name in tabs:
        try:
            # 탭 클릭 (CSS selector로 텍스트 매칭)
            tab_btns = driver.find_elements(By.CSS_SELECTOR, ".cmp-faq-search-tab button")
            clicked = False
            for btn in tab_btns:
                if btn.text.strip() == tab_name:
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    time.sleep(4)
                    break
            if not clicked:
                continue

            # 더보기 버튼 반복 클릭 (모두 로드)
            for _ in range(30):
                try:
                    mores = driver.find_elements(By.CSS_SELECTOR,
                        "button[class*='more'], a[class*='more'], .btn-more, "
                        "button[class*='load'], .cmp-btn-more")
                    visible = [m for m in mores if m.is_displayed()]
                    if not visible:
                        break
                    driver.execute_script("arguments[0].click();", visible[0])
                    time.sleep(2)
                except Exception:
                    break

            rows = parse_kia_faq(driver, tab_name)
            print(f"  [{tab_name}] {len(rows)}건")
            all_rows.extend(rows)

        except Exception as e:
            print(f"  [{tab_name}] 오류: {e}")

    # 전역 중복 제거
    seen_q, unique = set(), []
    for row in all_rows:
        if row["question"] not in seen_q:
            seen_q.add(row["question"])
            unique.append(row)

    print(f"  수집 완료: {len(unique)}건")
    return unique


# ── 제네시스 ─────────────────────────────────────────────────────────────────
def scrape_genesis() -> list[dict]:
    print("\n[제네시스] HTML 수집 시작")
    url = "https://www.genesis.com/kr/ko/support/faq.html"
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"}, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    items = soup.find_all(class_="cp-faq__accordion-item")
    print(f"  발견 항목: {len(items)}개")

    rows = []
    for item in items:
        label = item.find(class_="accordion-label")
        category = label.get_text(strip=True).strip("[]") if label else ""
        title = item.find(class_="accordion-title")
        question = title.get_text(strip=True) if title else ""
        panel = item.find(class_="accordion-panel-inner")
        answer = panel.get_text(" ", strip=True) if panel else ""
        if not question:
            continue
        rows.append({
            "company":      "제네시스",
            "category":     category,
            "sub_category": "",
            "question":     question,
            "answer":       answer,
            "source_url":   url,
            "collected_at": TODAY,
        })

    print(f"  수집 완료: {len(rows)}건")
    return rows


# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    all_rows = []
    driver = make_driver()

    try:
        # 현대 (Selenium 쿠키 + API)
        try:
            rows = scrape_hyundai(driver)
            save_csv(rows, OUTPUT_DIR / "hyundai_faq.csv")
            all_rows.extend(rows)
        except Exception as e:
            print(f"[현대] 오류: {e}")

        # 기아 (Selenium)
        try:
            rows = scrape_kia(driver)
            save_csv(rows, OUTPUT_DIR / "kia_faq.csv")
            all_rows.extend(rows)
        except Exception as e:
            print(f"[기아] 오류: {e}")

    finally:
        driver.quit()

    # 제네시스 (정적 HTML)
    try:
        rows = scrape_genesis()
        save_csv(rows, OUTPUT_DIR / "genesis_faq.csv")
        all_rows.extend(rows)
    except Exception as e:
        print(f"[제네시스] 오류: {e}")

    # 통합 저장
    if all_rows:
        save_csv(all_rows, OUTPUT_DIR / "all_faq.csv")

    # 로그
    log_path = OUTPUT_DIR / "collect_log.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"수집 일시: {TODAY}\n\n=== 결과 ===\n")
        for company in ["현대자동차", "기아자동차", "제네시스"]:
            cnt = sum(1 for r in all_rows if r["company"] == company)
            f.write(f"  {company}: {cnt}건\n")
        f.write(f"\n  합계: {len(all_rows)}건\n")

    print(f"\n[로그] {log_path}")
    print(f"\n완료: 총 {len(all_rows)}건")


if __name__ == "__main__":
    main()
